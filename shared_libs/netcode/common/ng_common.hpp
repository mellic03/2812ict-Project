#ifndef COUNTGAME_COMMON_H
#define COUNTGAME_COMMON_H

#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>
#include <stdint.h>
#include <ctype.h>

#include <sys/types.h>
#include <sys/mman.h>
#include <sys/time.h>
#include <sys/socket.h>
#include <fcntl.h>
#include <netinet/in.h>
#include <unistd.h>
#include <arpa/inet.h>

#include "../../geometry/fakeglm.hpp"

#define NUM_VERTS 468 // number of vertices in face model.

#define NG_HEADER_SIZE 1
#define NG_BODY_SIZE   (NUM_VERTS*sizeof(vertex))
#define NG_BUFFER_SIZE (NG_HEADER_SIZE + NG_BODY_SIZE)


// Protocol ------------------------------------------------------------
typedef enum
{
    NG_MESSAGE_TEXT = 11,

    NG_MESSAGE_USERID,
    NG_MESSAGE_VERTS_USER,
    NG_MESSAGE_VERTS_REQ,
    NG_MESSAGE_VERTS_RES,

    NG_MESSAGE_END,
    NG_MESSAGE_ERROR,
    NG_MESSAGE_MOVE,
    NG_MESSAGE_QUIT,

    NG_MESSAGE_TIMEOUT

} NG_MessageType;

#define  NG_MESSAGE_TEXT_STR       "[TEXT]        "
#define  NG_MESSAGE_VERTS_USER_STR "[VERTS_USER]  "
#define  NG_MESSAGE_VERTS_REQ_STR  "[VERTS_REQ]   "
#define  NG_MESSAGE_VERTS_RES_STR  "[VERTS_RES]   "
#define  NG_MESSAGE_END_STR        "[END]         "
#define  NG_MESSAGE_ERROR_STR      "[ERROR]       "
#define  NG_MESSAGE_MOVE_STR       "[MOVE]        "
#define  NG_MESSAGE_QUIT_STR       "[QUIT]        "

const char *NG_MessageType_str( NG_MessageType );
// ---------------------------------------------------------------------


// NG_Buffer -----------------------------------------------------------
typedef struct
{
    char *data;   // Don't access directly, instead use header and body.
    char *header; // First byte of buffer
    char *body;   // Rest of buffer

} NG_Buffer;

NG_Buffer  NG_Buffer_new         (             );
bool       NG_Buffer_bodyValid   ( NG_Buffer * );
void       NG_Buffer_clear       ( NG_Buffer * );
// ---------------------------------------------------------------------


// String functions ----------------------------------------------------
char *  NG_str_stripws     ( char *str               );
size_t  NG_str_count       ( const char *str, char c );
size_t  NG_str_countTokens ( const char *str         );
// ---------------------------------------------------------------------




struct FaceVertices
{
    int m_num_users;

    uint8_t *m_shared_byte; // Single byte, holds userid.
    vertex *m_shared_ptr;

    FaceVertices( int num_users ): m_num_users(num_users)
    {
        m_shared_ptr = (vertex *)mmap(
            NULL,
            num_users*sizeof(vertex)*NUM_VERTS,
            PROT_READ|PROT_WRITE,
            MAP_SHARED|MAP_ANONYMOUS,
            -1,
            0
        );

        m_shared_byte = (uint8_t *)mmap(
            NULL,
            sizeof(uint8_t),
            PROT_READ|PROT_WRITE,
            MAP_SHARED|MAP_ANONYMOUS,
            -1,
            0
        );
    };

    /** FaceVerticfes[i] == vertex array belonging to client i
    */
    vertex *operator [] (int i)
    {
        return m_shared_ptr + i*NUM_VERTS;
    };

};



#endif

