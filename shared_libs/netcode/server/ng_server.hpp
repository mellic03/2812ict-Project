#ifndef NG_SERVER_H
#define NG_SERVER_H

#include "../common/common.hpp"


#define NG_SERVER_TIMEOUT 30 // 30 second timeout

/** Server-side representation of the server
*/
typedef struct
{
    struct sockaddr_in addr;
    int       socketdesc;
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


NG_ClientRep NG_ClientRep_new   (                                     );
bool         NG_ClientRep_alive ( NG_ClientRep *                      );
void         NG_ClientRep_cut   ( NG_Server *, NG_ClientRep *         );
size_t       NG_Server_writen   ( NG_Server *, NG_ClientRep *, void *, size_t n );
size_t       NG_Server_readn    ( NG_Server *, NG_ClientRep *, void *, size_t n );



#endif
