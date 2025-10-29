from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QCheckBox,
                            QComboBox, QDialogButtonBox, QMessageBox, QTableWidgetItem)
from PySide6.QtCore import Qt
from ui.components.drag_drop_line_edit import DragDropLineEdit
from core.downloader import DownloadTask

class QueueAddDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Add to Queue")
        self.setModal(True)
        layout = QVBoxLayout(self)
        
        frm = QFormLayout()
        self.url_edit = DragDropLineEdit("Enter or drag a link here")
        self.audio_checkbox = QCheckBox("Audio Only")
        self.playlist_checkbox = QCheckBox("Playlist")
        self.subtitles_checkbox = QCheckBox("Download Subtitles")
        self.format_combo = QComboBox()
        self.format_combo.addItems(["mp4", "mkv", "webm", "flv", "avi"])
        
        frm.addRow("URL:", self.url_edit)
        frm.addRow(self.audio_checkbox)
        frm.addRow(self.playlist_checkbox)
        frm.addRow("Video Format:", self.format_combo)
        frm.addRow(self.subtitles_checkbox)
        layout.addLayout(frm)
        
        bb = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        bb.accepted.connect(self.on_ok)
        bb.rejected.connect(self.reject)
        layout.addWidget(bb)

    def on_ok(self):
        url = self.url_edit.text().strip()
        if not url:
            QMessageBox.warning(self, "Error", "No URL.")
            return
            
        audio_only = self.audio_checkbox.isChecked()
        playlist = self.playlist_checkbox.isChecked()
        subtitles = self.subtitles_checkbox.isChecked()
        output_format = self.format_combo.currentText()
        
        task = DownloadTask(
            url,
            self.parent.user_profile.get_default_resolution(),
            self.parent.user_profile.get_download_path(),
            self.parent.user_profile.get_proxy(),
            audio_only=audio_only,
            playlist=playlist,
            subtitles=subtitles,
            output_format=output_format,
            audio_format=self.parent.user_profile.get_audio_format() if audio_only else None,
            audio_quality=self.parent.user_profile.get_audio_quality() if audio_only else "320",
            from_queue=True
        )
        
        if hasattr(self.parent, 'page_queue') and hasattr(self.parent.page_queue, 'queue_table'):
            row = self.parent.page_queue.queue_table.rowCount()
            self.parent.page_queue.queue_table.insertRow(row)
            self.parent.page_queue.queue_table.setItem(row, 0, QTableWidgetItem("Fetching..."))
            self.parent.page_queue.queue_table.setItem(row, 1, QTableWidgetItem("Fetching..."))
            self.parent.page_queue.queue_table.setItem(row, 2, QTableWidgetItem(url))
            
            download_type = "Audio" if audio_only else "Video"
            if playlist:
                download_type += " - Playlist"
            self.parent.page_queue.queue_table.setItem(row, 3, QTableWidgetItem(download_type))
            self.parent.page_queue.queue_table.setItem(row, 4, QTableWidgetItem("0%"))
            self.parent.run_task(task, row)
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "Queue page not initialized properly.") 