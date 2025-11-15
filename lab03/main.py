import streamlit as st
import time
import matplotlib.pyplot as plt
import numpy as np

def step_by_step_line(x1, y1, x2, y2):
    pixels = []
    if x1 == x2:
        for y in range(min(y1, y2), max(y1, y2) + 1):
            pixels.append((x1, y))
        return pixels

    if x1 > x2:
        x1, y1, x2, y2 = x2, y2, x1, y1

    dx = x2 - x1
    dy = y2 - y1
    m = dy / dx

    if abs(dx) >= abs(dy):
        for x in range(x1, x2 + 1):
            y = int(round(y1 + m * (x - x1)))
            pixels.append((x, y))
    else:
        if y1 > y2:
            x1, y1, x2, y2 = x2, y2, x1, y1
        m_inv = dx / dy
        for y in range(y1, y2 + 1):
            x = int(round(x1 + m_inv * (y - y1)))
            pixels.append((x, y))
    return pixels


def dda_line(x1, y1, x2, y2):
    pixels = []
    dx = x2 - x1
    dy = y2 - y1

    steps = max(abs(dx), abs(dy))

    if steps == 0:
        return [(x1, y1)]

    x_increment = dx / steps
    y_increment = dy / steps
    print(x_increment, y_increment)

    x, y = float(x1), float(y1)
    for _ in range(steps + 1):
        pixels.append((round(x), round(y)))
        print(x, y, round(y))
        x += x_increment
        y += y_increment

    unique_points = []
    seen = set()
    for p in pixels:
        if p not in seen:
            unique_points.append(p)
            seen.add(p)

    return unique_points


def bresenham_line(x0, y0, x1, y1):
    points = []

    # Разница по осям
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)

    # Направление шага
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1

    # Начальная ошибка
    err = dx + dy

    x, y = x0, y0

    while True:
        points.append((x, y))

        # Проверяем, достигли ли мы конечной точки
        if x == x1 and y == y1:
            break

        # Удвоенное значение ошибки для проверки
        e2 = 2 * err

        # Корректировка ошибки и шаг по X
        if e2 >= dy:
            if x == x1: break # Предотвращает выход за пределы
            err += dy
            x += sx

        # Корректировка ошибки и шаг по Y
        if e2 <= dx:
            if y == y1: break # Предотвращает выход за пределы
            err += dx
            y += sy

    return points


def bresenham_circle(xc, yc, r):
    pixels_set = set()
    x, y = 0, r
    d = 3 - 2 * r

    def add_symmetric_pixels(cx, cy, dx, dy):
        pixels_set.add((cx + dx, cy + dy)); pixels_set.add((cx - dx, cy + dy))
        pixels_set.add((cx + dx, cy - dy)); pixels_set.add((cx - dx, cy - dy))
        pixels_set.add((cx + dy, cy + dx)); pixels_set.add((cx - dy, cy + dx))
        pixels_set.add((cx + dy, cy - dx)); pixels_set.add((cx - dy, cy - dx))

    while x <= y:
        add_symmetric_pixels(xc, yc, x, y)
        if d < 0:
            d = d + 4 * x + 6
        else:
            d = d + 4 * (x - y) + 10
            y -= 1
        x += 1
    return list(pixels_set)

def castle_pitteway(x1, y1, x2, y2):
    dx_total = abs(x2 - x1)
    dy_total = abs(y2 - y1)

    swapped = False
    if dy_total > dx_total:
        dx_total, dy_total = dy_total, dx_total # Меняем оси местами
        swapped = True

    a = dx_total
    b = dy_total

    # Шаг 2: Генерация строки движений по алгоритму со слайда 48
    if b == 0:
        # Горизонтальная/вертикальная линия
        move_string = 's' * a
    elif a == b:
        # Идеально диагональная линия
        move_string = 'd' * a
    else:
        # Общий случай из лекции
        y = b
        x = a - b
        m1 = "s"
        m2 = "d"
        while x != y:
            if x > y:
                x -= y
                m2 = m1 + m2
            else:
                y -= x
                m1 = m2 + m1
        # После завершения цикла, x-кратная последовательность m2 + m1
        move_string = (m2 + m1) * x

    # Шаг 3: Преобразование строки движений в пиксели
    pixels = []
    curr_x, curr_y = x1, y1
    pixels.append((curr_x, curr_y))

    # Определяем направление движения
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1

    for move in move_string:
        if move == 'd':
            # Диагональное смещение всегда по обеим осям
            curr_x += sx
            curr_y += sy
        else: # move == 's'
            # Прямое смещение зависит от того, меняли ли мы оси
            if swapped:
                curr_y += sy # Шаг 's' делается по доминирующей (теперь Y) оси
            else:
                curr_x += sx # Шаг 's' делается по доминирующей (X) оси
        pixels.append((curr_x, curr_y))

    return pixels

def wu_antialiasing_line(x1, y1, x2, y2):
    pixels = []

    # Функция для добавления пикселя с интенсивностью
    def plot(x, y, intensity):
        pixels.append((int(x), int(y), intensity))

    dx = x2 - x1
    dy = y2 - y1

    # Проверяем, крутая ли линия (ось Y доминирует)
    steep = abs(dy) > abs(dx)

    if steep:
        # Если крутая, меняем x и y местами
        x1, y1, x2, y2 = y1, x1, y2, x2
        dx, dy = dy, dx

    if x1 > x2:
        # Рисуем всегда слева направо
        x1, x2, y1, y2 = x2, x1, y2, y1
        dx, dy = -dx, -dy

    gradient = dy / dx if dx != 0 else 1.0

    # Обработка начальной точки
    y = y1 + gradient
    plot(x1, y1, 1.0)
    plot(x2, y2, 1.0)

    # Основной цикл
    for x in range(int(x1) + 1, int(x2)):
        # y - дробная часть. Определяет интенсивность.
        fractional_part = y - int(y)

        # Два пикселя, между которыми проходит линия
        p1_y, p2_y = int(y), int(y) + 1

        # Интенсивность обратно пропорциональна расстоянию
        intensity1 = 1 - fractional_part
        intensity2 = fractional_part

        if steep:
            # Если оси были поменяны, рисуем (y, x) вместо (x, y)
            plot(p1_y, x, intensity1)
            plot(p2_y, x, intensity2)
        else:
            plot(x, p1_y, intensity1)
            plot(x, p2_y, intensity2)

        y += gradient

    return pixels

def create_plot(pixels, algo_name, params, height):
    fig, ax = plt.subplots(figsize=(10, height))

    # Настройка координатной плоскости
    ax.set_aspect('equal', adjustable='box')
    ax.set_xlabel("Ось X")
    ax.set_ylabel("Ось Y")
    ax.spines['left'].set_position('zero')
    ax.spines['bottom'].set_position('zero')
    ax.spines['right'].set_color('none')
    ax.spines['top'].set_color('none')
    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)

    if 'окружность' in algo_name:
        xc, yc, r = params
        ideal_circle = plt.Circle((xc, yc), r, color='red', fill=False, linestyle='--', linewidth=1, label='Идеальная окружность')
        ax.add_patch(ideal_circle)
    else:
        x1, y1, x2, y2 = params
        ax.plot([x1, x2], [y1, y2], 'r--', linewidth=1, label='Идеальный отрезок')

    if pixels:
        # Проверяем, есть ли в данных интенсивность (третий элемент)
        is_antialiased = len(pixels[0]) == 3

        if is_antialiased:
            # Режим сглаживания
            px, py, intensities = zip(*pixels)
            # Создаем список цветов с альфа-каналом (прозрачностью)
            colors = [(0, 0, 0.7, i) for i in intensities] # Темно-синий с разной прозрачностью
            ax.scatter(px, py, c=colors, s=500, marker='s', label='Растеризация (сглаживание)', zorder=3)
        else:
            # Обычный режим
            px, py = zip(*pixels)
            ax.scatter(px, py, c='blue', s=50, marker='s', label='Растеризация', zorder=3)

        padding = 5
        xmin, xmax = (min(px) - padding, max(px) + padding)
        ymin, ymax = (min(py) - padding, max(py) + padding)
        ax.set_xlim(xmin, xmax); ax.set_ylim(ymin, ymax)

    ax.legend(loc="upper right")
    ax.set_title(f"Результат работы алгоритма: {algo_name}")

    return fig

st.set_page_config(layout="wide", page_title="Лабораторная работа №3")

st.title("Лабораторная работа №3: Базовые растровые алгоритмы")

# Словарь с алгоритмами
algorithms = {
    'Пошаговый': step_by_step_line,
    'ЦДА (DDA)': dda_line,
    'Брезенхем (линия)': bresenham_line,
    'Брезенхем (окружность)': bresenham_circle,
    'Кастл-Питвей': castle_pitteway,
    'Алгоритм Ву': wu_antialiasing_line
}

st.sidebar.header("Параметры")

selected_algo = st.sidebar.radio(
    "Выберите алгоритм:",
    list(algorithms.keys())
)

if 'окружность' in selected_algo:
    st.sidebar.subheader("Параметры окружности")
    xc = st.sidebar.number_input("Координата X центра (Xc)", value=10, step=1)
    yc = st.sidebar.number_input("Координата Y центра (Yc)", value=10, step=1)
    r = st.sidebar.number_input("Радиус (R)", value=8, min_value=1, step=1)
    params = (xc, yc, r)
else:
    st.sidebar.subheader("Параметры отрезка")
    x1 = st.sidebar.number_input("X1", value=2, step=1)
    y1 = st.sidebar.number_input("Y1", value=3, step=1)
    x2 = st.sidebar.number_input("X2", value=15, step=1)
    y2 = st.sidebar.number_input("Y2", value=10, step=1)
    params = (x1, y1, x2, y2)

st.sidebar.subheader("Настройки графика")
plot_height = st.sidebar.slider("Высота графика (пропорция)", min_value=4, max_value=16, value=8)

# Выполняем алгоритм и замеряем время
algo_func = algorithms[selected_algo]
start_time = time.perf_counter()
pixels = algo_func(*params)
end_time = time.perf_counter()
duration_ms = (end_time - start_time) * 1000

st.header("Результаты")
col1, col2 = st.columns(2)
col1.metric("Время выполнения", f"{duration_ms:.4f} мс")
col2.metric("Количество пикселей", f"{len(pixels)}")

st.info(algo_func)
st.info(params)

fig = create_plot(pixels, selected_algo, params, plot_height)
st.pyplot(fig, use_container_width=True)
