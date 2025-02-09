def overlay_on_map(x, y, C1):
    import scipy.io as sio
    import matplotlib.pyplot as plt
    import numpy as np
    import settings

    # Overlay concentrations on map
    plt.ion()
    mat_contents = sio.loadmat('map_')
    plt.figure()
    plt.imshow(mat_contents['A'], \
               extent=[np.min(mat_contents['ximage']), \
                       np.max(mat_contents['ximage']), \
                       np.min(mat_contents['yimage']), \
                       np.max(mat_contents['yimage'])])

    plt.xlabel('x (m)')
    plt.ylabel('y (m)')
    # plt.clim(0, 0.001)
    # plt.rcParams['pcolor.shading'] = 'nearest'
    plt.contour(x, y, np.mean(C1, axis=2)*1e6, cmap='hot')
    # plt.clabel(cs, cs.levels, inline=False, fmt='%.1f', fontsize=5)
    plt.title(settings.start_time[0:10])
    plt.show()
    plt.savefig('saved_figure1.png')
    return


# if __name__ == "__main__":
#     overlay_on_map()
