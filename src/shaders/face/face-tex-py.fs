#version 330 core

out vec4 fsout_color;

in vec3 fsin_fragpos;
in vec2 fsin_texcoords;

uniform sampler2D un_texture;

void main()
{
    vec3 albedo = texture(un_texture, fsin_texcoords).rgb;
    fsout_color = vec4(albedo, 1.0);
}

