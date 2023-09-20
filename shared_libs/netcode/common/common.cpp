#include "common.hpp"



size_t
readn( int fd, void *vptr, size_t n )
{
    char *ptr = (char *)vptr;
    size_t received;

    while (n > 0)
    {
        received = read(fd, ptr, n);
        n   -= received;
        ptr += received;
    }

    return received;
}


size_t
writen( int fd, const void *vptr, size_t n )
{
    const char *ptr = (const char *)vptr;
    size_t written;

    while (n > 0)
    {
        written = write(fd, ptr, n);
        n   -= written;
        ptr += written;
    }

    return written;
}


