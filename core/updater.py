import os
import sys
import json
import platform
import requests
import webbrowser
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QMessageBox, QLabel
from core.version import VERSION, get_version

class UpdateChecker(QObject):
    update_available = Signal(str, str)
    update_error = Signal(str)
    version_status = Signal(str, str)

    def __init__(self):
        super().__init__()
        self.current_version = VERSION
        # Temporarily disable update checking
        self.update_checking_enabled = False
        # Update URL should be configured by the deployment environment
        self.github_api_url = "https://api.github.com/repos/streamdownloader/YouTubePremiumDownloader/releases/latest"
        self.headers = {
            "User-Agent": f"YouTubeLabsDownloader/{VERSION} ({platform.system()} {platform.release()})",
            "Accept": "application/vnd.github.v6+json"
        }

    def check_for_updates(self):
        # Check if update checking is temporarily disabled
        if not self.update_checking_enabled:
            self.version_status.emit("Update checking disabled", "disabled")
            return
            
        try:
            response = requests.get(self.github_api_url, headers=self.headers, timeout=55)
            if response.status_code == 200:
                release_data = response.json()
                latest_version = release_data["tag_name"]
                html_url = release_data["html_url"]
                if self._compare_versions(latest_version, self.current_version) > 0:
                    self.update_available.emit(latest_version, html_url)
                    self.version_status.emit(f"Update to {latest_version} available", "update-available")
                else:
                    self.version_status.emit("Up to date", "up-to-date")
            else:
                self.update_error.emit(f"Failed to check for updates: {response.status_code}")
                self.version_status.emit("Update check failed", "error")
        except (requests.RequestException, requests.Timeout, ConnectionError, json.JSONDecodeError) as e:
            self.update_error.emit(f"Error checking for updates: {str(e)}")
            self.version_status.emit("Update check failed", "error")

    def _compare_versions(self, version1, version2):
        v1_parts = [int(x) for x in version1.lstrip('v').split('.')]
        v2_parts = [int(x) for x in version2.lstrip('v').split('.')]
        for i in range(max(len(v1_parts), len(v2_parts))):
            v1 = v1_parts[i] if i < len(v1_parts) else 0
            v2 = v2_parts[i] if i < len(v2_parts) else 0
            if v1 > v2:
                return 1
            elif v1 < v2:
                return -1
        return 0

class UpdateManager:
    def __init__(self, parent=None):
        self.parent = parent
        self.checker = UpdateChecker()
        self.checker.update_available.connect(self._handle_update_available)
        self.checker.update_error.connect(self._handle_update_error)
        self.checker.version_status.connect(self._handle_version_status)

    def check_for_updates(self):
        self.checker.check_for_updates()

    def _handle_update_available(self, version, html_url):
        # Allowlist GitHub release URLs to avoid opening arbitrary links
        if not (html_url.startswith("https://github.com/") and "/releases/" in html_url):
            self._handle_update_error("Unexpected update URL. Aborting open.")
            return
        reply = QMessageBox.question(
            self.parent,
            "Update Available",
            f"A new version ({version}) is available. Would you like to download it from GitHub?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            webbrowser.open(html_url)

    def _handle_update_error(self, error_message):
        QMessageBox.warning(self.parent, "Update Error", error_message)

    def _handle_version_status(self, status, status_type):
        if hasattr(self.parent, 'page_settings'):
            version_label = self.parent.page_settings.findChild(QLabel, "version_label")
            if version_label:
                version_label.setText(f"Version {get_version()} • {status}")
                if status_type == "up-to-date":
                    version_label.setStyleSheet("""
                        QLabel {
                            color: #4CAF50;
                            padding: 6px 16px;
                            border-radius: 15px;
                            background: rgba(76, 175, 80, 0.1);
                            font-size: 12pt;
                            font-weight: bold;
                            border: 1px solid rgba(76, 175, 80, 0.2);
                            margin: 5px;
                        }
                        QLabel:hover {
                            background: rgba(76, 175, 80, 0.15);
                            border: 1px solid rgba(76, 175, 80, 0.6);
                        }
                    """)
                elif status_type == "update-available":
                    version_label.setStyleSheet("""
                        QLabel {
                            color: #FFC557;
                            padding: 6px 16px;
                            border-radius: 15px;
                            background: rgba(255, 196, 7, 0.1);
                            font-size: 12pt;
                            font-weight: bold;
                            border: 1px solid rgba(255, 196, 7, 0.2);
                            margin: 5px;
                        }
                        QLabel:hover {
                            background: rgba(255, 196, 7, 0.15);
                            border: 1px solid rgba(255, 196, 7, 0.6);
                        }
                    """)
                elif status_type == "disabled":
                    version_label.setStyleSheet("""
                        QLabel {
                            color: #9E9E9E;
                            padding: 6px 16px;
                            border-radius: 15px;
                            background: rgba(158, 158, 158, 0.1);
                            font-size: 12pt;
                            font-weight: bold;
                            border: 1px solid rgba(158, 158, 158, 0.2);
                            margin: 5px;
                        }
                        QLabel:hover {
                            background: rgba(158, 158, 158, 0.15);
                            border: 1px solid rgba(158, 158, 158, 0.6);
                        }
                    """)
                else:  
                    version_label.setStyleSheet("""
                        QLabel {
                            color: #F44666;
                            padding: 6px 16px;
                            border-radius: 15px;
                            background: rgba(244, 67, 54, 0.1);
                            font-size: 12pt;
                            font-weight: bold;
                            border: 1px solid rgba(244, 67, 54, 0.2);
                            margin: 5px;
                        }
                        QLabel:hover {
                            background: rgba(244, 67, 54, 0.15);
                            border: 1px solid rgba(244, 67, 54, 0.6);
                        }
                    """) 