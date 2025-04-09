import sys
import signal
from datetime import datetime

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication

from services.price_fetcher import get_xrp_price
from ui.main_window import MainWindow

REFRESH_INTERVAL_MS = 15000  # 10 seconds


def update_price_ui(window):
    price = get_xrp_price()
    if price:
        timestamp = datetime.now().strftime("%H:%M:%S")
        window.price_label.setText(f"XRP Price: ${price:.4f}")
        window.api_info_label.setText("Data fetched from CoinGecko")

        # Store timestamped price point
        window.price_history.append((timestamp, price))

        # Keep only last 100 points
        if len(window.price_history) > 100:
            window.price_history.pop(0)

        # Prepare x and y data for chart
        x_data = list(range(len(window.price_history)))
        y_data = [p[1] for p in window.price_history]
        window.price_curve.setData(x_data, y_data)

        # Update last updated time
        window.time_label.setText(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        window.price_label.setText("Error fetching price.")
        window.api_info_label.setText("⚠️ Price unavailable. Check internet or API.")


def handle_exit(*args):
    print("Exiting XRP Tracker cleanly.")
    sys.exit()


if __name__ == "__main__":
    # Signal handling for graceful exit
    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)

    app = QApplication(sys.argv)
    window = MainWindow()
    window.price_history = []  # Internalize price history in window
    window.show()

    # Immediate first fetch
    update_price_ui(window)

    # Refresh every REFRESH_INTERVAL_MS
    timer = QTimer()
    timer.timeout.connect(lambda: update_price_ui(window))
    timer.start(REFRESH_INTERVAL_MS)

    sys.exit(app.exec_())
