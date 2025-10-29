from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QTableWidget, QTableWidgetItem, QHeaderView,
                            QDialog, QFormLayout, QCheckBox, QDateTimeEdit,
                            QComboBox)
from PySide6.QtCore import Qt, QDateTime, QTimer
from PySide6.QtGui import QFont
from ui.components.animated_button import AnimatedButton
from ui.components.drag_drop_line_edit import DragDropLineEdit
from core.downloader import DownloadTask

class SchedulerPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()
        self.setup_timer()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        lbl = QLabel("Scheduler (Planned Downloads)")
        lbl.setFont(QFont("Arial", 16, QFont.Bold))
        lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl)
        
        self.scheduler_table = QTableWidget()
        self.scheduler_table.setColumnCount(6)
        self.scheduler_table.setHorizontalHeaderLabels(["Datetime","URL","Type","Resolution","Subtitles","Status"])
        hh = self.scheduler_table.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(1, QHeaderView.Stretch)
        hh.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        layout.addWidget(self.scheduler_table)
        
        hl = QHBoxLayout()
        b_add = AnimatedButton("Add Scheduled Download")
        b_add.clicked.connect(self.add_scheduled_dialog)
        b_remove = AnimatedButton("Remove Selected")
        b_remove.clicked.connect(self.remove_scheduled_item)
        hl.addWidget(b_add)
        hl.addWidget(b_remove)
        layout.addLayout(hl)
        
        layout.addStretch()

    def setup_timer(self):
        self.scheduler_timer = QTimer()
        self.scheduler_timer.timeout.connect(self.check_scheduled_downloads)
        self.scheduler_timer.start(10000) 

    def add_scheduled_dialog(self):
        d = QDialog(self)
        d.setWindowTitle("Add Scheduled Download")
        d.setModal(True)
        ly = QVBoxLayout(d)
        
        frm = QFormLayout()
        dt_edit = QDateTimeEdit()
        dt_edit.setCalendarPopup(True)
        dt_edit.setDateTime(QDateTime.currentDateTime())
        url_edit = DragDropLineEdit("Enter link")
        c_audio = QCheckBox("Audio Only")
        c_subs = QCheckBox("Download Subtitles?")
        
        res_combo = QComboBox()
        res_combo.addItems(["144p","240p","360p","480p","720p","1080p","1440p","2160p","4320p"])
        res_combo.setCurrentText(self.parent.user_profile.get_default_resolution())
        
        frm.addRow("Datetime:", dt_edit)
        frm.addRow("URL:", url_edit)
        frm.addRow("Resolution:", res_combo)
        frm.addRow(c_audio)
        frm.addRow(c_subs)
        ly.addLayout(frm)
        
        b_ok = AnimatedButton("Add")
        b_cancel = AnimatedButton("Cancel")
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(b_ok)
        btn_layout.addWidget(b_cancel)
        ly.addLayout(btn_layout)
        
        def on_ok():
            dt_val = dt_edit.dateTime()
            url = url_edit.text().strip()
            if not url:
                self.parent.show_warning("Error", "No URL.")
                return
                
            row = self.scheduler_table.rowCount()
            self.scheduler_table.insertRow(row)
            self.scheduler_table.setItem(row, 0, QTableWidgetItem(dt_val.toString("yyyy-MM-dd HH:mm:ss")))
            self.scheduler_table.setItem(row, 1, QTableWidgetItem(url))
            
            download_type = "Audio" if c_audio.isChecked() else "Video"
            self.scheduler_table.setItem(row, 2, QTableWidgetItem(download_type))
            self.scheduler_table.setItem(row, 3, QTableWidgetItem(res_combo.currentText()))
            
            subs_text = "Yes" if c_subs.isChecked() else "No"
            self.scheduler_table.setItem(row, 4, QTableWidgetItem(subs_text))
            self.scheduler_table.setItem(row, 5, QTableWidgetItem("Scheduled"))
            
            d.accept()
            
        def on_cancel():
            d.reject()
            
        b_ok.clicked.connect(on_ok)
        b_cancel.clicked.connect(on_cancel)
        d.exec()

    def remove_scheduled_item(self):
        selected_rows = set()
        for item in self.scheduler_table.selectedItems():
            selected_rows.add(item.row())
        
        for row in sorted(selected_rows, reverse=True):
            self.scheduler_table.removeRow(row)

    def check_scheduled_downloads(self):
        now = QDateTime.currentDateTime()
        for row in range(self.scheduler_table.rowCount()):
            dt_str = self.scheduler_table.item(row, 0).text()
            scheduled_dt = QDateTime.fromString(dt_str, "yyyy-MM-dd HH:mm:ss")
            status_item = self.scheduler_table.item(row, 5)
            
            now_secs = now.toSecsSinceEpoch()
            scheduled_secs = scheduled_dt.toSecsSinceEpoch()
            
            if status_item and scheduled_secs <= now_secs and status_item.text() == "Scheduled":
                url = self.scheduler_table.item(row, 1).text()
                type_text = self.scheduler_table.item(row, 2).text().lower()
                resolution = self.scheduler_table.item(row, 3).text()
                subtitles = (self.scheduler_table.item(row, 4).text() == "Yes")
                
          
                
                task = DownloadTask(
                    url,
                    resolution,
                    self.parent.user_profile.get_download_path(),
                    self.parent.user_profile.get_proxy(),
                    audio_only=("audio" in type_text),
                    playlist=False,
                    subtitles=subtitles,
                    from_queue=True,
                    output_format="mp4",
                    audio_format=self.parent.user_profile.get_audio_format() if "audio" in type_text else None,
                    audio_quality=self.parent.user_profile.get_audio_quality() if "audio" in type_text else "320"
                )
                
                self.parent.run_task(task, row)
                self.scheduler_table.setItem(row, 5, QTableWidgetItem("Started")) 