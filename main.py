import sys
import signal
from datetime import datetime

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication

from services.price_fetcher import get_xrp_price, get_price_history
from ui.main_window import MainWindow

REFRESH_INTERVAL_MS = 15000  # 15 seconds (Adjusted as per previous code)

def update_price_ui(window):
    # Update the current price and chart based on the selected range
    price = get_xrp_price()  # Getting current price
    if price:
        timestamp = datetime.now().strftime("%H:%M:%S")
        window.price_label.setText(f"XRP Price: ${price:.4f}")
        window.api_info_label.setText("Data fetched from CoinGecko")

        # Store timestamped price point
        window.price_history.append((timestamp, price))

        # Keep only last 100 points (to avoid memory overflow)
        if len(window.price_history) > 100:
            window.price_history.pop(0)

        # Prepare x and y data for chart
        x_data = list(range(len(window.price_history)))  # x-axis: simple range of numbers
        y_data = [p[1] for p in window.price_history]  # y-axis: prices

        # Ensure x_data and y_data are numeric and finite
        x_data = [i for i in x_data if isinstance(i, (int, float))]
        y_data = [p for p in y_data if isinstance(p, (int, float))]

        # Filter out invalid data (e.g., None or NaN)
        x_data = [i for i in x_data if i is not None]
        y_data = [p for p in y_data if p is not None]

        # Update the plot data
        window.price_curve.setData(x_data, y_data)

        # Update last updated time
        window.time_label.setText(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        window.price_label.setText("Error fetching price.")
        window.api_info_label.setText("⚠️ Price unavailable. Check internet or API.")

def update_chart_for_selected_range(window, range_label):
    # Fetch price history for the selected range
    data = get_price_history(range=range_label)
    if data:
        timestamps = [datetime.fromtimestamp(item[0]) for item in data]
        prices = [item[1] for item in data]

        # Prepare x and y data for the chart
        x_data = [timestamp.strftime("%H:%M:%S") for timestamp in timestamps]  # Or format as needed
        y_data = prices

        # Ensure x_data and y_data are numeric and finite
        x_data = [i for i in x_data if isinstance(i, (int, float))]
        y_data = [p for p in y_data if isinstance(p, (int, float))]

        # Filter out invalid data (e.g., None or NaN)
        x_data = [i for i in x_data if i is not None]
        y_data = [p for p in y_data if p is not None]

        # Update the plot data
        window.price_curve.setData(x_data, y_data)

        # Update the UI with new data
        window.api_info_label.setText(f"Showing {range_label} data.")
    else:
        window.api_info_label.setText("Failed to fetch price history.")

    # Update last updated time
    window.time_label.setText(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

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

    # Set up range buttons to update chart based on the selected range
    for label, button in window.range_buttons.items():
        button.clicked.connect(lambda _, range=label: update_chart_for_selected_range(window, range))

    # Refresh every REFRESH_INTERVAL_MS
    timer = QTimer()
    timer.timeout.connect(lambda: update_price_ui(window))
    timer.start(REFRESH_INTERVAL_MS)

    sys.exit(app.exec_())
