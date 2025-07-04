import os
import sys
import threading
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
    try:
        from PIL.Image import Resampling
        RESAMPLE = Resampling.LANCZOS
    except ImportError:
        RESAMPLE = 1  # LANCZOS/ANTIALIAS для старых Pillow
except ImportError:
    print("Ошибка: Не удалось импортировать PIL. Установите: pip install Pillow")
    exit(1)
try:
    import tkinter as tk
    from tkinter import ttk, messagebox, filedialog
except ImportError:
    print("Ошибка: tkinter не найден. Установите Python с tkinter.")
    exit(1)

class VideoCollageGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Создание коллажей из видео")
        self.root.geometry("600x540")
        self.root.resizable(True, True)
        
        # Переменные
        self.video_folder = tk.StringVar(value="Video")
        self.output_folder = tk.StringVar(value="colage")
        self.processing = False
        self.video_files = []
        self.aspect_var = tk.StringVar(value="16:9")  # Новая переменная для формата
        
        self.setup_ui()
        self.check_folders()
        
    def setup_ui(self):
        # Главный фрейм
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Настройка весов для растягивания
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Заголовок
        title_label = ttk.Label(main_frame, text="Создание коллажей из видео", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Формат коллажа
        ttk.Label(main_frame, text="Формат коллажа:").grid(row=1, column=0, sticky="w", pady=5)
        aspect_frame = ttk.Frame(main_frame)
        aspect_frame.grid(row=1, column=1, sticky="w", pady=5)
        ttk.Radiobutton(aspect_frame, text="16:9 (горизонтальный)", variable=self.aspect_var, value="16:9").pack(side=tk.LEFT)
        ttk.Radiobutton(aspect_frame, text="9:16 (вертикальный)", variable=self.aspect_var, value="9:16").pack(side=tk.LEFT)
        
        # Папка с видео
        ttk.Label(main_frame, text="Папка с видео:").grid(row=2, column=0, sticky="w", pady=5)
        video_entry = ttk.Entry(main_frame, textvariable=self.video_folder, width=40)
        video_entry.grid(row=2, column=1, sticky="ew", padx=(10, 5), pady=5)
        ttk.Button(main_frame, text="Обзор", command=self.browse_video_folder).grid(row=2, column=2, pady=5)
        
        # Папка для коллажей
        ttk.Label(main_frame, text="Папка для коллажей:").grid(row=3, column=0, sticky="w", pady=5)
        output_entry = ttk.Entry(main_frame, textvariable=self.output_folder, width=40)
        output_entry.grid(row=3, column=1, sticky="ew", padx=(10, 5), pady=5)
        ttk.Button(main_frame, text="Обзор", command=self.browse_output_folder).grid(row=3, column=2, pady=5)
        
        # Кнопки управления
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=3, pady=20)
        
        self.refresh_btn = ttk.Button(button_frame, text="Обновить список", command=self.refresh_videos)
        self.refresh_btn.pack(side=tk.LEFT, padx=5)
        
        self.process_btn = ttk.Button(button_frame, text="Создать коллажи", command=self.start_processing)
        self.process_btn.pack(side=tk.LEFT, padx=5)
        
        # Список видео файлов
        ttk.Label(main_frame, text="Найденные видео файлы:").grid(row=5, column=0, sticky="w", pady=(20, 5))
        
        # Создаем Treeview для списка файлов
        columns = ("Имя файла", "Размер", "Длительность")
        self.video_tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=8)
        
        # Настройка колонок
        self.video_tree.heading("Имя файла", text="Имя файла")
        self.video_tree.heading("Размер", text="Размер")
        self.video_tree.heading("Длительность", text="Длительность")
        
        self.video_tree.column("Имя файла", width=200)
        self.video_tree.column("Размер", width=100)
        self.video_tree.column("Длительность", width=100)
        
        self.video_tree.grid(row=6, column=0, columnspan=3, sticky="nsew", pady=5)
        
        # Скроллбар для списка
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.video_tree.yview)
        scrollbar.grid(row=6, column=3, sticky="ns")
        self.video_tree.configure(yscrollcommand=scrollbar.set)
        
        # Прогресс бар
        ttk.Label(main_frame, text="Прогресс:").grid(row=7, column=0, sticky="w", pady=(20, 5))
        self.progress = ttk.Progressbar(main_frame, mode='determinate')
        self.progress.grid(row=8, column=0, columnspan=3, sticky="ew", pady=5)
        
        # Статус
        self.status_var = tk.StringVar(value="Готов к работе")
        status_label = ttk.Label(main_frame, textvariable=self.status_var, font=("Arial", 10))
        status_label.grid(row=9, column=0, columnspan=3, pady=10)
        
        # Лог
        ttk.Label(main_frame, text="Лог операций:").grid(row=10, column=0, sticky="w", pady=(20, 5))
        self.log_text = tk.Text(main_frame, height=6, width=70)
        self.log_text.grid(row=11, column=0, columnspan=3, sticky="nsew", pady=5)
        
        # Скроллбар для лога
        log_scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        log_scrollbar.grid(row=11, column=3, sticky="ns")
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        # Настройка весов для растягивания
        main_frame.rowconfigure(6, weight=1)
        main_frame.rowconfigure(11, weight=1)
        
    def log_message(self, message):
        """Добавляет сообщение в лог"""
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def browse_video_folder(self):
        """Выбор папки с видео"""
        folder = filedialog.askdirectory(title="Выберите папку с видео")
        if folder:
            self.video_folder.set(folder)
            self.refresh_videos()
            
    def browse_output_folder(self):
        """Выбор папки для коллажей"""
        folder = filedialog.askdirectory(title="Выберите папку для коллажей")
        if folder:
            self.output_folder.set(folder)
            
    def check_folders(self):
        """Проверяет наличие папок и создает их при необходимости"""
        # Проверяем папку с видео
        video_path = self.video_folder.get()
        if not os.path.exists(video_path):
            try:
                os.makedirs(video_path)
                self.log_message(f"Создана папка: {video_path}")
            except Exception as e:
                self.log_message(f"Ошибка создания папки {video_path}: {e}")
                
        # Проверяем папку для коллажей
        output_path = self.output_folder.get()
        if not os.path.exists(output_path):
            try:
                os.makedirs(output_path)
                self.log_message(f"Создана папка: {output_path}")
            except Exception as e:
                self.log_message(f"Ошибка создания папки {output_path}: {e}")
                
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
            
    def refresh_videos(self):
        """Обновляет список видео файлов"""
        self.video_tree.delete(*self.video_tree.get_children())
        self.video_files = []
        
        video_path = self.video_folder.get()
        if not os.path.exists(video_path):
            self.log_message(f"Папка {video_path} не существует")
            return
            
        video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv']
        
        for file in os.listdir(video_path):
            if any(file.lower().endswith(ext) for ext in video_extensions):
                file_path = os.path.join(video_path, file)
                size = self.get_file_size(file_path)
                duration = self.get_video_duration(file_path)
                duration_str = f"{duration:.1f}s" if duration > 0 else "Ошибка"
                
                self.video_tree.insert("", tk.END, values=(file, size, duration_str))
                self.video_files.append(file)
                
        self.log_message(f"Найдено {len(self.video_files)} видео файлов")
        self.status_var.set(f"Найдено {len(self.video_files)} видео файлов")
        
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
        """Создает коллаж из скриншотов 3x3 с нужным соотношением сторон"""
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
        
        # --- Новый код: вписываем в холст с нужным соотношением сторон ---
        aspect = self.aspect_var.get()
        if aspect == '16:9':
            target_w, target_h = 1920, 1080
        else:
            target_w, target_h = 1080, 1920
        collage_pil = Image.fromarray(collage)
        collage_pil.thumbnail((target_w, target_h), RESAMPLE)
        result = Image.new('RGB', (target_w, target_h), (0, 0, 0))
        x = (target_w - collage_pil.width) // 2
        y = (target_h - collage_pil.height) // 2
        result.paste(collage_pil, (x, y))
        result.save(output_path, 'JPEG', quality=95)
        return True
        
    def process_videos_thread(self):
        """Поток для обработки видео"""
        try:
            video_path = self.video_folder.get()
            output_path = self.output_folder.get()
            
            if not self.video_files:
                self.log_message("Нет видео файлов для обработки")
                return
                
            total_files = len(self.video_files)
            self.progress["maximum"] = total_files
            
            for i, video_file in enumerate(self.video_files):
                if not self.processing:  # Проверка на остановку
                    break
                    
                self.status_var.set(f"Обработка: {video_file}")
                self.log_message(f"Обрабатываю: {video_file}")
                
                try:
                    video_full_path = os.path.join(video_path, video_file)
                    screenshots = self.extract_screenshots(video_full_path, 9)
                    
                    if len(screenshots) == 9:
                        base_name = os.path.splitext(video_file)[0]
                        output_file = os.path.join(output_path, f"{base_name}.jpg")
                        
                        if self.create_collage(screenshots, output_file):
                            self.log_message(f"✅ Коллаж сохранен: {base_name}.jpg")
                        else:
                            self.log_message(f"❌ Ошибка создания коллажа для {video_file}")
                    else:
                        self.log_message(f"❌ Не удалось извлечь 9 скриншотов из {video_file}")
                        
                except Exception as e:
                    self.log_message(f"❌ Ошибка при обработке {video_file}: {str(e)}")
                
                self.progress["value"] = i + 1
                self.root.update_idletasks()
                
            self.status_var.set("Обработка завершена")
            self.log_message("🎉 Обработка всех видео завершена!")
            
        except Exception as e:
            self.log_message(f"❌ Критическая ошибка: {str(e)}")
        finally:
            self.processing = False
            self.process_btn.config(text="Создать коллажи")
            self.refresh_btn.config(state="normal")
            
    def start_processing(self):
        """Запускает обработку видео"""
        if self.processing:
            return
            
        if not self.video_files:
            messagebox.showwarning("Предупреждение", "Нет видео файлов для обработки!")
            return
            
        self.processing = True
        self.process_btn.config(text="Остановить")
        self.refresh_btn.config(state="disabled")
        self.progress["value"] = 0
        
        # Запускаем обработку в отдельном потоке
        thread = threading.Thread(target=self.process_videos_thread)
        thread.daemon = True
        thread.start()

def main():
    root = tk.Tk()
    app = VideoCollageGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 