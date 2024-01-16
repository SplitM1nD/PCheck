import tkinter as tk
from tkinter import ttk, messagebox
import platform
import psutil
from threading import Thread
from PIL import Image, ImageTk
import sys
import os
import speedtest
def resource_path(relative_path):
    """ Получить абсолютный путь к ресурсу, работает для разработки и для одного исполняемого файла """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

def get_cpu_info():
    cpu_freq = psutil.cpu_freq().current if psutil.cpu_freq() else 0
    cpu_cores = psutil.cpu_count(logical=False)
    return f"{cpu_freq} ГГц, {cpu_cores} ядер" if cpu_cores else "Неизвестно"

def get_system_info():
    return {
        "Операционная система": platform.system() + " " + platform.release(),
        "Оперативная память (ГБ)": round(psutil.virtual_memory().total / (1024**3), 2),
        "Процессор": get_cpu_info(),
        "Свободное место на диске (ГБ)": round(psutil.disk_usage('/').free / (1024**3), 2),
    }
def check_system_requirements(progress_update, test_result_text):
    system_info = get_system_info()
    errors = []
    
    if platform.system() != "Windows" or int(platform.release()) < 10:
        errors.append("Требуется Windows 10 или выше.")
    progress_update(25)

    if psutil.virtual_memory().total < 8 * 1024**3:
        errors.append("Недостаточно оперативной памяти (требуется более 8 ГБ).")
    progress_update(50)

    if psutil.cpu_freq() and psutil.cpu_freq().current < 2000:
        errors.append("Частота процессора ниже требуемой (требуется не менее 2 ГГц).")
    progress_update(75)

    if psutil.disk_usage('/').free < 20 * 1024**3:
        errors.append("Недостаточно свободного места на диске (требуется более 20 ГБ).")
    
    try:
        st = speedtest.Speedtest()
        st.download()
        system_info["Скорость загрузки (Мбит/с)"] = round(st.results.download / (1024**2), 2)
        if st.results.download < 30 * 10**6:  # 30 Мбит/с
            errors.append("Скорость интернета ниже требуемой (требуется более 30 Мбит/с).")
    except speedtest.ConfigRetrievalError:
        errors.append("Не удалось проверить скорость интернета.")
    
    progress_update(100)
    return errors, system_info

def set_background_image(path, bg_label):
    try:
        image = Image.open(path)
        image = image.resize((560, 380), Image.LANCZOS)
        bg_image = ImageTk.PhotoImage(image)
        bg_label.config(image=bg_image)
        bg_label.image = bg_image
    except Exception as e:
        print(f"Ошибка при загрузке изображения: {e}")

#Основная функция запуска теста

def run_test(progress_bar, test_result_text):
    def test():
        def update_progress(value):
            progress_bar['value'] = value
            progress_bar.update_idletasks()

        errors, system_info = check_system_requirements(update_progress, test_result_text)
        test_result_text.delete('1.0', tk.END)
        for key, value in system_info.items():
            test_result_text.insert(tk.END, f"{key}: {value}\n", 'info')
        if errors:
            test_result_text.insert(tk.END, "\nПК не соответствует критериям:\n", 'fail')
            for error in errors:
                test_result_text.insert(tk.END, f"- {error}\n", 'fail')
        else:
            test_result_text.insert(tk.END, "\nВсе системные требования выполнены.\n", 'pass')
        
        messagebox.showinfo("Тест завершен", "Тест системных требований завершен.")
        progress_bar.stop()

    messagebox.showinfo("Тест начат", "Пожалуйста, не выключайте компьютер и дождитесь завершения теста.")
    progress_bar.start(10)
    testing_thread = Thread(target=test)
    testing_thread.start()

app = tk.Tk()
app.title("Проверка системных требований")
app.geometry("560x380")

# Загрузка и установка иконки приложения
icon_path = resource_path("icon.ico")
icon_image = ImageTk.PhotoImage(Image.open(icon_path))
app.iconphoto(False, icon_image)

bg_label = tk.Label(app)
bg_label.place(x=0, y=0, relwidth=1, relheight=1)
image_path = resource_path("image_1.png")
set_background_image(image_path, bg_label)

progress_bar = ttk.Progressbar(app, orient=tk.HORIZONTAL, length=200, mode='indeterminate')
progress_bar.pack(pady=10)

test_result_text = tk.Text(app, font=("Helvetica", 8), height=8)
test_result_text.tag_configure('info', foreground='black')
test_result_text.tag_configure('pass', foreground='green')
test_result_text.tag_configure('fail', foreground='red')
test_result_text.pack(side=tk.BOTTOM, fill=tk.X, padx=8, pady=8)

run_test_button = tk.Button(app, text="Запустить тест", command=lambda: run_test(progress_bar, test_result_text))
run_test_button.pack(pady=10)

app.mainloop()
