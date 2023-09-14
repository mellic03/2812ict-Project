#include "ng_game.hpp"



NG_GameData
NG_GameData_new( int required_players )
{
    NG_GameData gd;

    gd.curr_sum = 0;
    gd.num_connected = 0;
    gd.required_players = required_players;
    gd.curr_player = 0;
    gd.clients = (NG_ClientRep *)calloc(required_players, sizeof(NG_ClientRep));

    return gd;
}



void
NG_GameStage_initiate( NG_Server *server )
{
    int res = NG_Server_listen(server);

    if (res < 0)
    {
        printf("[main] Error listening on port %u\n", server->port);
        NG_Server_exit(server, 1);
    }

    else
    {
        printf("Listening on port %u...\n", server->port);
    }
}


void
NG_GameStage_join( NG_Server *server, NG_GameData *gd )
{
    while (gd->num_connected < gd->required_players)
    {
        gd->clients[gd->num_connected] = NG_Server_accept(server, gd->num_connected);

        sprintf(
            server->buffer.body,
            "Welcome player %d.\nEnter your move when \"GO >> \" appears on the terminal.",
            gd->num_connected
        );
        NG_toClient(server, &gd->clients[gd->num_connected], NG_MESSAGE_TEXT);

        gd->num_connected += 1;
    }
}

void
NG_Game_cutPlayer( NG_Server *server, NG_ClientRep *client,
                   NG_GameData *gd, const char *reason )
{
    printf("Player %d was disconnected. Reason: %s\n", client->id, reason);
    NG_ClientRep_cut(server, client);
    gd->num_connected -= 1;
}


int
NG_Game_getPlayerMove( NG_Server *server, NG_ClientRep *client, NG_GameData *gd )
{
    sprintf(server->buffer.body, "Sum is %d", gd->curr_sum);
    NG_toClient(server, client, NG_MESSAGE_TEXT);

    // Do five times, if player makes bad move five times disconnect them.
    for (int badmoves=0; badmoves<5; badmoves++)
    {
        NG_MessageType msgtype;
        NG_toClient(server, client, NG_MESSAGE_REQ_VERTS);
        NG_fromClient(server, client, &msgtype);

        if (msgtype == NG_MESSAGE_TIMEOUT)
        {
            NG_Game_cutPlayer(server, client, gd, "Timeout");
            return 0;
        }

        // Immediately check for infringement.
        bool valid_msg = NG_Server_msgValid(server);
        if (valid_msg == false)
        {
            NG_Game_cutPlayer(server, client, gd, "Protocol infringement");
            return 0;
        }

        if (msgtype == NG_MESSAGE_MOVE)
        {
            int move = atoi(server->buffer.body);

            if (move >= 1 && move <= 9)
            {
                return move;
            }
            else
            {
                sprintf(server->buffer.body, "ERROR move must be in the interval [1:9].");
                NG_toClient(server, client, NG_MESSAGE_ERROR);                    
            }
        }

        else if (msgtype == NG_MESSAGE_QUIT)
        {
            NG_Game_cutPlayer(server, client, gd, "Player quit");
            return 0;
        }

        else // Should not execute. Only occurs if an infringement is missed by NG_Server_msgValid()
        {
            NG_Game_cutPlayer(server, client, gd, "Protocol infringement");
            return 0;
        }
    }


    // Client made five bad moves if at this point
    sprintf(server->buffer.body, "Disconnected for making five bad moves consecutively.");
    NG_toClient(server, client, NG_MESSAGE_TEXT);
    NG_Game_cutPlayer(server, client, gd, "Made five bad moves consecutively.");
    return 0;
}


void
NG_GameStage_play( NG_Server *server, NG_GameData *gd )
{
    /*
        curr_player is incremented at the start of
        the loop because it simplifies some of the logic.

        curr_player is initialised to -1 so the first
        player that joins gets to make a move first
        rather than the second player that joins.
    */

    gd->curr_player = -1; // (-1 + 1) % n == 0

    while (gd->curr_sum < 30)
    {
        gd->curr_player += 1;
        gd->curr_player %= gd->required_players;

        NG_ClientRep *client = &gd->clients[gd->curr_player];
        if (NG_ClientRep_alive(client) == false)
            continue;

        gd->curr_sum += NG_Game_getPlayerMove(server, client, gd);

        // If the current player has disconnected
        // there may be only one player left.
        if (gd->num_connected == 1)
        {
            break;
        }
    }
}



void
NG_GameStage_end( NG_Server *server, NG_GameData *gd )
{
    /*
        If the main loop broke because there is only
        one player left then that player needs to be found.
    
        If it broke because the sum reached 30 then the winner
        must be the current player.
    */
    if (gd->num_connected == 1)
    {
        for (int i=0; i<gd->required_players; i++)
        {
            if (gd->clients[i].connected == true)
            {
                gd->curr_player = i;
                sprintf(server->buffer.body, "You won!");
                NG_toClient(server, &gd->clients[i], NG_MESSAGE_TEXT);
                NG_toClient(server, &gd->clients[i], NG_MESSAGE_END);
            }
        }
        NG_Server_exit(server, 0);
    }

    for (int i=0; i<gd->required_players; i++)
    {
        if (i == gd->curr_player)
            sprintf(server->buffer.body, "You won!");
        else
            sprintf(server->buffer.body, "You lost!");

        if (gd->clients[i].connected)
        {
            NG_toClient(server, &gd->clients[i], NG_MESSAGE_TEXT);
            NG_toClient(server, &gd->clients[i], NG_MESSAGE_END);
        }
    }

    NG_Server_exit(server, 0);
}


void
NG_Game_exit( NG_Server *server, NG_GameData *gd )
{
    for (int i=0; i<gd->required_players; i++)
    {
        if (gd->clients[i].connected)
        {
            NG_ClientRep_cut(server, &gd->clients[i]);
        }
    }

    NG_Server_exit(server, 1);
}
