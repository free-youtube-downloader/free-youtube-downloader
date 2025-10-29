from PySide6.QtWidgets import (QWidget, QHBoxLayout, QListWidget, QListWidgetItem,
                            QFrame, QAbstractItemView, QGraphicsDropShadowEffect)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

class SideMenuLayout:
    def __init__(self, parent):
        self.parent = parent
        self.container = QWidget()
        self.container.setFixedWidth(240)
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self.container)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        
        
        self.side_menu = QListWidget()
        self.side_menu.setFixedWidth(220)
        self.side_menu.setSelectionMode(QAbstractItemView.SingleSelection)
        self.side_menu.setFlow(QListWidget.TopToBottom)
        self.side_menu.setSpacing(2)
        self.side_menu.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.side_menu.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.side_menu.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        
        menu_items = ["Home", "Video", "Audio", "History", "Settings", "Profile", "Queue", "Scheduler", "Batch"]
        for item_name in menu_items:
            item = QListWidgetItem(f"{self.get_menu_icon(item_name)}  {item_name}")
            item.setTextAlignment(Qt.AlignLeft)
            self.side_menu.addItem(item)
        
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(0)
        shadow.setColor(QColor(0, 0, 0, 50))
        self.side_menu.setGraphicsEffect(shadow)
        
        
        self.side_menu.setCurrentRow(0)
        self.side_menu.currentRowChanged.connect(self.parent.side_menu_changed)
        
        
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 255, 255, 0.1),
                    stop:0.5 rgba(255, 255, 255, 0.2),
                    stop:1 rgba(255, 255, 255, 0.1));
                width: 1px;
            }
        """)
        
        
        layout.addWidget(self.side_menu)
        layout.addWidget(separator)

    def get_menu_icon(self, name):
        icons = {
            "Home": "🏠",
            "Video": "🎥",
            "Audio": "🎵",
            "History": "📜",
            "Settings": "⚙️",
            "Profile": "👤",
            "Queue": "📋",
            "Scheduler": "⏰",
            "Batch": "📦"
        }
        return icons.get(name, "") 