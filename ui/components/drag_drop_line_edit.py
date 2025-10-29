from PySide6.QtWidgets import QLineEdit

class DragDropLineEdit(QLineEdit):
    def __init__(self, placeholder="Enter or drag a link here..."):
        super().__init__()
        self.setAcceptDrops(True)
        self.setPlaceholderText(placeholder)

    def dragEnterEvent(self, e):
        if e.mimeData().hasText():
            e.acceptProposedAction()

    def dropEvent(self, e):
        txt = e.mimeData().text().strip()
        self.setText(txt.replace("file://", "") if not txt.startswith("http") else txt) 