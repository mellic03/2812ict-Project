#ifndef NG_GAME_H
#define NG_GAME_H

#include "ng_server.hpp"



#define NG_GAME_TARGET_SUM 30


typedef struct
{
    int num_connected;
    int required_players;
    int curr_player;
    int curr_sum;
    NG_ClientRep *clients;

} NG_GameData;

NG_GameData NG_GameData_new( int required_players );


void NG_GameStage_initiate  ( NG_Server *                );
void NG_GameStage_join      ( NG_Server *, NG_GameData * );
void NG_GameStage_play      ( NG_Server *, NG_GameData * );
void NG_GameStage_end       ( NG_Server *, NG_GameData * );
void NG_Game_exit           ( NG_Server *, NG_GameData * );


#endif