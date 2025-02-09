def overlay_on_map1(x, y, C1):
    import scipy.io as sio
    import matplotlib.pyplot as plt
    import numpy as np
    import settings

    # Overlay concentrations on map
    plt.ion()
    mat_contents = sio.loadmat('map_')
    plt.figure()
    plt.axis('off')
    plt.imshow(mat_contents['A'], \
               extent=[np.min(mat_contents['ximage']), \
                       np.max(mat_contents['ximage']), \
                       np.min(mat_contents['yimage']), \
                       np.max(mat_contents['yimage'])])

    plt.xlabel('x (m)')
    plt.ylabel('y (m)')
    plt.clim(0.0001, 0.001)
    # plt.rcParams['pcolor.shading'] = 'nearest'
    # cs = plt.contour(x, y, np.mean(C1, axis=2) * 1e6, cmap='hot')
    # plt.clabel(cs, cs.levels, inline=True, fmt='%.1f', fontsize=5)
    plt.contour(x, y, np.mean(C1, axis=2), levels=[0.00008, 0.0001, 0.0002, 0.0003, 0.001], cmap='autumn_r')
    plt.title(f'gaussian plume, {settings.start_time[0:10]}')
    plt.savefig(f'{settings.start_time[0:10]}_gs_map.png')
    plt.show(block=False)

    plt.ioff()

    return


# if __name__ == "__main__":
#     overlay_on_map()
