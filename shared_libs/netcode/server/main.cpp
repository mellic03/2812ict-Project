#include "ng_game.hpp"


FaceVertices fshared(2);


void process_verts( NG_Server *server, NG_ClientRep *client )
{
    // Load server->buffer into fshared[id]
    int id = client->id;
    memcpy(fshared[id], server->buffer.body, NUM_VERTS*sizeof(vertex));
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

        sprintf(server.buffer.body, "Hello, client %d.", num_connected);
        NG_toClient(&server, &clients[num_connected], NG_MESSAGE_TEXT);

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
            process_verts(&server, client);

            printf(
                "Received data: %f %f %f\n",
                fshared[0][0].position.x,
                fshared[0][0].position.y,
                fshared[0][0].position.z
            );
        }
    }


    NG_Server_exit(&server, 0);

    return 0;
}

