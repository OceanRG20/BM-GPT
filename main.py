import sys
import threading
import time
from PyQt5.QtWidgets import (
    QApplication, QWidget, QTextEdit, QLineEdit, QPushButton, QVBoxLayout,
    QHBoxLayout, QCheckBox, QProgressBar, QGraphicsOpacityEffect
)
from PyQt5.QtCore import Qt, QTimer, QSize, QEvent
from PyQt5.QtGui import QTextCursor, QColor, QFont
from datetime import datetime

from chatgpt_client import ChatGPTClient
from ocr_capture import extract_bookmap_text


class ChatApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("📱 BM-GPT Live Assistant")
        self.resize(1200, 800)
        self.setMinimumSize(QSize(700, 500))
        self.setStyleSheet("background-color: #0d0d0d; color: #f0f0f0;")

        self.client = ChatGPTClient()
        self.timer = QTimer()
        self.timer.timeout.connect(self.handle_auto_commentary)

        font = QFont("Consolas", 16)
        bg_color = "#0d0d0d"

        self.chat_display = QTextEdit()
        self.chat_display.setFont(font)
        self.chat_display.setReadOnly(True)
        self.chat_display.setAutoFillBackground(True)
        self.chat_display.setStyleSheet("color: #f0f0f0; padding: 10px;")
        self.chat_display.viewport().setStyleSheet(f"background-color: {bg_color};")
        self.chat_display.setAcceptRichText(True)

        self.input_field = QLineEdit()
        self.input_field.setFont(font)
        self.input_field.setPlaceholderText("Type your message to GPT...")
        self.input_field.setStyleSheet(f"background-color: {bg_color}; color: white; padding: 8px;")
        self.input_field.returnPressed.connect(self.send_message)

        self.send_button = QPushButton("📤 Send")
        self.send_button.setFont(font)
        self.send_button.setStyleSheet("background-color: #00cc66; color: white; padding: 8px 14px;")
        self.send_button.clicked.connect(self.send_message)

        self.clear_button = QPushButton("🧹 Clear")
        self.clear_button.setFont(font)
        self.clear_button.setStyleSheet("background-color: #009966; color: white; padding: 8px 14px;")
        self.clear_button.clicked.connect(lambda: self.chat_display.clear())

        self.copy_button = QPushButton("📋 Copy")
        self.copy_button.setFont(font)
        self.copy_button.setStyleSheet("background-color: #3399ff; color: white; padding: 8px 14px;")
        self.copy_button.clicked.connect(lambda: QApplication.clipboard().setText(self.chat_display.toPlainText()))

        self.exit_button = QPushButton("❌ Exit")
        self.exit_button.setFont(font)
        self.exit_button.setStyleSheet("background-color: #cc0000; color: white; padding: 8px 14px;")
        self.exit_button.clicked.connect(lambda: QApplication.quit())

        self.switch_to_auto_checkbox = QCheckBox("Auto Mode")
        self.switch_to_auto_checkbox.setFont(font)
        self.switch_to_auto_checkbox.setStyleSheet("color: white; padding-left: 10px;")
        self.switch_to_auto_checkbox.stateChanged.connect(self.toggle_mode)

        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("QProgressBar::chunk { background-color: #00cc66; }")

        self.auto_mode_checkbox = QCheckBox("Manual Mode")
        self.auto_mode_checkbox.setFont(font)
        self.auto_mode_checkbox.setStyleSheet("color: white; padding-left: 10px;")
        self.auto_mode_checkbox.stateChanged.connect(self.toggle_mode)

        self.manual_ui = QWidget()
        manual_layout = QVBoxLayout()
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.send_button)
        input_layout.addWidget(self.clear_button)
        input_layout.addWidget(self.copy_button)
        input_layout.addWidget(self.exit_button)
        control_layout = QHBoxLayout()
        control_layout.addWidget(self.switch_to_auto_checkbox)
        manual_layout.addWidget(self.chat_display)
        manual_layout.addLayout(input_layout)
        manual_layout.addLayout(control_layout)
        self.manual_ui.setLayout(manual_layout)

        self.auto_ui = QWidget()
        auto_layout = QVBoxLayout()
        auto_top = QHBoxLayout()
        auto_top.setContentsMargins(10, 10, 10, 10)
        auto_top.setSpacing(10)
        auto_top.addWidget(self.progress_bar)
        auto_top.addWidget(self.auto_mode_checkbox)
        auto_layout.addLayout(auto_top)
        self.auto_ui.setLayout(auto_layout)
        self.auto_ui.setVisible(False)

        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.manual_ui)
        self.main_layout.addWidget(self.auto_ui)
        self.setLayout(self.main_layout)

    def send_message(self):
        user_input = self.input_field.text().strip()
        if not user_input:
            return
        self.append_message("🧑 You", user_input, QColor("#deb41c"))
        self.input_field.clear()
        threading.Thread(target=self.ask_gpt_and_display, args=(user_input,), daemon=True).start()

    def ask_gpt_and_display(self, text):
        response = self.client.ask_manual(text)
        self.append_html("📡 BM-GPT", response, QColor("#00ff4c"))

    def append_message(self, sender, message, color=QColor("white")):
        self.chat_display.setTextColor(color)
        self.chat_display.append(f"{sender}: {message}\n")

    def append_html(self, sender, html_content, color=QColor("white")):
        self.chat_display.setTextColor(color)
        self.chat_display.append(f"{sender}:\n")
        self.chat_display.insertHtml(html_content)
        self.chat_display.append("\n")

    def toggle_mode(self, state):
        sender = self.sender()
        if sender == self.switch_to_auto_checkbox and state == Qt.Checked:
            self.manual_ui.setVisible(False)
            self.auto_ui.setVisible(True)
            self.setFixedSize(400, 90)

            screen_geometry = QApplication.desktop().availableGeometry()
            window_width = self.frameGeometry().width()
            self.move(screen_geometry.width() - window_width, 0)

            self.progress_bar.setVisible(True)
            self.auto_mode_checkbox.setChecked(False)
            self.timer.start(3000)

            opacity_effect = QGraphicsOpacityEffect()
            opacity_effect.setOpacity(0.3)
            self.auto_ui.setGraphicsEffect(opacity_effect)

        elif sender == self.auto_mode_checkbox and state == Qt.Checked:
            self.timer.stop()
            self.manual_ui.setVisible(True)
            self.auto_ui.setVisible(False)
            self.resize(1200, 800)
            self.setMinimumSize(QSize(1200, 800))
            self.progress_bar.setVisible(False)
            self.switch_to_auto_checkbox.setChecked(False)

            self.auto_ui.setGraphicsEffect(None)

    def enterEvent(self, event):
        if self.auto_ui.isVisible():
            effect = QGraphicsOpacityEffect()
            effect.setOpacity(1.0)
            self.auto_ui.setGraphicsEffect(effect)

    def leaveEvent(self, event):
        if self.auto_ui.isVisible():
            effect = QGraphicsOpacityEffect()
            effect.setOpacity(0.4)
            self.auto_ui.setGraphicsEffect(effect)

    def handle_auto_commentary(self):
        self.progress_bar.setValue(0)
        for i in range(1, 101, 5):
            time.sleep(0.015)
            self.progress_bar.setValue(i)
        threading.Thread(target=self.perform_ocr_and_gpt, daemon=True).start()

    def perform_ocr_and_gpt(self):
        extracted_text = extract_bookmap_text()
        if not extracted_text:
            return
        response = self.client.ask_auto_image("bookmap_debug_capture.png")
        now = datetime.now().strftime("%H:%M:%S")
        self.append_html(f"📡 BM-GPT ({now})", response, QColor("#00ff4c"))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ChatApp()
    window.show()
    sys.exit(app.exec_())
