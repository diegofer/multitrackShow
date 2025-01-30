from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QSpacerItem, QSizePolicy, QPushButton, QTextEdit)                        
from gui.search_dialog import SearchDialog
from file_manager import cargar_canciones_de_carpeta, cargar_titulo_de_track
from load_audio_manager import load_tracks_from_zip, load_tracks_from_zip_parallel

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Multitrack Show")
        self.resize(1200, 650)

       
        self.playlist = []
        main_layout = QVBoxLayout()

        #### MENU BAR ###
        menu_layout = QHBoxLayout() 

        self.boton_izquierda1 = QPushButton("Izquierda 1")
        self.play_btn = QPushButton()
        self.play_btn.setFixedSize(120, 60)
        self.play_btn.setIcon(QIcon("assets/img/play.svg"))
        self.play_btn.setIconSize(QSize(50, 50))
        self.boton_derecha1 = QPushButton("⚙️")

        menu_layout.addWidget(self.boton_izquierda1)
        menu_layout.addSpacerItem(QSpacerItem(20, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        menu_layout.addWidget(self.play_btn)
        menu_layout.addSpacerItem(QSpacerItem(20, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        menu_layout.addWidget(self.boton_derecha1)

        #### PLAYLIST BAR ###
        self.playlist_layout = QHBoxLayout()
        self.playlist_layout.setContentsMargins(0, 0, 0, 0)
        self.playlist_layout.setAlignment(Qt.AlignmentFlag.AlignLeft) 
        self.playlist_layout.setSpacing(5)

        self.plus_btn = QPushButton()
        self.plus_btn.setFixedSize(50, 100)
        self.plus_btn.setIcon(QIcon("assets\img\plus-circle.svg"))
        self.plus_btn.setIconSize(self.plus_btn.size()  * 0.7)
        self.plus_btn.clicked.connect(self.open_serch_dialog)

        self.playlist_layout.addWidget(self.plus_btn)


        #### MIXER SECTION ###
        mixer_layout = QHBoxLayout()
        area_expansible = QTextEdit()
        area_expansible.setPlaceholderText("Área expansible (rellena el espacio restante)")
        area_expansible.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        mixer_layout.addWidget(area_expansible)


        #### ADD LAYOUTS ###
        main_layout.addLayout(menu_layout)
        main_layout.addLayout(self.playlist_layout)
        main_layout.addLayout(mixer_layout)

        self.setLayout(main_layout)


    def open_serch_dialog(self):
        search_dialog = SearchDialog()
        search_dialog.song_selected.connect(self.load_song_to_playlist)
        search_dialog.exec()

    def load_song_to_playlist(self, ruta):
        print(ruta)
        multitrack_loaded = {}
        tracks, samplerate, text_file = load_tracks_from_zip_parallel(ruta, None)
        
        multitrack_loaded["tracks"] = tracks
        multitrack_loaded["sr"] = samplerate
        multitrack_loaded["txt"] = text_file
        
        self.playlist.append(multitrack_loaded)
        
        multitrack_index = len(self.playlist) - 1

        print(samplerate)
        print(tracks)
        print(text_file)

        song_btn = QPushButton(f'cancion {multitrack_index}')
        song_btn.setProperty('index', multitrack_index)
        song_btn.setFixedSize(150, 100)

        song_btn.clicked.connect(lambda checked=False, boton=song_btn: self.boton_clicado(boton, checked))

        self.playlist_layout.addWidget(song_btn)

    def boton_clicado(self, boton, checked):
        dato = boton.property("index")  # Recupera el dato numérico
        print(f"Botón '{boton.text()}' clicado. Dato asociado: {dato}")
    

# --- Configuración y ejecución
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