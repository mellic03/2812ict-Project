#version 330 core

out vec4 fsout_color;

in vec3 fsin_fragpos;
in vec3 fsin_normal;
in vec2 fsin_texcoords;

const vec3 light_pos = vec3(5.0, -5.0, 5.0);
const float spec_exponent = 32;

uniform vec3 un_view_pos;
uniform sampler2D un_texture;

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

    vec3 albedo = texture(un_texture, fsin_texcoords).rgb;

    vec3 ambient  = attenuation * albedo * vec3(1.0, 1.0, 1.0);
    vec3 diffuse  = attenuation * albedo * diffuse_f * vec3(1.0, 1.0, 1.0);
    vec3 specular = attenuation * albedo * specular_f * 1;

    vec3 result = ambient + diffuse + specular;

    fsout_color = vec4(albedo, 1.0);
}

