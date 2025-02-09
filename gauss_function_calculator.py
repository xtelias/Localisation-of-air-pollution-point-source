import numpy as np
import sys
from scipy.special import erfcinv as erfcinv
from dispersions_calculator import calc_sigmas


def gauss_func(Q, u, dir1, x, y, z, xs, ys, H, Dy, Dz, STABILITY):
    u1 = u
    x1 = x - xs  # shift the coordinates so that stack is centre point
    y1 = y - ys

    # components of u in x and y directions
    wx = u1 * np.sin((dir1 - 180.) * np.pi / 180.);
    wy = u1 * np.cos((dir1 - 180.) * np.pi / 180.);

    # Need angle between point x, y and the wind direction, so use scalar product:
    dot_product = wx * x1 + wy * y1;
    # product of magnitude of vectors:
    magnitudes = u1 * np.sqrt(x1 ** 2. + y1 ** 2.);

    # angle between wind and point (x,y)
    subtended = np.arccos(dot_product / (magnitudes + 1e-15));
    # distance to point x,y from stack
    hypotenuse = np.sqrt(x1 ** 2. + y1 ** 2.);

    # distance along the wind direction to perpendicular line that intersects
    # x,y
    downwind = np.round(np.cos(subtended) * hypotenuse, 2);

    # Now calculate distance cross wind.
    crosswind = np.sin(subtended) * hypotenuse;

    ind = np.where(downwind > 0.);
    C = np.zeros((len(x), len(y)));

    # sig_y=sqrt(2.*Dy.*downwind./u1);
    # sig_z=sqrt(2.*Dz.*downwind./u1);

    # calculate sigmas based on stability and distance downwind
    (sig_y, sig_z) = calc_sigmas(STABILITY, downwind)

    C[ind] = (Q / (2. * np.pi * u1 * sig_y[ind] * sig_z[ind])
              * np.exp(-crosswind[ind] ** 2. / (2. * sig_y[ind] ** 2.))
              * (np.exp(-(z[ind] - H) ** 2. / (2. * sig_z[ind] ** 2.))
                 + np.exp(-(z[ind] + H) ** 2. / (2. * sig_z[ind] ** 2.))))

    # print(f'c ind = {len(C[ind])}')
    # for i in range(len(C[ind]+1)):
    #     round(C[ind][i], 8)
    # print(f'C[ind] = {C[ind]}')
    # f = open('text.txt', 'w')
    # for i in range(0, len(C[ind])):
    #     # c = np.ndarray.tolist(C[ind][i])
    #     # print(f'C[ind][i] = {c}')
    #     c1 = np.array2string(C[ind][i])
    #     # f.write('c=' + c1 + '\n')
    # f.close()

    return C
