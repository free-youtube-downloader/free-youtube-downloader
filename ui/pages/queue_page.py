from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QTableWidget, QTableWidgetItem, QHeaderView,
                            QDialog, QFormLayout, QComboBox, QCheckBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from ui.components.animated_button import AnimatedButton
from ui.dialogs.batch_add_dialog import BatchAddDialog
from ui.components.drag_drop_line_edit import DragDropLineEdit
from core.downloader import DownloadTask

class QueuePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
      
        lbl = QLabel("Download Queue")
        lbl.setFont(QFont("Arial", 16, QFont.Bold))
        lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl)
        
        
        self.queue_table = QTableWidget()
        self.queue_table.setColumnCount(5)
        self.queue_table.setHorizontalHeaderLabels(["Title","Channel","URL","Type","Progress"])
        hh = self.queue_table.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.Stretch)
        hh.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(2, QHeaderView.Stretch)
        hh.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(4, QHeaderView.Stretch)
        layout.addWidget(self.queue_table)
        
        
        hl = QHBoxLayout()
        b_add = AnimatedButton("Add to Queue")
        b_batch = AnimatedButton("Batch Add")
        b_add.clicked.connect(self.add_queue_item_dialog)
        b_batch.clicked.connect(self.open_batch_add_dialog)
        b_start = AnimatedButton("Start Queue")
        b_start.clicked.connect(self.start_queue)
        b_cancel = AnimatedButton("Cancel All")
        b_cancel.clicked.connect(self.parent.cancel_active)
        hl.addWidget(b_add)
        hl.addWidget(b_batch)
        hl.addWidget(b_start)
        hl.addWidget(b_cancel)
        layout.addLayout(hl)
        
        layout.addStretch()

    def add_queue_item_dialog(self):
        d = QDialog(self)
        d.setWindowTitle("Add to Queue")
        d.setModal(True)
        ly = QVBoxLayout(d)
        
        frm = QFormLayout()
        url_edit = DragDropLineEdit("Enter or drag a link here")
        c_audio = QCheckBox("Audio Only")
        c_pl = QCheckBox("Playlist")
        c_subs = QCheckBox("Download Subtitles")
        fmt_combo = QComboBox()
        fmt_combo.addItems(["mp4","mkv","webm","flv","avi"])
        
        frm.addRow("URL:", url_edit)
        frm.addRow(c_audio)
        frm.addRow(c_pl)
        frm.addRow("Video Format:", fmt_combo)
        frm.addRow(c_subs)
        ly.addLayout(frm)
        
        b_ok = AnimatedButton("Add")
        b_cancel = AnimatedButton("Cancel")
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(b_ok)
        btn_layout.addWidget(b_cancel)
        ly.addLayout(btn_layout)
        
        def on_ok():
            url = url_edit.text().strip()
            if not url:
                self.parent.show_warning("Error", "No URL.")
                return
                
            audio_only = c_audio.isChecked()
            playlist = c_pl.isChecked()
            subtitles = c_subs.isChecked()
           
            output_format = self.parent.user_profile.get_audio_format() if audio_only else fmt_combo.currentText()
            
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
            
            row = self.queue_table.rowCount()
            self.queue_table.insertRow(row)
            self.queue_table.setItem(row, 0, QTableWidgetItem("Fetching..."))
            self.queue_table.setItem(row, 1, QTableWidgetItem("Fetching..."))
            self.queue_table.setItem(row, 2, QTableWidgetItem(url))
            
            download_type = "Audio" if audio_only else "Video"
            if playlist:
                download_type += " - Playlist"
            self.queue_table.setItem(row, 3, QTableWidgetItem(download_type))
            self.queue_table.setItem(row, 4, QTableWidgetItem("0%"))
            
            self.parent.run_task(task, row)
            d.accept()
            
        def on_cancel():
            d.reject()
            
        b_ok.clicked.connect(on_ok)
        b_cancel.clicked.connect(on_cancel)
        d.exec()

    def open_batch_add_dialog(self):
        dlg = BatchAddDialog(self.parent)
        dlg.exec()

    def start_queue(self):
        count_started = 0
        for row in range(self.queue_table.rowCount()):
            status_item = self.queue_table.item(row, 4)
            if status_item and ("Queued" in status_item.text() or "0%" in status_item.text()):
                if count_started < self.parent.max_concurrent_downloads:
                    url = self.queue_table.item(row, 2).text()
                    type_text = self.queue_table.item(row, 3).text().lower()
                    audio_only = ("audio" in type_text)
                    playlist = ("playlist" in type_text)
                    
                    output_format = self.parent.user_profile.get_audio_format() if audio_only else "mp4"
                    
                    task = DownloadTask(
                        url,
                        self.parent.user_profile.get_default_resolution(),
                        self.parent.user_profile.get_download_path(),
                        self.parent.user_profile.get_proxy(),
                        audio_only=audio_only,
                        playlist=playlist,
                        output_format=output_format,
                        audio_format=self.parent.user_profile.get_audio_format() if audio_only else None,
                        audio_quality=self.parent.user_profile.get_audio_quality() if audio_only else "320",
                        from_queue=True
                    )
                    
                    self.parent.run_task(task, row)
                    self.queue_table.setItem(row, 4, QTableWidgetItem("Started"))
                    count_started += 1
                    
        self.parent.append_log("Queue started.") 