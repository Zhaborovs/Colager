import os
import sys
import time
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

class VideoCollageProcessor:
    def __init__(self, video_folder="Video", output_folder="colage"):
        self.video_folder = video_folder
        self.output_folder = output_folder
        self.video_files = []
        
    def check_and_create_folders(self):
        """Проверяет наличие папок и создает их при необходимости"""
        print("🔍 Проверка папок...")
        
        # Проверяем папку с видео
        if not os.path.exists(self.video_folder):
            try:
                os.makedirs(self.video_folder)
                print(f"✅ Создана папка: {self.video_folder}")
            except Exception as e:
                print(f"❌ Ошибка создания папки {self.video_folder}: {e}")
                return False
        else:
            print(f"✅ Папка {self.video_folder} существует")
            
        # Проверяем папку для коллажей
        if not os.path.exists(self.output_folder):
            try:
                os.makedirs(self.output_folder)
                print(f"✅ Создана папка: {self.output_folder}")
            except Exception as e:
                print(f"❌ Ошибка создания папки {self.output_folder}: {e}")
                return False
        else:
            print(f"✅ Папка {self.output_folder} существует")
            
        return True
        
    def scan_video_files(self):
        """Сканирует папку на наличие видео файлов"""
        print(f"\n🔍 Поиск видео файлов в папке {self.video_folder}...")
        
        if not os.path.exists(self.video_folder):
            print(f"❌ Папка {self.video_folder} не существует")
            return False
            
        video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv']
        self.video_files = []
        
        for file in os.listdir(self.video_folder):
            if any(file.lower().endswith(ext) for ext in video_extensions):
                self.video_files.append(file)
                
        if not self.video_files:
            print("❌ Видео файлы не найдены!")
            print(f"   Поместите видео файлы в папку: {self.video_folder}")
            print(f"   Поддерживаемые форматы: {', '.join(video_extensions)}")
            return False
            
        print(f"✅ Найдено {len(self.video_files)} видео файлов:")
        for i, file in enumerate(self.video_files, 1):
            file_path = os.path.join(self.video_folder, file)
            size = self.get_file_size(file_path)
            duration = self.get_video_duration(file_path)
            duration_str = f"{duration:.1f}s" if duration > 0 else "Ошибка"
            print(f"   {i}. {file} ({size}, {duration_str})")
            
        return True
        
    def get_file_size(self, file_path):
        """Получает размер файла в читаемом формате"""
        size = os.path.getsize(file_path)
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
        
    def get_video_duration(self, video_path):
        """Получает длительность видео в секундах"""
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                return 0
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = frame_count / fps
            cap.release()
            return duration
        except Exception:
            return 0
            
    def extract_screenshots(self, video_path, num_screenshots=9):
        """Извлекает указанное количество скриншотов из видео"""
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            return []
        
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        frame_indices = []
        for i in range(num_screenshots):
            frame_index = int((i + 0.5) * total_frames / num_screenshots)
            frame_indices.append(frame_index)
        
        screenshots = []
        
        for frame_index in frame_indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
            ret, frame = cap.read()
            
            if ret:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                screenshots.append(frame_rgb)
        
        cap.release()
        return screenshots
        
    def create_collage(self, screenshots, output_path):
        """Создает коллаж из скриншотов 3x3"""
        if len(screenshots) != 9:
            return False
        
        base_height, base_width = screenshots[0].shape[:2]
        target_size = min(base_width, base_height)
        
        collage_width = target_size * 3
        collage_height = target_size * 3
        collage = np.zeros((collage_height, collage_width, 3), dtype=np.uint8)
        
        for i, screenshot in enumerate(screenshots):
            row = i // 3
            col = i % 3
            
            resized = cv2.resize(screenshot, (target_size, target_size))
            
            y_start = row * target_size
            y_end = (row + 1) * target_size
            x_start = col * target_size
            x_end = (col + 1) * target_size
            
            collage[y_start:y_end, x_start:x_end] = resized
        
        collage_pil = Image.fromarray(collage)
        collage_pil.save(output_path, 'JPEG', quality=95)
        
        return True
        
    def process_videos(self):
        """Обрабатывает все видео файлы"""
        print(f"\n🎬 Начинаю обработку {len(self.video_files)} видео файлов...")
        print("=" * 60)
        
        successful = 0
        failed = 0
        
        for i, video_file in enumerate(self.video_files, 1):
            print(f"\n📹 [{i}/{len(self.video_files)}] Обрабатываю: {video_file}")
            
            try:
                video_path = os.path.join(self.video_folder, video_file)
                screenshots = self.extract_screenshots(video_path, 9)
                
                if len(screenshots) == 9:
                    base_name = os.path.splitext(video_file)[0]
                    output_path = os.path.join(self.output_folder, f"{base_name}.jpg")
                    
                    if self.create_collage(screenshots, output_path):
                        output_size = self.get_file_size(output_path)
                        print(f"   ✅ Коллаж сохранен: {base_name}.jpg ({output_size})")
                        successful += 1
                    else:
                        print(f"   ❌ Ошибка создания коллажа для {video_file}")
                        failed += 1
                else:
                    print(f"   ❌ Не удалось извлечь 9 скриншотов из {video_file} (получено {len(screenshots)})")
                    failed += 1
                    
            except Exception as e:
                print(f"   ❌ Ошибка при обработке {video_file}: {str(e)}")
                failed += 1
                
        print("\n" + "=" * 60)
        print(f"🎉 Обработка завершена!")
        print(f"   ✅ Успешно: {successful}")
        print(f"   ❌ Ошибок: {failed}")
        print(f"   📁 Коллажи сохранены в: {self.output_folder}")
        
        return successful, failed
        
    def run(self):
        """Основной метод запуска программы"""
        print("🎬 Программа для создания коллажей из видео")
        print("=" * 60)
        
        # Проверяем папки
        if not self.check_and_create_folders():
            return False
            
        # Сканируем видео файлы
        if not self.scan_video_files():
            return False
            
        # Обрабатываем видео
        successful, failed = self.process_videos()
        
        return successful > 0

def main():
    processor = VideoCollageProcessor()
    success = processor.run()
    
    if success:
        print("\n✅ Программа завершена успешно!")
    else:
        print("\n❌ Программа завершена с ошибками!")
        
    input("\nНажмите Enter для выхода...")

if __name__ == "__main__":
    main() 