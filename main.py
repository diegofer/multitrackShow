from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QSpacerItem, QSizePolicy, QPushButton, QTextEdit)                        
from gui.search_dialog import SearchDialog
from file_manager import cargar_canciones_de_carpeta, cargar_titulo_de_track


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

        #### PLAYLIST ###
        playlist_layout = QHBoxLayout()
        playlist_layout.setAlignment(Qt.AlignmentFlag.AlignLeft) 

        self.plus_btn = QPushButton()
        self.plus_btn.setFixedSize(50, 50)
        self.plus_btn.setIcon(QIcon("assets\img\plus-circle.svg"))
        self.plus_btn.setIconSize(self.plus_btn.size()  * 0.7)
        self.plus_btn.clicked.connect(self.open_serch_dialog)

        playlist_layout.addWidget(self.plus_btn)


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
        #aqui cargamos los tracks de audio en un thread

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