#version 330 core

out vec4 fsout_color;

uniform vec3 un_color;

void main()
{
    fsout_color = vec4(un_color, 1.0);
}

