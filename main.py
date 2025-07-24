import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTextEdit, QLineEdit,
    QPushButton, QHBoxLayout, QCheckBox, QLabel
)
from PyQt5.QtGui import QTextCursor, QColor, QTextCharFormat, QFont
from PyQt5.QtCore import Qt, QTimer
from datetime import datetime

from chatgpt_client import ChatGPTClient
from ocr_capture import extract_bookmap_text

class GPTWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🧠 BM-GPT Live Assistant")
        self.setMinimumSize(1024, 720)
        self.resize(1024, 720)
        self.setStyleSheet("""
            QWidget { background-color: #111; font-family: Consolas; font-size: 14px; color: #eee; }
            QLineEdit { background-color: #222; color: #fff; border: 1px solid #555; padding: 6px; border-radius: 5px; }
            QPushButton { background-color: #2ecc71; color: white; font-weight: bold; padding: 6px 14px; border-radius: 8px; }
            QPushButton:hover { background-color: #27ae60; }
            QTextEdit { background-color: #000; padding: 8px; border: 1px solid #333; }
            QCheckBox { color: #aaa; }
        """)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.layout.addWidget(self.chat_display)

        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type your message to GPT...")
        self.input_field.returnPressed.connect(self.send_message)
        self.send_button = QPushButton("📤 Send")
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.send_button)
        self.layout.addLayout(input_layout)

        control_layout = QHBoxLayout()
        self.mode_toggle = QCheckBox("Auto-Commentary Mode")
        self.mode_toggle.stateChanged.connect(self.toggle_mode)
        self.mode_label = QLabel("🔴 Manual mode")
        self.mode_label.setStyleSheet("color: red; font-weight: bold; padding-left: 10px;")
        self.clear_button = QPushButton("🚹 Clear")
        self.clear_button.clicked.connect(self.clear_display)
        self.copy_button = QPushButton("📂 Copy")
        self.copy_button.clicked.connect(self.copy_display)
        control_layout.addWidget(self.mode_toggle)
        control_layout.addWidget(self.mode_label)
        control_layout.addStretch()
        control_layout.addWidget(self.clear_button)
        control_layout.addWidget(self.copy_button)
        self.layout.addLayout(control_layout)

        self.gpt = ChatGPTClient()

        self.timer = QTimer()
        self.timer.setInterval(3000)  # Every 10 seconds
        self.timer.timeout.connect(self.handle_auto_commentary)
        self.timer.start()

    def toggle_mode(self):
        if self.mode_toggle.isChecked():
            self.mode_label.setText("🟩 Auto mode")
            self.mode_label.setStyleSheet("color: lightgreen; font-weight: bold; padding-left: 10px;")
        else:
            self.mode_label.setText("🔴 Manual mode")
            self.mode_label.setStyleSheet("color: red; font-weight: bold; padding-left: 10px;")

    def handle_auto_commentary(self):
        if not self.mode_toggle.isChecked():
            return

        extracted_text = extract_bookmap_text()
        if not extracted_text:
            self.append_message("🧠 BM-GPT", "No data from Bookmap. Skipped integration.", QColor("#ff6666"))
            return

        now = datetime.now().strftime("%H:%M:%S")
        self.append_message("🧠 BM-GPT", f"[{now}] Analyzing Bookmap data...", QColor("#ffaa33"))
        self.send_to_gpt(extracted_text, show_interpreting=False)

    def send_message(self):
        user_text = self.input_field.text().strip()
        if not user_text:
            return
        self.append_message("🧑 You", user_text, QColor("#ccff66"))
        self.input_field.clear()
        self.send_to_gpt(user_text, show_interpreting=True)

    def send_to_gpt(self, text, show_interpreting=True):
        if show_interpreting:
            self.append_message("🧠 BM-GPT", f"Interpreting: '{text}'", QColor("#ffa500"))
        response = self.gpt.ask(text)
        self.append_message("🧠 BM-GPT\n", response, QColor("#66ffcc"))

    def append_message(self, sender, message, color):
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.End)
        fmt = QTextCharFormat()
        fmt.setForeground(color)
        fmt.setFontWeight(QFont.Bold if "BM-GPT" in sender else QFont.Normal)
        cursor.insertText(f"{sender}: ", fmt)
        fmt.setFontWeight(QFont.Normal)
        cursor.insertText(f"{message}\n\n", fmt)
        self.chat_display.setTextCursor(cursor)
        self.chat_display.ensureCursorVisible()

    def clear_display(self):
        self.chat_display.clear()

    def copy_display(self):
        QApplication.clipboard().setText(self.chat_display.toPlainText())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GPTWindow()
    window.show()
    sys.exit(app.exec_())
