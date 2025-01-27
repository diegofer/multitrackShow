import zipfile
import io
import soundfile as sf
import librosa
import concurrent.futures


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
        with concurrent.futures.ThreadPoolExecutor() as executor:
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