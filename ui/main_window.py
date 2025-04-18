from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
import pyqtgraph as pg
from datetime import datetime
from services.price_fetcher import get_price_history, get_xrp_price


class PriceFetcherThread(QThread):
    # Define a signal to communicate with the main thread
    price_updated = pyqtSignal(float)
    history_updated = pyqtSignal(list)

    def run(self):
        # Fetch the current price and history
        try:
            price = get_xrp_price()
            if price:
                self.price_updated.emit(price)

            # Here, we assume 'get_price_history' returns a list of (timestamp, price) tuples
            data = get_price_history('1D')  # Default range is '1D'
            self.history_updated.emit(data)
        except Exception as e:
            print("[ERROR] Fetching data failed:", str(e))


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("XRP Price Tracker")
        self.setGeometry(100, 100, 600, 400)

        self.init_ui()
        self.apply_dark_theme()

        # Thread to handle background work
        self.price_thread = PriceFetcherThread()
        self.price_thread.price_updated.connect(self.update_price_ui)
        self.price_thread.history_updated.connect(self.update_chart_ui)
        self.price_thread.start()  # Start the thread to fetch data

        self.price_history = []  # Initialize price history for the chart

    def init_ui(self):
        # Price Display Label
        self.price_label = QLabel("Loading XRP Price...", self)
        self.price_label.setFont(QFont("Arial", 20, QFont.Bold))
        self.price_label.setAlignment(Qt.AlignCenter)

        # Last Updated Time Label
        self.time_label = QLabel("Last Updated: --:--", self)
        self.time_label.setFont(QFont("Arial", 10))
        self.time_label.setAlignment(Qt.AlignRight)

        # API Info Label
        self.api_info_label = QLabel("Fetching data from CryptoCompare...")
        self.api_info_label.setFont(QFont("Arial", 10))
        self.api_info_label.setAlignment(Qt.AlignLeft)

        # Range Buttons
        self.range_buttons = {
            "1D": QPushButton("1D"),
            "1W": QPushButton("1W"),
            "1M": QPushButton("1M"),
            "1Y": QPushButton("1Y"),
        }

        button_layout = QHBoxLayout()
        for label, button in self.range_buttons.items():
            button.clicked.connect(lambda _, r=label: self.change_range(r))
            button_layout.addWidget(button)

        # Chart Widget
        self.chart = pg.PlotWidget()
        self.chart.showGrid(x=True, y=True)
        self.chart.setBackground("#1e1e1e")
        self.chart.getPlotItem().setTitle("XRP Price Movement", color="#00FFAA")
        self.chart.getPlotItem().getAxis("left").setPen(pg.mkPen(color="#ffffff"))
        self.chart.getPlotItem().getAxis("bottom").setPen(pg.mkPen(color="#ffffff"))
        self.chart.getPlotItem().getAxis("left").setTextPen(pg.mkPen(color="#ffffff"))
        self.chart.getPlotItem().getAxis("bottom").setTextPen(pg.mkPen(color="#ffffff"))
        self.price_curve = self.chart.plot(pen=pg.mkPen(color="#00FFAA", width=2))

        # Assemble top info
        top_info_layout = QHBoxLayout()
        top_info_layout.addWidget(self.api_info_label)
        top_info_layout.addWidget(self.time_label)

        # Main Layout
        layout = QVBoxLayout()
        layout.addLayout(top_info_layout)
        layout.addWidget(self.price_label)
        layout.addLayout(button_layout)
        layout.addWidget(self.chart)

        self.setLayout(layout)

        # Timer for periodic price updates
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.fetch_new_price)
        self.timer.start(15000)  # Update every 15 seconds

    def apply_dark_theme(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #121212;
                color: #ffffff;
                font-family: 'Arial';
                font-size: 14px;
            }
            QPushButton {
                background-color: #1e1e1e;
                border: 1px solid #00FFAA;
                color: #00FFAA;
                padding: 6px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2e2e2e;
            }
            QLabel {
                color: #00FFAA;
            }
            QGraphicsView {
                border: 1px solid #333;
            }
        """)

    def update_price_ui(self, price):
        """Update the UI with the current price."""
        self.price_label.setText(f"XRP Price: ${price:.4f}")
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.setText(f"Last Updated: {current_time}")

    def update_chart_ui(self, data):
        """Update the chart with the fetched historical data."""
        if data:
            timestamps, prices = zip(*data)
            self.price_curve.setData(x=list(range(len(prices))), y=prices)
            self.api_info_label.setText("Showing 1D data from CryptoCompare API")

    def fetch_new_price(self):
        """Fetch the latest price and history data."""
        self.price_thread.start()  # Start the thread to fetch new data

    def change_range(self, range_label):
        """
        Triggered when a time range button is clicked.
        Fetches historical data and updates the chart.
        """
        try:
            data = get_price_history(range_label)
            if not data:
                raise ValueError("No data received for range: " + range_label)

            timestamps, prices = zip(*data)
            formatted_times = [datetime.fromtimestamp(t) for t in timestamps]

            self.price_curve.setData(x=list(range(len(prices))), y=prices)
            self.api_info_label.setText(f"Showing {range_label} data from CryptoCompare API")

            latest_price = prices[-1]
            self.price_label.setText(f"XRP Price: ${latest_price:.4f}")

            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.time_label.setText(f"Last Updated: {current_time}")

        except Exception as e:
            self.price_label.setText("Error fetching price")
            self.api_info_label.setText(f"Error: {str(e)}")
            print("[ERROR]", str(e))
