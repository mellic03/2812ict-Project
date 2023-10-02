#version 330 core

out vec4 fsout_color;

in vec3 fsin_fragpos;
in vec3 fsin_normal;
in vec2 fsin_texcoords;

const vec3 light_direction = vec3(1.0, 1.0, 1.0);

uniform vec3 un_color;
uniform vec3 un_specular;
uniform vec3 un_view_pos;
uniform sampler2D un_texture;
uniform float un_spec_exponent;

void main()
{
    vec3 light_ambient = vec3(0.1);
    vec3 light_diffuse = vec3(1.0, 1.0, 1.0);

    vec3 view_dir = normalize(un_view_pos - fsin_fragpos);

    vec3 frag_to_light = normalize(-light_direction);
    // float diffuse_f = max(dot(fsin_normal, frag_to_light), 0.0);
    float diffuse_f = dot(fsin_normal, frag_to_light);
    diffuse_f = (diffuse_f + 1.0) / 2.0;


    vec3 halfway_dir = normalize(frag_to_light + view_dir);  
    float specular_f = pow(max(dot(fsin_normal, halfway_dir), 0.0), un_spec_exponent);


    vec3 albedo = texture(un_texture, fsin_texcoords).rgb;

    vec3 ambient  = albedo * light_ambient;
    vec3 diffuse  = albedo * diffuse_f * light_diffuse;
    vec3 specular = albedo * specular_f * un_specular;
    vec3 result   = ambient + diffuse + specular;

    fsout_color = vec4(result, 1.0);

}

