import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMessageBox, QDialog
from ui.main_window import MainWindow
from core.version import get_version

@pytest.fixture
def main_window(qapp, temp_data_dir, mock_ffmpeg, monkeypatch):
    
    def mock_exec(self):
        return QDialog.Accepted
    monkeypatch.setattr('ui.dialogs.profile_dialog.ProfileDialog.exec_', mock_exec)
    
    window = MainWindow(ffmpeg_found=True, ffmpeg_path="dummy")
    yield window
    window.close()

def test_main_window_init(main_window):
    assert main_window.windowTitle() == f"TubeTok Downloader {get_version()}"
    assert main_window.isVisible() == False
    # One extra page added for Batch downloader
    assert main_window.main_stack.count() == 9  

def test_side_menu_navigation(main_window, qtbot):
    main_window.show()
    initial_index = main_window.main_stack.currentIndex()
    
    main_window.side_menu.setCurrentRow(2)
    qtbot.wait(550)
    assert main_window.main_stack.currentIndex() == 2
    
    main_window.side_menu.setCurrentRow(4)
    qtbot.wait(550)
    assert main_window.main_stack.currentIndex() == 4

def test_profile_dialog(main_window, qtbot, monkeypatch):
    def mock_exec(self):
        return QDialog.Accepted
    
    monkeypatch.setattr('ui.dialogs.profile_dialog.ProfileDialog.exec_', mock_exec)
    main_window.prompt_user_profile()
    assert main_window.user_profile.data["name"] is not None

def test_theme_switching(main_window, qtbot):
    initial_theme = main_window.theme_manager.current_theme
    new_theme = "Light" if initial_theme == "Dark" else "Dark"
    main_window.page_settings.theme_combo.setCurrentText(new_theme)
    main_window.theme_manager.change_theme(new_theme)
    qtbot.wait(550)
    assert main_window.theme_manager.current_theme != initial_theme
    assert main_window.user_profile.get_theme() == main_window.theme_manager.current_theme

def test_tray_icon(main_window):
    assert main_window.tray_manager.tray_icon is not None
    assert main_window.tray_manager.tray_icon.isVisible()
    
    tray_menu = main_window.tray_manager.tray_icon.contextMenu()
    actions = [act.text() for act in tray_menu.actions()]
    assert "Restore" in actions
    assert "Quit" in actions

def test_search_functionality(main_window, qtbot):
    main_window.show()
    main_window.top_search_edit.setText("settings")
    qtbot.mouseClick(main_window.search_btn, Qt.LeftButton)
    qtbot.wait(550)
    assert main_window.search_system.popup.isVisible()
    assert main_window.search_system.popup.list_widget.count() > 0
    main_window.top_search_edit.clear()
    qtbot.mouseClick(main_window.search_btn, Qt.LeftButton)
    qtbot.wait(550)
    assert not main_window.search_system.popup.isVisible()

def test_concurrent_downloads_setting(main_window):
    initial_value = main_window.max_concurrent_downloads
    main_window.page_settings.concurrent_combo.setCurrentText("5")
    main_window.profile_manager.set_max_concurrent_downloads(0)
    assert main_window.max_concurrent_downloads == 5
    main_window.page_settings.concurrent_combo.setCurrentText("6")
    main_window.profile_manager.set_max_concurrent_downloads(0)
    assert main_window.max_concurrent_downloads == 6

def test_theme_change(main_window):
    initial_theme = main_window.theme_manager.current_theme
    main_window.theme_manager.change_theme("Dark")
    assert main_window.theme_manager.current_theme != initial_theme
    assert main_window.user_profile.get_theme() == main_window.theme_manager.current_theme
    main_window.theme_manager.change_theme(initial_theme) 