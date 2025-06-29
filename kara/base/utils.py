import re


def pascal_to_snake(name):
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


def get_contrast_color(hex_code):
    """
    Calculates the luminance from the given hex code and determines
    the appropriate foreground color (black or white)
    for optimal contrast against the background.
    """
    hex_code = hex_code.lstrip("#")
    if len(hex_code) == 3:
        hex_code = "".join([c * 2 for c in hex_code])

    # Converting hex color to rgb
    # fmt: off
    r, g, b = [int(hex_code[i:i + 2], 16) for i in (0, 2, 4)]
    # fmt: on
    # Determine luminance
    luminance = (r * 0.299 + g * 0.587 + b * 0.114) / 255
    return "black" if luminance > 0.5 else "white"
