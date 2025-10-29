from PySide6.QtWidgets import QStatusBar, QHBoxLayout, QLabel, QProgressBar, QWidget
from PySide6.QtCore import Qt
from ui.components.animated_button import AnimatedButton

class StatusBarLayout:
    def __init__(self, parent):
        self.parent = parent
        self.container = QStatusBar()
        self.progress_bar = None
        self.init_ui()

    def init_ui(self):
        layout_widget = QWidget()
        layout = QHBoxLayout(layout_widget)
        layout.setContentsMargins(5, 2, 5, 2)
        layout.setSpacing(10)

        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimumHeight(28)
        self.progress_bar.setFormat("Ready")  
        self.progress_bar.setAlignment(Qt.AlignCenter)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)  
        layout.addWidget(self.progress_bar, stretch=1)  

        self.container.addPermanentWidget(layout_widget, 1)
        self.parent.setStatusBar(self.container) 