from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QCheckBox,
                            QDialogButtonBox, QMessageBox, QDateTimeEdit, QTableWidgetItem)
from PySide6.QtCore import Qt, QDateTime
from ui.components.drag_drop_line_edit import DragDropLineEdit

class ScheduleAddDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Add Scheduled Download")
        self.setModal(True)
        layout = QVBoxLayout(self)
        
        frm = QFormLayout()
        self.datetime_edit = QDateTimeEdit()
        self.datetime_edit.setCalendarPopup(True)
        self.datetime_edit.setDateTime(QDateTime.currentDateTime())
        
        self.url_edit = DragDropLineEdit("Enter link")
        self.audio_checkbox = QCheckBox("Audio Only")
        self.subtitles_checkbox = QCheckBox("Download Subtitles?")
        
        frm.addRow("Datetime:", self.datetime_edit)
        frm.addRow("URL:", self.url_edit)
        frm.addRow(self.audio_checkbox)
        frm.addRow(self.subtitles_checkbox)
        layout.addLayout(frm)
        
        bb = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        bb.accepted.connect(self.on_ok)
        bb.rejected.connect(self.reject)
        layout.addWidget(bb)

    def on_ok(self):
        datetime_val = self.datetime_edit.dateTime()
        url = self.url_edit.text().strip()
        
        if not url:
            QMessageBox.warning(self, "Error", "No URL.")
            return
            
        row = self.parent.scheduler_table.rowCount()
        self.parent.scheduler_table.insertRow(row)
        self.parent.scheduler_table.setItem(row, 0, QTableWidgetItem(datetime_val.toString("yyyy-MM-dd HH:mm:ss")))
        self.parent.scheduler_table.setItem(row, 1, QTableWidgetItem(url))
        
        download_type = "Audio" if self.audio_checkbox.isChecked() else "Video"
        self.parent.scheduler_table.setItem(row, 2, QTableWidgetItem(download_type))
        
        subtitles_text = "Yes" if self.subtitles_checkbox.isChecked() else "No"
        self.parent.scheduler_table.setItem(row, 3, QTableWidgetItem(subtitles_text))
        self.parent.scheduler_table.setItem(row, 4, QTableWidgetItem("Scheduled"))
        
        self.accept() 