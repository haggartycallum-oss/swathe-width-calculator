import numpy as np
from swathe.geometry import check_dish_limits, calc_beam_height, calc_swath


# =============================================================================
# Scan parameters
# =============================================================================

ramp_period_full = 380e-6   # seconds
wavelength       = 0.003    # metres
velocity         = 240      # m/s
image_widths     = np.array([246, 512])   # pixels
ranges           = np.arange(1750, 3050, 50)  # metres
altitude         = 950      # metres
beam_width       = np.deg2rad(1.2)  # rad

# Servo limits
max_dish_angle = np.deg2rad(30)  # rad

# Target (MLRS) and Johnson's criteria
extent        = 6.97  # metres
J_crit_recog  = 12    # pixels
J_crit_detect = 2     # pixels

CRR_recog  = extent / J_crit_recog   # m/pix
CRR_detect = extent / J_crit_detect  # m/pix
CRR        = np.array([CRR_recog, CRR_detect])  # [recog, detect] m/pix
CRR_labels = ['Recog', 'Detect']


def run_calculation():
    """Run the swathe width calculation across all ranges and combinations.

    Returns
    -------
    swathe_width, swath_start, swath_end : np.ndarray
        Arrays of shape (n_ranges, n_imgs, n_crr)
    """
    n_ranges = len(ranges)
    n_imgs   = len(image_widths)
    n_crr    = len(CRR)

    swathe_width = np.zeros((n_ranges, n_imgs, n_crr))
    swath_start  = np.zeros((n_ranges, n_imgs, n_crr))
    swath_end    = np.zeros((n_ranges, n_imgs, n_crr))

    for crr_idx, crr in enumerate(CRR):
        for img_idx, img in enumerate(image_widths):

            image_integration_time = img * ramp_period_full
            coverage_rate          = beam_width / image_integration_time

            for r_idx, r in enumerate(ranges):

                # Look-down and squint angles
                ld_angle = np.arcsin(altitude / r)
                sq_angle = np.arcsin(
                    (wavelength * r)
                    / (2 * velocity * ramp_period_full * img * crr * np.cos(ld_angle))
                )

                vertical_range = r * np.cos(sq_angle)

                # Max scan time from beam footprint height and platform velocity
                beam_height = calc_beam_height(r, ld_angle, beam_width)
                scan_time   = (beam_height / velocity) / 2  # divide by 2: acquisition at beam centre

                # Max sweep angle from coverage rate and available scan time
                max_sweep = scan_time * coverage_rate

                if check_dish_limits(max_sweep + sq_angle, ld_angle, max_dish_angle):
                    # Full sweep available — calculate swath normally
                    w, s, e = calc_swath(r, sq_angle, max_sweep, vertical_range, beam_width)

                elif check_dish_limits(sq_angle, ld_angle, max_dish_angle):
                    # Sweep clipped by dish gimbal limit — recalculate max sweep
                    max_sweep = np.arccos(np.cos(max_dish_angle) / np.cos(ld_angle)) - sq_angle
                    w, s, e   = calc_swath(r, sq_angle, max_sweep, vertical_range, beam_width)

                else:
                    # Squint angle alone exceeds dish limits — zero output
                    w, s, e = 0, 0, 0

                swathe_width[r_idx, img_idx, crr_idx] = w
                swath_start [r_idx, img_idx, crr_idx] = s
                swath_end   [r_idx, img_idx, crr_idx] = e

    return swathe_width, swath_start, swath_end