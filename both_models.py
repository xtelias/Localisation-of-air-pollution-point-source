import numpy as np
import sys
import tqdm as tqdm
import pandas as pd
import settings

from ermaks_solution import ermak_func
from gauss_function_calculator import gauss_func
from draw_on_map1 import overlay_on_map1
from draw_on_map2 import overlay_on_map2
from data_collector import weather_data_collect
from openmeteo_api_call import stability_classes, humidify, RH

import matplotlib.pyplot as plt
from matplotlib import rc

rc('font', **{'family': 'sans-serif', 'sans-serif': ['Helvetica']})

rc('text', usetex=True)


def smooth(y, box_pts):
    box = np.ones(box_pts) / box_pts
    y_smooth = np.convolve(y, box, mode='same')
    return y_smooth


# Aerosol properties
HUMIDIFY = 1  # 0 - NO HUMIDIFY; 1 - HUMIDIFY
# MODEL = 2   # 1 - Gauss 2 - Ermak - no need this here since we use both models at once
# DRY_AEROSOL = 1

# SECTION 0: Definitions (normally don't modify this section)
# view
PLAN_VIEW = 1
HEIGHT_SLICE = 2
SURFACE_TIME = 3
NO_PLOT = 4

# wind field
CONSTANT_WIND = 1
FLUCTUATING_WIND = 2
PREVAILING_WIND = 3

# number of stacks
ONE_STACK = 1
TWO_STACKS = 2
THREE_STACKS = 3

# stability of the atmosphere
CONSTANT_STABILITY = 1
ANNUAL_CYCLE = 2
stability_str = ['A', 'B', 'C', \
                 'D', 'E', 'F']

HYDROGEN_SULFIDE = 1
SULPHURIC_ACID = 2
ORGANIC_ACID = 3
AMMONIUM_NITRATE = 4
nu = [2., 2., 1., 2.]  # quantity
rho_s = [.0015392, 1840., 1500., 1725.]
Ms = [34.1e-3, 98e-3, 200e-3, 80e-3]
Mw = 18e-3

dxy = 100  # resolution of the model in both x and y directions
dz = 10
x = np.mgrid[-2500:2500 + dxy:dxy]  # solve on a 5 km domain
y = x  # x-grid is same as y-grid
###########################################################################


# SECTION 1: Configuration

# RH = 0.90  # Relative humidity
aerosol_type = HYDROGEN_SULFIDE

dry_size = 10e-9

# stab1 = 5  # set from 1-6
stability_used = CONSTANT_STABILITY

output = PLAN_VIEW  # HEIGHT_SLICE PLAN_VIEW
x_slice = 26  # position (1-50) to take the slice in the x-direction
y_slice = 1  # position (1-50) to plot concentrations vs time

wind = CONSTANT_WIND
stacks = 3
stack_x = [-400., 1000., -200.]  # dns 1 ss; dns 650; kaleikino
stack_y = [-900., 900., 700.]

Q = [0.2193426339 * 1, 0.0059080595 * 1, 0.01927522629 * 1]  # mass emitted per unit time
# Q = [0.2193426339, 0., 0.] # test Q
H = [51.6, 33., 4.]  # stack height, m
days = 3  # run the model for 365 days
# --------------------------------------------------------------------------
times = np.mgrid[1:days * 24 + 1:1] / 24.

Dy = 10.
Dz = 10.

# SECTION 2: Act on the configuration information

# Decide which stability profile to use
if stability_used == CONSTANT_STABILITY:

    # stability = stab1 * np.ones((days * 24, 1))
    stability = stability_classes
    # print('stab class:', stability)
    # stability_str = stability_str[stab1 - 1]
    stability_str = settings.start_time[0:10]
elif stability_used == ANNUAL_CYCLE:

    stability = np.round(2.5 * np.cos(times * 2. * np.pi / 365.) + 3.5)
    stability_str = 'Annual cycle'
else:
    sys.exit()

# decide what kind of run to do, plan view or y-z slice, or time series
if output == PLAN_VIEW or output == SURFACE_TIME or output == NO_PLOT:

    C1 = np.zeros((len(x), len(y), days * 24))  # array to store data, initialised to be zero
    C2 = np.zeros((len(x), len(y), days * 24))  # this one is for ermak's

    [x, y] = np.meshgrid(x, y)  # x and y defined at all positions on the grid
    z = np.zeros(np.shape(x))  # z is defined to be at ground level.
# elif output == HEIGHT_SLICE:
#     z = np.mgrid[0:500 + dz:dz]  # z-grid
#
#     C1 = np.zeros((len(y), len(z), days * 24))  # array to store data, initialised to be zero
#
#     [y, z] = np.meshgrid(y, z)  # y and z defined at all positions on the grid
#     x = x[x_slice] * np.ones(np.shape(y))  # x is defined to be x at x_slice
else:
    sys.exit()

# wind_speed = 5. * np.ones((days * 24, 1))  # m/s
wind_direction, wind_velocity = weather_data_collect()
# print(wind_direction, wind_velocity)
wind_speed = np.array(wind_velocity)
# print('wind speed:', wind_speed)
# wind_speed = np.array([[0.7], [0.5], [0.2], [0.7], [0.1], [0.5], [0.4], [0.4],
#                        [0.4], [0.4], [0.5], [1.8], [2], [1.5], [1.6], [2.2],
#                        [1.7], [3.3], [3.5], [2.8], [4], [2.6], [2.7], [2.7],
#
#                        [0.7], [0.5], [0.2], [0.7], [0.1], [0.5], [0.4], [0.4],
#                        [0.4], [0.4], [0.5], [1.8], [2], [1.5], [1.6], [2.2],
#                        [1.7], [3.3], [3.5], [2.8], [4], [2.6], [2.7], [2.7],
#
#                        [0.7], [0.5], [0.2], [0.7], [0.1], [0.5], [0.4], [0.4],
#                        [0.4], [0.4], [0.5], [1.8], [2], [1.5], [1.6], [2.2],
#                        [1.7], [3.3], [3.5], [2.8], [4], [2.6], [2.7], [2.7],
#                        ])
# print(f'wind speed={wind_speed}') #- test array

if wind == CONSTANT_WIND:
    wind_dir = np.array(wind_direction)
    # wind_dir = 90. * np.ones((days * 24, 1))  # test massive
    # wind_dir = np.array([[90], [90], [90], [90], [90], [90], [90], [90],
    #                      [90], [90], [90], [90], [90], [90], [90], [90],
    #                      [90], [90], [90], [90], [90], [90], [90], [90],
    #
    #                      [90], [90], [90], [90], [90], [90], [90], [90],
    #                      [90], [90], [90], [90], [90], [90], [90], [90],
    #                      [90], [90], [90], [90], [90], [90], [90], [90],
    #
    #                      [90], [90], [90], [90], [90], [90], [90], [90],
    #                      [90], [90], [90], [90], [90], [90], [90], [90],
    #                      [90], [90], [90], [90], [90], [90], [90], [90]
    #                      ])
    # print(f'wind dir - {wind_dir}') #- test array
    wind_dir_str = 'Constant wind'
# elif wind == FLUCTUATING_WIND:
#     wind_dir = 360. * np.random.rand(days * 24, 1)
#     wind_dir_str = 'Random wind'
# elif wind == PREVAILING_WIND:
#     wind_dir = -np.sqrt(2.) * erfcinv(2. * np.random.rand(24 * days, 1)) * 40.  # norminv(rand(days.*24,1),0,40)
#     # note at this point you can add on the prevailing wind direction, i.e.
#     wind_dir = wind_dir + 45
#     wind_dir[np.where(wind_dir >= 360.)] = \
#         np.mod(wind_dir[np.where(wind_dir >= 360)], 360)
#     wind_dir_str = 'Prevailing wind'
# else:
#     sys.exit()
# --------------------------------------------------------------------------


# SECTION 3: Main loop

C1 = np.zeros((len(x), len(y), len(wind_dir)))
C2 = np.zeros((len(x), len(y), len(wind_dir)))

for i in tqdm.tqdm(range(0, len(wind_dir))):
    for j in range(0, stacks):
        C = np.ones((len(x), len(y)))
        C = gauss_func(Q[j], wind_speed[i], wind_dir[i], x, y, z,
                       stack_x[j], stack_y[j], H[j], Dy, Dz, stability[i])
        C_e = np.ones((len(x), len(y)))
        C_e = ermak_func(Q[j], wind_speed[i], wind_dir[i], x, y, z,
                         stack_x[j], stack_y[j], H[j], Dy, Dz, stability[i])
        # print(f'x={x}, y={y}, c={C}')
        C1[:, :, i] = C1[:, :, i] + np.round(C * 1e3, 8)
        C2[:, :, i] = C2[:, :, i] + np.round(C_e * 1e3, 8)
        # print(i, C1[19][12][i])

# SECTION 4: Post process / output

# decide whether to humidify the aerosol and hence increase the mass
if HUMIDIFY == 1:
    for i in range(0, len(humidify)):
        if humidify[i] == 1:
            # print('dry')
            continue
        elif humidify[i] == 2:
            mass = np.pi / 6. * rho_s[aerosol_type] * dry_size ** 3.
            moles = mass / Ms[aerosol_type]

            nw = RH[i] * nu[aerosol_type] * moles / (1. - RH[i])
            mass2 = nw * Mw + moles * Ms[aerosol_type]

            # C1 = C1 * mass2 / mass
            C1[:, :, i] = C1[:, :, i] * mass2 / mass
            C2[:, :, i] = C2[:, :, i] * mass2 / mass
            # C1[:, :, i + 1] = C1[:, :, i + 1] * mass2 / mass
            # C1[:, :, i + 2] = C1[:, :, i + 2] * mass2 / mass

            # print('wet')
        else:
            sys.exit()

np.round(C1, 6)
np.round(C2, 6)

# conc_data = []
conc_data1 = []
conc_data2 = []
conc_data3 = []
conc_data4 = []
conc_data5 = []

conc_data_e1 = []
conc_data_e2 = []
conc_data_e3 = []
conc_data_e4 = []
conc_data_e5 = []

# in range (N) N - num of timestamps
for i in range(72):  # C1[40][32] - dns 650 C1[19][12] - DNS-1SS
    # C1[14][45] - GZU_100 C1[16][20] - PSP Aktash C1[7][43] - Kaleikino
    conc_data1.append(C1[33][40][i])  # dns 650
    conc_data2.append(C1[13][19][i])  # DNS-1SS
    conc_data3.append(C1[45][13][i])  # GZU_100
    conc_data4.append(C1[20][16][i])  # PSP Aktash
    conc_data5.append(C1[43][6][i])  # Kaleikino
    conc_data_e1.append(C2[33][40][i])  # dns 650
    conc_data_e2.append(C2[13][19][i])  # DNS-1SS
    conc_data_e3.append(C2[45][13][i])  # GZU_100
    conc_data_e4.append(C2[20][16][i])  # PSP Aktash
    conc_data_e5.append(C2[43][6][i])  # Kaleikino
    # conc_data_e5.append(C2[27][18][i])  # Minnibaevo
    # print(C1[40][32][i] * 1000)

# C1[33][40][71] = 100
# C1[13][19][71] = 100
# C1[45][13][71] = 100
# C1[20][16][71] = 100
# C1[43][6][71] = 100
# C1[27][18][71] = 100

df = pd.DataFrame({f'sensor dns 650 {settings.start_time[0:10]} gauss:': conc_data1,
                   'dns 650 ermak:': conc_data_e1,
                   f'sensor dns1ss  gauss:': conc_data2,
                   'dns1ss ermak:': conc_data_e2,
                   f'sensor gzu100 gauss:': conc_data3,
                   'gzu100 ermak:': conc_data_e3,
                   f'sensor psp aktash gauss:': conc_data4,
                   'psp aktash ermak:': conc_data_e4,
                   f'sensor kaleikino gauss:': conc_data5,
                   'kaleikino ermaks:': conc_data_e5}
                  )
df.to_excel("C:\\Users\\powerdrive\\src\\gaussian_plume\\output.xlsx")

# df = pd.DataFrame({f'sensor {settings.station_id}; {settings.start_time[0:10]}': conc_data_e})
# df.to_excel("C:\\Users\\ilia\\PycharmProjects\\gaussian_plume\\output_ermak.xlsx")
# output the plots

if output == PLAN_VIEW:
    plt.figure()
    plt.ion()
    plt.axis('off')
    plt.rcParams['pcolor.shading'] = 'nearest'
    plt.pcolor(x, y, np.mean(C1, axis=2), cmap='coolwarm')  # coolwarm
    plt.clim(0.00005, 0.001)
    plt.title(f'gaussian plume, {settings.start_time[0:10]}')
    # plt.xlabel('x (M)')
    # plt.ylabel('y (M)')
    cb1 = plt.colorbar()
    cb1.set_label(r'$\mu$ g m$^{-3}$')
    plt.savefig(f'{settings.start_time[0:10]}_gs.png')
    plt.show()

    plt.figure()
    plt.ion()
    plt.axis('off')
    plt.rcParams['pcolor.shading'] = 'nearest'
    plt.pcolor(x, y, np.mean(C2, axis=2), cmap='coolwarm')  # coolwarm
    plt.clim(0.00005, 0.001)
    plt.title(f'ermak\'s solution, {settings.start_time[0:10]}')
    # plt.xlabel('x (M)')
    # plt.ylabel('y (M)')
    cb1 = plt.colorbar()
    cb1.set_label(r'$\mu$ g m$^{-3}$')
    plt.savefig(f'{settings.start_time[0:10]}_erm.png')
    plt.show()
    plt.ioff()

    overlay_on_map1(x, y, C1)
    overlay_on_map2(x, y, C2)

    plt.show()

elif output == HEIGHT_SLICE:
    plt.figure()
    plt.ion()
    plt.rcParams['pcolor.shading'] = 'nearest'

    plt.pcolor(y, z, np.mean(C1, axis=2) * 1e3, cmap='jet')
    plt.clim((0, 1e2))
    plt.xlabel('y (M)')
    plt.ylabel('z (M)')
    plt.title(' height slice ')
    cb1 = plt.colorbar()
    cb1.set_label(r'$\mu$ g m$^{-3}$')
    plt.show()
    plt.savefig('saved_figure.png')

elif output == SURFACE_TIME:
    f, (ax1, ax2) = plt.subplots(2, sharex=True, sharey=False)
    ax1.plot(times, 1e6 * np.squeeze(C1[y_slice, x_slice, :]))
    try:
        ax1.plot(times, smooth(1e6 * np.squeeze(C1[y_slice, x_slice, :]), 24), 'r')
        ax1.legend(('Hourly mean', 'Daily mean'))
    except:
        sys.exit()

    ax1.set_xlabel('time (days)')
    ax1.set_ylabel(r'Mass loading ($\mu$ g m$^{-3}$)')
    ax1.set_title('surface' + '\n')

    ax2.plot(times, stability)
    ax2.set_xlabel('time (days)')
    ax2.set_ylabel('Stability parameter')
    f.show()

elif output == NO_PLOT:
    print('don''t plot')
    overlay_on_map1(x, y, C1)
    overlay_on_map2(x, y, C2)
else:
    sys.exit()
