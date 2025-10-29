from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit,
                            QDialogButtonBox, QMessageBox, QFileDialog, QLabel)
from PySide6.QtCore import Qt
from ui.components.animated_button import AnimatedButton
import os

class ProfileDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.selected_picture_path = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Create User Profile")
        self.setModal(True)
        layout = QVBoxLayout(self)
        
        frm = QFormLayout()
        self.name_edit = QLineEdit()
        self.pic_btn = AnimatedButton("Select Picture (Optional)")
        self.pic_label = QLabel("No file selected.")
        
        self.pic_btn.clicked.connect(self.pick_pic)
        
        frm.addRow("Name:", self.name_edit)
        frm.addRow("Picture:", self.pic_btn)
        frm.addRow(self.pic_label)
        
        bb = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        bb.accepted.connect(self.on_ok)
        bb.rejected.connect(self.reject)
        
        layout.addLayout(frm)
        layout.addWidget(bb)

    def pick_pic(self):
        path, _ = QFileDialog.getOpenFileName(self, "Profile Picture", "", "Images (*.png *.jpg *.jpeg)")
        if path:
            self.selected_picture_path = path
            self.pic_label.setText(os.path.basename(path))

    def on_ok(self):
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Error", "Please provide a name.")
            return
            
        if self.selected_picture_path:
            self.parent.user_profile.set_profile(name, self.selected_picture_path, self.parent.user_profile.get_download_path())
        else:
            self.parent.user_profile.set_profile(name, "", self.parent.user_profile.get_download_path())
            
        self.accept()
        self.parent.update_profile_ui() 