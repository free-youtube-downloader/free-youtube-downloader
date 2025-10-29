import pytest
import os
import json
from PySide6.QtWidgets import QApplication
from core.profile import UserProfile
from core.utils import get_data_dir

@pytest.fixture
def profile(temp_data_dir):
    
    profile = UserProfile()
    profile.data = {
        "name": "Test User",
        "profile_picture": "",
        "download_path": os.path.join(temp_data_dir, "downloads"),
        "default_resolution": "720p",
        "proxy": "",
        "theme": "Dark",
        "history_enabled": True
    }
    return profile

def test_profile_initialization(profile):
   
    assert profile.data["name"] == "Test User"
    assert profile.data["theme"] == "Dark"
    assert profile.data["history_enabled"] == True
    assert "downloads" in profile.data["download_path"]

def test_profile_setters(profile):
    
    test_pic_dir = os.path.join(os.path.dirname(profile.profile_path), "images")
    os.makedirs(test_pic_dir, exist_ok=True)
    test_pic = os.path.join(test_pic_dir, "test.png")
    with open(test_pic, "w") as f:
        f.write("test")
    
     
    profile.set_profile("New User", test_pic, "/new/path")
    assert profile.data["name"] == "New User"
    assert "profile_test.png" in profile.data["profile_picture"]
    assert profile.data["download_path"] == "/new/path"
    
    
    profile.set_theme("Light")
    assert profile.data["theme"] == "Light"
    
    
    profile.set_default_resolution("1080p")
    assert profile.data["default_resolution"] == "1080p"
    
    
    profile.set_proxy("http://proxy:8080")
    assert profile.data["proxy"] == "http://proxy:8080"
    
    
    profile.set_history_enabled(False)
    assert profile.data["history_enabled"] == False

def test_profile_getters(profile):
   
    assert profile.get_theme() == "Dark"
    assert profile.get_default_resolution() == "720p"
    assert profile.get_proxy() == ""
    assert profile.get_download_path() == os.path.join(profile.data["download_path"])
    assert profile.is_history_enabled() == True

def test_profile_save_load(profile, temp_data_dir):
   
    test_pic_dir = os.path.join(os.path.dirname(profile.profile_path), "images")
    os.makedirs(test_pic_dir, exist_ok=True)
    test_pic = os.path.join(test_pic_dir, "test.png")
    with open(test_pic, "w") as f:
        f.write("test")
    
    
    profile.set_profile("Save Test", test_pic, "/test/path")
    profile.set_theme("Light")
    
   
    profile.save_profile()
    
    new_profile = UserProfile()
    
    
    assert new_profile.data["name"] == "Save Test"
    assert "profile_test.png" in new_profile.data["profile_picture"]
    assert new_profile.data["theme"] == "Light"

def test_profile_validation(profile):
    
    assert profile.is_profile_complete() == True
    
    
    profile.data["name"] = ""
    assert profile.is_profile_complete() == False

    profile.data["name"] = "Test User"
    profile.data["download_path"] = ""
    assert profile.is_profile_complete() == True  

def test_profile_default_values():
    
    profile = UserProfile()
    
    assert profile.data["theme"] in ["Dark", "Light"]
    assert profile.data["default_resolution"] in ["144p", "240p", "360p", "480p", "720p", "1080p"]
    assert isinstance(profile.data["history_enabled"], bool)
    assert isinstance(profile.data["proxy"], str)

def test_profile_download_path_creation(temp_data_dir):
    
    profile = UserProfile()
    test_path = os.path.join(temp_data_dir, "new_downloads")
    
    
    os.makedirs(test_path, exist_ok=True)
    
    profile.set_profile("Test", "", test_path)
    assert os.path.exists(test_path)

def test_profile_picture_handling(profile, temp_data_dir):
    
    test_pic_dir = os.path.join(os.path.dirname(profile.profile_path), "images")
    os.makedirs(test_pic_dir, exist_ok=True)
    test_pic = os.path.join(test_pic_dir, "test.png")
    with open(test_pic, "w") as f:
        f.write("test")
    
   
    profile.set_profile("Test", test_pic, profile.data["download_path"])
    assert "profile_test.png" in profile.data["profile_picture"]
    assert os.path.exists(profile.data["profile_picture"])
