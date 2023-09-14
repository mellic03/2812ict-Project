#include "ng_game.hpp"


FaceVertices fshared(2);




void verts_for_all(NG_Server *server, NG_ClientRep *clients, int num_clients)
{

    for (int i=0; i<num_clients; i++)
    {
        for (int j=0; j<num_clients; j++)
        {
            if (j == i)
                continue;
            
            sprintf(server->buffer.body, "%c\0", (unsigned char)i);
            NG_toClient(server, &clients[j], NG_MESSAGE_VERTS_USER);

            memcpy(server->buffer.body, fshared[i], NUM_VERTS*sizeof(vertex));
            NG_toClient(server, &clients[j], NG_MESSAGE_VERTS_RES);
        }
    }
}


int main( int argc, char **argv )
{
    if (argc != 3)
    {
        printf("usage: server <port number> <required players>\n");
        return 1;
    }

    uint16_t port = atoi(argv[1]);

    NG_Server server = NG_Server_new(port);
    NG_Server_listen(&server);


    int num_connected = 0;
    int num_needed = atoi(argv[2]);
    NG_ClientRep *clients = (NG_ClientRep *)calloc(num_needed, sizeof(NG_ClientRep));

    while (num_connected < num_needed)
    {
        clients[num_connected] = NG_Server_accept(&server, num_connected);
        printf("[C%d >> server] connected.\n", num_connected);

        sprintf(server.buffer.body, "%c\0", (unsigned char)(num_connected));
        NG_toClient(&server, &clients[num_connected], NG_MESSAGE_USERID);

        num_connected += 1;
    }


    int current = -1;
    while (num_connected > 0)
    {
        current = (current + 1) % num_needed;
        NG_ClientRep *client = &clients[current];

        if (client->connected == false)
            continue;

        NG_MessageType msgtype;
        NG_toClient(&server, client, NG_MESSAGE_VERTS_REQ);
        NG_fromClient(&server, client, &msgtype);

        if (msgtype == NG_MESSAGE_QUIT)
        {
            NG_toClient(&server, client, NG_MESSAGE_END);
            client->connected = false;
            num_connected -= 1;
        }

        else if (msgtype == NG_MESSAGE_VERTS_RES)
        {
            int id = client->id;
            memcpy(fshared[id], server.buffer.body, NUM_VERTS*sizeof(vertex));
        }

        if (current == num_needed-1)
        {
            verts_for_all(&server, clients, num_needed);
        }
    }


    NG_Server_exit(&server, 0);

    return 0;
}

