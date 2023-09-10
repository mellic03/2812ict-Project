#include <iostream>
#include <fstream>
#include <stdint.h>
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
calculate_normals( void *ptr, size_t size )
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




/**
 * @param verts_size number of floats in vertex array
 * @param indices_size number of ints in indices array
 * 
*/

extern "C" void
load_canonical_face_model(
    void *verts_ptr,     size_t verts_size,      const char *verts_path,
    void *indices_ptr,   size_t indices_size,    const char *indices_path )
{
    float    *vertices = (float *)(verts_ptr);
    uint32_t *indices  = (uint32_t *)(indices_ptr);

    // std::cout << "verts_size: " << verts_size << "\n";
    // std::cout << "indices_size: " << indices_size << "\n";

    std::ifstream stream(verts_path);
    std::string line;

    int i = 0;
    int count = 0;
    while (std::getline(stream, line))
    {
        if (line == "")
            continue;

        vertices[i] = std::stof(line);
        i += 1;
        count += 1;

        if (count == 3)
        {
            vertices[i+1] = 0.0;
            vertices[i+2] = 0.0;
            vertices[i+3] = 1.0;
            i += 3;
            count += 3;
        }

        else if (count == 8)
        {
            count = 0;
        }
    }



    stream = std::ifstream(indices_path);

    i = 0;
    while (std::getline(stream, line))
    {
        if (line == "")
            continue;

        indices[i] = std::stoi(line);
        i += 1;
    }
}