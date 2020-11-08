#version 330 core
out vec4 FragColor;

in vec2 TexCoord;

uniform sampler2D texture_0;
uniform sampler2D texture_1;

uniform float highlightAmount;

void main()
{
    vec4 Texture = mix(texture(texture_0, TexCoord), texture(texture_1, TexCoord),
                  vec4(texture(texture_1, TexCoord)).a * 0.3);
    FragColor = mix(Texture, vec4(0, 0.8, 0.4, 1), highlightAmount);

//    vec4 metalBit;
//    if (texture(texture_1, TexCoord).a != 0.0f) {
//        metalBit = vec4(texture(texture_1, TexCoord).rgb, 1);
//    } else {
//        metalBit = vec4(0.0f);
//    }
//    vec4 Texture = metalBit;
//    FragColor = mix(Texture, vec4(0, 0.8, 0.4, 1), highlightAmount);
//    FragColor = texture(texture_0, TexCoord);
}