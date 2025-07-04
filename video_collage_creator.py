import os
try:
    import cv2
except ImportError:
    print("Ошибка: Не удалось импортировать cv2. Установите: pip install opencv-python")
    exit(1)
try:
    import numpy as np
except ImportError:
    print("Ошибка: Не удалось импортировать numpy. Установите: pip install numpy")
    exit(1)
try:
    from PIL import Image
except ImportError:
    print("Ошибка: Не удалось импортировать PIL. Установите: pip install Pillow")
    exit(1)
import math

def get_video_duration(video_path):
    """Получает длительность видео в секундах"""
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count / fps
    cap.release()
    return duration

def extract_screenshots(video_path, num_screenshots=9):
    """Извлекает указанное количество скриншотов из видео"""
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print(f"Ошибка: Не удалось открыть видео {video_path}")
        return []
    
    # Получаем информацию о видео
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    # Вычисляем кадры для извлечения скриншотов
    frame_indices = []
    for i in range(num_screenshots):
        frame_index = int((i + 0.5) * total_frames / num_screenshots)
        frame_indices.append(frame_index)
    
    screenshots = []
    
    for frame_index in frame_indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        ret, frame = cap.read()
        
        if ret:
            # Конвертируем BGR в RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            screenshots.append(frame_rgb)
        else:
            print(f"Ошибка при чтении кадра {frame_index}")
    
    cap.release()
    return screenshots

def create_collage(screenshots, output_path):
    """Создает коллаж из скриншотов 3x3"""
    if len(screenshots) != 9:
        print(f"Ошибка: ожидается 9 скриншотов, получено {len(screenshots)}")
        return False
    
    # Определяем размеры для каждого скриншота
    # Используем размер первого скриншота как базовый
    base_height, base_width = screenshots[0].shape[:2]
    
    # Вычисляем размер для каждого скриншота в коллаже
    # Делаем их квадратными для равномерности
    target_size = min(base_width, base_height)
    
    # Создаем пустой коллаж
    collage_width = target_size * 3
    collage_height = target_size * 3
    collage = np.zeros((collage_height, collage_width, 3), dtype=np.uint8)
    
    # Размещаем скриншоты в коллаже
    for i, screenshot in enumerate(screenshots):
        row = i // 3
        col = i % 3
        
        # Изменяем размер скриншота
        resized = cv2.resize(screenshot, (target_size, target_size))
        
        # Вычисляем позицию в коллаже
        y_start = row * target_size
        y_end = (row + 1) * target_size
        x_start = col * target_size
        x_end = (col + 1) * target_size
        
        # Вставляем скриншот в коллаж
        collage[y_start:y_end, x_start:x_end] = resized
    
    # Сохраняем коллаж
    collage_pil = Image.fromarray(collage)
    collage_pil.save(output_path, 'JPEG', quality=95)
    
    return True

def process_videos():
    """Обрабатывает все видео файлы в папке Video"""
    video_folder = "Video"
    output_folder = "colage"
    
    # Создаем папку для коллажей, если её нет
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Получаем список видео файлов
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv']
    video_files = []
    
    for file in os.listdir(video_folder):
        if any(file.lower().endswith(ext) for ext in video_extensions):
            video_files.append(file)
    
    if not video_files:
        print("Видео файлы не найдены в папке Video")
        return
    
    print(f"Найдено {len(video_files)} видео файлов")
    
    for video_file in video_files:
        video_path = os.path.join(video_folder, video_file)
        print(f"\nОбрабатываю: {video_file}")
        
        try:
            # Получаем длительность видео
            duration = get_video_duration(video_path)
            print(f"Длительность: {duration:.2f} секунд")
            
            # Извлекаем скриншоты
            screenshots = extract_screenshots(video_path, 9)
            
            if len(screenshots) == 9:
                # Создаем имя выходного файла
                base_name = os.path.splitext(video_file)[0]
                output_path = os.path.join(output_folder, f"{base_name}.jpg")
                
                # Создаем коллаж
                if create_collage(screenshots, output_path):
                    print(f"Коллаж сохранен: {output_path}")
                else:
                    print(f"Ошибка при создании коллажа для {video_file}")
            else:
                print(f"Не удалось извлечь 9 скриншотов из {video_file}")
                
        except Exception as e:
            print(f"Ошибка при обработке {video_file}: {str(e)}")

if __name__ == "__main__":
    print("Программа для создания коллажей из видео")
    print("=" * 50)
    process_videos()
    print("\nОбработка завершена!") 