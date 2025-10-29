from PySide6.QtWidgets import QListWidgetItem
from PySide6.QtCore import Qt
from ui.components.search_popup import SearchPopup

class SearchSystem:
    search_map = {
        "proxy": (4, "You can find the proxy setting in the Settings page. Manage your connection speed or access by entering your proxy address or bandwidth limit under Settings > Proxy/BW. Don't forget to click 'Apply' after making changes."),
        "home": (0, "Home page: Overview of TokLabs video Downloader, quick start guide, and general information. See the main features and latest updates here."),
        "video": (1, "Video Page: Download videos in MP4 format. Paste your link and use 'Download Single Video' or 'Download Playlist Video' to save videos to your default folder."),
        "audio": (2, "Audio Page: Download audio only. Paste your link and use 'Download Single Audio' or 'Download Playlist Audio' to save audio files. Ideal for music and podcasts."),
        "settings": (4, "Settings: Configure all technical and appearance options here, including proxy, theme, download path, and resolution. Remember to click the relevant 'Apply' button after each change."),
        "resolution": (4, "Find the resolution setting in the Settings page. Choose your preferred video quality here."),
        "profile": (5, "Profile page: Manage your user information, profile picture, and social media links."),
        "queue": (6, "Queue page: Add multiple downloads to the queue and start them all at once."),
        "history": (3, "History page: View, search, and delete your past downloads."),
        "scheduler": (7, "Scheduler: Create scheduled downloads to start automatically at a specific date and time."),
        "download path": (4, "Set your download folder in the Settings page. You can change the default folder as needed."),
        "theme": (4, "Theme setting is in the Settings page. Switch between dark and light themes as you prefer."),
        "logs": (8, "Logs section: View all important events and errors within the app."),
        "download": (1, "Use the Video or Audio pages to start your downloads."),
        "audio": (2, "Download audio files using the Audio page."),
        "video": (1, "Download video files using the Video page."),
        "planned": (7, "Create scheduled downloads with the Scheduler page."),
        "issues": (8, "See the logs for any download issues and troubleshooting information."),
        "speed": (8, "Check Settings and logs for information about download speed and optimization."),
        "youtubego.org": (0, "Visit youtubego.org for more information and updates.")
    }

    def __init__(self, main_window):
        self.main_window = main_window
        self.search_edit = main_window.top_bar_layout.search_edit
        self.search_btn = main_window.top_bar_layout.search_btn
        self.side_menu = main_window.side_menu
        self.popup = SearchPopup(main_window)
        self.setup_connections()

    def setup_connections(self):
        self.search_btn.clicked.connect(self.top_search_clicked)
        self.search_edit.returnPressed.connect(self.top_search_clicked)
        self.popup.list_widget.itemClicked.connect(self.search_item_clicked)
        self.search_edit.textEdited.connect(self.hide_popup)
        self.search_edit.editingFinished.connect(self.hide_popup)

    def top_search_clicked(self):
        query = self.search_edit.text().lower().strip()
        self.popup.clear()
        if not query:
            self.popup.hide()
            return
        matches_found = False
        for k, v in self.search_map.items():
            if k.startswith(query) or query in k:
                item = QListWidgetItem(f"{k.capitalize()}: {v[1]}")
                item.setData(Qt.UserRole, v[0])
                self.popup.addItem(item)
                matches_found = True
        if matches_found:
            self.show_popup()
        else:
            self.popup.hide()

    def show_popup(self):
        edit = self.search_edit
        global_pos = edit.mapToGlobal(edit.rect().bottomLeft())
        width = edit.width() + self.search_btn.width() + 10
        self.popup.show_at(global_pos, width)

    def hide_popup(self, *args):
        self.popup.hide()

    def search_item_clicked(self, item):
        page_index = item.data(Qt.UserRole)
        self.side_menu.setCurrentRow(page_index)
        self.popup.hide() 