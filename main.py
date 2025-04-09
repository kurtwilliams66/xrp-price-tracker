import sys

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication

from services.price_fetcher import get_xrp_price
from ui.main_window import MainWindow

price_history = []

def update_price_ui(window):
    price = get_xrp_price()
    if price:
        window.price_label.setText(f"XRP Price: ${price:.4f}")
        price_history.append(price)

        # Keep only last 100 points
        if len(price_history) > 100:
            price_history.pop(0)
        window.price_curve.setData(price_history)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    # Refresh every 10 seconds
    timer = QTimer()
    timer.timeout.connect(lambda: update_price_ui(window))
    timer.start(10000)  # ms

    sys.exit(app.exec_())

