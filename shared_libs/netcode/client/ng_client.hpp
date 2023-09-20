#ifndef NG_CLIENT_H
#define NG_CLIENT_H

#include "../common/common.hpp"



/** Client-side representation of the client
*/
typedef struct
{
    int socketdesc;

} NG_Client;


/** Client-side representation of the server
*/
typedef struct
{
    struct sockaddr_in addr;

} NG_ServerRep;



NG_Client       NG_Client_new     (                             );
void            NG_Client_connect ( NG_Client *, NG_ServerRep * );
void            NG_Client_exit    ( NG_Client *, int retcode    );

NG_ServerRep    NG_ServerRep_new  ( in_addr_t ip,  uint16_t port);

size_t          NG_Client_writen  ( NG_Client *, NG_ServerRep *, void *, size_t );
size_t          NG_Client_readn   ( NG_Client *, NG_ServerRep *, void *, size_t );


#endif
