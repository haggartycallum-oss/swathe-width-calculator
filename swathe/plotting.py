import matplotlib.pyplot as plt


COLOURS = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red']


def make_legend_label(img, crr_label):
    return f'W={img}px, {crr_label}'


def plot_swathe_width(ranges, swathe_width, image_widths, CRR_labels):
    n_crr = len(CRR_labels)
    fig, ax = plt.subplots()

    for img_idx, img in enumerate(image_widths):
        for crr_idx, crr_label in enumerate(CRR_labels):
            colour = COLOURS[img_idx * n_crr + crr_idx]
            label  = make_legend_label(img, crr_label)
            ax.plot(ranges, swathe_width[:, img_idx, crr_idx], color=colour, label=label)

    ax.set_xlabel('Range (m)')
    ax.set_ylabel('Swathe Width (m)')
    ax.set_title('Swathe Width vs Range')
    ax.legend()
    ax.grid(True)
    return fig


def plot_swath_start_end(ranges, swath_start, swath_end, image_widths, CRR_labels):
    n_crr = len(CRR_labels)
    fig, ax = plt.subplots()

    for img_idx, img in enumerate(image_widths):
        for crr_idx, crr_label in enumerate(CRR_labels):
            colour = COLOURS[img_idx * n_crr + crr_idx]
            label  = make_legend_label(img, crr_label)
            ax.plot(ranges, swath_start[:, img_idx, crr_idx], color=colour, linestyle='--', label=f'{label} start')
            ax.plot(ranges, swath_end  [:, img_idx, crr_idx], color=colour, linestyle='-',  label=f'{label} end')

    ax.set_xlabel('Range (m)')
    ax.set_ylabel('Cross-range position (m)')
    ax.set_title('Swath Start and End vs Range')
    ax.legend()
    ax.grid(True)
    return fig