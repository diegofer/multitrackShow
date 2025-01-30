from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSlider, QPushButton
from PySide6.QtCore import Qt


class TrackWidget(QWidget):
    def __init__(self, track_name="Track 0", parent=None):
        super().__init__(parent)
        self.track_name = track_name
        self.setFixedWidth(70)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Centrar horizontalmente
        layout.setContentsMargins(0, 0, 0, 0)

        # Botón de mute
        self.mute_button = QPushButton("Mute")
        layout.addWidget(self.mute_button)
        
        # Botón de solo
        self.solo_button = QPushButton("Solo")
        layout.addWidget(self.solo_button)
        
        # Slider vertical
        self.slider = QSlider(Qt.Vertical)
        self.slider.setMinimum(0)
        self.slider.setMaximum(100)
        self.slider.setValue(50)
        self.slider.setStyleSheet("QSlider::handle { width: 50px; height: 20px; }")
        layout.addWidget(self.slider, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Título del instrumento
        self.label = QLabel(self.track_name)
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)
        
        self.setLayout(layout)