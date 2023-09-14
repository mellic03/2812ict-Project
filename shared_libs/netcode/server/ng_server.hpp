#ifndef NG_SERVER_H
#define NG_SERVER_H

#include "../common/ng_common.hpp"


#define NG_SERVER_TIMEOUT 30 // 30 second timeout

/** Server-side representation of the server
*/
typedef struct
{
    struct sockaddr_in addr;
    int       socketdesc;
    NG_Buffer buffer;
    uint16_t  port;

} NG_Server;


/** Server-side representation of the client
*/
typedef struct
{
    struct sockaddr_in addr;
    int  socketdesc;
    bool connected;
    int  id;

} NG_ClientRep;


NG_Server    NG_Server_new      ( uint16_t port            );
int          NG_Server_listen   ( NG_Server *              );
NG_ClientRep NG_Server_accept   ( NG_Server *, int id      );
bool         NG_Server_msgValid ( NG_Server *              );
void         NG_Server_exit     ( NG_Server *, int retcode );


NG_ClientRep NG_ClientRep_new   (                                               );
bool         NG_ClientRep_alive ( NG_ClientRep *                                );
void         NG_ClientRep_cut   ( NG_Server *, NG_ClientRep *                   );
void         NG_toClient        ( NG_Server *, NG_ClientRep *, NG_MessageType   );
void         NG_fromClient      ( NG_Server *, NG_ClientRep *, NG_MessageType * );



#endif
