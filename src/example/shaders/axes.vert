#version 330 core
layout (location = 0) in vec3 aPos;
layout (location = 1) in vec2 aTexCoord;

out vec2 TexCoord;

uniform mat4 transformMat;
const float reciprScaleOnscreen = 0.3;  // todo change to uniform

void main()
{
    float w = (transformMat * vec4(0,0,0,1)).w;
    w *= reciprScaleOnscreen;
    gl_Position = transformMat * vec4(aPos.xyz * w, 1);
    TexCoord = aTexCoord;
}