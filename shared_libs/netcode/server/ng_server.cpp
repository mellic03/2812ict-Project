#include "ng_server.hpp"



NG_Server
NG_Server_new( uint16_t port )
{
    NG_Server server;

    server.port = port;
    server.buffer = NG_Buffer_new();
    server.socketdesc = socket(AF_INET, SOCK_STREAM, 0);
    server.addr.sin_addr.s_addr = INADDR_ANY;
    server.addr.sin_family = AF_INET;
    server.addr.sin_port = htons(port);

    int res = bind(
        server.socketdesc,
        (struct sockaddr *) &server.addr,
        sizeof(server.addr)
    );

    if (res < 0)
    {
        printf("[NG_Server_new] Cannot access port %u.\n", port);
        NG_Server_exit(&server, 1);
    }


    // Set receive timeout duration -----------------------------
    struct timeval timeout;
    timeout.tv_sec = NG_SERVER_TIMEOUT;

    res = setsockopt(
        server.socketdesc,
        SOL_SOCKET,
        SO_RCVTIMEO,
        &timeout,
        sizeof(timeout)
    );

    if (res < 0)
    {
        printf("Error setting socket timout duration.\n");
        NG_Server_exit(&server, 1);
    }
    // ----------------------------------------------------------

    return server;
}


int
NG_Server_listen( NG_Server *server )
{
    int res = listen(server->socketdesc, 10);
 
    if (res < 0)
    {
        printf("[NG_Server_listen] Error listening on port %u\n", server->port);
        NG_Server_exit(server, 1);
    }

    else
    {
        printf("Listening on port %u...\n", server->port);
    }

    return res;
}


NG_ClientRep
NG_Server_accept( NG_Server *server, int id )
{
    NG_ClientRep client = NG_ClientRep_new();
    client.id = id;

    socklen_t clientlen = sizeof(client.addr);
    client.socketdesc = accept(
        server->socketdesc,
        (struct sockaddr *) &client.addr,
        &clientlen
    );

    if (client.socketdesc < 0)
    {
        printf("[NG_Server_accept] Failure accepting socket connection.\n");
        NG_Server_exit(server, 1);
    }

    client.connected = true;

    return client;
}


/** Check if a message received by the server is valid.
 * @note Only call this after NG_fromClient().
 * @return True if valid message, false otherwise (infringement).
*/
bool
NG_Server_msgValid( NG_Server *server )
{
    NG_MessageType msgtype = (NG_MessageType)(*server->buffer.header);

    // Is an infringement if the client sent any messages other than MOVE or QUIT.
    if (msgtype < NG_MESSAGE_MOVE || msgtype > NG_MESSAGE_QUIT)
    {
        return false;
    }

    // If MOVE, ensure the rest of the buffer is valid.
    if (msgtype == NG_MESSAGE_MOVE)
    {
        return NG_Buffer_bodyValid(&server->buffer);
    }

    // Otherwise, message must be QUIT (due to the first condition)
    // The buffer body containing data alongside a QUIT message is an infringement.
    if (strlen(server->buffer.body) != 0)
    {
        return false;
    }

    // By this point the buffer must hold a valid message.
    return true;
}


/** Close the server socket connection and exit the program.
 * @param server pointer to NG_Server.
 * @param retcode value to return to operating system. 
*/
void
NG_Server_exit( NG_Server *server, int retcode )
{
    close(server->socketdesc);
    exit(retcode);
}



bool
NG_ClientRep_alive( NG_ClientRep *client )
{

    return client->connected;
}


/** Disconnect a client from the server.
*/
void
NG_ClientRep_cut( NG_Server *server, NG_ClientRep *client )
{
    NG_Buffer_clear(&server->buffer);
    NG_toClient(server, client, NG_MESSAGE_END);
    client->connected = false;
}


NG_ClientRep
NG_ClientRep_new()
{
    NG_ClientRep client;
    client.socketdesc = 0;
    client.connected  = false;
    client.id = -1;
    return client;
}


/** Send a message to the client.
 * @note If sending text, place the text in server->buffer.body.
 * @note server->buffer will be cleared after sending the message.
 * @param msgtype the message type.
*/
void
NG_toClient( NG_Server *server, NG_ClientRep *client, NG_MessageType msgtype )
{
    *server->buffer.header = (char)msgtype;

    const char *msg_str = NG_MessageType_str(msgtype);
    printf("[server >> C%d] %s", client->id, msg_str);
    if (msgtype == NG_MESSAGE_TEXT || msgtype == NG_MESSAGE_ERROR)
        printf(" \"%s\"", server->buffer.body);
    printf("\n");

    int res = send(client->socketdesc, server->buffer.data, NG_BUFFER_SIZE, MSG_CONFIRM);
    if (res < 0) // Socket error.
    {
        printf("[NG_toClient] Error sending data to client\n");
        NG_Server_exit(server, 1);
    }

    // NG_Buffer_clear(&server->buffer);
}


/** Receive a message from the client.
 * @param msgtype pointer to return message type of incoming message.
 * @note Any text sent alongside the message will be placed inside server->buffer.body.
 * @note The message type can be retrieved manually by casting the value in
 *       sever->buffer.header to a NG_MessageType.
*/
void
NG_fromClient( NG_Server *server, NG_ClientRep *client, NG_MessageType *msgtype )
{
    NG_Buffer_clear(&server->buffer);

    int res = recv(client->socketdesc, server->buffer.data, NG_BUFFER_SIZE, 0);
    if (res < 0) // Socket error.
    {
        *msgtype = NG_MESSAGE_TIMEOUT;
        return;
    }

    *msgtype = (NG_MessageType)(*server->buffer.header);

    const char *msg_str = NG_MessageType_str(*msgtype);
    printf("[C%d >> server] %s", client->id, msg_str);
    if (*msgtype == NG_MESSAGE_MOVE)
        printf(" \"%s\"", server->buffer.body);
    printf("\n");

}

