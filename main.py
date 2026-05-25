import os
import sys
import json
import atexit
import platform
from PySide6.QtCore import Qt, QProcess, QTimer
from PySide6.QtGui import QPalette, QColor, QTextCursor, QIcon
from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QLineEdit,
    QLabel, QSpinBox, QAbstractSpinBox, QGroupBox, QGridLayout,
    QHBoxLayout, QTextEdit, QSplitter
)

class Config(object):
    VERSION_NUMBER = 'v1.0'
    COPYRIGHT = 2026
    CREDIT = 'github.com/vauth'

if getattr(sys, 'frozen', False): CURRENT_DIR = os.path.dirname(sys.executable)
else: CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(CURRENT_DIR, "config.json")

DEFAULT_CONFIG = {
    "LISTEN_HOST": "0.0.0.0",
    "LISTEN_PORT": 40443,
    "CONNECT_IP": "104.19.229.21",
    "CONNECT_PORT": 443,
    "FAKE_SNI": "www.hcaptcha.com"
}

ARCH_ALIASES = {
    "x86_64": "amd64",
    "amd64": "amd64",
    "aarch64": "arm64",
    "arm64": "arm64"
}

ARCH = ARCH_ALIASES.get(platform.machine().lower(), "amd64")
BINARY_FILE = os.path.join(CURRENT_DIR, f"sni-spoof-linux-{ARCH}")


class ConsoleOutput(QTextEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setReadOnly(True)
        self.setStyleSheet(
            "QTextEdit {background-color: #111; color: #ffffff; border-radius: 8px; "
            "font-family: Consolas, monospace; padding: 8px; selection-background-color: #474747;}"
            "QScrollBar:vertical {background: #111; border-radius: 8px;}"
            "QScrollBar::handle:vertical {background: #474747; border-radius: 8px;}"
            "QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {background: #111;}"
            "QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {background: none; border: none;}"
        )


class SniSpoofApp(QWidget):
    def __init__(self):
        super().__init__()
        
        self.process = QProcess(self)
        self.process.setWorkingDirectory(CURRENT_DIR)
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.errorOccurred.connect(self.handle_error)
        self.process.finished.connect(self.handle_finished)

        self.initUI()
        self.load_config()
        atexit.register(lambda: self.stop_core(on_exit=True))

        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self.check_files_status)
        self.status_timer.start(1500)
        self.check_files_status()

    def initUI(self):
        print('SNI SPOOF')
        self.setWindowTitle('SNI Spoof')

        self.setFixedWidth(800)
        self.setFixedHeight(500)

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(0, 0, 0))
        self.setPalette(palette)

        self.splitter = QSplitter(Qt.Horizontal)

        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        self.start_button = QPushButton('Start Core', self)
        self.start_button.clicked.connect(self.start_core)
        self.start_button.setStyleSheet(
            "QPushButton:pressed {background-color: rgb(30, 30, 30); border: 2px solid white;}"
            "QPushButton {background-color: #111; border-radius: 8px; color: white; min-height: 35px;}"
            "QPushButton:disabled {color: #4caf50; background-color: rgb(30, 30, 30)}"
        )
        left_layout.addWidget(self.start_button)

        self.stop_button = QPushButton('Stop Core', self)
        self.stop_button.clicked.connect(self.stop_core)
        self.stop_button.setEnabled(False)
        self.stop_button.setStyleSheet(
            "QPushButton:pressed {background-color: rgb(30, 30, 30); border: 2px solid white;}"
            "QPushButton {background-color: #111; border-radius: 8px; color: white; min-height: 35px;}"
            "QPushButton:disabled {color: #f44336; background-color: rgb(30, 30, 30)}"
        )
        left_layout.addWidget(self.stop_button)

        self.status_label = QLabel("Checking status...", self)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("QLabel {background-color: #111; border-radius: 8px; padding: 5px;}")
        left_layout.addWidget(self.status_label)

        grouper = QGroupBox("Configuration")
        grouper.setStyleSheet(
            "QGroupBox { border: 2px solid #111; border-radius: 8px; color: white; margin-top: 10px;} QGroupBox::title { subcontrol-origin: margin; left: 10px; }")
        grid = QGridLayout()
        grid.setSpacing(8)

        input_style = (
            "QLineEdit, QSpinBox {background-color: #111; border-radius: 8px; min-height: 30px; "
            "selection-background-color: #474747; color: white; padding: 0 5px;}"
            "QLineEdit:focus, QSpinBox:focus {border: 2px solid white;}"
        )

        self.listen_host = QLineEdit(self)
        self.listen_host.setPlaceholderText('Listen Host (0.0.0.0)')
        self.listen_host.setAlignment(Qt.AlignCenter)
        self.listen_host.setStyleSheet(input_style)

        self.listen_port = QSpinBox(self)
        self.listen_port.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.listen_port.setRange(1, 65535)
        self.listen_port.setAlignment(Qt.AlignCenter)
        self.listen_port.setStyleSheet(input_style)

        self.connect_ip = QLineEdit(self)
        self.connect_ip.setPlaceholderText('Connect IP')
        self.connect_ip.setAlignment(Qt.AlignCenter)
        self.connect_ip.setStyleSheet(input_style)

        self.connect_port = QSpinBox(self)
        self.connect_port.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.connect_port.setRange(1, 65535)
        self.connect_port.setAlignment(Qt.AlignCenter)
        self.connect_port.setStyleSheet(input_style)

        self.fake_sni = QLineEdit(self)
        self.fake_sni.setPlaceholderText('Fake SNI (e.g. hcaptcha.com)')
        self.fake_sni.setAlignment(Qt.AlignCenter)
        self.fake_sni.setStyleSheet(input_style)

        grid.addWidget(QLabel("<span style='color:white;'>L-Host:</span>"), 0, 0)
        grid.addWidget(self.listen_host, 0, 1)
        grid.addWidget(QLabel("<span style='color:white;'>L-Port:</span>"), 0, 2)
        grid.addWidget(self.listen_port, 0, 3)

        grid.addWidget(QLabel("<span style='color:white;'>C-IP:</span>"), 1, 0)
        grid.addWidget(self.connect_ip, 1, 1)
        grid.addWidget(QLabel("<span style='color:white;'>C-Port:</span>"), 1, 2)
        grid.addWidget(self.connect_port, 1, 3)

        grid.addWidget(QLabel("<span style='color:white;'>SNI:</span>"), 2, 0)
        grid.addWidget(self.fake_sni, 2, 1, 1, 3)

        grouper.setLayout(grid)
        left_layout.addWidget(grouper)
        left_layout.addStretch()

        self.made_by = QLabel(f"{Config.COPYRIGHT} | {Config.CREDIT} | {Config.VERSION_NUMBER}", self)
        self.made_by.setStyleSheet("QLabel {color: white;}")
        left_layout.addWidget(self.made_by, alignment=Qt.AlignCenter)

        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        self.console_output = ConsoleOutput()
        right_layout.addWidget(self.console_output)

        clear_logs_button = QPushButton('Clear Logs', self)
        clear_logs_button.clicked.connect(self.clear_logs)
        clear_logs_button.setStyleSheet(
            "QPushButton:pressed {background-color: rgb(30, 30, 30); border: 2px solid white;}"
            "QPushButton {background-color: #111; border-radius: 8px; color: white; min-height: 35px;}"
        )
        right_layout.addWidget(clear_logs_button)

        self.splitter.addWidget(left_panel)
        self.splitter.addWidget(right_panel)
        self.splitter.setSizes([350, 450])

        main_layout = QHBoxLayout(self)
        main_layout.addWidget(self.splitter)
        self.setLayout(main_layout)

        sys.stdout = self
        sys.stderr = self

    def check_files_status(self):
        core_ok = os.path.exists(BINARY_FILE)
        config_ok = os.path.exists(CONFIG_FILE)

        c_color = "#4caf50" if core_ok else "#f44336"
        c_text = "OK" if core_ok else "MISSING"

        cfg_color = "#4caf50" if config_ok else "#f44336"
        cfg_text = "OK" if config_ok else "MISSING"

        status_html = (
            f"<span style='color:white; font-weight:bold;'>Core: </span>"
            f"<span style='color:{c_color}; font-weight:bold;'>{c_text}</span>"
            f"&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;"
            f"<span style='color:white; font-weight:bold;'>Config: </span>"
            f"<span style='color:{cfg_color}; font-weight:bold;'>{cfg_text}</span>"
        )
        self.status_label.setText(status_html)

    def _sanitize_text(self, value, default):
        if value is None:
            return default
        cleaned = str(value).strip()
        return cleaned if cleaned else default

    def _sanitize_port(self, value, default):
        try:
            port = int(value)
        except (TypeError, ValueError):
            return default
        return port if 1 <= port <= 65535 else default

    def _apply_config(self, data):
        self.listen_host.setText(data["LISTEN_HOST"])
        self.listen_port.setValue(data["LISTEN_PORT"])
        self.connect_ip.setText(data["CONNECT_IP"])
        self.connect_port.setValue(data["CONNECT_PORT"])
        self.fake_sni.setText(data["FAKE_SNI"])

    def _load_config_data(self):
        data = DEFAULT_CONFIG.copy()
        if not os.path.exists(CONFIG_FILE):
            return data, False
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                loaded = json.load(f)
            if not isinstance(loaded, dict):
                raise ValueError("Config file is not a JSON object.")
        except Exception as e:
            print(f"Error loading config: {e}")
            return data, False
        data["LISTEN_HOST"] = self._sanitize_text(loaded.get("LISTEN_HOST"), DEFAULT_CONFIG["LISTEN_HOST"])
        data["LISTEN_PORT"] = self._sanitize_port(loaded.get("LISTEN_PORT"), DEFAULT_CONFIG["LISTEN_PORT"])
        data["CONNECT_IP"] = self._sanitize_text(loaded.get("CONNECT_IP"), DEFAULT_CONFIG["CONNECT_IP"])
        data["CONNECT_PORT"] = self._sanitize_port(loaded.get("CONNECT_PORT"), DEFAULT_CONFIG["CONNECT_PORT"])
        data["FAKE_SNI"] = self._sanitize_text(loaded.get("FAKE_SNI"), DEFAULT_CONFIG["FAKE_SNI"])
        return data, True

    def load_config(self):
        data, loaded = self._load_config_data()
        self._apply_config(data)
        if loaded:
            print("Configuration loaded.")
        else:
            print("Config not found or invalid. Using defaults.")

    def save_config(self):
        try:
            data = {
                "LISTEN_HOST": self._sanitize_text(self.listen_host.text(), DEFAULT_CONFIG["LISTEN_HOST"]),
                "LISTEN_PORT": self._sanitize_port(self.listen_port.value(), DEFAULT_CONFIG["LISTEN_PORT"]),
                "CONNECT_IP": self._sanitize_text(self.connect_ip.text(), DEFAULT_CONFIG["CONNECT_IP"]),
                "CONNECT_PORT": self._sanitize_port(self.connect_port.value(), DEFAULT_CONFIG["CONNECT_PORT"]),
                "FAKE_SNI": self._sanitize_text(self.fake_sni.text(), DEFAULT_CONFIG["FAKE_SNI"])
            }
            self._apply_config(data)
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            print("Configuration saved.")
            self.check_files_status()
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False

    def start_core(self):
        if self.process.state() != QProcess.NotRunning:
            print("Core is already running.")
            return

        if not os.path.exists(BINARY_FILE):
            print("Error: Core binary missing. Please place it in the directory.")
            return
        if not os.access(BINARY_FILE, os.X_OK):
            print("Error: Core binary is not executable.")
            return

        if self.save_config():
            print("Starting Core...")
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)

            command = "pkexec"
            args = ["sh", "-c", f"cd '{CURRENT_DIR}' && '{BINARY_FILE}'"]
            self.process.start(command, args)

    def stop_core(self, on_exit=False):
        if self.process.state() == QProcess.NotRunning:
            if not on_exit:
                print("Core is not running.")
            return

        print("Stopping Core...")
        binary_name = os.path.basename(BINARY_FILE)
        QProcess.execute("pkexec", ["pkill", "-f", binary_name])

        self.process.terminate()
        self.process.waitForFinished(1000)

        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        print("Core Stopped.")

    def write(self, text):
        self.console_output.moveCursor(QTextCursor.End)
        self.console_output.insertPlainText(text)
        self.console_output.moveCursor(QTextCursor.End)

    def flush(self):
        pass

    def clear_logs(self):
        self.console_output.clear()

    def _write_process_output(self, data):
        if not data:
            return
        text = bytes(data).decode('utf-8', errors='replace')
        self.write(text)

    def handle_stdout(self):
        self._write_process_output(self.process.readAllStandardOutput())

    def handle_stderr(self):
        self._write_process_output(self.process.readAllStandardError())

    def handle_error(self, error):
        print(f"Process error: {self.process.errorString()}")
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def handle_finished(self, exitCode, exitStatus):
        print(f"\n[Process exited with code {exitCode}]\n")
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SniSpoofApp()
    ex.show()
    sys.exit(app.exec())
