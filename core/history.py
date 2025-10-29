import os
import json
from PySide6.QtWidgets import QTableWidgetItem
from core.config import config_manager

DATA_DIR = config_manager.config.paths.get_data_dir()
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)
HISTORY_FILE = os.path.join(DATA_DIR, "history.json")

def load_history_initial(table):
    if not os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, indent=4)
    else:
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                history = json.load(f)
                for entry in history:
                    row = table.rowCount()
                    table.insertRow(row)
                    # Check if entry has new format with title and channel
                    if "title" in entry and "channel" in entry:
                        title = entry.get("title", "Unknown Title")
                        channel = entry.get("channel", "Unknown Channel")
                        url = entry.get("url", "")
                        table.setItem(row, 0, QTableWidgetItem(title))
                        table.setItem(row, 1, QTableWidgetItem(channel))
                        table.setItem(row, 2, QTableWidgetItem(url))
                    else:
                        # Legacy format - just URL
                        url = entry.get("url", "")
                        table.setItem(row, 0, QTableWidgetItem("Unknown Title"))
                        table.setItem(row, 1, QTableWidgetItem("Unknown Channel"))
                        table.setItem(row, 2, QTableWidgetItem(url))
        except Exception as e:
            print(f"Error loading history: {e}")

def save_history(table):
    history = []
    for r in range(table.rowCount()):
        title_item = table.item(r, 0)
        channel_item = table.item(r, 1)
        url_item = table.item(r, 2)
        
        title = title_item.text() if title_item else "Unknown Title"
        channel = channel_item.text() if channel_item else "Unknown Channel"
        url = url_item.text() if url_item else ""
        
        # Skip empty rows
        if not url.strip():
            continue
            
        history.append({
            "title": title,
            "channel": channel,
            "url": url
        })
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=4, ensure_ascii=False)

def add_history_entry(table, title="", channel="", url="", enabled=True):
    if not enabled:
        return
    row = table.rowCount()
    table.insertRow(row)
    
    # Set default values if empty
    if not title:
        title = "Unknown Title"
    if not channel:
        channel = "Unknown Channel"
    
    table.setItem(row, 0, QTableWidgetItem(title))
    table.setItem(row, 1, QTableWidgetItem(channel))
    table.setItem(row, 2, QTableWidgetItem(url))
    save_history(table)

def delete_selected_history(table, log_callback):
    selected_rows = set()
    for it in table.selectedItems():
        selected_rows.add(it.row())
    for r in sorted(selected_rows, reverse=True):
        table.removeRow(r)
    log_callback(f"Deleted {len(selected_rows)} history entries.")
    save_history(table)

def delete_all_history(table, confirm, log_callback):
    ans = confirm()
    if ans:
        table.setRowCount(0)
        log_callback("All history deleted.")
        save_history(table)

def search_history(table, txt):
    txt = txt.lower()
    for r in range(table.rowCount()):
        hide = True
        for c in range(table.columnCount()):
            it = table.item(r, c)
            if it and txt in it.text().lower():
                hide = False
                break
        table.setRowHidden(r, hide)

def export_history(file_path):
    """Export history data to a JSON file"""
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            history = json.load(f)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=4, ensure_ascii=False)
        return True
    except (OSError, PermissionError, json.JSONDecodeError, json.JSONEncodeError) as e:
        print(f"Error exporting history: {e}")
        return False
