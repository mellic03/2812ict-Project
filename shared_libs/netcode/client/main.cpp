#include "../common/ng_common.hpp"
#include "ng_client.hpp"


FaceVertices *fsharedptr;


/*
    Process for receiving other users vertex data

    1. Receive NG_MESSAGE_VERTS_USER. The first byte of buffer.body will be the userid.
    2. Send NG_MESSAGE_VERTS_REQ to server.
    3. Wait for NG_MESSAGE_VERTS_RES from server.
    4. server::fshared[userid] is now in client->buffer.body.
*/



extern "C" void
child_main( char *hostname, uint16_t port )
{
    FaceVertices &fshared = *fsharedptr;

    // Wait for message and then perform the appropriate action
    uint8_t userid;
    NG_Client client = NG_Client_new();
    NG_ServerRep server = NG_ServerRep_new(inet_addr(hostname), port);
    NG_Client_connect(&client, &server);

    while (1)
    {
        NG_MessageType msgtype;
        NG_fromServer(&client, &server, &msgtype);
    
        if (msgtype == NG_MESSAGE_USERID)
        {
            userid = client.buffer.body[0];
            *fshared.m_shared_byte = userid;
            printf("[USERID] %d\n", userid);
        }

        else if (msgtype == NG_MESSAGE_TEXT)
        {
            printf("[TEXT] %s\n", client.buffer.body);
        }

        else if (msgtype == NG_MESSAGE_VERTS_REQ)
        {
            printf("[VERTS_REQ]\n");
            memcpy(client.buffer.body, fshared[userid], NUM_VERTS*sizeof(vertex));
            NG_toServer(&client, &server, NG_MESSAGE_VERTS_RES);
        }

        else if (msgtype == NG_MESSAGE_VERTS_USER)
        {
            int id = client.buffer.body[0];
            printf("this id: %d, them id: %d\n", userid, id);
            NG_fromServer(&client, &server, NULL);
            memcpy(fshared[id], client.buffer.body, NUM_VERTS*sizeof(vertex));
        }

        else if (msgtype == NG_MESSAGE_END)
        {
            printf("[END]\n");
            NG_Client_exit(&client, 0);
        }
    }

}


/** Give the user's face vertex array to the client program.
*/
extern "C" void
client_update_vertices( void *npverts )
{
    FaceVertices &fshared = *fsharedptr;
    memcpy(fshared[*fshared.m_shared_byte], npverts, NUM_VERTS*sizeof(vertex));    
}


/** Retrieve another users vertex data and store it in npverts.
*/
extern "C" void
client_get_vertices( void *npverts, int id )
{
    FaceVertices &fshared = *fsharedptr;
    memcpy(npverts, fshared[id], NUM_VERTS*sizeof(vertex));    
}


/** Retrieve userid.
*/
extern "C" int
client_get_userid()
{
    FaceVertices &fshared = *fsharedptr;
    return *fshared.m_shared_byte;
}


/** Call to initialize client from Python
*/
extern "C" void
client_init( char *hostname, uint16_t port )
{
    fsharedptr = new FaceVertices(2);

    FaceVertices &fshared = *fsharedptr;
    fshared[0][0].position = { 10.0f, 11.0f, 12.0f };

    if (fork() == 0)
        child_main(hostname, port);
}


int main(int argc, char **argv)
{
    fsharedptr = new FaceVertices(2);

    FaceVertices &fshared = *fsharedptr;
    fshared[0][0].position = { 10.0f, 11.0f, 12.0f };

    if (fork() == 0)
        child_main(argv[1], atoi(argv[2]));

    return 0;
}



