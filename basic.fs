#version 330 core

out vec4 fsout_color;

in vec3 fsin_fragpos;
in vec3 fsin_normal;

vec3 light_pos = vec3(-10.0, -15.0, 0.0);

uniform vec3 un_color;

void main()
{
    light_pos.x += 0.00001;

    vec3 light_dir = normalize(light_pos - fsin_fragpos);
    float light_dist = length(light_pos - fsin_fragpos);

    float strength = dot(light_dir, fsin_normal);
    strength = (strength + 1.0) / 2.0;

    vec3 color = strength * un_color;
    fsout_color = vec4(color, 1.0);
}



