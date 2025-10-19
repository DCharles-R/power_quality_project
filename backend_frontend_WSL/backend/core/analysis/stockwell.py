import time
import numpy as np
import pandas as pd
from scipy.special import i0

# --- NO HAY CAMBIOS EN ESTA FUNCIÓN ---
# La Transformada de Stockwell Modificada (MST) con ventana de Kaiser
def modified_stockwell_transform(signal, fs, p=2, alpha=1.0):
    """
    Calcula la Transformada de Stockwell Modificada (MST) de una señal.
    (El cuerpo de esta función permanece igual)
    """
    N = len(signal)
    t = np.arange(N) / fs
    freqs = np.fft.fftfreq(N, 1 / fs)
    signal_fft = np.fft.fft(signal)
    mst_matrix = np.zeros((N // 2, N), dtype=np.complex64)
    print("Calculando la MST. Esto puede tardar un momento...")
    for n in range(1, N // 2):
        if freqs[n] <= 2 * 60:
            beta = alpha * 10 * n
        else:
            beta = alpha * 0.055 * n
        k = np.arange(N)
        inside_sqrt = beta ** 2 - (k * np.pi) ** 2
        sqrt_val = np.emath.sqrt(inside_sqrt)
        second_term_kscw = np.ones_like(sqrt_val, dtype=np.complex64)
        non_zero_indices = sqrt_val != 0
        second_term_kscw[non_zero_indices] = np.sinh(sqrt_val[non_zero_indices]) / sqrt_val[non_zero_indices]
        w_ka_p = ((N / i0(beta)) * second_term_kscw) ** p
        shifted_window = np.roll(w_ka_p, n)
        product = signal_fft * shifted_window
        mst_row = np.fft.ifft(product)
        mst_matrix[n, :] = mst_row
    print("Cálculo completado.")
    return mst_matrix, freqs[:N // 2], t


def mst_processing(signal):
    # ==============================================================================
    # --- SECCIÓN MODIFICADA: CARGA DE LA SEÑAL REAL DESDE EL CSV ---
    # ==============================================================================
    
    # --- Parámetros de la Señal REAL ---
    # Frecuencia de muestreo del STM32 (512 muestras/ciclo * 60 ciclos/s)
    fs = 30720  # Hz
    
    # Cargar los datos desde tu archivo CSV organizado
    # try:
    #     df_events = pd.read_csv('eventos_organizados.csv')
    # except FileNotFoundError:
    #     print("Error: No se encontró el archivo 'eventos_organizados.csv'.")
    #     exit()
    # 
    # # --- Elige qué evento quieres analizar ---
    # # Cambia este número para analizar otras capturas (0 para la primera, 1 para la segunda, etc.)
    # event_index_to_analyze = 5
    # 
    # if event_index_to_analyze >= len(df_events):
    #     print(f"Error: El índice {event_index_to_analyze} está fuera de rango. El archivo solo tiene {len(df_events)} eventos.")
    #     exit()
    # 
    # # Selecciona la fila del evento y extrae los valores de las muestras
    # # Usamos .iloc[n] para seleccionar la n-ésima fila.
    # # El primer valor es 'event_id', así que lo omitimos con [1:].
    # signal_row = df_events.iloc[event_index_to_analyze]
    # signal = signal_row.values[1:].astype(float) # Convierte los valores a números flotantes
    # 
    # # Obtiene el event_id para usarlo en el título de la gráfica
    # event_id = signal_row['event_id']
    
    # Asegurarse de que la señal no tenga valores NaN (Not a Number)
    if np.isnan(signal).any():
        print("Advertencia: Se encontraron valores nulos en la señal, se reemplazarán por 0.")
        signal = np.nan_to_num(signal)
    
    # Normalizar la señal (opcional pero recomendado para el análisis)
    # Esto escala la señal para que sus valores estén entre -1 y 1
    signal = signal - np.mean(signal) # Centrar en cero
    if np.max(np.abs(signal)) > 0:
        signal = signal / np.max(np.abs(signal))
    
    # --- FIN DE LA SECCIÓN MODIFICADA ---
    
    # --- Ejecución de la Transformada (Sin cambios, pero con los datos reales) ---
    p_order = 1
    alpha_factor = 0.05
    
    start_time = time.time()
    MST, FREQS, T = modified_stockwell_transform(signal, fs, p=p_order, alpha=alpha_factor)
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Tiempo de ejecución: {execution_time:.6f} segundos")
    
    # # --- Visualización de Resultados (Títulos actualizados) ---
    # fig, axs = plt.subplots(2, 1, figsize=(15, 10), sharex=True)
    # 
    # # Gráfica 1: Señal de entrada REAL
    # axs[0].plot(T, signal)
    # axs[0].set_title(f'Señal Capturada (Evento: {event_id})')
    # axs[0].set_ylabel('Amplitud Normalizada')
    # axs[0].grid(True)
    # axs[0].set_xlim(T[0], T[-1])
    # 
    # # Gráfica 2: Resultado de la MST
    # magnitude = np.abs(MST)
    # im = axs[1].pcolormesh(T, FREQS, magnitude, shading='gouraud', cmap='jet')
    # fig.colorbar(im, ax=axs[1], label='Magnitud')
    # axs[1].set_title('Resultado de la Transformada de Stockwell Modificada (MST)')
    # axs[1].set_ylabel('Frecuencia (Hz)')
    # axs[1].set_xlabel('Tiempo (s)')
    # axs[1].set_ylim(0, 1000)  # Ajustar el límite de frecuencia para ver los primeros armónicos
    # 
    # plt.tight_layout()
    # plt.show()
    return MST