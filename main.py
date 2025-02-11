from PySide6.QtCore import Qt, QSize
from PySide6.QtCore import QObject, QThreadPool, QRunnable, QThread
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QSpacerItem, QSizePolicy, QPushButton, QTextEdit)                        
from gui.search_dialog import SearchDialog
from gui.track_widget import TrackWidget
from file_manager import cargar_canciones_de_carpeta, cargar_titulo_de_track
from load_audio_manager import load_tracks_from_zip_parallel
from pprint import pprint
import numpy as np
import sounddevice as sd
import threading

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
        mixer_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        track = TrackWidget('Click')
        track1 = TrackWidget('Bass')
        track2 = TrackWidget('Gitar')
        track3 = TrackWidget('Drumps')
        track4 = TrackWidget('EG 1')
        track5 = TrackWidget('EG 2')


        mixer_layout.addWidget(track)
        mixer_layout.addWidget(track1)
        mixer_layout.addWidget(track2)
        mixer_layout.addWidget(track3)
        mixer_layout.addWidget(track4)
        mixer_layout.addWidget(track5)


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
        pprint(self.playlist)
        
        multitrack_index = len(self.playlist) - 1

        # Actualizar PLAYLIST BAR con botones
        song_title = self.get_title_from_stream(text_file)
        song_btn = QPushButton(song_title)
        song_btn.setProperty('index', multitrack_index)
        song_btn.setFixedSize(150, 100)

        song_btn.clicked.connect(lambda checked=False, boton=song_btn: self.boton_clicado(boton, checked))

        self.playlist_layout.addWidget(song_btn)

    def boton_clicado(self, boton, checked):
        index = boton.property("index")  # Recupera el dato numérico
        print(f"Botón '{boton.text()}' clicado. Dato asociado: {index}")
        self.play_song(index)

    def get_title_from_stream(self, text_stream):
        header_section = text_stream.split("[Header]")[1].split("[End Header]")[0]
        title_line = header_section.strip().splitlines()[2]
        return title_line
    
    def play_song(self, index):
        tracks_dict     = self.playlist[index]['tracks']
        tracks = np.array( list(tracks_dict.values()), dtype=np.float32 ) #con solo List funcina pero por precaucion
        samplerate = self.playlist[index]['sr']
        max_channels = 2
        event = threading.Event()
    
        print(tracks)
        # Asegurarse de que todas las pistas tienen la misma longitud y número de canales
        max_length = max(len(track) for track in tracks)
        for i in range(len(tracks)):
            print(isinstance(i, np.ndarray))
            # Rellenar pistas cortas con ceros
            tracks[i] = np.pad(tracks[i], ((0, max_length - len(tracks[i])), (0, 0)), 'constant')
            # Convertir pistas con menos canales a tener `max_channels` (rellenar con ceros)
            if tracks[i].shape[1] < max_channels:
                tracks[i] = np.pad(tracks[i], ((0, 0), (0, max_channels - tracks[i].shape[1])), 'constant')

        # Combinar todas las pistas en un arreglo multicanal
        data = sum(tracks)  # Suma todas las pistas (combinación multicanal)
        
        # Normalizar para evitar distorsión
        max_val = np.max(np.abs(data))
        if max_val > 1.0:
            data /= max_val

        print(f"Loaded {len(tracks)} tracks with {max_channels} channels at {samplerate} Hz.")

        # Usar un diccionario para manejar el índice de reproducción
        state = {'current_frame': 0}

        # Callback para manejar reproducción por streaming
        def callback(outdata, frames, time, status):
            if status:
                print(status)

            # Manejar los datos en bloques
            chunksize = min(len(data) - state['current_frame'], frames)
            outdata[:chunksize, :] = data[state['current_frame']:state['current_frame'] + chunksize, :]
            
            if chunksize < frames:  # Final de la reproducción
                outdata[chunksize:, :] = 0
                raise sd.CallbackStop()

            state['current_frame'] += chunksize

        # Crear el flujo de salida para todos los canales
        stream = sd.OutputStream(
            samplerate=samplerate,
           #device=args.device,
            channels=max_channels,  # Configurar salida multicanal
            callback=callback,
            finished_callback=event.set
        )

        with stream:
            print("Playing...")
            event.wait()  # Esperar hasta que termine la reproducción

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