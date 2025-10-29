from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QTextEdit,
    QPushButton, QComboBox, QCheckBox, QLabel, QFileDialog, QMessageBox, QTableWidgetItem
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from core.downloader import DownloadTask


class BatchPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("Batch Downloader")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        form = QFormLayout()
        self.urls_edit = QTextEdit()
        self.urls_edit.setPlaceholderText("Paste one URL per line, or use 'Import .txt' to load a file...")
        self.urls_edit.setAcceptRichText(False)

        self.audio_checkbox = QCheckBox("Audio Only")
        self.playlist_checkbox = QCheckBox("Playlist")
        self.subtitles_checkbox = QCheckBox("Download Subtitles")

        self.format_combo = QComboBox()
        self.format_combo.addItems(["mp4", "mkv", "webm", "flv", "avi"])

        form.addRow("URLs:", self.urls_edit)
        form.addRow(self.audio_checkbox)
        form.addRow(self.playlist_checkbox)
        form.addRow("Video Format:", self.format_combo)
        form.addRow(self.subtitles_checkbox)
        layout.addLayout(form)

        btn_row = QHBoxLayout()
        self.btn_import = QPushButton("Import .txt")
        self.btn_add = QPushButton("Add and Start")
        self.btn_clear = QPushButton("Clear")
        btn_row.addWidget(self.btn_import)
        btn_row.addStretch()
        btn_row.addWidget(self.btn_clear)
        btn_row.addWidget(self.btn_add)
        layout.addLayout(btn_row)

        self.btn_import.clicked.connect(self.on_import)
        self.btn_add.clicked.connect(self.on_add)
        self.btn_clear.clicked.connect(lambda: self.urls_edit.clear())

    def on_import(self):
        file_path, _ = QFileDialog.getOpenFileName(self.parent, "Import URLs from file", "", "Text Files (*.txt);;All Files (*.*)")
        if not file_path:
            return
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                self.urls_edit.setPlainText(f.read())
        except Exception as e:
            QMessageBox.warning(self, "Import Error", f"Could not read file: {e}")

    def _collect_urls(self):
        raw = self.urls_edit.toPlainText().splitlines()
        urls = []
        for line in raw:
            url = line.strip()
            if not url:
                continue
            if url.startswith("http://") or url.startswith("https://"):
                urls.append(url)
            else:
                if url.startswith("www.") or "." in url:
                    urls.append("https://" + url)
        seen = set()
        unique_urls = []
        for u in urls:
            if u not in seen:
                seen.add(u)
                unique_urls.append(u)
        return unique_urls

    def on_add(self):
        urls = self._collect_urls()
        if not urls:
            QMessageBox.warning(self, "Error", "No valid URLs found.")
            return

        if not hasattr(self.parent, 'page_queue') or not hasattr(self.parent.page_queue, 'queue_table'):
            QMessageBox.warning(self, "Error", "Queue page not initialized properly.")
            return

        audio_only = self.audio_checkbox.isChecked()
        playlist = self.playlist_checkbox.isChecked()
        subtitles = self.subtitles_checkbox.isChecked()
        output_format = self.parent.user_profile.get_audio_format() if audio_only else self.format_combo.currentText()

        for url in urls:
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


