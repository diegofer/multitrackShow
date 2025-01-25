import sys
import os
import zipfile

def cargar_titulo_de_track(ruta_zip, nombre_archivo="Tracks.txt"):
    """Extrae el título de la segunda línea DESPUÉS de [Header]."""
    try:
        with zipfile.ZipFile(ruta_zip, 'r') as archivo_zip:
            try:
                with archivo_zip.open(nombre_archivo) as archivo_tracks:
                    contenido = archivo_tracks.read().decode('utf-8')
                    header_section = contenido.split("[Header]")[1].split("[End Header]")[0]
                    title_line = header_section.strip().splitlines()[2]
                    if title_line:
                        return title_line
                    else:
                        print(f"Advertencia: No se encontraron [Header] y al menos dos líneas después en {ruta_zip} o formato incorrecto")
                        return None
            except KeyError:
                return None  # Tracks.txt no está en el ZIP
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo ZIP en: {ruta_zip}")
        return None
    except zipfile.BadZipFile:
        print(f"Advertencia: {ruta_zip} no es un ZIP válido.")
        return None
    except Exception as e:
        print(f"Error inesperado al procesar {ruta_zip}: {e}")
        return None


def cargar_canciones_de_carpeta(ruta_carpeta, nombre_archivo_tracks="Tracks.txt"):
    """Carga canciones SOLO de ZIPs que contienen el archivo especificado."""
    canciones_totales = []
    for nombre_archivo in os.listdir(ruta_carpeta):
        ruta_archivo = os.path.join(ruta_carpeta, nombre_archivo)
        if os.path.isfile(ruta_archivo) and nombre_archivo.endswith(".zip"):
            titulo = cargar_titulo_de_track(ruta_archivo, nombre_archivo_tracks) #Se le pasa el nombre del archivo a cargar_titulo_de_track
            if titulo:
                canciones_totales.append((titulo, ruta_archivo))
    return canciones_totales