#version 330 core

out vec4 fsout_color;

in vec3 fsin_fragpos;
in vec3 fsin_normal;

const vec3 light_direction = vec3(-5.0, 5.0, 5.0);
const float spec_exponent = 16;

uniform vec3 un_color;
uniform vec3 un_view_pos;

void main()
{
    vec3 light_ambient = vec3(0.1);
    vec3 light_diffuse = vec3(1.0, 1.0, 1.0);

    vec3 view_dir = normalize(un_view_pos - fsin_fragpos);

    vec3 frag_to_light = normalize(-light_direction);
    float diffuse_f = max(dot(fsin_normal, frag_to_light), 0.0);
    // float diffuse_f = dot(fsin_normal, frag_to_light);
    // diffuse_f = (diffuse_f + 1.0) / 2.0;


    vec3 halfway_dir = normalize(frag_to_light + view_dir);  
    float specular_f = pow(max(dot(fsin_normal, halfway_dir), 0.0), spec_exponent);


    vec3 ambient  = un_color * light_ambient;
    vec3 diffuse  = un_color * diffuse_f * light_diffuse;
    vec3 specular = un_color * specular_f * 1;
    vec3 result   = ambient + diffuse + specular;

    fsout_color = vec4(fsin_normal, 1.0);
}

