#version 330 core

out vec4 fsout_color;

in vec3 fsin_fragpos;
in vec3 fsin_normal;

const vec3 light_pos = vec3(-10.0, 5.0, 0.0);

void main()
{
    vec3 light_dir = normalize(light_pos - fsin_fragpos);
    float strength = dot(light_dir, fsin_normal);
    strength = (strength + 1.0) / 2.0;

    vec3 color = strength * vec3(fsin_fragpos.x, fsin_fragpos.y, 1.0);

    fsout_color = vec4(color, 1.0);
}



