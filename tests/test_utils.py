import pytest
import os
import tempfile
from PIL import Image
import numpy as np
from core.utils import (
    get_data_dir,
    set_circular_pixmap,
    format_speed,
    format_time
)
from PySide6.QtWidgets import QWidget, QLabel
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

@pytest.fixture
def test_widget(qapp):
    return QWidget()

@pytest.fixture
def test_label(qapp):
    return QLabel()

def test_get_data_dir(temp_data_dir, monkeypatch):
    monkeypatch.setattr('sys.platform', 'win32')
    monkeypatch.setattr('os.environ', {'APPDATA': os.path.dirname(temp_data_dir)})
    
    expected_path = os.path.join(os.path.dirname(temp_data_dir), 'TubeTokDownloader')
    
    data_dir = get_data_dir()
    
    assert os.path.exists(data_dir)
    assert os.path.isdir(data_dir)
    assert data_dir == expected_path

def test_set_circular_pixmap(test_label):
    pixmap = QPixmap(100, 100)
    pixmap.fill(Qt.red)
    
    set_circular_pixmap(test_label, pixmap)
    
    result_pixmap = test_label.pixmap()
    assert result_pixmap is not None
    assert result_pixmap.width() == 50
    assert result_pixmap.height() == 50

def test_format_speed():
    assert format_speed(500) == "500 B/s"
    
    assert format_speed(1500) == "1.50 KB/s"
    
    assert format_speed(1500000) == "1.50 MB/s"
    
    assert format_speed(1500000000) == "1500.00 MB/s"

def test_format_time():
    assert format_time(45) == "45s"
    
    assert format_time(125) == "2m 5s"
    
    assert format_time(3665) == "1h 1m 5s"
