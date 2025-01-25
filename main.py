import sys
import os
import zipfile
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QApplication, QWidget,QLabel, QListWidgetItem, QListWidget,
                             QVBoxLayout, QHBoxLayout, QGridLayout, QSpacerItem, QLineEdit, 
                             QSpacerItem, QSizePolicy, QDialog,
                             QMessageBox, QPushButton)

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

class SearchDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Buscar")
        self.setModal(True)  # Establecer la ventana como modal
        self.setFixedSize(300, 400)  # Tamaño fijo para la ventana

        # Lista completa de canciones
        self.canciones = canciones

        layout = QVBoxLayout()

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Buscar")
        self.search_box.textChanged.connect(self.filtrar_canciones)

        

        # Lista para mostrar canciones filtradas
        self.resultados_lista = QListWidget()
        self.resultados_lista.itemClicked.connect(self.procesar_seleccion) 

        layout.addWidget(self.search_box)
        layout.addWidget(self.resultados_lista)
        self.setLayout(layout)

        self.actualizar_lista(self.canciones)  # Mostrar todas las canciones al inicio

    def actualizar_lista(self, canciones):
        """Actualiza la lista de resultados."""
        self.resultados_lista.clear()
        for titulo, ruta in canciones:
            item = QListWidgetItem(titulo)  # Mostrar solo el título
            item.setData(Qt.ItemDataRole.UserRole, ruta)  # Almacenar la ruta como dato oculto
            self.resultados_lista.addItem(item)

    def filtrar_canciones(self, texto):
        """Filtra las canciones según el texto ingresado en la caja de búsqueda."""
        texto = texto.lower()
        canciones_filtradas = [
            (titulo, ruta) for titulo, ruta in self.canciones if texto in titulo.lower()
        ]
        self.actualizar_lista(canciones_filtradas)

    def procesar_seleccion(self, item):
        """Maneja la selección de un ítem en la lista."""
        try:
            titulo = item.text()  # Obtener el título mostrado
            ruta = item.data(Qt.ItemDataRole.UserRole)  # Obtener la ruta oculta
            QMessageBox.information(self, "Selección", f"Seleccionaste:\nTítulo: {titulo}\nRuta: {ruta}")
            print(f"Seleccionaste: {titulo} -> {ruta}")
            # Aquí puedes agregar lógica para manejar la canción seleccionada
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al procesar la selección: {e}")

class MainWindow(QWidget):
    def __init__(self, canciones):
        super().__init__()

        self.setWindowTitle("Multitrack Show")

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
        self.boton_centro1 = QPushButton("Centro 1")
        self.boton_derecha1 = QPushButton("Derecha 1")

        menu_layout.addWidget(self.boton_izquierda1)
        menu_layout.addSpacerItem(QSpacerItem(20, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        menu_layout.addWidget(self.boton_centro1)
        menu_layout.addSpacerItem(QSpacerItem(20, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        menu_layout.addWidget(self.boton_derecha1)

        #### PLAYLIST ###
        playlist_layout = QHBoxLayout()

        self.search_btn = QPushButton("+")
        self.search_btn.clicked.connect(self.open_serch_dialog)

        playlist_layout.addWidget(self.search_btn)

        main_layout.addLayout(menu_layout)
        main_layout.addLayout(playlist_layout)

        self.setLayout(main_layout)


    def open_serch_dialog(self):
        search_dialog = SearchDialog()
        search_dialog.exec()

    


# --- Configuración y ejecución (sin cambios)
library_path = "C:\WorshipSong Band\Library"
file_metadata = "Tracks.txt"
canciones = cargar_canciones_de_carpeta(library_path, file_metadata)

if not canciones:
    print("No se pudieron cargar las canciones. Saliendo...")
    exit()

if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        window = MainWindow(canciones)
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        print(f"Error crítico: {e}")