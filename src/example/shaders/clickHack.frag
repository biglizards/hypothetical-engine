#version 330 core
out vec4 FragColor;

uniform vec4 entityColour;

void main()
{
   FragColor = entityColour;
}
