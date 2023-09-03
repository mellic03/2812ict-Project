#version 330 core

layout (location = 0) in vec3 vsin_pos;
layout (location = 1) in vec3 vsin_normal;
layout (location = 2) in vec2 vsin_uv;

out vec3 fsin_fragpos;
out vec3 fsin_normal;
out vec2 fsin_uv;

uniform mat4 proj;
uniform mat4 model;

void main()
{
    vec4 worldpos = model * vec4(vsin_pos, 1.0);

    fsin_fragpos = worldpos.xyz;
    fsin_normal  = mat3(model) * vsin_normal;
    fsin_uv      = vsin_uv;

    gl_Position = proj * worldpos;
}
