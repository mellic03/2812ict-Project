#version 330 core

layout (location = 0) in vec3 vsin_pos;
layout (location = 1) in vec3 vsin_normal;
layout (location = 2) in vec2 vsin_texcoord;

out vec3 fsin_fragpos;
out vec3 fsin_normal;

uniform mat4 un_proj;
uniform mat4 un_view;
uniform mat4 un_model;

void main()
{
    vec4 worldpos = un_model * vec4(vsin_pos, 1.0);

    fsin_fragpos = worldpos.xyz;
    fsin_normal  = normalize(un_model * vec4(vsin_normal, 0.0)).xyz;

    gl_Position = un_proj * un_view * worldpos;
}



