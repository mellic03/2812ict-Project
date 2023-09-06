#version 330 core

out vec4 fsout_color;

in vec3 fsin_fragpos;
in vec3 fsin_normal;

const vec3 light_pos = vec3(5.0, -5.0, 5.0);
const float spec_exponent = 16;

uniform vec3 un_color;
uniform vec3 un_view_pos;

void main()
{
    vec3 view_dir = normalize(un_view_pos - fsin_fragpos);

    float d = distance(fsin_fragpos, light_pos);

    vec3 frag_to_light = normalize(light_pos - fsin_fragpos);
    float diffuse_f = max(dot(fsin_normal, frag_to_light), 0.0);

    vec3 halfway_dir = normalize(frag_to_light + view_dir);  
    float specular_f = pow(max(dot(fsin_normal, halfway_dir), 0.0), spec_exponent);


    float attenuation = 1.0 / (
          0.1
        + 0.5 * d
        // + 0.1 * d*d
    );


    vec3 ambient  = attenuation * un_color * vec3(1.0, 1.0, 1.0);
    vec3 diffuse  = attenuation * un_color * diffuse_f * vec3(1.0, 1.0, 1.0);
    vec3 specular = attenuation * un_color * specular_f * 10;

    vec3 result = ambient + diffuse + specular;

    fsout_color = vec4(result, 1.0);
}

