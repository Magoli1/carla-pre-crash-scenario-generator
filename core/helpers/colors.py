from typing import List, Set

COLORS = {
    "Black": {"r": 0, "g": 0, "b": 0},
    "Maroon": {"r": 128, "g": 0, "b": 0},
    "Green": {"r": 0, "g": 128, "b": 0},
    "Olive": {"r": 128, "g": 128, "b": 0},
    "Navy": {"r": 0, "g": 0, "b": 128},
    "Purple": {"r": 128, "g": 0, "b": 128},
    "Teal": {"r": 0, "g": 128, "b": 128},
    "Silver": {"r": 192, "g": 192, "b": 192},
    "Grey": {"r": 128, "g": 128, "b": 128},
    "Red": {"r": 255, "g": 0, "b": 0},
    "Lime": {"r": 0, "g": 255, "b": 0},
    "Yellow": {"r": 255, "g": 255, "b": 0},
    "Blue": {"r": 0, "g": 0, "b": 255},
    "Fuchsia": {"r": 255, "g": 0, "b": 255},
    "Aqua": {"r": 0, "g": 255, "b": 255},
    "White": {"r": 255, "g": 255, "b": 255},
}


def get_color_names() -> List[str]:
    """Get the names of all supported colors for the vehicles

    :returns: The names of the colors
    :rtype: list
    """
    return list(COLORS.keys())


def compare_color_lists(color_names: List[str]) -> Set[str]:
    """Compare a lists of color names with the list of all supported colors

    :param color_names: A list of color names
    :type color_names: list
    :returns: Color names in the input list which are not supported
    :rtype: set
    """
    return set(color_names) - set(get_color_names())


def get_color_by_name(color_name: str) -> (int, int, int):
    """Get the RGB value of supported color

    :param color_names: The name of the color
    :type color_names: str
    :returns: red (0-255), green (0-255), blue (0-255)
    :rtype: (int, int, int)
    """
    if color_name not in COLORS:
        raise Exception("{} is not a supported color".format(color_name))
    return COLORS[color_name]["r"], COLORS[color_name]["g"], COLORS[color_name]["b"]
