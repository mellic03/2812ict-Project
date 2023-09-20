#include "ng_client.hpp"


NG_Client
NG_Client_new()
{
    NG_Client client;

    client.socketdesc = socket(AF_INET, SOCK_STREAM, 0);

    if (client.socketdesc < 0)
        perror("Could not create socket");


    struct timeval timeout;
    timeout.tv_sec = 30;

    int res = setsockopt(
        client.socketdesc,
        SOL_SOCKET,
        SO_RCVTIMEO,
        &timeout,
        sizeof(timeout)
    );

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




size_t
NG_Client_writen( NG_Client *client, NG_ServerRep *server, void *data, size_t n )
{
    return writen(client->socketdesc, data, n);
}

size_t
NG_Client_readn( NG_Client *client, NG_ServerRep *server, void *data, size_t n )
{
    return readn(client->socketdesc, data, n);
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
