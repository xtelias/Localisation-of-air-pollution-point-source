import numpy as np
from ermaks_solution import ermak_func  # Подключаем модель Д. Эрмака
from openmeteo_api_call import get_weather_for_single_point  # Получаем погоду для одной точки
from data_collector import fetch_data_for_single_point # Получаем концентрацию и скор/напр ветра для одной точки из БДfr
from draw_on_map_with_point import overlay_on_map_with_point # Отрисовка
import time

# Свойства аэрозоля (определены в both_models)
HUMIDIFY = 0
dry_size = 10e-9
rho_s = [.0015392, 1840., 1500., 1725.]
Ms = [34.1e-3, 98e-3, 200e-3, 80e-3]
Mw = 18e-3
nu = [2., 2., 1., 2.]

# Координаты точек интереса (из both_models)
sensor_locations = {
    "dns_650": (33, 40),
    "dns_1ss": (13, 19),
    "gzu_100": (45, 13),
    "psp_aktash": (20, 16),
    "kaleikino": (43, 6),
    "minnibaevo": (-27, 18),
}

sensor_coords = [-760, 70]
#overlay_on_map_with_point(sensor_coords)
# [-760, 70] - координаты сенсора точки 248

# Фитнес-функция
def fitness_function(params, station_id, start_time):
    """
    Функция для оценки разности концентраций.
    params: [x, y, z, Q] - координаты и интенсивность выброса
    station_id: ID станции в базе данных
    start_time: Время для запроса концентрации
    """
    x_source, y_source, z_source, Q = params

    # Получаем погодные данные (стабильность и влажность)
    stability_class, humidity = get_weather_for_single_point(start_time[0:10])

    # Расчет дисперсий
    #Dy, Dz = calc_sigmas(stability_class, np.array([x_source])) # есть в ermak_solution

    # Получаем измеренную концентрацию из базы и актуальные данные о скорости и направлении ветра
    measured_concentration, wind_direction, wind_speed = fetch_data_for_single_point(start_time, station_id)

    # Координаты сетки
    dxy = 100  # Разрешение сетки
    x = np.mgrid[-2500:2500 + dxy:dxy]
    y = x
    [grid_x, grid_y] = np.meshgrid(x, y)
    grid_z = np.zeros(np.shape(grid_x))  # Уровень земли
    Dy = 10.
    Dz = 10.

    # Вычисляем концентрацию в точке интереса (датчик)
    grid_concentration = ermak_func(
        Q,  # Интенсивность выброса
        wind_speed,  # Актуальная скорость ветра
        wind_direction,  # Актуальное направление ветра
        grid_x,
        grid_y,
        grid_z,
        x_source,
        y_source,
        z_source,
        10,
        10,
        stability_class # тут косяк
    )

    # Влияние влажности
    if HUMIDIFY == 1:
        mass = np.pi / 6. * rho_s[0] * dry_size ** 3.
        moles = mass / Ms[0]
        nw = humidity * nu[0] * moles / (1. - humidity)
        mass2 = nw * Mw + moles * Ms[0]
        grid_concentration *= mass2 / mass

    # Получаем индекс точки интереса
    sensor_x, sensor_y = sensor_locations["minnibaevo"]  # Для выбранной станции
    predicted_concentration = grid_concentration[sensor_x, sensor_y]

    # Возвращаем разность между измеренной и рассчитанной концентрацией
    return abs(predicted_concentration - measured_concentration)


# PSO алгоритм
def pso(num_particles, bounds, fitness_function, station_id, start_time, num_iterations=200, w=0.5, c1=1.5, c2=1.5):
    """
    Основной PSO алгоритм.
    """
    start_time_exec = time.time()  # Засекаем время начала выполнения
    positions = np.random.uniform(bounds[:, 0], bounds[:, 1], (num_particles, bounds.shape[0]))
    velocities = np.random.uniform(-1, 1, (num_particles, bounds.shape[0]))
    best_positions = positions.copy()
    best_fitnesses = np.full(num_particles, np.inf)

    global_best_position = None
    global_best_fitness = np.inf

    for iteration in range(num_iterations):
        for i in range(num_particles):
            fitness = fitness_function(positions[i], station_id, start_time)

            # Обновляем личный и глобальный бесты
            if fitness < best_fitnesses[i]:
                best_fitnesses[i] = fitness
                best_positions[i] = positions[i].copy()

            if fitness < global_best_fitness:
                global_best_fitness = fitness
                global_best_position = positions[i].copy()

        # Обновляем скорости и позиции частиц
        r1 = np.random.random(positions.shape)
        r2 = np.random.random(positions.shape)
        velocities = (
            w * velocities +
            c1 * r1 * (best_positions - positions) +
            c2 * r2 * (global_best_position - positions)
        )
        positions += velocities
        positions = np.clip(positions, bounds[:, 0], bounds[:, 1])

        print(f"Итерация {iteration + 1}/{num_iterations}, Лучший фитнес: {global_best_fitness}")

    elapsed_time = time.time() - start_time_exec
    print(f"Время выполнения: {elapsed_time:.2f} секунд")

    return global_best_position, global_best_fitness


# Функция для вызова из GUI
def run_pso_gui(station_id, start_time):
    """
    Функция запуска PSO из GUI.
    """
    bounds = np.array([
        [-2500, 2500],  # x
        [-2500, 2500],  # y
        [0, 100],       # z
        [0, 10]         # Q (интенсивность выброса)
    ])

    best_params, best_fitness = pso(
        num_particles=50,
        bounds=bounds,
        fitness_function=fitness_function,
        station_id=station_id,
        start_time=start_time
    )

    result_message = (
        f"Лучшие параметры источника:\n"
        f"X: {best_params[0]:.2f}, Y: {best_params[1]:.2f}, Z: {best_params[2]:.2f}, Q: {best_params[3]:.2f}\n"
        f"Лучший фит: {best_fitness:.4f}"
    )
    print(result_message)
    return best_params


# Тестовый запуск, если файл запущен напрямую
if __name__ == "__main__":
    station_id = 248  # minnibaevo
    start_time = "2022-06-29T11:20:00.000"  # Пример времени
    optimized_values = run_pso_gui(station_id, start_time)
    source_coords = [optimized_values[0],optimized_values[1]]
    overlay_on_map_with_point(source_coords)

