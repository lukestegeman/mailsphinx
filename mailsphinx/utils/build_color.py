













def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb_color):
    return '#{:02X}{:02X}{:02X}'.format(*rgb_color)

def blend_colors(hex_color, hex_background_color, alpha):
    r, g, b = hex_to_rgb(hex_color)
    r_background, g_background, b_background = hex_to_rgb(hex_background_color)
    
    r_blend = int(alpha * r + (1 - alpha) * r_background)
    g_blend = int(alpha * g + (1 - alpha) * g_background)
    b_blend = int(alpha * b + (1 - alpha) * b_background)
    
    return rgb_to_hex((r_blend, g_blend, b_blend))

def get_transparent_color(hex_color, alpha):
    output_color = blend_colors(hex_color, '#FFFFFF', alpha)
    return output_color
