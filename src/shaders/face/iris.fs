#version 330 core

out vec4 fsout_color;

in vec3 fsin_fragpos;
in vec3 fsin_normal;
in vec2 fsin_texcoords;

uniform vec3 un_color;

void main()
{
    fsout_color = vec4(un_color, 1.0);
}

