from __future__ import annotations

from datetime import datetime
import logging

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.algorithms.btcusdt_basic import ALGORITHM_INFO
from app.core.config import load_config, load_algorithms, save_keys
from app.exchange.binance_client import BinanceClient
from app.exchange.price_ws import PriceWebSocket


class MainWindow(QMainWindow):
    price_signal = Signal(dict)
    error_signal = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("ALGOBTC Terminal")
        self.resize(900, 600)

        self.config = load_config()
        self.binance_client = BinanceClient()
        self.price_ws: PriceWebSocket | None = None

        self._init_ui()
        self.price_signal.connect(self._on_price_update)
        self.error_signal.connect(self._on_error)
        self._refresh_keys_status()

    def _init_ui(self) -> None:
        root = QWidget()
        layout = QVBoxLayout(root)

        status_layout = QHBoxLayout()
        self.binance_status = QLabel("Binance: DISCONNECTED")
        self.ws_status = QLabel("WebSocket: STOPPED")
        self.pair_status = QLabel("Current Pair: BTCUSDT")
        status_layout.addWidget(self.binance_status)
        status_layout.addWidget(self.ws_status)
        status_layout.addWidget(self.pair_status)
        status_layout.addStretch()
        layout.addLayout(status_layout)

        tabs = QTabWidget()
        tabs.addTab(self._build_dashboard_tab(), "Dashboard")
        tabs.addTab(self._build_algorithms_tab(), "Algorithms")
        tabs.addTab(self._build_settings_tab(), "Settings")
        tabs.addTab(self._build_errors_tab(), "Errors")
        layout.addWidget(tabs)

        self.setCentralWidget(root)

    def _build_dashboard_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        self.pair_label = QLabel("Pair: BTCUSDT")
        self.last_label = QLabel("Last price: -")
        self.bid_label = QLabel("Bid: -")
        self.ask_label = QLabel("Ask: -")
        self.spread_label = QLabel("Spread: -")
        self.update_label = QLabel("Last update time: -")
        self.source_label = QLabel("Source: WebSocket")

        for label in [self.pair_label, self.last_label, self.bid_label, self.ask_label, self.spread_label, self.update_label, self.source_label]:
            layout.addWidget(label)

        btn_row = QHBoxLayout()
        connect_btn = QPushButton("Connect Binance")
        connect_btn.clicked.connect(self._test_binance)

        start_btn = QPushButton("Start BTCUSDT WS")
        start_btn.clicked.connect(self._start_ws)

        stop_btn = QPushButton("Stop WS")
        stop_btn.clicked.connect(self._stop_ws)

        btn_row.addWidget(connect_btn)
        btn_row.addWidget(start_btn)
        btn_row.addWidget(stop_btn)
        layout.addLayout(btn_row)
        layout.addStretch()
        return widget

    def _build_algorithms_tab(self) -> QWidget:
        widget = QWidget()
        layout = QHBoxLayout(widget)

        algo_list = QListWidget()
        for algo in load_algorithms():
            algo_list.addItem(f"{algo['name']} | {algo['pair']} | {algo['mode']} | {algo['status']}")

        right_panel = QVBoxLayout()
        desc = QLabel(ALGORITHM_INFO["description"])
        desc.setWordWrap(True)
        right_panel.addWidget(desc)

        for text in ["New Algorithm", "Edit Algorithm", "Run DRY-RUN"]:
            button = QPushButton(text)
            button.setEnabled(False)
            right_panel.addWidget(button)

        right_panel.addStretch()
        layout.addWidget(algo_list, 2)
        wrap = QWidget()
        wrap.setLayout(right_panel)
        layout.addWidget(wrap, 3)
        return widget

    def _build_settings_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        form = QFormLayout()
        self.api_key_input = QLineEdit(self.config["binance"].get("api_key", ""))
        self.api_secret_input = QLineEdit(self.config["binance"].get("api_secret", ""))
        self.api_secret_input.setEchoMode(QLineEdit.Password)

        form.addRow("API Key", self.api_key_input)
        form.addRow("API Secret", self.api_secret_input)
        layout.addLayout(form)

        self.keys_status_label = QLabel("Settings: Keys not saved")
        layout.addWidget(self.keys_status_label)

        btn_row = QHBoxLayout()
        save_btn = QPushButton("Save Keys")
        save_btn.clicked.connect(self._save_keys)
        test_btn = QPushButton("Test Connection")
        test_btn.clicked.connect(self._test_binance)
        btn_row.addWidget(save_btn)
        btn_row.addWidget(test_btn)

        layout.addLayout(btn_row)
        layout.addStretch()
        return widget

    def _build_errors_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        self.errors_box = QTextEdit()
        self.errors_box.setReadOnly(True)
        layout.addWidget(self.errors_box)
        return widget

    def _refresh_keys_status(self) -> None:
        has_keys = bool(self.api_key_input.text().strip() and self.api_secret_input.text().strip())
        self.keys_status_label.setText("Settings: Keys saved" if has_keys else "Settings: Keys not saved")

    def _save_keys(self) -> None:
        save_keys(self.api_key_input.text(), self.api_secret_input.text())
        self.binance_client = BinanceClient()
        self._refresh_keys_status()
        QMessageBox.information(self, "Saved", "Binance keys saved to data/config.json")

    def _test_binance(self) -> None:
        ok, message = self.binance_client.test_connection()
        self.binance_status.setText("Binance: CONNECTED" if ok else "Binance: DISCONNECTED")
        if ok:
            QMessageBox.information(self, "Binance", message)
        else:
            self._on_error(message)
            QMessageBox.warning(self, "Binance", message)

    def _start_ws(self) -> None:
        if self.price_ws and self.price_ws.is_running():
            return
        self.price_ws = PriceWebSocket("btcusdt", self.price_signal.emit, self.error_signal.emit)
        self.price_ws.start()
        self.ws_status.setText("WebSocket: RUNNING")

    def _stop_ws(self) -> None:
        if self.price_ws:
            self.price_ws.stop()
        self.ws_status.setText("WebSocket: STOPPED")

    def _on_price_update(self, data: dict) -> None:
        self.last_label.setText(f"Last price: {data['last']:.2f}")
        self.bid_label.setText(f"Bid: {data['bid']:.2f}")
        self.ask_label.setText(f"Ask: {data['ask']:.2f}")
        self.spread_label.setText(f"Spread: {data['spread']:.2f}")
        self.update_label.setText(f"Last update time: {data['time']}")
        self.source_label.setText(f"Source: {data['source']}")

    def _on_error(self, message: str) -> None:
        self.ws_status.setText("WebSocket: ERROR")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{timestamp}] {message}"
        self.errors_box.append(line)
        logging.error(line)
