from PySide6.QtWidgets import QFrame, QListWidget, QVBoxLayout
from PySide6.QtCore import Qt

class SearchPopup(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent, Qt.Popup | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.list_widget = QListWidget()
        self.list_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.list_widget.setMinimumHeight(200)
        self.list_widget.setMaximumHeight(400)
        layout.addWidget(self.list_widget)

    def show_at(self, pos, width):
        self.setGeometry(pos.x(), pos.y(), width, self.list_widget.height())
        self.show()

    def clear(self):
        self.list_widget.clear()

    def addItem(self, item):
        self.list_widget.addItem(item) 