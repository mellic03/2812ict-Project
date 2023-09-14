#include "ng_common.hpp"



const char *
NG_MessageType_str( NG_MessageType msgtype )
{
    switch (msgtype)
    {
        case NG_MESSAGE_TEXT:           return NG_MESSAGE_TEXT_STR;
        case NG_MESSAGE_VERTS_USER:     return NG_MESSAGE_VERTS_USER_STR;
        case NG_MESSAGE_VERTS_REQ:      return NG_MESSAGE_VERTS_REQ_STR;
        case NG_MESSAGE_VERTS_RES:      return NG_MESSAGE_VERTS_RES_STR;
        case NG_MESSAGE_END:            return NG_MESSAGE_END_STR;
        case NG_MESSAGE_ERROR:          return NG_MESSAGE_ERROR_STR;
        case NG_MESSAGE_MOVE:           return NG_MESSAGE_MOVE_STR;
        case NG_MESSAGE_QUIT:           return NG_MESSAGE_QUIT_STR;

        default:                        return "[INFRINGEMENT]";
    }
}




NG_Buffer
NG_Buffer_new()
{
    NG_Buffer buffer;

    buffer.data = (char *)calloc(NG_BUFFER_SIZE, sizeof(char));
    buffer.header = buffer.data + 0;
    buffer.body   = buffer.data + NG_HEADER_SIZE;

    return buffer;
}



/** Sanitize the contents of an NG_Buffer.
 * @return True if buffer contents are a valid MOVE message, false otherwise.
*/
bool
NG_Buffer_bodyValid( NG_Buffer *buffer )
{
    size_t len = strlen(buffer->body);

    // Zero-length buffer is invalid.
    if (len == 0)
    {
        printf("A\n");
        return false;
    }

    // Remove newline if it exists.
    if (buffer->body[len-1] == '\n')
    {
        buffer->body[len-1] = '\0';
        len -= 1;   
    }

    // Strip whitespace and write stripped string back into buffer.
    char *stripped = NG_str_stripws(buffer->body);
    sprintf(buffer->body, stripped);

    // Buffer is valid if it contains only "quit".
    if (strcmp(buffer->body, "quit") == 0)
        return true;

    // A valid MOVE message contains only one token (the move).
    size_t num_tokens = NG_str_countTokens(buffer->body);
    if (num_tokens != 1)
        return false;

    // A valid MOVE must be entirely numeric.
    for (size_t i=0; i<len; i++)
    {
        unsigned char c = (unsigned char)buffer->body[i];
        if (isdigit(c) == false)
            return false;
    }

    // If this point is reached then the input is valid.
    return true;
}


/** Clear the data contained inside an NG_Buffer struct.
 * @note Only erases the data up to the first null terminator.
 * Any data that exists beyond the first null terminator will
 * not be erased.
*/
void
NG_Buffer_clear( NG_Buffer *buffer )
{
    // No point erasing whole buffer if already mostly zeroes.
    size_t len = NG_HEADER_SIZE + strlen(buffer->body);
    memset(buffer->data, '\0', len);
}


/** Strip leading and trailing whitespace from a string.
 * @note Can alter the input string by adding a null terminator.
 * @param str the input string
 * @return pointer to some point within str
*/
char *
NG_str_stripws( char *str )
{
    char *strip = str;

    int len = strlen(strip);
    if (len == 0)
    {
        return strip;
    }

    // Trailing whitespace -------------
    int idx = len-1;
    while (strip[idx] == ' ' && idx > 0)
    {
        idx--;
    }
    strip[idx+1] = '\0';
    // ----------------------------------

    // Leading whitespace ---------------
    while (*strip == ' ')
    {
        strip++;
    }
    // ----------------------------------

    return strip;
}

/** Count the number of ocurrences of a char in a string.
 * @param str the string to search through
 * @param c the char to search for
 * @return the number of ocurrences of c in str
*/
size_t
NG_str_count( const char *str, char c )
{
    size_t count = 0;

    while (*str)
    {
        if (*str == c)
            count++;
        str++;
    }

    return count;
}


/** Count the number of whitespace-separated tokens in a string.
 * @note Does not modify the input string.
 * @param str the input string
 * @return the number of whitespace-separated tokens in str
*/
size_t
NG_str_countTokens( const char *input )
{
    char *copy = (char *)malloc((strlen(input)+1) * sizeof(char));
    strcpy(copy, input);

    char delim[] = " ";
    char *token;

    size_t count = 0;
    token = strtok(copy, delim);
    while (token != NULL)
    {
        token = strtok(NULL, delim);
        count += 1;
    }

    return count;
}


