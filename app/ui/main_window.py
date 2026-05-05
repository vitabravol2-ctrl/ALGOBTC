from __future__ import annotations

from datetime import datetime
import logging

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
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

from app.algorithms.algorithm_profile import DEFAULT_PROFILE
from app.core.config import load_algorithms, load_config, save_algorithms, save_keys
from app.exchange.binance_client import BinanceClient
from app.exchange.price_ws import PriceWebSocket
from app.runtime.algorithm_runtime import AlgorithmRuntime


class MainWindow(QMainWindow):
    price_signal = Signal(dict)
    error_signal = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("ALGOBTC Terminal")
        self.resize(1000, 650)
        self.config = load_config()
        self.algorithms = load_algorithms()
        self.current_profile = self.algorithms[0] if self.algorithms else DEFAULT_PROFILE.copy()
        self.binance_client = BinanceClient()
        self.price_ws: PriceWebSocket | None = None
        self.algorithm_runtime = AlgorithmRuntime(self._algo_log)
        self.last_decision = "-"
        self._init_ui()
        self.price_signal.connect(self._on_price_update)
        self.error_signal.connect(self._on_error)
        self._refresh_keys_status()

    def _init_ui(self) -> None:
        root = QWidget(); layout = QVBoxLayout(root)
        tabs = QTabWidget()
        tabs.addTab(self._build_dashboard_tab(), "Dashboard")
        tabs.addTab(self._build_algorithms_tab(), "Algorithms")
        tabs.addTab(self._build_settings_tab(), "Settings")
        tabs.addTab(self._build_errors_tab(), "Errors")
        layout.addWidget(tabs); self.setCentralWidget(root)

    def _build_dashboard_tab(self):
        w = QWidget(); l = QVBoxLayout(w)
        self.mode_label = QLabel("Trading mode: DRY-RUN")
        self.active_algo_label = QLabel("Active algorithm: -")
        self.position_status = QLabel("Position status: FLAT")
        self.pnl_label = QLabel("PnL %: 0.00")
        self.last_trade_label = QLabel("Last trade: -")
        self.last_label = QLabel("Last price: -"); self.bid_label = QLabel("Bid: -"); self.ask_label = QLabel("Ask: -")
        for x in [self.mode_label,self.active_algo_label,self.position_status,self.pnl_label,self.last_trade_label,self.last_label,self.bid_label,self.ask_label]: l.addWidget(x)
        row=QHBoxLayout();
        for t,cb in [("Connect Binance",self._test_binance),("Start BTCUSDT WS",self._start_ws),("Stop WS",self._stop_ws)]:
            b=QPushButton(t); b.clicked.connect(cb); row.addWidget(b)
        l.addLayout(row); return w

    def _build_algorithms_tab(self):
        w=QWidget(); l=QHBoxLayout(w)
        self.algo_list=QListWidget(); self.algo_list.addItem(self.current_profile["name"]); l.addWidget(self.algo_list,2)
        r=QVBoxLayout(); f=QFormLayout()
        self.pair_input=QLineEdit("BTCUSDT"); self.amount_input=QLineEdit(str(self.current_profile.get("trade_amount_usdt",20)))
        self.tick_input=QLineEdit(str(self.current_profile["conditions"]["entry"]["ticks"]))
        self.tp_input=QLineEdit(str(self.current_profile["conditions"]["exit"]["profit_percent"]))
        self.sl_input=QLineEdit(str(self.current_profile["conditions"]["stop"]["loss_percent"]))
        self.enabled_box=QCheckBox(); self.enabled_box.setChecked(bool(self.current_profile.get("enabled",False)))
        for k,v in [("Pair",self.pair_input),("Trade amount USDT",self.amount_input),("Entry tick down",self.tick_input),("Take profit %",self.tp_input),("Stop loss %",self.sl_input),("Enabled",self.enabled_box)]: f.addRow(k,v)
        r.addLayout(f)
        row=QHBoxLayout()
        for t,cb in [("Save Algorithm",self._save_algorithm),("Start DRY-RUN",self._start_algorithm),("Stop Algorithm",self._stop_algorithm)]:
            b=QPushButton(t); b.clicked.connect(cb); row.addWidget(b)
        r.addLayout(row)
        self.algo_status=QLabel("Algorithm status: STOPPED"); self.pos_qty=QLabel("Position qty: 0"); self.entry_price=QLabel("Entry price: -"); self.current_pnl=QLabel("Current PnL %: 0.00"); self.last_decision_label=QLabel("Last decision: -")
        self.algo_log_box=QTextEdit(); self.algo_log_box.setReadOnly(True)
        for x in [self.algo_status,self.pos_qty,self.entry_price,self.current_pnl,self.last_decision_label,self.algo_log_box]: r.addWidget(x)
        wrap=QWidget(); wrap.setLayout(r); l.addWidget(wrap,3); return w

    def _build_settings_tab(self):
        w=QWidget(); l=QVBoxLayout(w); f=QFormLayout()
        self.api_key_input=QLineEdit(self.config["binance"].get("api_key","")); self.api_secret_input=QLineEdit(self.config["binance"].get("api_secret","")); self.api_secret_input.setEchoMode(QLineEdit.Password)
        f.addRow("API Key",self.api_key_input); f.addRow("API Secret",self.api_secret_input); l.addLayout(f)
        self.keys_status_label=QLabel(); l.addWidget(self.keys_status_label)
        row=QHBoxLayout(); s=QPushButton("Save Keys"); s.clicked.connect(self._save_keys); t=QPushButton("Test Connection"); t.clicked.connect(self._test_binance); row.addWidget(s); row.addWidget(t); l.addLayout(row)
        return w

    def _build_errors_tab(self):
        w=QWidget(); l=QVBoxLayout(w); self.errors_box=QTextEdit(); self.errors_box.setReadOnly(True); l.addWidget(self.errors_box); return w

    def _refresh_keys_status(self): self.keys_status_label.setText("Settings: Keys saved" if self.api_key_input.text().strip() and self.api_secret_input.text().strip() else "Settings: Keys not saved")
    def _save_keys(self): save_keys(self.api_key_input.text(),self.api_secret_input.text()); self._refresh_keys_status(); QMessageBox.information(self,"Saved","Keys saved")
    def _test_binance(self): ok,msg=self.binance_client.test_connection(); QMessageBox.information(self,"Binance",msg) if ok else self._on_error(msg)
    def _start_ws(self):
        if self.price_ws and self.price_ws.is_running(): return
        self.price_ws=PriceWebSocket("btcusdt",self.price_signal.emit,self.error_signal.emit); self.price_ws.start()
    def _stop_ws(self):
        if self.price_ws: self.price_ws.stop()

    def _save_algorithm(self):
        p=self.current_profile
        p["pair"]=self.pair_input.text().strip() or "BTCUSDT"; p["trade_amount_usdt"]=float(self.amount_input.text()); p["enabled"]=self.enabled_box.isChecked()
        p["conditions"]["entry"]["ticks"]=float(self.tick_input.text()); p["conditions"]["exit"]["profit_percent"]=float(self.tp_input.text()); p["conditions"]["stop"]["loss_percent"]=float(self.sl_input.text())
        save_algorithms([p]); QMessageBox.information(self,"Algorithm","Saved")

    def _start_algorithm(self): self.algorithm_runtime.start_algorithm(self.current_profile); self.algo_status.setText("Algorithm status: RUNNING"); self.active_algo_label.setText(f"Active algorithm: {self.current_profile['name']}")
    def _stop_algorithm(self): self.algorithm_runtime.stop_algorithm(self.current_profile["id"]); self.algo_status.setText("Algorithm status: STOPPED")

    def _on_price_update(self, data: dict):
        self.last_label.setText(f"Last price: {data['last']:.2f}"); self.bid_label.setText(f"Bid: {data['bid']:.2f}"); self.ask_label.setText(f"Ask: {data['ask']:.2f}")
        self.algorithm_runtime.on_price_update(data)
        pos=self.algorithm_runtime.trade_engine.position
        if pos:
            self.position_status.setText("Position status: OPEN"); self.pos_qty.setText(f"Position qty: {pos['qty']:.6f}"); self.entry_price.setText(f"Entry price: {pos['entry_price']:.2f}")
            self.current_pnl.setText(f"Current PnL %: {pos.get('unrealized_pnl',0.0):.4f}"); self.pnl_label.setText(f"PnL %: {pos.get('unrealized_pnl',0.0):.4f}")
        else: self.position_status.setText("Position status: FLAT")

    def _algo_log(self, message: str):
        self.last_decision = message; self.last_decision_label.setText(f"Last decision: {message}"); self.algo_log_box.append(message); self.last_trade_label.setText(f"Last trade: {message}")

    def _on_error(self, message: str):
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"); line=f"[{timestamp}] {message}"; self.errors_box.append(line); logging.error(line)
