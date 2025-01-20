import sys
import os
import zipfile
from PyQt6.QtWidgets import (QApplication, QWidget, QLabel, QComboBox,
                             QVBoxLayout)

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

class MainWindow(QWidget):
    def __init__(self, canciones):
        super().__init__()

        self.setWindowTitle("Reproductor Multitrack")

        # --- Estilo oscuro ---
        self.setStyleSheet("""
            QWidget {
                background-color: #282c34; /* Gris oscuro */
                color: #abb2bf; /* Gris claro */
            }
            QLabel {
                color: #abb2bf;
            }
            QComboBox {
                background-color: #3e4451;
                color: #abb2bf;
                border: 1px solid #5c6370;
            }
            QComboBox QAbstractItemView {
                background-color: #3e4451;
                color: #abb2bf;
                border: 1px solid #5c6370;
                selection-background-color: #5c6370; /* Color de selección */
            }
            QComboBox QLineEdit {
                background-color: #3e4451;
                color: #abb2bf;
                border: none;
            }
        """)

        layout = QVBoxLayout()

        label_cancion = QLabel("Selecciona una canción:")
        layout.addWidget(label_cancion)

        self.combobox = QComboBox()
        for title, path in canciones:
            self.combobox.addItem(title,path)

        self.combobox.activated.connect(self.load_song)
  
        self.combobox.setEditable(True)

        self.combobox.lineEdit().textChanged.connect(self.filtrar_canciones)

        layout.addWidget(self.combobox)

        self.setLayout(layout)

    def load_song(self, index):
        ruta_zip = self.combobox.itemData(index)
        if ruta_zip:
            print(f"Seleccionaste: {ruta_zip}")

    def filtrar_canciones(self, texto):
        pass

# --- Configuración y ejecución (sin cambios)
library_path = "C:\WorshipSong Band\Library"
file_metadata = "Tracks.txt"
canciones = cargar_canciones_de_carpeta(library_path, file_metadata)

if not canciones:
    print("No se pudieron cargar las canciones. Saliendo...")
    exit()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow(canciones)
    window.show()
    sys.exit(app.exec())