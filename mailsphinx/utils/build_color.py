def hex_to_rgb(hex_color):
    """
    Converts HEX color to RGB.
    
    Parameters
    ----------
    hex_color : str
    
    Returns
    -------
    rgb_color : tuple(int, int, int)
    """
    hex_color = hex_color.lstrip('#')
    rgb_color = tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
    return rgb_color

def rgb_to_hex(rgb_color):
    """
    Converts RGB color to HEX.

    Parameters
    ----------
    rgb_color : tuple(int, int, int)
    
    Returns
    -------
    hex_color : str
    """
    hex_color = '#{:02X}{:02X}{:02X}'.format(*rgb_color)
    return hex_color

def blend_colors(hex_color, hex_background_color, alpha):
    """
    Blends together a main color and the background color, given a specific opacity fraction.

    Parameters
    ----------
    hex_color : str

    hex_background_color : str
    
    alpha : float

    Returns
    -------
    rgb_blend : tuple(int, int, int)
    """
    r, g, b = hex_to_rgb(hex_color)
    r_background, g_background, b_background = hex_to_rgb(hex_background_color)
    r_blend = int(alpha * r + (1 - alpha) * r_background)
    g_blend = int(alpha * g + (1 - alpha) * g_background)
    b_blend = int(alpha * b + (1 - alpha) * b_background)
    rgb_blend = rgb_to_hex((r_blend, g_blend, b_blend))
    return rgb_blend

def get_transparent_color(hex_color, alpha):
    """
    Returns equivalent color to translucent color with white background.
    
    Parameters
    ----------
    hex_color : str

    alpha : float

    Returns
    -------
    output_color : tuple(int, int, int)
    """
    output_color = blend_colors(hex_color, '#FFFFFF', alpha)
    return output_color
