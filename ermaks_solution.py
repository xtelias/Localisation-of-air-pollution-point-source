import numpy as np
from diffusivity_calc import calc_sigmas_k
from scipy.special import erfc
import warnings


# suppress warnings
# warnings.filterwarnings('ignore')


def ermak_func(Q, u, dir1, x, y, z, xs, ys, H, Dy, Dz, STABILITY):
    u1 = u
    x1 = x - xs  # shift the coordinates so that stack is centre point
    y1 = y - ys

    # components of u in x and y directions
    wx = u1 * np.sin((dir1 - 180.) * np.pi / 180.)
    wy = u1 * np.cos((dir1 - 180.) * np.pi / 180.)

    # Need angle between point x, y and the wind direction, so use scalar product:
    dot_product = wx * x1 + wy * y1
    # product of magnitude of vectors:
    magnitudes = u1 * np.sqrt(x1 ** 2. + y1 ** 2.)

    # angle between wind and point (x,y)
    subtended = np.arccos(dot_product / (magnitudes + 1e-15))
    # distance to point x,y from stack
    hypotenuse = np.sqrt(x1 ** 2. + y1 ** 2.)

    # distance along the wind direction to perpendicular line that intersects
    # x,y
    downwind = np.round(np.cos(subtended) * hypotenuse, 2)

    # Now calculate distance cross wind.
    crosswind = np.sin(subtended) * hypotenuse

    # print(np.size(downwind), np.size(crosswind))

    C = np.zeros((len(x), len(y)), dtype=np.longdouble);

    d = 18e-5

    W_dep = -0.0732  # H2S Baek's dry deposition velocity

    rho = 1.36  # H2S density

    W_set = rho * 9.8 * pow(d, 2) / 18 * 18e-6

    Wo = W_dep - (W_set / 2)

    # sig_y=sqrt(2.*Dy.*downwind./u1); # simple variant
    # sig_z=sqrt(2.*Dz.*downwind./u1);

    # calculate sigmas based on stability and distance downwind

    (sig_y, sig_z) = calc_sigmas_k(STABILITY, downwind)

    ind = np.where(downwind > 0.)
    K = np.ones(np.shape(sig_z))

    K[ind] = (sig_z[ind] ** 2) * u1 / (2 * downwind[ind])

    sigz_sq = np.zeros(np.shape(sig_z)) # squared dispersion for 3rd exponent
    for i in range(len(sig_z[ind])):
        sigz_sq[ind][i] = sig_z[ind][i] * sig_z[ind][i]

    third_exp = np.zeros((len(x), len(y)), dtype=np.longdouble)

    third_exp[ind] = np.exp((Wo * (z[ind] + H)) / K[ind] + (pow(Wo, 2) *
                                                            sigz_sq[ind]) / (2 * np.float_power(K[ind], 2)))

    # third_exp[ind] = np.exp((Wo * (z[ind] + H)) / K[ind] + (pow(Wo, 2) *
    #         np.float_power(sig_z[ind], 2)) / (2 * np.float_power(K[ind], 2)))

    # third_exp[ind] = np.exp((Wo * (z[ind] + H)) / K[ind] + (pow(Wo, 2) *
    #                                                         (np.power(sig_z[ind], 1))) / (2 * np.float_power(K[ind], 2)))

    # third_exp[ind] = np.exp((Wo * (z[ind] + H)) / K[ind] + (pow(Wo, 2) *
    #                                                         np.float_power(sig_z[ind], 2)) / (2 * K[ind] ** 1))

    C[ind] = (Q / (2. * np.pi * u1 * sig_y[ind] * sig_z[ind])
              * np.exp(-crosswind[ind] ** 2 / (2 * (sig_y[ind] ** 2)))
              * np.exp(-W_set * (z[ind] - H) / (2. * K[ind]) - ((W_set ** 2) * sig_z[ind] ** 2) / 8 * (K[ind] ** 2))
              * (np.exp(-(z[ind] - H) ** 2 / (2 * sig_z[ind] ** 2)) +
                 np.exp(-(z[ind] + H) ** 2 / (2 * sig_z[ind] ** 2)) -
                 ((np.sqrt(2 * np.pi) * Wo * sig_z[ind]) / K[ind]) *
                 third_exp[ind] *  # problem
                 erfc(Wo * sig_z[ind] / np.sqrt(2) * K[ind] + (z[ind] + H) / np.sqrt(2) * sig_z[ind])))

    # np.exp((Wo * (z[ind] + H) / K[ind]) + (Wo ** 2. * (sig_z[ind] ** 2.)) / (2 * K[ind] ** 2.)) *  # problem line
    # print(np.argwhere(np.isnan(C)))
    # C[np.argwhere(np.isnan(C))] = 0.

    return C
