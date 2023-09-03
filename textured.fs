#version 330 core

out vec4 fsout_color;
in vec3 fsin_fragpos;
in vec2 fsin_uv;

uniform sampler2D un_texture;

void main()
{
    vec3 color = texture(un_texture, fsin_uv).rgb;
    fsout_color = vec4(color, 1.0);
}
