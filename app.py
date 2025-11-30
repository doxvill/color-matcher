import streamlit as st
import google.generativeai as genai
from PIL import Image, ImageDraw, ImageFont
import json
import io
import os
from typing import List, Dict, Tuple
import math

# Настройка страницы
st.set_page_config(
    page_title="Color Matcher",
    page_icon="🎨",
    layout="wide"
)

# Словарь популярных цветов RAL Classic (30 цветов)
RAL_COLORS = {
    "RAL 1000": "#CDBA88",
    "RAL 1001": "#D0B084",
    "RAL 1002": "#D2AA6D",
    "RAL 1003": "#F9A800",
    "RAL 1004": "#E49E00",
    "RAL 1005": "#C18700",
    "RAL 1006": "#D5A900",
    "RAL 1007": "#D89700",
    "RAL 1011": "#AF8A54",
    "RAL 1012": "#DDAF27",
    "RAL 1013": "#E3D9C6",
    "RAL 1014": "#DDC49A",
    "RAL 1015": "#E6D2B5",
    "RAL 1016": "#F5D033",
    "RAL 1017": "#F8A700",
    "RAL 1018": "#F7B500",
    "RAL 1019": "#F0A000",
    "RAL 1020": "#CCA96B",
    "RAL 1021": "#F9B900",
    "RAL 1023": "#F8B500",
    "RAL 1024": "#C8B482",
    "RAL 1026": "#FFFF00",
    "RAL 1027": "#F5C900",
    "RAL 1028": "#FFBB00",
    "RAL 1032": "#F6A600",
    "RAL 1033": "#F5A300",
    "RAL 1034": "#E8A300",
    "RAL 1035": "#E79E00",
    "RAL 1036": "#E49E00",
    "RAL 1037": "#D08F00"
}

# Дополнительные популярные цвета для расширения палитры
RAL_COLORS_EXTENDED = {
    **RAL_COLORS,
    "RAL 2000": "#E25303",
    "RAL 2001": "#DD4F00",
    "RAL 2002": "#C63927",
    "RAL 2003": "#FA842B",
    "RAL 2004": "#E75B12",
    "RAL 2005": "#FF4B00",
    "RAL 2007": "#FF6B00",
    "RAL 2008": "#F44600",
    "RAL 2009": "#FF8C00",
    "RAL 2010": "#E86C00",
    "RAL 3000": "#C1121C",
    "RAL 3001": "#A52019",
    "RAL 3002": "#A2231D",
    "RAL 3003": "#A21414",
    "RAL 3004": "#701D23",
    "RAL 3005": "#5E2028",
    "RAL 3007": "#412227",
    "RAL 3009": "#6D342D",
    "RAL 3011": "#7A2E2D",
    "RAL 3012": "#C85A54",
    "RAL 3013": "#D05D56",
    "RAL 3014": "#D4635D",
    "RAL 3015": "#E07B7B",
    "RAL 3016": "#C85A54",
    "RAL 3017": "#C85A54",
    "RAL 3018": "#C85A54",
    "RAL 3020": "#C1121C",
    "RAL 3022": "#D84A20",
    "RAL 3024": "#E25303",
    "RAL 3026": "#F44600",
    "RAL 3027": "#B32428",
    "RAL 3028": "#C1121C",
    "RAL 3031": "#A52019",
    "RAL 3032": "#701D23",
    "RAL 3033": "#A21414",
    "RAL 4001": "#816183",
    "RAL 4002": "#8D3C4B",
    "RAL 4003": "#C4618C",
    "RAL 4004": "#651E38",
    "RAL 4005": "#76689A",
    "RAL 4006": "#903373",
    "RAL 4007": "#47243C",
    "RAL 4008": "#844C82",
    "RAL 4009": "#9D8692",
    "RAL 4010": "#C4618C",
    "RAL 5000": "#1E3A82",
    "RAL 5001": "#1E5584",
    "RAL 5002": "#00387B",
    "RAL 5003": "#1F3057",
    "RAL 5004": "#192F5B",
    "RAL 5005": "#0F4C75",
    "RAL 5007": "#005B8C",
    "RAL 5008": "#1F3057",
    "RAL 5009": "#0D4F8C",
    "RAL 5010": "#00387B",
    "RAL 5011": "#1E5584",
    "RAL 5012": "#0089B6",
    "RAL 5013": "#193153",
    "RAL 5014": "#63717B",
    "RAL 5015": "#0078B3",
    "RAL 5017": "#005B8C",
    "RAL 5018": "#007CB0",
    "RAL 5019": "#005B8C",
    "RAL 5020": "#004F7C",
    "RAL 5021": "#1E5584",
    "RAL 5022": "#2D5973",
    "RAL 5023": "#2175B8",
    "RAL 5024": "#0F4C75",
    "RAL 6000": "#316650",
    "RAL 6001": "#287233",
    "RAL 6002": "#2D572C",
    "RAL 6003": "#424632",
    "RAL 6004": "#1F3A3D",
    "RAL 6005": "#2F4538",
    "RAL 6006": "#3E3B32",
    "RAL 6007": "#343B29",
    "RAL 6008": "#39352A",
    "RAL 6009": "#31372B",
    "RAL 6010": "#35682D",
    "RAL 6011": "#587246",
    "RAL 6012": "#343E40",
    "RAL 6013": "#6C7C59",
    "RAL 6014": "#47402E",
    "RAL 6015": "#3D403A",
    "RAL 6016": "#1E5945",
    "RAL 6017": "#4C6B3F",
    "RAL 6018": "#6B7E4F",
    "RAL 6019": "#9CAF88",
    "RAL 6020": "#354733",
    "RAL 6021": "#86A47C",
    "RAL 6022": "#3E3B32",
    "RAL 6024": "#83AF95",
    "RAL 6025": "#5F9E6E",
    "RAL 6026": "#2D572C",
    "RAL 6027": "#7FB069",
    "RAL 6028": "#2F4538",
    "RAL 6029": "#3D403A",
    "RAL 6032": "#008F39",
    "RAL 6033": "#00B04F",
    "RAL 6034": "#00A550",
    "RAL 6035": "#00A550",
    "RAL 6036": "#1F3A3D",
    "RAL 6037": "#00A550",
    "RAL 6038": "#00A550",
    "RAL 7000": "#78858B",
    "RAL 7001": "#8A9597",
    "RAL 7002": "#8C9291",
    "RAL 7003": "#817863",
    "RAL 7004": "#7A7B7A",
    "RAL 7005": "#6B6F70",
    "RAL 7006": "#6F7271",
    "RAL 7008": "#6B6F70",
    "RAL 7009": "#636B6F",
    "RAL 7010": "#4E5459",
    "RAL 7011": "#4C4E51",
    "RAL 7012": "#4E5459",
    "RAL 7013": "#827B77",
    "RAL 7015": "#6B6F70",
    "RAL 7016": "#5F6061",
    "RAL 7021": "#4C4E51",
    "RAL 7022": "#464B4E",
    "RAL 7023": "#3E3F41",
    "RAL 7024": "#6B6F70",
    "RAL 7026": "#4C4E51",
    "RAL 7030": "#939388",
    "RAL 7031": "#5F6061",
    "RAL 7032": "#7A7B7A",
    "RAL 7033": "#6B6F70",
    "RAL 7034": "#939388",
    "RAL 7035": "#C0C0C0",
    "RAL 7036": "#5F6061",
    "RAL 7037": "#C0C0C0",
    "RAL 7038": "#C0C0C0",
    "RAL 7039": "#A9A9A9",
    "RAL 7040": "#9CA0A3",
    "RAL 7042": "#8A9597",
    "RAL 7043": "#B4B4B4",
    "RAL 7044": "#9CA0A3",
    "RAL 7045": "#6B6F70",
    "RAL 7046": "#9CA0A3",
    "RAL 7047": "#C0C0C0",
    "RAL 7048": "#9CA0A3",
    "RAL 8000": "#8C6E46",
    "RAL 8001": "#A0662B",
    "RAL 8002": "#8C6E46",
    "RAL 8003": "#7A5A3A",
    "RAL 8004": "#6B4E2B",
    "RAL 8007": "#6B4E2B",
    "RAL 8008": "#6B4E2B",
    "RAL 8011": "#5C4032",
    "RAL 8012": "#6B4E2B",
    "RAL 8014": "#4A3728",
    "RAL 8015": "#5C4032",
    "RAL 8016": "#4A3728",
    "RAL 8017": "#4A3728",
    "RAL 8019": "#4A3728",
    "RAL 8022": "#1C1C1C",
    "RAL 8023": "#A5A5A5",
    "RAL 8024": "#6B6F70",
    "RAL 8025": "#464B4E",
    "RAL 8028": "#3E3F41",
    "RAL 8029": "#1C1C1C",
    "RAL 9001": "#F4F4F4",
    "RAL 9002": "#E8E8E8",
    "RAL 9003": "#FFFFFF",
    "RAL 9004": "#1C1C1C",
    "RAL 9005": "#0A0A0A",
    "RAL 9006": "#A5A5A5",
    "RAL 9007": "#8A8A8A",
    "RAL 9010": "#FFFFFF",
    "RAL 9011": "#1C1C1C",
    "RAL 9012": "#F4F4F4",
    "RAL 9016": "#F4F4F4",
    "RAL 9017": "#1C1C1C",
    "RAL 9018": "#F4F4F4",
    "RAL 9022": "#9CA0A3",
    "RAL 9023": "#B4B4B4"
}

def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Конвертирует HEX цвет в RGB."""
    hex_color = hex_color.lstrip('#').upper()
    if len(hex_color) != 6:
        raise ValueError(f"Неверный формат HEX цвета: {hex_color}")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def color_distance(color1: Tuple[int, int, int], color2: Tuple[int, int, int]) -> float:
    """
    Вычисляет цветовое расстояние между двумя RGB цветами
    используя формулу Delta E (упрощенная версия).
    """
    r1, g1, b1 = color1
    r2, g2, b2 = color2
    
    # Используем формулу цветовой разницы (Euclidean distance в RGB пространстве)
    # Можно также использовать более точную формулу Delta E, но для простоты используем Euclidean
    return math.sqrt((r1 - r2)**2 + (g1 - g2)**2 + (b1 - b2)**2)

def find_closest_ral(hex_color: str, ral_dict: Dict[str, str] = None) -> Tuple[str, str]:
    """
    Находит ближайший RAL цвет для заданного HEX цвета.
    
    Args:
        hex_color: HEX код цвета (например, "#FF5733")
        ral_dict: Словарь RAL цветов (по умолчанию используется RAL_COLORS_EXTENDED)
    
    Returns:
        Tuple с названием RAL и HEX кодом ближайшего цвета
    """
    if ral_dict is None:
        ral_dict = RAL_COLORS_EXTENDED  # Используем расширенный словарь для лучшей точности
    
    try:
        target_rgb = hex_to_rgb(hex_color)
    except ValueError as e:
        st.error(f"Ошибка обработки цвета {hex_color}: {e}")
        return "RAL 9003", "#FFFFFF"  # Возвращаем белый по умолчанию
    
    min_distance = float('inf')
    closest_ral = None
    closest_hex = None
    
    for ral_name, ral_hex in ral_dict.items():
        try:
            ral_rgb = hex_to_rgb(ral_hex)
            distance = color_distance(target_rgb, ral_rgb)
            
            if distance < min_distance:
                min_distance = distance
                closest_ral = ral_name
                closest_hex = ral_hex
        except ValueError:
            continue  # Пропускаем невалидные цвета в словаре
    
    if closest_ral is None:
        return "RAL 9003", "#FFFFFF"  # Возвращаем белый по умолчанию
    
    return closest_ral, closest_hex

def analyze_colors_with_gemini(image: Image.Image, api_key: str) -> List[str]:
    """
    Анализирует изображение с помощью Gemini API и извлекает 5 доминирующих цветов.
    
    Args:
        image: PIL Image объект
        api_key: API ключ для Google Gemini
    
    Returns:
        Список из 5 HEX кодов цветов
    """
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = """Проанализируй это изображение интерьера и найди 5 доминирующих цветов.
        Верни результат ТОЛЬКО в формате JSON массива, без дополнительного текста:
        ["#HEX1", "#HEX2", "#HEX3", "#HEX4", "#HEX5"]
        
        Пример ответа:
        ["#8B7355", "#D4C5B9", "#3A3A3A", "#E8DCC6", "#5A5A5A"]
        
        Важно: верни только JSON массив, никакого другого текста."""
        
        response = model.generate_content([prompt, image])
        response_text = response.text.strip()
        
        # Очистка ответа от markdown форматирования, если есть
        if response_text.startswith("```json"):
            response_text = response_text.replace("```json", "").replace("```", "").strip()
        elif response_text.startswith("```"):
            response_text = response_text.replace("```", "").strip()
        
        colors = json.loads(response_text)
        
        if isinstance(colors, list):
            # Проверяем, что все элементы - валидные HEX коды
            valid_colors = []
            for color in colors:
                if isinstance(color, str) and color.startswith('#') and len(color) == 7:
                    try:
                        # Проверяем, что это валидный HEX
                        int(color[1:], 16)
                        valid_colors.append(color.upper())
                    except ValueError:
                        continue
            
            if len(valid_colors) >= 5:
                return valid_colors[:5]
            elif len(valid_colors) > 0:
                st.warning(f"Найдено только {len(valid_colors)} валидных цветов. Используем их.")
                return valid_colors
            else:
                st.error("API вернул невалидные HEX коды. Попробуйте еще раз.")
                return []
        else:
            st.error("API вернул неверный формат. Ожидался массив цветов.")
            return []
            
    except json.JSONDecodeError as e:
        st.error(f"Ошибка парсинга JSON: {e}")
        if 'response_text' in locals():
            st.info(f"Ответ API: {response_text[:200]}")
        return []
    except Exception as e:
        error_msg = str(e)
        if "API_KEY" in error_msg or "api_key" in error_msg.lower():
            st.error("Неверный API ключ. Проверьте правильность ключа.")
        elif "quota" in error_msg.lower() or "limit" in error_msg.lower():
            st.error("Превышен лимит запросов к API. Попробуйте позже.")
        else:
            st.error(f"Ошибка при анализе изображения: {error_msg}")
        return []

def generate_moodboard(colors_data: List[Dict[str, str]]) -> Image.Image:
    """
    Генерирует изображение moodboard с цветовыми плашками.
    
    Args:
        colors_data: Список словарей с ключами 'hex', 'ral_name', 'ral_hex'
    
    Returns:
        PIL Image объект
    """
    if not colors_data:
        raise ValueError("Список цветов пуст")
    
    # Параметры изображения
    square_size = 200
    padding = 40
    text_height = 100
    image_width = len(colors_data) * (square_size + padding) + padding
    image_height = square_size + text_height + padding * 2
    
    # Создание изображения
    img = Image.new('RGB', (image_width, image_height), color='white')
    draw = ImageDraw.Draw(img)
    
    # Попытка загрузить шрифт, если не получится - используем стандартный
    font_large = None
    font_small = None
    
    # Список возможных путей к шрифтам
    font_paths = [
        "arial.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibri.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux
        "/System/Library/Fonts/Helvetica.ttc"  # macOS
    ]
    
    for font_path in font_paths:
        try:
            font_large = ImageFont.truetype(font_path, 20)
            font_small = ImageFont.truetype(font_path, 16)
            break
        except:
            continue
    
    if font_large is None:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    x_offset = padding
    
    for color_info in colors_data:
        try:
            hex_color = color_info['hex']
            ral_name = color_info['ral_name']
            ral_hex = color_info['ral_hex']
            
            # Рисуем квадрат с цветом
            square_coords = [
                x_offset,
                padding,
                x_offset + square_size,
                padding + square_size
            ]
            rgb_color = hex_to_rgb(hex_color)
            draw.rectangle(square_coords, fill=rgb_color, outline='#333333', width=2)
            
            # Текст под квадратом
            text_y = padding + square_size + 10
            
            # RAL название
            try:
                text_bbox = draw.textbbox((0, 0), ral_name, font=font_large)
                text_width = text_bbox[2] - text_bbox[0]
                text_x = x_offset + (square_size - text_width) // 2
                draw.text((text_x, text_y), ral_name, fill='#333333', font=font_large)
            except:
                # Если не получилось с шрифтом, используем простой текст
                draw.text((x_offset + 10, text_y), ral_name, fill='#333333')
            
            # HEX код
            hex_text = f"HEX: {hex_color}"
            try:
                text_bbox = draw.textbbox((0, 0), hex_text, font=font_small)
                text_width = text_bbox[2] - text_bbox[0]
                text_x = x_offset + (square_size - text_width) // 2
                draw.text((text_x, text_y + 30), hex_text, fill='#666666', font=font_small)
            except:
                draw.text((x_offset + 10, text_y + 30), hex_text, fill='#666666')
            
            # RAL HEX код
            ral_hex_text = f"RAL: {ral_hex}"
            try:
                text_bbox = draw.textbbox((0, 0), ral_hex_text, font=font_small)
                text_width = text_bbox[2] - text_bbox[0]
                text_x = x_offset + (square_size - text_width) // 2
                draw.text((text_x, text_y + 50), ral_hex_text, fill='#666666', font=font_small)
            except:
                draw.text((x_offset + 10, text_y + 50), ral_hex_text, fill='#666666')
            
            x_offset += square_size + padding
        except Exception as e:
            # Пропускаем проблемные цвета, но продолжаем обработку
            continue
    
    return img

def main():
    st.title("🎨 Color Matcher")
    st.markdown("### Приложение для анализа цветов интерьера и поиска ближайших RAL цветов")
    
    # Боковая панель для настроек
    with st.sidebar:
        st.header("⚙️ Настройки")
        api_key = st.text_input(
            "Google Gemini API Key",
            type="password",
            help="Введите ваш API ключ от Google Gemini"
        )
        
        if not api_key:
            st.warning("⚠️ Пожалуйста, введите API ключ для продолжения")
            st.info("Получить API ключ можно на: https://makersuite.google.com/app/apikey")
            return
    
    # Загрузка изображения
    uploaded_file = st.file_uploader(
        "Загрузите фото интерьера",
        type=['png', 'jpg', 'jpeg'],
        help="Поддерживаются форматы: PNG, JPG, JPEG"
    )
    
    if uploaded_file is not None:
        try:
            # Отображение загруженного изображения
            image = Image.open(uploaded_file)
            
            # Конвертация в RGB, если необходимо
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            st.image(image, caption="Загруженное изображение", use_container_width=True)
            
            # Кнопка анализа
            if st.button("🔍 Анализировать цвета", type="primary"):
                if not api_key or api_key.strip() == "":
                    st.error("⚠️ Пожалуйста, введите API ключ в боковой панели")
                else:
                    with st.spinner("Анализирую изображение с помощью Gemini AI... Это может занять несколько секунд."):
                        hex_colors = analyze_colors_with_gemini(image, api_key)
                        
                        if hex_colors:
                            st.success("✅ Анализ завершен!")
                            
                            # Поиск ближайших RAL цветов
                            colors_data = []
                            for hex_color in hex_colors:
                                ral_name, ral_hex = find_closest_ral(hex_color)
                                colors_data.append({
                                    'hex': hex_color,
                                    'ral_name': ral_name,
                                    'ral_hex': ral_hex
                                })
                            
                            # Сохранение в session state
                            st.session_state['colors_data'] = colors_data
                            st.session_state['hex_colors'] = hex_colors
                            
                            # Перезагрузка страницы для отображения результатов
                            st.rerun()
                        else:
                            st.warning("Не удалось извлечь цвета. Попробуйте загрузить другое изображение.")
        
        except Exception as e:
            st.error(f"Ошибка при загрузке изображения: {e}")
            st.info("Убедитесь, что файл является валидным изображением (PNG, JPG, JPEG)")
    
    # Отображение результатов
    if 'colors_data' in st.session_state and st.session_state['colors_data']:
        st.divider()
        st.header("🎨 Найденные цвета")
        
        colors_data = st.session_state['colors_data']
        
        # Создание колонок для цветовых плашек
        cols = st.columns(5)
        
        for idx, color_info in enumerate(colors_data):
            with cols[idx]:
                hex_color = color_info['hex']
                ral_name = color_info['ral_name']
                ral_hex = color_info['ral_hex']
                
                # Цветовая плашка
                st.markdown(
                    f'<div style="width: 100%; height: 150px; background-color: {hex_color}; '
                    f'border-radius: 10px; border: 2px solid #ddd; margin-bottom: 10px;"></div>',
                    unsafe_allow_html=True
                )
                
                # Информация о цвете
                st.markdown(f"**{ral_name}**")
                
                # HEX код с возможностью копирования
                st.code(hex_color, language=None)
                
                # RAL HEX код
                st.caption(f"RAL: {ral_hex}")
        
        # Генерация и скачивание moodboard
        st.divider()
        st.header("📥 Экспорт палитры")
        
        if st.button("🎨 Сгенерировать и скачать Moodboard", type="primary"):
            with st.spinner("Генерирую moodboard..."):
                try:
                    moodboard_img = generate_moodboard(colors_data)
                    
                    # Конвертация в байты для скачивания
                    img_buffer = io.BytesIO()
                    moodboard_img.save(img_buffer, format='PNG')
                    img_buffer.seek(0)
                    
                    st.success("✅ Moodboard готов!")
                    st.image(moodboard_img, caption="Ваша палитра", use_container_width=True)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.download_button(
                            label="📥 Скачать палитру (PNG)",
                            data=img_buffer.getvalue(),
                            file_name="color_palette.png",
                            mime="image/png",
                            use_container_width=True
                        )
                    with col2:
                        # Также сохраняем в JPG
                        img_buffer_jpg = io.BytesIO()
                        moodboard_img.save(img_buffer_jpg, format='JPEG', quality=95)
                        img_buffer_jpg.seek(0)
                        st.download_button(
                            label="📥 Скачать палитру (JPG)",
                            data=img_buffer_jpg.getvalue(),
                            file_name="color_palette.jpg",
                            mime="image/jpeg",
                            use_container_width=True
                        )
                    
                except Exception as e:
                    st.error(f"Ошибка при генерации moodboard: {e}")

if __name__ == "__main__":
    main()

