from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout, QPushButton
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from core.version import get_version

class FeatureCard(QFrame):
    def __init__(self, title, description, page_index, parent=None):
        super().__init__(parent)
        self.setObjectName("featureCard")
        self.page_index = page_index
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        desc_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(desc_label)
        
        button = QPushButton("Go")
        button.setCursor(Qt.PointingHandCursor)
        button.clicked.connect(self.on_button_clicked)
        layout.addWidget(button)

    def on_button_clicked(self):
        main_window = self.window()
        if main_window:
            main_window.side_menu_changed(self.page_index)

class HomePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        header_frame = QFrame()
        header_frame.setObjectName("headerFrame")
        header_layout = QVBoxLayout(header_frame)

        welcome_label = QLabel(f"TokLabs video Downloader {get_version()}")
        welcome_label.setFont(QFont("Arial", 24, QFont.Bold))
        welcome_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(welcome_label)

        subtitle_label = QLabel("Video & Audio Downloader")
        subtitle_label.setFont(QFont("Arial", 14))
        subtitle_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(subtitle_label)

        main_layout.addWidget(header_frame)

        features_frame = QFrame()
        features_frame.setObjectName("featuresFrame")
        features_layout = QVBoxLayout(features_frame)

        features_title = QLabel("Features")
        features_title.setFont(QFont("Arial", 16, QFont.Bold))
        features_layout.addWidget(features_title)

        grid_layout = QGridLayout()
        grid_layout.setSpacing(15)

        features = [
            ("Video Download", "Download videos with various quality options", 1),
            ("Audio Download", "Download audio in your preferred format", 2),
            ("Download History", "View and manage your download history", 3),
            ("Settings", "Configure download settings and preferences", 4),
            ("Profile", "Manage your user profile and preferences", 5),
            ("Queue", "Manage multiple downloads in queue", 6)
        ]

        for i, (title, desc, page_index) in enumerate(features):
            card = FeatureCard(title, desc, page_index, self)
            grid_layout.addWidget(card, i // 2, i % 2)

        features_layout.addLayout(grid_layout)
        main_layout.addWidget(features_frame)

        main_layout.addStretch() 