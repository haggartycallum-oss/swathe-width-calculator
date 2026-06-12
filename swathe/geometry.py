import numpy as np


def check_dish_limits(az, el, max_dish_angle):
    """Return True if the composite angle is within the dish gimbal limit."""
    comp_angle = np.arccos(np.cos(el) * np.cos(az))
    return comp_angle <= max_dish_angle


def calc_beam_height(r, ld_angle, beam_width):
    """Return the ground footprint height of the beam at a given range."""
    beam_bottom = r * np.tan(0.5 * np.pi - ld_angle - 0.5 * beam_width)
    beam_top    = r * np.tan(0.5 * np.pi - ld_angle + 0.5 * beam_width)
    return beam_top - beam_bottom


def calc_swath(r, sq_angle, max_sweep, vertical_range, beam_width):
    """Return (swathe_width, swath_start, swath_end) for a given geometry."""
    total_angle = sq_angle + max_sweep
    R2          = np.hypot(vertical_range, r * np.sin(total_angle))
    start       = r  * np.sin(sq_angle)
    end         = R2 * np.sin(total_angle) + 2 * r * np.sin(beam_width / 2)
    width       = end - start
    return width, start, end