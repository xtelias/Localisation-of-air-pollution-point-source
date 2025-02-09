def overlay_on_map_with_point(point_coords):
    """
    Отрисовывает концентрации на карте и добавляет точку источника.

    Args:
    - x, y: сетка координат.
    - C1: массив концентраций.
    - point_coords: координаты точки (x, y) для отрисовки.
    """
    import scipy.io as sio
    import matplotlib.pyplot as plt
    import numpy as np
    import settings

    # Загружаем карту
    mat_contents = sio.loadmat('map2_')
    plt.figure()
    plt.axis('off')
    plt.imshow(mat_contents['A'],
               extent=[np.min(mat_contents['ximage']),
                       np.max(mat_contents['ximage']),
                       np.min(mat_contents['yimage']),
                       np.max(mat_contents['yimage'])])

    # Добавляем контуры концентраций
    # plt.contour(x, y, np.mean(C1, axis=2), levels=[0.00008, 0.0001, 0.0002, 0.0003, 0.001], cmap='autumn_r')

    # Добавляем точку источника
    #plt.scatter(point_coords[0], point_coords[1], c='red', marker='s',  alpha=.5, s=45, label='Source Point Area')
    plt.scatter(point_coords[0], point_coords[1], c='red', marker='o', alpha=.5, s=10, label='Source Point Area')
    # Подписи
    plt.xlabel('x (m)')
    plt.ylabel('y (m)')
    plt.title(f'source point area predicted by PSO, {settings.start_time[0:10]}')
    plt.legend()

    # Сохранение и отображение карты
    plt.savefig(f'{settings.start_time[0:10]}_source_point_map.png')
    plt.show()

    return


# # Пример координат источника
# source_coords = [1920, 390]  # Заменить на полученные координаты из PSO
# source_coords = [-760, 70] # координаты сенсора точки 248
# # Отрисовка точки на карте
# overlay_on_map_with_point(source_coords)
