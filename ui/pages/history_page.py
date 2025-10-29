from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QTableWidget, QTableWidgetItem, QHeaderView, 
                            QCheckBox, QLineEdit)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from ui.components.animated_button import AnimatedButton
from core.history import delete_selected_history, delete_all_history, search_history, load_history_initial

class HistoryPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Title
        lbl = QLabel("Download History")
        lbl.setFont(QFont("Arial", 16, QFont.Bold))
        lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl)
        
        # History table
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(3)
        self.history_table.setHorizontalHeaderLabels(["Title", "Channel", "URL"])
        hh = self.history_table.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.Stretch)  # Title column stretches
        hh.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Channel column fits content
        hh.setSectionResizeMode(2, QHeaderView.Stretch)  # URL column stretches
        layout.addWidget(self.history_table)
        
        # Buttons
        hl = QHBoxLayout()
        del_sel_btn = AnimatedButton("Delete Selected")
        del_sel_btn.clicked.connect(lambda: delete_selected_history(self.history_table, self.parent.append_log))
        del_all_btn = AnimatedButton("Delete All")
        del_all_btn.clicked.connect(lambda: delete_all_history(self.history_table, self.confirm_delete_all, self.parent.append_log))
        hl.addWidget(del_sel_btn)
        hl.addWidget(del_all_btn)
        layout.addLayout(hl)
        
        # Search
        s_hl = QHBoxLayout()
        self.search_hist_edit = QLineEdit()
        self.search_hist_edit.setPlaceholderText("Search in history (title, channel, or URL)...")
        s_btn = AnimatedButton("Search")
        s_btn.clicked.connect(self.search_history_in_table)
        s_hl.addWidget(self.search_hist_edit)
        s_hl.addWidget(s_btn)
        layout.addLayout(s_hl)
        
        layout.addStretch()
        
        # Load history
        load_history_initial(self.history_table)

    def showEvent(self, event):
        
        super().showEvent(event)
        self.history_table.setRowCount(0)  
        load_history_initial(self.history_table)  
        if self.parent:
            self.parent.append_log("History refreshed")

    def search_history_in_table(self):
        txt = self.search_hist_edit.text().lower().strip()
        search_history(self.history_table, txt)

    def confirm_delete_all(self):
        return self.parent.show_question("Delete All", "Are you sure?") 