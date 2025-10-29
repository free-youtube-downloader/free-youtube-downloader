from PySide6.QtCore import QObject, Signal
from core.ffmpeg_installer import install_ffmpeg


class FFmpegInstallWorker(QObject):
    finished = Signal(bool, str, str)  # success, message_or_path, bin_path

    def run(self):
        ok, result = install_ffmpeg()
        if ok:
            self.finished.emit(True, result, result)
        else:
            self.finished.emit(False, result, "")


