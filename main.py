from swathe.calculation import run_calculation, ranges, image_widths, CRR_labels
from swathe.plotting import plot_swathe_width, plot_swath_start_end
import matplotlib.pyplot as plt


def main():
    swathe_width, swath_start, swath_end = run_calculation()

    plot_swathe_width(ranges, swathe_width, image_widths, CRR_labels)
    plot_swath_start_end(ranges, swath_start, swath_end, image_widths, CRR_labels)

    plt.show()


if __name__ == '__main__':
    main()