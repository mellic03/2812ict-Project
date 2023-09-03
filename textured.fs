#version 330 core

out vec4 fsout_color;

in vec3 fsin_fragpos;
in vec3 fsin_normal;
in vec2 fsin_uv;

uniform sampler2D un_texture;

const vec3 light_pos = vec3(-10.0, -15.0, 0.0);

void main()
{
    vec3 light_dir = normalize(light_pos - fsin_fragpos);
    float strength = dot(light_dir, fsin_normal);
    strength = (strength + 1.0) / 2.0;

    vec3 color = strength * texture(un_texture, fsin_uv).rgb;

    fsout_color = vec4(color, 1.0);
}
