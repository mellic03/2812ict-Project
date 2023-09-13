#pragma once


namespace glm
{
    struct vec2
    {
        union { float x, r; };
        union { float y, g; };
    };

    struct vec3
    {
        union { float x, r; };
        union { float y, g; };
        union { float z, b; };
    };

    float  mag       ( const vec3 &v                );
    vec3   normalize ( vec3 v                       );
    float  dot       ( const vec3 &u, const vec3 &v );
    vec3   cross     ( const vec3 &u, const vec3 &v );
    float  angle     ( const vec3 &u, const vec3 &v );
}



glm::vec3 operator  +  ( const glm::vec3 &u, const glm::vec3 &v );
glm::vec3 operator  -  ( const glm::vec3 &u, const glm::vec3 &v );
glm::vec3 operator  *  ( const float &f,     const glm::vec3 &v );
glm::vec3 &operator += ( glm::vec3 &u, const glm::vec3 &v       );
glm::vec3 &operator /= ( glm::vec3 &v, float f                  );

