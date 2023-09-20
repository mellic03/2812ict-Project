#include <iostream>
#include <fstream>
#include <stdint.h>
#include <cmath>
#include <vector>

// #include <GL/glew.h>
// #include <GL/gl.h>
#include "fakeglm.hpp"



std::vector<std::vector<glm::vec3>> adj_normals;


extern "C" void
calculate_normals( void *vertices_ptr, void *indices_ptr, size_t indices_size )
{
    vertex *vertices  = (vertex *)vertices_ptr;
    uint32_t *indices = (uint32_t *)indices_ptr;
    size_t num_verts  = indices_size;

    // Reset adjacent normals
    for (auto &v: adj_normals)
    {
        v.resize(0);
    }

    for (size_t i=0; i<num_verts; i++)
    {
        int idx = indices[i];
        vertices[idx].normal = { 0.0f, 0.0f, 0.0f };
    }

    for (size_t i=0; i<num_verts; i+=3)
    {
        size_t idx0 = indices[i+0];
        size_t idx1 = indices[i+1];
        size_t idx2 = indices[i+2];

        vertex *v0 = &vertices[idx0];
        vertex *v1 = &vertices[idx1];
        vertex *v2 = &vertices[idx2];

        glm::vec3 p0 = v0->position;
        glm::vec3 p1 = v1->position;
        glm::vec3 p2 = v2->position;

        const glm::vec3 N = cross(p1-p0, p2-p0);

        float theta0 = glm::angle(p1-p0, p2-p0);
        float theta1 = glm::angle(p2-p1, p0-p1);
        float theta2 = glm::angle(p0-p2, p1-p0);

        v0->normal += theta0 * N;
        v1->normal += theta1 * N;
        v2->normal += theta2 * N;
    }


    for (size_t i=0; i<num_verts; i++)
    {
        int idx = indices[i];

        // glm::vec3 normal = { 0.0f, 0.0f, 0.0f };

        // for (const auto &n: adj_normals[idx])
        //     normal += n;

        vertices[idx].normal = glm::normalize(vertices[idx].normal);
    }
}




extern "C" void
load_CFM(
    void *verts_ptr,     size_t verts_size,      const char *verts_path,
    void *indices_ptr,   size_t indices_size,    const char *indices_path )
{
    float    *vertices = (float *)(verts_ptr);
    uint32_t *indices  = (uint32_t *)(indices_ptr);


    // indices_size == number of vertices
    adj_normals.resize(indices_size);


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
            vertices[i+1] = 0.0f;
            vertices[i+2] = 0.0f;
            vertices[i+3] = 1.0f;
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



extern "C" void
lerp_verts( void *verts0_ptr, void *verts1_ptr, size_t num_verts, float alpha )
{
    vertex *verts0 = (vertex *)(verts0_ptr);
    vertex *verts1 = (vertex *)(verts1_ptr);

    for (size_t i=0; i<num_verts; i++)
    {
        glm::vec3 &p0 = verts0[i].position;
        glm::vec3 &p1 = verts1[i].position;
        p0 = alpha*p0 + (1.0-alpha)*p1;
    }
}
