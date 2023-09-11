#version 330 core

layout (location = 0) in vec3 vsin_pos;
layout (location = 1) in vec3 vsin_normal;
layout (location = 2) in vec2 vsin_texcoords;

out vec3 fsin_fragpos;
out vec3 fsin_normal;
out vec2 fsin_texcoords;

uniform mat4 proj;
uniform mat4 un_view;
uniform mat4 model;

void main()
{
    vec4 worldpos = model * vec4(vsin_pos, 1.0);

    fsin_fragpos = worldpos.xyz;
    fsin_normal  = normalize(model * vec4(vsin_normal, 0.0)).xyz;
    fsin_texcoords = vsin_texcoords;

    gl_Position = proj * un_view * worldpos;
}
