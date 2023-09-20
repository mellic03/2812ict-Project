#pragma once


#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>
#include <stdint.h>
#include <stddef.h>
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

#define NUM_VERTS 468


typedef enum
{
    TEXT     = 1 << 1,
    VERT_REQ,
    VERT_RES,
    VERT_USR

} NG_MessageType;


size_t  readn  ( int fd,       void *vptr, size_t n );
size_t  writen ( int fd, const void *vptr, size_t n );


struct SharedVertices
{
    int m_num_users;

    uint8_t *m_shared_byte; // Single byte, holds userid.
    vertex *m_shared_ptr;

    SharedVertices( int num_users ): m_num_users(num_users)
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
