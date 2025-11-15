import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io

def apply_threshold(image, threshold_value, method_otsu):
    gray_image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

    threshold_type = cv2.THRESH_BINARY
    if method_otsu:
        threshold_type |= cv2.THRESH_OTSU

    otsu_thresh_val, result_image = cv2.threshold(gray_image, threshold_value, 255, threshold_type)

    return result_image, int(otsu_thresh_val)

def apply_unsharp_masking(image, radius, amount):
    if radius % 2 == 0:
        radius += 1

    blurred = cv2.GaussianBlur(image, (radius, radius), 0)

    # Result = Original + amount * (Original - Blurred)
    sharpened = cv2.addWeighted(image, 1.0 + amount, blurred, -amount, 0)

    return sharpened

st.set_page_config(layout="wide", page_title="Обработка изображений (Вариант 7)")

st.title("Лабораторная работа №2: Обработка изображений")
st.write("Глобальная пороговая обработка и увеличение резкости")


st.sidebar.title("Панель управления")

st.sidebar.header("1. Загрузка изображения")
uploaded_file = st.sidebar.file_uploader("Выберите изображение...", type=["jpg", "jpeg", "png", "bmp"])

if 'original_image' not in st.session_state:
    st.session_state.original_image = None
    st.session_state.processed_image = None
    st.session_state.last_otsu_thresh = 127

if uploaded_file is not None:
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    # Важно: OpenCV читает в формате BGR. PIL/Streamlit работают с RGB.
    # Поэтому конвертируем сразу после чтения.
    image_bgr = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    st.session_state.original_image = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    st.session_state.processed_image = st.session_state.original_image.copy()


if st.session_state.original_image is not None:
    col1, col2 = st.columns(2)

    with col1:
        st.header("Оригинал")
        st.image(st.session_state.original_image, use_column_width=True)

    st.sidebar.header("2. Глобальная пороговая обработка")
    method = st.sidebar.radio("Метод:", ("Ручной", "Метод Оцу"))

    is_otsu = (method == "Метод Оцу")

    threshold_value = st.sidebar.slider(
        "Значение порога", 0, 255, 127,
        disabled=is_otsu,
        help="Этот слайдер неактивен, когда выбран метод Оцу."
    )

    if st.sidebar.button("Применить порог"):
        processed, otsu_val = apply_threshold(st.session_state.original_image, threshold_value, is_otsu)
        st.session_state.processed_image = processed
        if is_otsu:
            st.session_state.last_otsu_thresh = otsu_val

    if is_otsu:
        st.sidebar.info(f"Вычисленный порог Оцу: **{st.session_state.last_otsu_thresh}**")

    st.sidebar.header("3. Увеличение резкости")
    sharpen_amount = st.sidebar.slider("Сила эффекта", 0.1, 3.0, 1.5, 0.1)
    sharpen_radius = st.sidebar.slider("Радиус размытия", 1, 21, 5, 2)

    if st.sidebar.button("Применить резкость"):
        processed = apply_unsharp_masking(st.session_state.original_image, sharpen_radius, sharpen_amount)
        st.session_state.processed_image = processed

    with col2:
        st.header("Результат")
        st.image(st.session_state.processed_image, use_column_width=True)

        try:
            result_pil = Image.fromarray(st.session_state.processed_image.astype('uint8'))
            buf = io.BytesIO()
            if len(result_pil.getbands()) == 1:
                result_pil = result_pil.convert("L")
            else:
                result_pil = result_pil.convert("RGB")

            result_pil.save(buf, format="PNG")
            byte_im = buf.getvalue()

            st.download_button(
                label="Скачать результат",
                data=byte_im,
                file_name="processed_image.png",
                mime="image/png"
            )
        except Exception as e:
            st.error(f"Не удалось подготовить файл для скачивания: {e}")

else:
    st.info("Пожалуйста, загрузите изображение, используя панель слева.")
