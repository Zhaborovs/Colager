#!/usr/bin/env python3
"""
Тестовый скрипт для проверки работоспособности программы создания коллажей
"""

import os
import sys
from video_collage_creator import get_video_duration, extract_screenshots, create_collage

def test_video_processing():
    """Тестирует обработку видео файлов"""
    print("Тестирование программы создания коллажей...")
    print("=" * 50)
    
    # Проверяем наличие папки Video
    if not os.path.exists("Video"):
        print("❌ Папка Video не найдена")
        return False
    
    # Получаем список видео файлов
    video_files = [f for f in os.listdir("Video") if f.lower().endswith('.mp4')]
    
    if not video_files:
        print("❌ Видео файлы не найдены в папке Video")
        return False
    
    print(f"✅ Найдено {len(video_files)} видео файлов")
    
    # Тестируем каждый видео файл
    for video_file in video_files:
        video_path = os.path.join("Video", video_file)
        print(f"\n📹 Тестирую: {video_file}")
        
        try:
            # Тест 1: Получение длительности
            duration = get_video_duration(video_path)
            print(f"   ✅ Длительность: {duration:.2f} секунд")
            
            # Тест 2: Извлечение скриншотов
            screenshots = extract_screenshots(video_path, 9)
            if len(screenshots) == 9:
                print(f"   ✅ Извлечено {len(screenshots)} скриншотов")
                
                # Тест 3: Создание коллажа
                test_output = f"test_{video_file.replace('.mp4', '.jpg')}"
                if create_collage(screenshots, test_output):
                    print(f"   ✅ Коллаж создан: {test_output}")
                    # Удаляем тестовый файл
                    os.remove(test_output)
                else:
                    print(f"   ❌ Ошибка создания коллажа")
                    return False
            else:
                print(f"   ❌ Не удалось извлечь 9 скриншотов (получено {len(screenshots)})")
                return False
                
        except Exception as e:
            print(f"   ❌ Ошибка при обработке: {str(e)}")
            return False
    
    print("\n🎉 Все тесты пройдены успешно!")
    return True

if __name__ == "__main__":
    success = test_video_processing()
    sys.exit(0 if success else 1) 