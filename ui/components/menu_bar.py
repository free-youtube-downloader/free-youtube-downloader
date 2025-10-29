from PySide6.QtWidgets import QMenuBar, QMessageBox, QDialog, QVBoxLayout, QTextBrowser
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt
import requests
import webbrowser
import html
from ui.dialogs.batch_add_dialog import BatchAddDialog

class LicenseDialog(QDialog):
    def __init__(self, title, content, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumSize(600, 400)
        
        layout = QVBoxLayout(self)
        text_browser = QTextBrowser()
        text_browser.setOpenExternalLinks(True)
        text_browser.setHtml(content)
        layout.addWidget(text_browser)

class MenuBarManager:
    def __init__(self, main_window):
        self.main_window = main_window
        self.menu_bar = None
        self.init_menu_bar()

    def init_menu_bar(self):
        self.menu_bar = self.main_window.menuBar()
        
        # File Menu
        file_menu = self.menu_bar.addMenu("File")
        
        exit_action = QAction("Exit", self.main_window)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.main_window.close)
        
        reset_profile_action = QAction("Reset Profile", self.main_window)
        reset_profile_action.triggered.connect(self.main_window.reset_profile)
        
        export_profile_action = QAction("Export Profile", self.main_window)
        export_profile_action.triggered.connect(self.main_window.profile_manager.export_profile)
        
        import_profile_action = QAction("Import Profile", self.main_window)
        import_profile_action.triggered.connect(self.main_window.profile_manager.import_profile)
        
        file_menu.addAction(exit_action)
        file_menu.addAction(reset_profile_action)
        file_menu.addAction(export_profile_action)
        file_menu.addAction(import_profile_action)
        
        # Batch add to queue
        batch_add_action = QAction("Batch Add to Queue", self.main_window)
        batch_add_action.setShortcut("Ctrl+B")
        batch_add_action.triggered.connect(self.open_batch_add_dialog)
        file_menu.addAction(batch_add_action)
        
        
        help_menu = self.menu_bar.addMenu("Help")
        
        about_action = QAction("About", self.main_window)
        about_action.triggered.connect(self.show_about_info)
        
        repository_action = QAction("Project Repository", self.main_window)
        repository_action.triggered.connect(self.show_repository_info)
        
        report_bug_action = QAction("Report Bug", self.main_window)
        report_bug_action.triggered.connect(self.open_bug_report)
        
        support_dev_action = QAction("Support Development", self.main_window)
        support_dev_action.triggered.connect(self.open_support_page)
        
        # Licenses submenu
        licenses_menu = help_menu.addMenu("Licenses")
        
        # TokLabs video Downloader License
        toklabslicense = QAction("TokLabs video Downloader License", self.main_window)
        toklabslicense.triggered.connect(self.show_youtubego_license)
        licenses_menu.addAction(toklabslicense)
        
        # Qt/PySide6 License
        qt_license = QAction("Qt/PySide6 License", self.main_window)
        qt_license.triggered.connect(self.show_qt_license)
        licenses_menu.addAction(qt_license)
        
        # FFmpeg License
        ffmpeg_license = QAction("FFmpeg License", self.main_window)
        ffmpeg_license.triggered.connect(self.show_ffmpeg_license)
        licenses_menu.addAction(ffmpeg_license)
        
        help_menu.addAction(about_action)
        help_menu.addAction(repository_action)
        help_menu.addAction(report_bug_action)
        help_menu.addAction(support_dev_action)

    def open_batch_add_dialog(self):
        dlg = BatchAddDialog(self.main_window)
        dlg.exec()

    def show_about_info(self):
        from core.version import get_version
        QMessageBox.information(
            self.main_window, 
            "About", 
            f"TokLabs Video Downloader {get_version()}\n\n"
            "A powerful, cross-platform video downloader application.\n\n"
            "Licensed under GNU GPL v3"
        )

    def show_repository_info(self):
        QMessageBox.information(
            self.main_window, 
            "Repository", 
            "Visit the project repository for source code, documentation, and support."
        )

    def open_bug_report(self):
        QMessageBox.information(
            self.main_window, 
            "Bug Report", 
            "Please report bugs through the project repository's issue tracker."
        )

    def open_support_page(self):
        QMessageBox.information(
            self.main_window, 
            "Support", 
            "Thank you for considering supporting this project!\n\n"
            "You can contribute by:\n"
            "• Reporting bugs and issues\n"
            "• Contributing code improvements\n"
            "• Sharing the project with others"
        )

    def show_youtubego_license(self):
        # Try to read local license file
        try:
            with open("LICENSE", "r", encoding="utf-8") as f:
                license_text = f.read()
        except FileNotFoundError:
            license_text = "GNU General Public License v3.0\n\nPlease see the LICENSE file in the project repository."
        
        # Escape to avoid rendering unexpected HTML
        safe_license_html = f"<pre>{html.escape(license_text)}</pre>"
        dialog = LicenseDialog("TokLabs Video Downloader License (GPL v3)", safe_license_html, self.main_window)
        dialog.exec()

    def show_qt_license(self):
        qt_license_url = "https://www.qt.io/licensing/"
        try:
            response = requests.get(qt_license_url, timeout=10)
            content = response.text
        except (requests.RequestException, requests.Timeout, ConnectionError) as e:
            print(f"Warning: Could not fetch Qt license: {e}")
            content = """
            <h3>Qt/PySide6 License Information</h3>
            <p>Qt and PySide6 are licensed under the LGPL v3 license.</p>
            <p>For more information, visit: <a href="https://www.qt.io/licensing/">Qt Licensing</a></p>
            """
        
        # Display as-is from official site in a browser-like view; still escape as a defense-in-depth if needed
        safe_content = content if content.strip().startswith("<") else f"<pre>{html.escape(content)}</pre>"
        dialog = LicenseDialog("Qt/PySide6 License", safe_content, self.main_window)
        dialog.exec()

    def show_ffmpeg_license(self):
        ffmpeg_license_url = "https://www.ffmpeg.org/legal.html"
        try:
            response = requests.get(ffmpeg_license_url, timeout=10)
            content = response.text
        except (requests.RequestException, requests.Timeout, ConnectionError) as e:
            print(f"Warning: Could not fetch FFmpeg license: {e}")
            content = """
            <h3>FFmpeg License Information</h3>
            <p>FFmpeg is licensed under the LGPL v2.1+ and GPL v2+.</p>
            <p>For more information, visit: <a href="https://www.ffmpeg.org/legal.html">FFmpeg Legal</a></p>
            """
        
        safe_content = content if content.strip().startswith("<") else f"<pre>{html.escape(content)}</pre>"
        dialog = LicenseDialog("FFmpeg License", safe_content, self.main_window)
        dialog.exec()