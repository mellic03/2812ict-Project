#include <iostream>
#include <cmath>

// #include <GL/glew.h>
// #include <GL/gl.h>


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


vec3 operator + (const vec3 &u, const vec3 &v)
{
    return {u.x+v.x, u.y+v.y, u.z+v.z};
}


vec3 operator - (const vec3 &u, const vec3 &v)
{
    return {u.x-v.x, u.y-v.y, u.z-v.z};
}


vec3 &operator /= (vec3 &v, float f)
{
    v.x /= f; v.y /= f; v.z /= f;
    return v;
}


float dot(const vec3 &u, const vec3 &v)
{
    return u.x*v.x + u.y*v.y + u.z*v.z;
}


vec3 cross(const vec3 &u, const vec3 &v)
{
    return {
         u.y*v.z - u.z*v.y,
        -u.x*v.z + u.z*v.x,
         u.x*v.y - u.y*v.x
    };
}


vec3 normalize(vec3 v)
{
    float magSq = v.x*v.x + v.y*v.y + v.z*v.z;
    float mag = sqrt(magSq);
    v /= mag;
    return v;
}


struct vertex
{
    vec3 position;
    vec3 normal;
    vec2 uv;
};


extern "C" void
process_vertices( void *ptr, size_t size )
{
    vertex *vertices = (vertex *)ptr;
    size_t num_verts = size/8;

    for (size_t i=0; i<num_verts; i+=3)
    {
        vertex *v0 = &vertices[i+0];
        vertex *v1 = &vertices[i+1];
        vertex *v2 = &vertices[i+2];

        vec3 p0 = v0->position;
        vec3 p1 = v1->position;
        vec3 p2 = v2->position;

        vec3 normal = normalize(cross(p1-p0, p2-p0));
        v0->normal = normal;
        v1->normal = normal;
        v2->normal = normal;
    }
}

