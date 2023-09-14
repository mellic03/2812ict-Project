#include "ng_client.hpp"


NG_Client
NG_Client_new()
{
    NG_Client client;

    client.buffer = NG_Buffer_new();
    client.socketdesc = socket(AF_INET, SOCK_STREAM, 0);

    if (client.socketdesc < 0)
        perror("Could not create socket");

    return client;
}


void
NG_Client_connect( NG_Client *client, NG_ServerRep *server )
{
    int res = connect(
        client->socketdesc,
        (struct sockaddr *) &server->addr,
        sizeof(server->addr)
    );

    if (res == -1)
    {
        printf("[NG_Client_connect] Failure connecting to server\n");
        NG_Client_exit(client, 1);
    }
}


/** Close the client socket connection and exit the program.
 * @param server pointer to NG_Client.
 * @param retcode value to return to operating system. 
*/
void
NG_Client_exit( NG_Client *client, int retcode )
{
    close(client->socketdesc);
    exit(retcode);
}



/** Send a message to the server.
 * @note If sending text, place the text in client->buffer.body.
 * @note client->buffer will be cleared after sending the message.
 * @param msgtype the message type.
*/
void
NG_toServer( NG_Client *client, NG_ServerRep *server, NG_MessageType msgtype )
{
    *client->buffer.header = (char)msgtype;

    int res = send(client->socketdesc, client->buffer.data, NG_BUFFER_SIZE, MSG_CONFIRM);
    if (res < 0)
    {
        printf("[NG_toServer] Error sending data to server\n");
        NG_Client_exit(client, 1);
    }

    NG_Buffer_clear(&client->buffer);
}


void
NG_fromServer( NG_Client *client, NG_ServerRep *server, NG_MessageType *msgtype )
{
    NG_Buffer_clear(&client->buffer); // zero-out all data first

    int res = recv(client->socketdesc, client->buffer.data, NG_BUFFER_SIZE, 0);
    if (res < 0)
    {
        printf("[NG_fromServer] Error recieving data from server\n");
        NG_Client_exit(client, 1);
    }

    NG_MessageType msg_type = (NG_MessageType)(*client->buffer.header);

    if (msgtype != NULL)
        *msgtype = msg_type;
}



NG_ServerRep
NG_ServerRep_new( in_addr_t ip, uint16_t port )
{
    NG_ServerRep server;
    server.addr.sin_addr.s_addr = ip;
    server.addr.sin_family = AF_INET;
    server.addr.sin_port = htons(port);
    return server;
}
