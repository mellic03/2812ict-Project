#include "ng_server.hpp"



NG_Server
NG_Server_new( uint16_t port )
{
    NG_Server server;

    server.port = port;
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

    return client;
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


size_t
NG_Server_writen( NG_Server *server, NG_ClientRep *client, void *data, size_t n )
{
    return writen(client->socketdesc, data, n);
}

size_t
NG_Server_readn( NG_Server *server, NG_ClientRep *client, void *data, size_t n )
{
    return readn(client->socketdesc, data, n);
}

