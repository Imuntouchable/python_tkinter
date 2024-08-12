import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize_scalar
import tkinter as tk
from tkinter import ttk
from numpy.polynomial import Polynomial
from tkinter import messagebox
from tkinter import messagebox
import os
import validate_email

# Определение системы ОДУ первого порядка
def circuit_ode(t, y, E, R, L, C):
    U, dU = y
    d2U = (E - R * dU - U / C) / L
    return [dU, d2U]

# Реализация метода Эйлера
def euler_method(f, y0, t0, t1, h, E, R, L, C):
    t = np.arange(t0, t1, h)
    y = np.zeros((len(t), len(y0)))
    y[0] = y0
    for i in range(1, len(t)):
        y[i] = y[i-1] + h * np.array(f(t[i-1], y[i-1], E, R, L, C))
    return t, y

# Аппроксимация решения многочленом 5-й степени
def poly_approx(t, U, degree):
    p = Polynomial.fit(t, U, degree)
    return p

# Поиск максимального значения многочлена методом золотого сечения
def find_max_poly(p, t0, t1):
    result = minimize_scalar(lambda t: -p(t), bounds=(t0, t1), method='bounded')
    Tmax = result.x
    Umax = p(Tmax)
    return Tmax, Umax

# Решение задачи
def solve_circuit(E, R, C, L):
    t0 = 0
    t1 = 4e-3
    h = 2e-4
    y0 = [0, 0]
    
    # Решение системы ОДУ методом Эйлера
    t, y = euler_method(circuit_ode, y0, t0, t1, h, E, R, L, C)
    U = y[:, 0]
    
    # Аппроксимация решения многочленом 5-й степени
    p = poly_approx(t, U, 5)
    
    # Поиск максимального значения многочлена методом золотого сечения
    Tmax, Umax = find_max_poly(p, t0, t1)
    
    return t, U, Tmax, Umax, p

def plot_solution(t, U, p):
    plt.figure(figsize=(10, 6))  # Установим размеры фигуры
    
    # График численного решения методом Эйлера
    plt.plot(t, U, label='Численное решение', color='blue')
    
    # График аппроксимации многочленом 5-й степени
    plt.plot(t, p(t), label='Аппроксимация многочленом 5-й степени', linestyle='--', color='red')
    
    plt.xlabel('Время (с)')
    plt.ylabel('Напряжение (В)')
    plt.legend()
    plt.title('Напряжение на конденсаторе')
    plt.grid(True)
    plt.show()

# Функция для записи результатов в текстовый файл
def save_to_txt(Tmax, Umax):
    txt_file = "RLC_Results.txt"
    with open(txt_file, 'w', encoding='utf-8') as file:
        file.write("Результаты решения задачи RLC цепи\n")
        file.write(f"Первое максимальное напряжение (Umax): {Umax:.10f} В\n")
        file.write(f"Время достижения первого максимума (Tmax): {Tmax:.10f} с\n")

def open_solution_window():
    def update_solution():
        try:
            E = float(entry_E.get())
            R = float(entry_R.get())
            C = float(entry_C.get()) * 1e-6  # Преобразование из мкФ в Ф
            L = float(entry_L.get())
        except ValueError:
            messagebox.showwarning("Ошибка ввода", "Пожалуйста, введите корректные числовые значения.")
            return
        
        t, U, Tmax, Umax, p = solve_circuit(E, R, C, L)
        euler_results.config(state=tk.NORMAL)
        euler_results.delete(1.0, tk.END)
        euler_results.insert(tk.END, f"{U}")
        euler_results.config(state=tk.DISABLED)
        
        poly_results.config(state=tk.NORMAL)
        poly_results.delete(1.0, tk.END)
        poly_results.insert(tk.END, f"{p}")
        poly_results.config(state=tk.DISABLED)
        
        max_results_label.config(text=f"Первое максимальное напряжение (Umax): {Umax:.10f} В\nВремя достижения первого максимума (Tmax): {Tmax:.10f} с\n")
        
        return t, U, p, Tmax, Umax
    solution_window = tk.Tk()
    solution_window.title("Решение задачи RLC цепи")

    window_width = 900
    window_height = 700
    screen_width = solution_window.winfo_screenwidth()
    screen_height = solution_window.winfo_screenheight()
    position_top = int(screen_height/2 - window_height/2)
    position_right = int(screen_width/2 - window_width/2)
    solution_window.geometry(f'{window_width}x{window_height}+{position_right}+{position_top}')
    
    style = ttk.Style()
    style.configure('Solution.TLabel', font=('Times New Roman', 14))

    frame = ttk.Frame(solution_window, padding="10 10 10 10")
    frame.grid(column=0, row=0, padx=10)

    explanation = ("Программа решает задачу о напряжении на конденсаторе в RLC цепи.\n"
                   "Шаги выполнения:\n")
    explanation_label = ttk.Label(frame, text=explanation, style='Solution.TLabel', justify=tk.LEFT)
    explanation_label.grid(column=0, row=0, columnspan=2, sticky=tk.W, pady=5)
    
    input_frame = ttk.Frame(frame, padding="10 10 10 10")
    input_frame.grid(column=0, row=1, columnspan=2, sticky=tk.W, pady=5)
    
    ttk.Label(input_frame, text="E (В):", style='Solution.TLabel').grid(column=0, row=0, sticky=tk.W, pady=5)
    entry_E = ttk.Entry(input_frame)
    entry_E.grid(column=1, row=0, sticky=tk.W, pady=5)
    entry_E.insert(0, "10")
    
    ttk.Label(input_frame, text="R (Ом):", style='Solution.TLabel').grid(column=0, row=1, sticky=tk.W, pady=5)
    entry_R = ttk.Entry(input_frame)
    entry_R.grid(column=1, row=1, sticky=tk.W, pady=5)
    entry_R.insert(0, "10")
    
    ttk.Label(input_frame, text="C (мкФ):", style='Solution.TLabel').grid(column=0, row=2, sticky=tk.W, pady=5)
    entry_C = ttk.Entry(input_frame)
    entry_C.grid(column=1, row=2, sticky=tk.W, pady=5)
    entry_C.insert(0, "1")
    
    ttk.Label(input_frame, text="L (Гн):", style='Solution.TLabel').grid(column=0, row=3, sticky=tk.W, pady=5)
    entry_L = ttk.Entry(input_frame)
    entry_L.grid(column=1, row=3, sticky=tk.W, pady=5)
    entry_L.insert(0, "1")
    
    euler_label = ttk.Label(frame, text="1. Решение системы дифференциальных уравнений методом Эйлера:", style='Solution.TLabel', font=('Times New Roman', 14, 'bold'))
    euler_label.grid(column=0, row=2, sticky=tk.W, pady=5)
    euler_results = tk.Text(frame, wrap=tk.WORD, width=80, height=5)
    euler_results.grid(column=0, row=3, columnspan=2, pady=5)
    euler_results.config(state=tk.DISABLED)
    
    poly_label = ttk.Label(frame, text="2. Аппроксимация полученного решения многочленом 5-й степени:", style='Solution.TLabel', font=('Times New Roman', 14, 'bold'))
    poly_label.grid(column=0, row=4, sticky=tk.W, pady=5)
    poly_results = tk.Text(frame, wrap=tk.WORD, width=80, height=5)
    poly_results.grid(column=0, row=5, columnspan=2, pady=5)
    poly_results.config(state=tk.DISABLED)
    
    max_label = ttk.Label(frame, text="3. Поиск максимального значения многочлена методом золотого сечения:", style='Solution.TLabel', font=('Times New Roman', 14, 'bold'))
    max_label.grid(column=0, row=6, sticky=tk.W, pady=5)
    max_results_label = ttk.Label(frame, text="", style='Solution.TLabel')
    max_results_label.grid(column=0, row=7, columnspan=2, sticky=tk.W, pady=5)

    button_frame = ttk.Frame(solution_window)
    button_frame.grid(column=0, row=4, padx=10)
    ttk.Button(button_frame, text="Решить", command=update_solution, style='Solution.TButton').grid(column=0, row=4, padx=55)
    ttk.Button(button_frame, text="Показать график", command=lambda: plot_solution(t, U, p), style='Solution.TButton').grid(column=1, row=4, padx=55)
    ttk.Button(button_frame, text="Сохранить ответ", command=lambda: save_to_txt(Tmax, Umax), style='Solution.TButton').grid(column=2, row=4, padx=55)
    ttk.Button(button_frame, text="Техническая поддержка", command=lambda: open_email_window(), style='Solution.TButton').grid(column=3, row=4, padx=55)

    t, U, p, Tmax, Umax = update_solution()
    solution_window.mainloop()



def open_email_window():
    email_window = tk.Tk()
    email_window.title("Email Form")
    
    # Центрирование окна на экране
    window_width = 500
    window_height = 400
    screen_width = email_window.winfo_screenwidth()
    screen_height = email_window.winfo_screenheight()
    position_top = int(screen_height/2 - window_height/2)
    position_right = int(screen_width/2 - window_width/2)
    email_window.geometry(f'{window_width}x{window_height}+{position_right}+{position_top}')
    
    # Создание полей для ввода данных
    from_label = tk.Label(email_window, text="От:")
    from_label.grid(row=0, column=0, padx=10, pady=10)
    from_entry = tk.Entry(email_window, width=30)
    from_entry.grid(row=0, column=1, padx=10, pady=10, sticky='we')
        
    to_label = tk.Label(email_window, text="Кому:")
    to_label.grid(row=1, column=0, padx=10, pady=10)
    to_entry = tk.Entry(email_window, width=30)
    to_entry.grid(row=1, column=1, padx=10, pady=10, sticky='we')
        
    subject_label = tk.Label(email_window, text="Тема:")
    subject_label.grid(row=2, column=0, padx=10, pady=10)
    subject_entry = tk.Entry(email_window, width=30)
    subject_entry.grid(row=2, column=1, padx=10, pady=10, sticky='we')
        
    body_label = tk.Label(email_window, text="Напишите что-нибудь:")
    body_label.grid(row=3, column=0, padx=10, pady=10)
    body_entry = tk.Entry(email_window, width=50)
    body_entry.grid(row=3, column=1, padx=10, pady=10, sticky='we')
    
    button_frame = ttk.Frame(email_window)
    button_frame.grid(row=4, columnspan=2, pady=10)  # Ensure the frame spans both columns
    
    send_button = ttk.Button(button_frame, text="Отправить", command=lambda: send(email_window))
    send_button.grid(row=0, column=0, pady=(0,10), padx=20, sticky='e')

    def send(parent_window):
        # Получение данных из формы
        from_email = from_entry.get()
        to_email = to_entry.get()
        subject = subject_entry.get()
        body = body_entry.get()
        
        # Проверка корректности email
        if not validate_email.validate_email(from_email):
            messagebox.showwarning("Ошибка", "Пожалуйста, введите корректный адрес электронной почты.", parent=parent_window)
            return
        
        # Сохранение данных в файл
        filename = "email_data.txt"
        filepath = os.path.join(os.getcwd(), filename)
        with open(filepath, "w") as file:
            file.write(f"From: {from_email}\n")
            file.write(f"Subject: {subject}\n")
            file.write(f"Body: {body}\n")
        
        # Показываем сообщение об успешной отправке
        messagebox.showinfo("Успешно", "Данные успешно отправлены.", parent=parent_window)
        
        # Закрываем только окно с формой ввода
        parent_window.destroy()
    
    email_window.mainloop()

def task_window():
    task_window = tk.Tk()
    task_window.title("Текст задания")

    # Центрирование окна на экране
    window_width = 800
    window_height = 600  # Увеличил высоту окна для изображения
    screen_width = task_window.winfo_screenwidth()
    screen_height = task_window.winfo_screenheight()
    position_top = int(screen_height/2 - window_height/2)
    position_right = int(screen_width/2 - window_width/2)
    task_window.geometry(f'{window_width}x{window_height}+{position_right}+{position_top}')

    frame = ttk.Frame(task_window, padding="10 10 10 10")
    frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))


    task_text = (
        "    Зависимость напряжения на конденсаторе от времени после замыкания\n"
        "ключа описывается дифференциальным уравнением U(t) + (R/L)*U(t) + ((U(t) - E) / (L * C)) = 0,\n"
        "с начальными условиями U(0) = 0, U(0) = 0\n"
    )
    
    task_label = ttk.Label(frame, text=task_text, anchor='center', justify='left')
    task_label.grid(column=0, row=1, sticky=tk.W)
    canvas = tk.Canvas(frame, width=300, height=200)
    art_obj = tk.PhotoImage(file="circuit.png")
    canvas.create_image(0, 0, anchor=tk.NW, image=art_obj)
    canvas.grid(column=0, row=2, sticky=tk.W)
    task2_text = (
        "    Требуется:\n"
        "    С погрешностью не более 10 мксек, найти момент времени Тmax,\n"
        "в который напряжение на конденсаторе U(t) достигает первого (наибольшего)\n"
        "максимального значения Umax при соответствующее значение напряжения Umax при\n"
        "следующих исходных данных: E=10B, R=10Ом. С = 1мкФ, L = 1Гн\n"
        "    Методические указанеия:\n"
        "    1. Для получения зависимости U(t) привести заданное ОДУ 2-го порядка\n"
        "к системе ОДУ первого порядка и решить ее методом Эйлера с автоматическим выбором\n"
        "шага интегрирования при t ε [0; 4*10^-3] сек. и шагом таблицы h = 2*10^-4 сек.\n"
        "обеспечив погрешность не более 0,1В\n"
        "    2. Аппроксимировать полученное решение многочленом 5-й степени с вычислением погрешности аппроксимации.\n"
        "    3. Для поиска максимального значения многочлена выбранной степени использовать один\n"
        "из численных методов одномерной оптимизации.\n"
    )
    
    task_label = ttk.Label(frame, text=task2_text, anchor='center', justify='left')
    task_label.grid(column=0, row=3, sticky=tk.W)
    def close_and_open_solution():
        task_window.destroy()
        open_solution_window()

    ttk.Button(frame, text="Решение", command=close_and_open_solution).grid(column=0, row=4, padx=350)

    task_window.mainloop()

# Функция для создания приветственного окна
def create_welcome_window():
    root = tk.Tk()  # Создаем основное окно Tk
    root.title("Титульное окно")
    style = ttk.Style()
    style.configure('Solution.TLabel', font=('Times New Roman', 14))
    # Центрирование окна на экране
    window_width = 1100
    window_height = 700
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    position_top = int(screen_height/2 - window_height/2)
    position_right = int(screen_width/2 - window_width/2)
    root.geometry(f'{window_width}x{window_height}+{position_right}+{position_top}')
    
    frame = ttk.Frame(root, padding="10 10 10 10")
    frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    # Текст из изображения
    header_text = ("МИНИСТЕРСТВО ЦИФРОВОГО РАЗВИТИЯ, СВЯЗИ И МАССОВЫХ КОММУНИКАЦИЙ РОССИЙСКОЙ ФЕДЕРАЦИИ\n"
               "Ордена Трудового Красного Знамени федеральное государственное бюджетное образовательное учреждение высшего образования\n"
               "«Московский технический университет связи и информатики»\n" + 5 * "\n")
    project_text = (" " * 70 + "ПРОЕКТ\n" + (" " * 70 + "ПО УЧЕБНОЙ(ТЕХНОЛОГИЧЕСКОЙ) ПРАКТИКЕ" + 9 * "\n"))

    header_label = ttk.Label(frame, text=header_text, style='Solution.TLabel', anchor='center', justify='center')
    header_label.grid(column=0, row=0, sticky=tk.W)

    project_label = ttk.Label(frame, text=project_text, style='Solution.TLabel', anchor='center', justify='center')
    project_label.grid(column=0, row=1, sticky=tk.W)
    student_info = ("Выполнил: студент гр. БЭИ2202\n"
                    "Тогузов А. А.\n"
                    "Вариант 139\n"
                    "Проверил: стар. преподаватель каф. Информатика Юсков И. О.\n"
                    )
    
    student_info_label = ttk.Label(frame, text=student_info, style='Solution.TLabel', anchor='e', justify='left')
    student_info_label.grid(column=0, row=2, sticky=tk.E)

    
    def close_and_open_task():
        root.destroy()
        task_window()
    ttk.Button(frame, text="Перейти к заданию", command=close_and_open_task, style='Solution.TButton').grid(column=0, row=3, padx=10, pady=10)

    
    root.mainloop()

if __name__ == "__main__":
    create_welcome_window()
