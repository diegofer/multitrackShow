from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (QApplication, QListWidgetItem, QListWidget,
                             QVBoxLayout, QLineEdit, QDialog,
                             QMessageBox)

class SearchDialog(QDialog):

    song_selected = Signal(str)

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Buscar")
        self.setModal(True)  # Establecer la ventana como modal
        self.setFixedSize(300, 400)  # Tamaño fijo para la ventana

        # Lista completa de canciones
        self.canciones = QApplication.instance().property("canciones")

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
        ruta = item.data(Qt.ItemDataRole.UserRole)
        self.song_selected.emit(ruta)
        self.accept()


        """Maneja la selección de un ítem en la lista."""
        # try:
        #     titulo = item.text()  # Obtener el título mostrado
        #     ruta = item.data(Qt.ItemDataRole.UserRole)  # Obtener la ruta oculta
        #     QMessageBox.information(self, "Selección", f"Seleccionaste:\nTítulo: {titulo}\nRuta: {ruta}")
        #     print(f"Seleccionaste: {titulo} -> {ruta}")
        #     # Aquí puedes agregar lógica para manejar la canción seleccionada
        # except Exception as e:
        #     QMessageBox.critical(self, "Error", f"Error al procesar la selección: {e}")