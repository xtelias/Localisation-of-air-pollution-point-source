from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from threading import Thread
from tkinter import messagebox  # Для всплывающих окон
import subprocess
import sys
from PSO import run_pso_gui  #  для запуска PSO


# Функция для загрузки настроек из settings.py
def load_settings(file_path):
    settings = {}
    try:
        with open(file_path, "r") as file:
            exec(file.read(), {}, settings)  # Выполнение кода Python из файла
    except FileNotFoundError:
        print(f"Ошибка: файл {file_path} не найден.")
    except Exception as e:
        print(f"Ошибка при чтении настроек: {e}")
    return settings


# Функция для сохранения настроек в settings.py
def save_settings(file_path, settings):
    try:
        with open(file_path, "w") as file:
            for key, value in settings.items():
                file.write(f"{key} = {repr(value)}\n")
    except Exception as e:
        print(f"Ошибка при сохранении настроек: {e}")


# Функция для запуска both_models.py в отдельном потоке
def run_both_models_thread(instance):
    def run_file():
        try:
            # Запускаем both_models.py в текущем интерпретаторе Python
            subprocess.run([sys.executable, "both_models.py"])
        except Exception as e:
            print(f"Ошибка при запуске both_models.py: {e}")

    # Создаем и запускаем поток
    thread = Thread(target=run_file)
    thread.start()


# Функция для запуска PSO и отображения результатов
def run_pso_thread(instance=None):  # Добавляем аргумент 'instance', чтобы избежать ошибки
    def run_file():
        try:
            # Получаем параметры из настроек
            settings = load_settings('settings.py')
            station_id = settings.get('station_id', 252)  # Используем значение из настроек
            start_time = settings.get('start_time', '2024-12-01T12:00:00.000')  # Используем значение из настроек

            # Запускаем PSO
            result_message = run_pso_gui(station_id, start_time)

            # Отображаем результаты в всплывающем окне
            messagebox.showinfo("Результаты PSO", result_message)

        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка:\n{str(e)}")

    # Запускаем PSO в отдельном потоке
    thread = Thread(target=run_file)
    thread.start()


# Функция для завершения приложения
def close_app(instance):
    App.get_running_app().stop()


# Основной GUI
def build_gui():
    layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

    label = Label(text="Добро пожаловать в приложение!")
    layout.add_widget(label)

    # Загружаем настройки из settings.py
    settings_file = "settings.py"
    settings = load_settings(settings_file)

    # Поля для ввода параметров из settings.py
    inputs = {}
    for key, value in settings.items():
        row = BoxLayout(orientation='horizontal', size_hint=(1, None), height=40)
        label = Label(text=f"{key}:", size_hint=(0.3, 1))
        text_input = TextInput(text=str(value), multiline=False, size_hint=(0.7, 1))
        inputs[key] = text_input
        row.add_widget(label)
        row.add_widget(text_input)
        layout.add_widget(row)

    # Кнопка "Сохранить настройки"
    def save_settings_button(instance):
        for key, text_input in inputs.items():
            value = text_input.text
            if key == "station_id" and value.isdigit():
                settings[key] = int(value)
            else:
                settings[key] = value
        save_settings(settings_file, settings)
        print("Настройки сохранены:", settings)

    save_button = Button(
        text="Сохранить настройки",
        size_hint=(1, 0.2),
        background_color=(0, 1, 0, 1),
    )
    save_button.bind(on_press=save_settings_button)
    layout.add_widget(save_button)

    # Первая кнопка для запуска both_models.py
    run_button1 = Button(
        text="Запустить симуляцию модели Гауссова шлейфа",
        size_hint=(1, 0.2),
        background_color=(0, 0.5, 1, 1),
    )
    run_button1.bind(on_release=run_both_models_thread)
    layout.add_widget(run_button1)

    # Вторая кнопка для запуска both_models.py
    run_button2 = Button(
        text="Запустить симуляцию продукционной модели с учетом влияния осадков",
        size_hint=(1, 0.2),
        background_color=(1, 0.5, 0, 1),
    )
    run_button2.bind(on_release=run_both_models_thread)
    layout.add_widget(run_button2)

    # Третья кнопка для запуска решения обратной задачи
    run_button3 = Button(
        text="Запустить симуляцию алгоритма роя частиц для поиска источников в указанный момент времени",
        size_hint=(1, 0.2),
        background_color=(1, 0.5, 0, 1),
    )
    run_button3.bind(on_release=run_pso_thread)  # Обновлено для запуска PSO
    layout.add_widget(run_button3)

    # Кнопка для выхода
    exit_button = Button(
        text="Выход",
        size_hint=(1, 0.2),
        background_color=(1, 0, 0, 1),
    )
    exit_button.bind(on_press=close_app)
    layout.add_widget(exit_button)

    return layout


# Приложение
class MainApp(App):
    def build(self):
        return build_gui()


# Запуск приложения
if __name__ == "__main__":
    MainApp().run()
