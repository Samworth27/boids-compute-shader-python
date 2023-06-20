#version 330

in vec2 g_uv;
in vec3 g_color;

out vec4 out_color;

float random(vec2 st) {
  return fract(sin(dot(st.xy, vec2(12.9898, 78.233))) * 43758.5453123);
}

void main() {
  float l = length(vec2(0.5, 0.5) - g_uv.xy);
  if (l > 0.5) {
    discard;
  }
  float alpha;
  if (l == 0.0)
    alpha = 1.0;
  else
    alpha = min(1.0, .60 - l * 2);

  vec3 c = g_color.rgb;
  c.xy += g_uv.xy * 0.05;
  out_color = vec4(c, alpha);
}