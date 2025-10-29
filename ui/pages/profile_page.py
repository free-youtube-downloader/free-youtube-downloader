from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, 
                            QFormLayout, QLineEdit, QFileDialog,
                            QGroupBox, QGridLayout)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPixmap
from ui.components.animated_button import AnimatedButton
import os

class ProfilePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        lbl = QLabel("Profile Page - Customize your details")
        lbl.setFont(QFont("Arial", 16, QFont.Bold))
        lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl)
        
        form_layout = QFormLayout()
        
        self.profile_name_edit = QLineEdit()
        self.profile_name_edit.setText(self.parent.user_profile.data["name"])
        form_layout.addRow("Name:", self.profile_name_edit)
        
        self.pic_label = QLabel("No file selected.")
        if self.parent.user_profile.data["profile_picture"]:
            self.pic_label.setText(os.path.basename(self.parent.user_profile.data["profile_picture"]))
        
        pic_btn = AnimatedButton("Change Picture")
        self.remove_pic_btn = AnimatedButton("Remove Picture")
        self.remove_pic_btn.setVisible(bool(self.parent.user_profile.data["profile_picture"]))
        
        pic_btn.clicked.connect(self.pick_pic)
        self.remove_pic_btn.clicked.connect(self.remove_pic)
        
        form_layout.addRow("Picture:", pic_btn)
        form_layout.addRow(self.pic_label)
        form_layout.addRow(self.remove_pic_btn)
        
        layout.addLayout(form_layout)
        
        self.preferences_group = QGroupBox("User Preferences")
        self.preferences_layout = QGridLayout()
        
        self.theme_value = QLabel()
        self.theme_value.setStyleSheet("font-weight: bold;")
        self.preferences_layout.addWidget(QLabel("Theme:"), 0, 0)
        self.preferences_layout.addWidget(self.theme_value, 0, 1)
        
        self.resolution_value = QLabel()
        self.resolution_value.setStyleSheet("font-weight: bold;")
        self.preferences_layout.addWidget(QLabel("Default Resolution:"), 1, 0)
        self.preferences_layout.addWidget(self.resolution_value, 1, 1)
        
        self.audio_format_value = QLabel()
        self.audio_format_value.setStyleSheet("font-weight: bold;")
        self.preferences_layout.addWidget(QLabel("Audio Format:"), 2, 0)
        self.preferences_layout.addWidget(self.audio_format_value, 2, 1)
        
        self.download_path_value = QLabel()
        self.download_path_value.setStyleSheet("font-weight: bold;")
        self.download_path_value.setWordWrap(True)
        self.preferences_layout.addWidget(QLabel("Download Path:"), 3, 0)
        self.preferences_layout.addWidget(self.download_path_value, 3, 1)
        
        self.history_value = QLabel()
        self.history_value.setStyleSheet("font-weight: bold;")
        self.preferences_layout.addWidget(QLabel("History Enabled:"), 4, 0)
        self.preferences_layout.addWidget(self.history_value, 4, 1)
        
        self.proxy_value = QLabel()
        self.proxy_value.setStyleSheet("font-weight: bold;")
        self.proxy_value.setWordWrap(True)
        self.preferences_layout.addWidget(QLabel("Proxy:"), 5, 0)
        self.preferences_layout.addWidget(self.proxy_value, 5, 1)
        
        self.preferences_group.setLayout(self.preferences_layout)
        layout.addWidget(self.preferences_group)
        
        save_btn = AnimatedButton("Save Profile")
        save_btn.clicked.connect(self.save_profile)
        layout.addWidget(save_btn)
        
        layout.addStretch()
        
        self.refresh_preferences()

    def refresh_preferences(self):
        self.theme_value.setText(self.parent.user_profile.get_theme())
        self.resolution_value.setText(self.parent.user_profile.get_default_resolution())
        self.audio_format_value.setText(self.parent.user_profile.get_audio_format())
        self.download_path_value.setText(self.parent.user_profile.get_download_path())
        self.history_value.setText("Yes" if self.parent.user_profile.is_history_enabled() else "No")
        self.proxy_value.setText(self.parent.user_profile.get_proxy() or "Not Set")

    def pick_pic(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Profile Picture", "", "Images (*.png *.jpg *.jpeg)")
        if path:
            self.pic_label.setText(os.path.basename(path))
            self.pic_label.setProperty("selected_path", path)
            self.remove_pic_btn.setVisible(True)

    def remove_pic(self):
        self.parent.user_profile.remove_profile_picture()
        self.pic_label.setText("No file selected.")
        self.pic_label.setProperty("selected_path", "")
        self.remove_pic_btn.setVisible(False)
        self.parent.profile_pic_label.setPixmap(QPixmap())
        self.parent.profile_name_label.setText("User")

    def save_profile(self):
        name = self.profile_name_edit.text().strip()
        if not name:
            self.parent.show_warning("Error", "Please provide a name.")
            return
        
        pic_path = self.pic_label.property("selected_path")
        if not pic_path:
            pic_path = self.parent.user_profile.data["profile_picture"]
        self.parent.user_profile.set_profile(
            name, 
            pic_path, 
            self.parent.user_profile.get_download_path()
        )
        self.parent.profile_manager.update_profile_ui()
        self.refresh_preferences()
        self.parent.show_info("Success", "Profile settings saved successfully.")
        
    def showEvent(self, event):
        super().showEvent(event)
        self.refresh_preferences() 