import zipfile
import io, os
import soundfile as sf
import librosa
import concurrent.futures
import psutil


def load_tracks_from_zip(ruta):
    tracks = {}
    samplerate = None
    max_channels = 0

    with zipfile.ZipFile(ruta, 'r') as zip_file:
        for filename in zip_file.namelist():
            if filename.endswith(('.wav', '.ogg', '.flac')): 
                print(f"Procesando archivo: {filename}") 

                with zip_file.open(filename) as file:
                    file_data = io.BytesIO(file.read())

                    try:
                        data, fs = sf.read(file_data, always_2d=True)
                        if samplerate is None:
                            samplerate = fs
                        elif samplerate != fs:
                            print(f"Advertencia: Frecuencia de muestreo inconsistente en {filename}. Resampleando a {samplerate}.")
                            data = librosa.resample(data.T, orig_sr=fs, target_sr=samplerate).T
                        
                        max_channels = max(max_channels, data.shape[1])
                        tracks[filename] = data

                    except Exception as e:
                        print(f"Error procesando {filename}: {e}")

    print("tracks cargados")
    return tracks, samplerate

###### CARGA PARALLELA DE AUDIO #######
"""
    Permite cargar audio usando todos los hilos disponibles para mayor velocidad
"""

# definir el numero de hilos a usar
def calcular_hilos_adaptativos(porcentaje=75, reserva=2):
    total_hilos = os.cpu_count()
    uso_actual = psutil.cpu_percent(interval=1, percpu=True)
    hilos_libres = sum(1 for uso in uso_actual if uso < 50)
    hilos_por_porcentaje = int(total_hilos * (porcentaje / 100))
    
    # Toma el mínimo entre los hilos calculados por porcentaje y los hilos libres menos la reserva
    hilos_a_usar = max(1, min(hilos_por_porcentaje, hilos_libres - reserva))
    return hilos_a_usar


def process_audio_file(zip_file, filename, samplerate=None):
    try:
        with zip_file.open(filename) as file:
            file_data = io.BytesIO(file.read())
            data, fs = sf.read(file_data, always_2d=True)
            
            if samplerate and samplerate != fs:
                print(f"Resampleando {filename} de {fs} a {samplerate} Hz.")
                data = librosa.resample(data.T, orig_sr=fs, target_sr=samplerate).T
        print(f"archivo procesado {filename}")
        return filename, data, fs
    except Exception as e:
        print(f"Error procesando {filename}: {e}")
        return filename, None, None

def load_tracks_from_zip_parallel(zip_path, common_samplerate=None):
    """
    Carga y procesa archivos .ogg desde un ZIP utilizando paralelización.
    """
    tracks = {}
    samplerate = common_samplerate  # Establece un samplerate común si se proporciona

    with zipfile.ZipFile(zip_path, 'r') as zip_file:
        # Filtra solo los archivos .ogg dentro del ZIP
        ogg_files = [filename for filename in zip_file.namelist() if filename.endswith('.ogg')]
        
        print(f"Archivos .ogg encontrados: {ogg_files}")

        # Usa ThreadPoolExecutor para procesar los archivos en paralelo
        num_hilos = calcular_hilos_adaptativos(porcentaje=75, reserva=2)
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_hilos) as executor:
            total_hilos = os.cpu_count()
            print(f"Hilos totales disponibles: {total_hilos}")
            print(f"Número de hilos utilizados: {executor._max_workers}")
            futures = {
                executor.submit(process_audio_file, zip_file, filename, samplerate): filename
                for filename in ogg_files
            }

            for future in concurrent.futures.as_completed(futures):
                filename = futures[future]
                try:
                    result_filename, data, fs = future.result()
                    if data is not None:
                        tracks[result_filename] = data 
                        # Si no se especificó un samplerate común, usar el del primer archivo
                        if samplerate is None:
                            samplerate = fs

                except Exception as e:
                    print(f"Error en el procesamiento paralelo de {filename}: {e}")

    return tracks, samplerate