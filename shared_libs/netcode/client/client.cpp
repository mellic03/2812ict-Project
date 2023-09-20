#include "ng_client.hpp"



int main( int argc, char **argv )
{
    SharedVertices vshared(2);
    uint8_t userid = 0;

    char *   hostname = argv[1];
    uint16_t port     = atol(argv[2]);

    NG_Client client = NG_Client_new();
    NG_ServerRep server = NG_ServerRep_new(inet_addr(hostname), port);
    NG_Client_connect(&client, &server);

    char *buffer = (char *)malloc(NUM_VERTS*sizeof(vertex));


    NG_MessageType msgtype;

    while (1)
    {
        NG_Client_readn(&client, &server, &msgtype, 1);

        if (*buffer == VERT_REQ) // Vertex data request, send vertices to server
        {
            NG_Client_writen(&client, &server, vshared[userid], NUM_VERTS*sizeof(vertex));
        }

        else if (*buffer == VERT_USR) // Server wants to send vertex data of another user.
        {
            uint8_t other_userid;

            // 1 byte, userid of other user.
            NG_Client_readn(&client, &server, &other_userid, 1);
            
            // Read vertex data of other user into the correct array in vshared.
            NG_Client_readn(&client, &server, vshared[other_userid], NUM_VERTS*sizeof(vertex));
        }

    }

    return 0;
}


