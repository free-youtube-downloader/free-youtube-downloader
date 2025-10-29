import os
import shutil
import json
import zipfile
from PySide6.QtWidgets import QFileDialog, QMessageBox
from PySide6.QtCore import Qt
from core.utils import get_data_dir

class ProfileManager:
    def __init__(self, main_window):
        self.main_window = main_window
        self.user_profile = main_window.user_profile

    def export_profile(self):
        try:
            temp_dir = os.path.join(get_data_dir(), "temp_export")
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            os.makedirs(temp_dir)

            profile_file = os.path.join(temp_dir, "user_profile.json")
            with open(profile_file, "w") as f:
                json.dump(self.user_profile.data, f, indent=4)

            history_file = os.path.join(temp_dir, "history.json")
            from core.history import export_history
            export_history(history_file)

            if self.user_profile.data["profile_picture"]:
                try:
                    if os.path.exists(self.user_profile.data["profile_picture"]):
                        shutil.copy2(self.user_profile.data["profile_picture"], os.path.join(temp_dir, "profile_picture.png"))
                except Exception as e:
                    QMessageBox.warning(self.main_window, "Profile Picture", f"Error copying profile picture: {e}")

            file_path, _ = QFileDialog.getSaveFileName(
                self.main_window,
                "Export Profile",
                os.path.join(os.path.expanduser("~"), "youtubego_profile.zip"),
                "Zip Files (*.zip)"
            )

            if file_path:
                shutil.make_archive(file_path.replace(".zip", ""), 'zip', temp_dir)
                QMessageBox.information(self.main_window, "Success", "Profile exported successfully!")
            else:
                QMessageBox.warning(self.main_window, "Cancelled", "Profile export cancelled.")

            shutil.rmtree(temp_dir)

        except Exception as e:
            QMessageBox.critical(self.main_window, "Error", f"Failed to export profile: {str(e)}")
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)

    def import_profile(self):
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self.main_window,
                "Import Profile",
                os.path.expanduser("~"),
                "Zip Files (*.zip)"
            )
            if not file_path:
                return
            temp_dir = os.path.join(get_data_dir(), "temp_import")
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            os.makedirs(temp_dir)
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                # Safe extraction to prevent Zip Slip
                abs_dest = os.path.abspath(temp_dir)
                try:
                    for member in zip_ref.namelist():
                        target_path = os.path.abspath(os.path.join(abs_dest, member))
                        if not (target_path + os.sep).startswith(abs_dest + os.sep) and target_path != abs_dest:
                            raise ValueError(f"Insecure path in zip entry: {member}")
                    for info in zip_ref.infolist():
                        target = os.path.abspath(os.path.join(abs_dest, info.filename))
                        if info.is_dir():
                            os.makedirs(target, exist_ok=True)
                        else:
                            os.makedirs(os.path.dirname(target), exist_ok=True)
                            with zip_ref.open(info, 'r') as src, open(target, 'wb') as dst:
                                shutil.copyfileobj(src, dst)
                except Exception as ex:
                    shutil.rmtree(temp_dir, ignore_errors=True)
                    QMessageBox.critical(self.main_window, "Import Error", f"Invalid or unsafe archive structure: {ex}")
                    return

            profile_file = os.path.join(temp_dir, "user_profile.json")
            if os.path.exists(profile_file):
                with open(profile_file, "r") as f:
                    profile_data = json.load(f)
                self.user_profile.data = profile_data
                self.user_profile.save_profile()

            history_file = os.path.join(temp_dir, "history.json")
            if os.path.exists(history_file):
                data_dir = get_data_dir()
                shutil.copy2(history_file, os.path.join(data_dir, "history.json"))

            pic_file = os.path.join(temp_dir, "profile_picture.png")
            if os.path.exists(pic_file):
                dest_pic = os.path.join(get_data_dir(), "profile_picture.png")
                os.makedirs(os.path.dirname(dest_pic), exist_ok=True)
                shutil.copy2(pic_file, dest_pic)
                self.user_profile.data["profile_picture"] = dest_pic
                self.user_profile.save_profile()

            shutil.rmtree(temp_dir)

            try:
                if hasattr(self.main_window.page_settings, 'res_combo'):
                    self.main_window.page_settings.res_combo.setCurrentText(self.user_profile.get_default_resolution())
                if hasattr(self.main_window.page_settings, 'proxy_edit'):
                    self.main_window.page_settings.proxy_edit.setText(self.user_profile.get_proxy())
                self.main_window.update_profile_ui()
                if hasattr(self.main_window, 'page_history') and hasattr(self.main_window.page_history, 'history_table'):
                    self.main_window.initialize_history()
                self.main_window.theme_manager.apply_current_theme()
            except Exception as ui_error:
                QMessageBox.warning(self.main_window, "Warning", f"Some UI elements couldn't be updated: {str(ui_error)}\nPlease restart the application.")

            QMessageBox.information(self.main_window, "Success", "Profile imported successfully! Please restart the app for all changes to take effect.")
        except Exception as e:
            QMessageBox.critical(self.main_window, "Error", f"Failed to import profile: {str(e)}")
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)

    def reset_profile(self):
        if os.path.exists(self.user_profile.profile_path):
            os.remove(self.user_profile.profile_path)
        
        from core.history import HISTORY_FILE
        if os.path.exists(HISTORY_FILE):
            os.remove(HISTORY_FILE)
            
        if self.user_profile.data.get("profile_picture") and os.path.exists(self.user_profile.data["profile_picture"]):
            try:
                os.remove(self.user_profile.data["profile_picture"])
            except OSError as e:
                self.main_window.append_log(f"Warning: Could not remove profile picture: {e}")
        
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.information(self.main_window, "Reset Profile", "Profile data, history, and profile picture removed. Please restart.")
        self.main_window.append_log("Profile, history, and profile picture have been reset.")

    def update_profile_ui(self):
        from PySide6.QtGui import QPixmap
        if self.user_profile.data["profile_picture"]:
            pixmap = QPixmap(self.user_profile.data["profile_picture"]).scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.main_window.profile_pic_label.setPixmap(pixmap)
        else:
            self.main_window.profile_pic_label.setPixmap(QPixmap())
        self.main_window.profile_name_label.setText(self.user_profile.data["name"] if self.user_profile.data["name"] else "User")

    def select_download_path(self):
        from PySide6.QtWidgets import QFileDialog, QMessageBox
        folder = QFileDialog.getExistingDirectory(self.main_window, "Select Download Folder")
        if folder:
            self.user_profile.set_profile(self.user_profile.data["name"], self.user_profile.data["profile_picture"], folder)
            self.main_window.page_settings.download_path_edit.setText(folder)
            self.main_window.append_log(f"Download path changed to {folder}")

    def set_max_concurrent_downloads(self, idx):
        val = self.main_window.page_settings.concurrent_combo.currentText()
        self.main_window.max_concurrent_downloads = int(val)
        self.main_window.append_log(f"Max concurrent downloads set to {val}")
        try:
            self.main_window.thread_pool.setMaxThreadCount(self.main_window.max_concurrent_downloads)
        except Exception:
            pass

    def apply_resolution(self):
        from PySide6.QtWidgets import QMessageBox
        sr = self.main_window.page_settings.res_combo.currentText()
        self.user_profile.set_default_resolution(sr)
        prx = self.main_window.page_settings.proxy_edit.text().strip()
        self.user_profile.set_proxy(prx)
        self.main_window.append_log(f"Resolution set: {sr}, Proxy: {prx}")
        QMessageBox.information(self.main_window, "Settings", f"Resolution: {sr}\nProxy: {prx}") 