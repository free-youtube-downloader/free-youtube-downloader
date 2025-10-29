from PySide6.QtCore import QThreadPool, Signal, QObject
import pytest
from core.downloader import DownloadTask, DownloadQueueWorker
import os
import tempfile
from core.utils import get_data_dir

@pytest.fixture
def download_task(temp_data_dir):
    return DownloadTask(
        url="https://www.youtube.com/watch?v=test",
        resolution="720p",
        folder=temp_data_dir,
        proxy="",
        audio_only=False,
        playlist=False,
        subtitles=False,
        output_format="mp4",
        from_queue=False
    )

@pytest.fixture
def thread_pool():
    return QThreadPool()

def test_download_task_creation(download_task):
    assert download_task.url == "https://www.youtube.com/watch?v=test"
    assert download_task.resolution == "720p"
    assert download_task.audio_only == False
    assert download_task.playlist == False
    assert download_task.output_format == "mp4"

def test_download_task_audio_only(temp_data_dir):
    task = DownloadTask(
        url="https://www.youtube.com/watch?v=test",
        resolution="720p",
        folder=temp_data_dir,
        proxy="",
        audio_only=True,
        playlist=False,
        subtitles=False,
        output_format="mp3",
        from_queue=False
    )
    assert task.audio_only == True
    assert task.output_format == "mp3"

class SignalCatcher(QObject):
    progress_signal = Signal(int, float)
    status_signal = Signal(int, str)
    log_signal = Signal(str)
    info_signal = Signal(int, str, str)

    def __init__(self):
        super().__init__()
        self.progress_values = []
        self.status_messages = []
        self.log_messages = []
        self.info_data = []

        self.progress_signal.connect(self.on_progress)
        self.status_signal.connect(self.on_status)
        self.log_signal.connect(self.on_log)
        self.info_signal.connect(self.on_info)

    def on_progress(self, row, progress):
        self.progress_values.append(progress)

    def on_status(self, row, status):
        self.status_messages.append(status)

    def on_log(self, message):
        self.log_messages.append(message)

    def on_info(self, row, title, channel):
        self.info_data.append((title, channel))

def test_download_queue_worker(download_task, thread_pool, qtbot):
    progress_values = []
    status_messages = []
    log_messages = []
    info_data = []

    def on_progress(row, progress):
        progress_values.append(progress)

    def on_status(row, status):
        status_messages.append(status)

    def on_log(message):
        log_messages.append(message)

    def on_info(row, title, channel):
        info_data.append((title, channel))

    worker = DownloadQueueWorker(
        task=download_task,
        row=0,
        progress_signal=on_progress,
        status_signal=on_status,
        log_signal=on_log,
        info_signal=on_info
    )

    on_progress(0, 50.0)
    on_status(0, "Downloading...")
    on_log("Download started")
    on_info(0, "Test Video", "Test Channel")

    assert len(progress_values) == 1
    assert progress_values[0] == 50.0
    assert len(status_messages) == 1
    assert status_messages[0] == "Downloading..."
    assert len(log_messages) == 1
    assert log_messages[0] == "Download started"
    assert len(info_data) == 1
    assert info_data[0] == ("Test Video", "Test Channel")

def test_download_task_with_proxy(temp_data_dir):
    proxy = "http://proxy.example.com:8080"
    task = DownloadTask(
        url="https://www.youtube.com/watch?v=test",
        resolution="720p",
        folder=temp_data_dir,
        proxy=proxy,
        audio_only=False,
        playlist=False,
        subtitles=False,
        output_format="mp4",
        from_queue=False
    )
    assert task.proxy == proxy

def test_download_task_with_subtitles(temp_data_dir):
    task = DownloadTask(
        url="https://www.youtube.com/watch?v=test",
        resolution="720p",
        folder=temp_data_dir,
        proxy="",
        audio_only=False,
        playlist=False,
        subtitles=True,
        output_format="mp4",
        from_queue=False
    )
    assert task.subtitles == True

def test_download_task_playlist(temp_data_dir):
    task = DownloadTask(
        url="https://www.youtube.com/playlist?list=test",
        resolution="720p",
        folder=temp_data_dir,
        proxy="",
        audio_only=False,
        playlist=True,
        subtitles=False,
        output_format="mp4",
        from_queue=False
    )
    assert task.playlist == True
