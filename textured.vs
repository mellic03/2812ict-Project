#version 330 core

layout (location = 0) in vec3 vsin_pos;
layout (location = 1) in vec2 vsin_uv;
out vec3 fsin_fragpos;
out vec2 fsin_uv;

void main()
{
    fsin_fragpos = vsin_pos;
    fsin_uv = vsin_uv;
    gl_Position = vec4(vsin_pos, 1.0);
}
