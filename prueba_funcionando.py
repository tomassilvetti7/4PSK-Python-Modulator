import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import tkinter as tk

# Parámetros básicos
fs = 1000  # Frecuencia de muestreo
fc = 10  # Frecuencia de la portadora (mucho más baja)
symbol_duration = 0.05  # Duración de cada símbolo (intervalos de 0.05 segundos)
total_bits = 32  # Total de bits a enviar
total_duration = 2  # Duración total de la animación en segundos
frames_per_symbol = int(fs * symbol_duration)  # Número de frames por símbolo

# Variable global para los bits y la entrada
global bits, entry

# Función para convertir caracteres a binario usando ASCII
def chars_to_binary(chars):
    binary_str = ''.join(format(ord(c), '08b') for c in chars)  # 8 bits por carácter
    return binary_str[:total_bits]  # Limitar a total_bits

# Función que se llama al presionar el botón de continuar
def on_continue():
    chars = entry_chars.get()
    if len(chars) > 4:
        chars = chars[:4]  # Limitar a 4 caracteres
    binary_input = chars_to_binary(chars)

    # Mostrar la tabla de verdad y la segunda ventana para ingresar el código binario
    open_modulation_window(chars, binary_input)

# Función que abre la ventana de modulación
def open_modulation_window(chars, initial_binary_input):
    global bits, entry
    bits = np.array([int(bit) for bit in initial_binary_input])  # Convertir a array de bits

    # Crear ventana de modulación
    modulation_window = tk.Toplevel(root)
    modulation_window.title("Simulación de Modulación")
    modulation_window.geometry('600x500')  # Aumentar tamaño para mostrar la tabla

    # Crear frame para la entrada de texto y botones
    input_frame = tk.Frame(modulation_window)
    input_frame.pack(padx=20, pady=20)

    # Función de validación para limitar la entrada a 32 caracteres
    def validate_length(P):
        if len(P) > 32:
            return False
        return True

    vcmd = modulation_window.register(validate_length)

    # Crear entrada de texto para el código binario
    entry_label = tk.Label(input_frame, text="Ingresa el código binario (máx. 32 bits):")
    entry_label.pack(pady=10)
    entry = tk.Entry(input_frame, validate="key", validatecommand=(vcmd, '%P'), width=30)
    entry.pack(pady=10)

    # Inicializar el campo con el input de caracteres
    entry.insert(0, initial_binary_input)

    # Crear botón para modulación
    button = tk.Button(input_frame, text="Empezar Modulación", command=on_modulate)
    button.pack(pady=20)

    # Crear etiqueta para la tabla de verdad
    truth_table_label = tk.Label(input_frame, text="", justify=tk.LEFT)
    truth_table_label.pack(pady=10)

    # Mostrar la tabla de verdad
    display_truth_table(chars, truth_table_label)

# Función para mostrar la tabla de verdad
def display_truth_table(chars, truth_table_label):
    truth_table_text = "Tabla de Verdad:\n"
    for char in chars:
        truth_table_text += f"{char}: {format(ord(char), '08b')}\n"
    truth_table_label.config(text=truth_table_text)

# Función de modulación 4-PSK
def modulate_psk(bits, fc, fs, t):
    symbols = bits.reshape(-1, 2)  # 4-PSK agrupa 2 bits
    phases = {
        (0, 0): 0,
        (0, 1): np.pi/2,
        (1, 1): np.pi,
        (1, 0): -np.pi/2
    }
    phases_signal = np.array([phases[tuple(symbol)] for symbol in symbols])
    phases_signal = np.repeat(phases_signal, len(t) // len(phases_signal))
    return np.cos(2 * np.pi * fc * t + phases_signal)

# Función para actualizar la gráfica en tiempo real
def update(frame, signal_carrier, signal_data, signal_modulated, lines, text_objects):
    global bits  # Hacer que bits sea accesible aquí
    # Actualizar los datos de cada señal en tiempo real (con diferentes colores)
    lines[0].set_data(t[:frame], signal_carrier[:frame])
    lines[1].set_data(t[:frame], signal_data[:frame])
    lines[2].set_data(t[:frame], signal_modulated[:frame])

    # Añadir líneas verticales para dividir los intervalos de a dos
    for i in range(1, total_bits // 2 + 1):  # Cada símbolo representa 2 bits
        for ax in axs:
            ax.axvline(x=i * 2 * symbol_duration, color='gray', linestyle='--', linewidth=0.5)

    # Actualizar el texto sobre el gráfico de la señal modulada
    for i in range(total_bits // 2):  # Solo actualizamos para símbolos
        if frame >= i * frames_per_symbol * 2:
            text_objects[i].set_text(f'{bits[i * 2]}{bits[i * 2 + 1]}')
            text_objects[i].set_position((i * 2 * symbol_duration + symbol_duration, 1.2))

    return lines + text_objects

# Función que se llama al presionar el botón de modulación
def on_modulate():
    global bits, entry  # Definir bits y entry como global
    binary_input = entry.get()
    if len(binary_input) > total_bits:
        binary_input = binary_input[:total_bits]  # Limitar a 32 bits
    bits = np.array([int(bit) for bit in binary_input])

    # Asegurarse de que la longitud sea un múltiplo de 2
    if len(bits) % 2 != 0:
        bits = np.append(bits, 0)  # Añadir un 0 si hay un número impar de bits

    global t, axs
    t = np.arange(0, len(bits) * symbol_duration, 1/fs)  # Vector de tiempo ajustado a la longitud de los bits

    # Señal portadora
    signal_carrier = np.cos(2 * np.pi * fc * t)

    # Para la señal de datos, simplemente usaremos los bits repetidos en el tiempo
    signal_data = np.repeat(bits, frames_per_symbol)

    # Modulación PSK
    signal_modulated = modulate_psk(bits[:len(bits)//2*2], fc, fs, t)

    # Configurar gráfico para tiempo real
    fig, axs = plt.subplots(3, 1, figsize=(10, 10))

    # Configurar ejes
    axs[0].set_xlim(0, len(bits) * symbol_duration)
    axs[0].set_ylim(-1.5, 1.5)
    axs[0].set_title("Señal Portadora")
    axs[0].set_ylabel("Amplitud")

    axs[1].set_xlim(0, len(bits) * symbol_duration)
    axs[1].set_ylim(-1.5, 1.5)
    axs[1].set_title("Señal de Datos")
    axs[1].set_ylabel("Amplitud")

    axs[2].set_xlim(0, len(bits) * symbol_duration)
    axs[2].set_ylim(-1.5, 1.5)
    axs[2].set_title("Señal Modulada - 4-PSK")
    axs[2].set_ylabel("Amplitud")

    # Inicializar las líneas de las gráficas de las señales
    line_carrier, = axs[0].plot([], [], color='blue')
    line_data, = axs[1].plot([], [], color='green')
    line_modulated, = axs[2].plot([], [], color='red')

    lines = [line_carrier, line_data, line_modulated]

    # Crear objetos de texto para mostrar los bits agrupados de a dos
    text_objects = []
    for i in range(total_bits // 2):
        text = axs[2].text(0, 0, '', ha='center', va='bottom', fontsize=10)
        text_objects.append(text)

    # Animación en tiempo real para completar los 32 bits en 2 segundos
    ani = FuncAnimation(fig, update, frames=len(t), fargs=(signal_carrier, signal_data, signal_modulated, lines, text_objects),
                        interval=int(total_duration * 1000 / len(t)), blit=True)

    plt.tight_layout()
    plt.show()

# Crear ventana principal de Tkinter
root = tk.Tk()
root.title("Entrada de Caracteres")
root.geometry('400x300')

# Crear frame para la entrada de texto y botón
input_frame = tk.Frame(root)
input_frame.pack(padx=20, pady=20)

# Crear entrada de texto para los caracteres
entry_label = tk.Label(input_frame, text="Ingresa hasta 4 caracteres:")
entry_label.pack(pady=10)
entry_chars = tk.Entry(input_frame, width=30)
entry_chars.pack(pady=10)

# Crear botón para continuar
continue_button = tk.Button(input_frame, text="Continuar", command=on_continue)
continue_button.pack(pady=20)

# Iniciar el loop de Tkinter
root.mainloop()
