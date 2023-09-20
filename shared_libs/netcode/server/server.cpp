#include "ng_server.hpp"




int main( int argc, char **argv )
{
    SharedVertices vshared(2);

    uint16_t port          = atoi(argv[1]);
    int      num_needed    = atoi(argv[2]);
    int      num_connected = 0;


    NG_Server server = NG_Server_new(port);
    NG_Server_listen(&server);

    NG_ClientRep *clients = (NG_ClientRep *)calloc(num_needed, sizeof(NG_ClientRep));

    while (num_connected < num_needed)
    {
        clients[num_connected] = NG_Server_accept(&server, num_connected);

        NG_MessageType msgtype = TEXT;
        NG_Server_writen(&server, &clients[num_connected], &msgtype, 1);

        num_connected += 1;
    }


    int curr = -1;
    while (1)
    {
        curr = (curr + 1) % num_needed;

        NG_MessageType msgtype = VERT_REQ;
        NG_Server_writen(&server, &clients[curr], &msgtype, 1);
        NG_Server_readn(&server, &clients[curr], vshared[curr], NUM_VERTS*sizeof(vertex));


    }



    return 0;
}