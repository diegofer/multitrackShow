import sys
import os
import zipfile
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QApplication, QWidget, 
                             QVBoxLayout, QHBoxLayout, QSpacerItem, 
                             QSpacerItem, QSizePolicy, 
                             QPushButton, QTextEdit)

from gui.search_dialog import SearchDialog

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
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Multitrack Show")
        self.resize(1200, 650)

        # --- Estilo oscuro ---
        self.setStyleSheet("""
            QWidget {
                background-color: #282c34; /* Gris oscuro */
                color: #abb2bf; /* Gris claro */
            }
            QLabel {
                color: #abb2bf;
            }
            QLineEdit {
                background-color: #3e4451;
                color: #abb2bf;
                border: 1px solid #5c6370;
            }
            QListWidget {
                background-color: #3e4451;
                color: #abb2bf;
                border: 1px solid #5c6370;
            }
            QListWidget::item:selected {
                background-color: #5c6370; /* Color de selección */
                color: white;
            }
        """)
        
        main_layout = QVBoxLayout()

        #### MENU ###
        menu_layout = QHBoxLayout() 

        self.boton_izquierda1 = QPushButton("Izquierda 1")
        self.boton_centro1 = QPushButton("▶️ Play")
        self.boton_derecha1 = QPushButton("⚙️")

        menu_layout.addWidget(self.boton_izquierda1)
        menu_layout.addSpacerItem(QSpacerItem(20, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        menu_layout.addWidget(self.boton_centro1)
        menu_layout.addSpacerItem(QSpacerItem(20, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        menu_layout.addWidget(self.boton_derecha1)

        #### PLAYLIST ###
        playlist_layout = QHBoxLayout()
        playlist_layout.setAlignment(Qt.AlignmentFlag.AlignLeft) 

        self.search_btn = QPushButton("➕")
        self.search_btn.setFixedSize(50, 50)
        self.search_btn.clicked.connect(self.open_serch_dialog)

        playlist_layout.addWidget(self.search_btn)

        

        #### MIXER ###
        mixer_layout = QHBoxLayout()
        area_expansible = QTextEdit()
        area_expansible.setPlaceholderText("Área expansible (rellena el espacio restante)")
        area_expansible.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        mixer_layout.addWidget(area_expansible)


        #### ADD LAYOUTS ###
        main_layout.addLayout(menu_layout)
        main_layout.addLayout(playlist_layout)
        main_layout.addLayout(mixer_layout)

        self.setLayout(main_layout)


    def open_serch_dialog(self):
        search_dialog = SearchDialog()
        search_dialog.song_selected.connect(self.load_song_to_playlist)
        search_dialog.exec()

    def load_song_to_playlist(self, ruta):
        print(ruta)

# --- Configuración y ejecución (sin cambios)
library_path = "C:\WorshipSong Band\Library"
file_metadata = "Tracks.txt"
canciones = cargar_canciones_de_carpeta(library_path, file_metadata)

if not canciones:
    print("No se pudieron cargar las canciones. Saliendo...")
    exit()

if __name__ == "__main__":
    try:
        app = QApplication([])
        app.setProperty("canciones", canciones)

        window = MainWindow()
        window.show()
        app.exec()
    except Exception as e:
        print(f"Error crítico: {e}")