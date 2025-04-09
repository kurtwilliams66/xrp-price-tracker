# ui/main_window.py
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
import pyqtgraph as pg

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("XRP Price Tracker")
        self.setGeometry(100, 100, 400, 300)

        # Price Display
        self.price_label = QLabel("Loading price...", self)
        self.price_label.setStyleSheet("font-size: 24px;")

        # Chart Widget
        self.chart = pg.PlotWidget()
        self.chart.showGrid(x=True, y=True)
        self.chart.setBackground('w')  # or 'k' for dark mode
        self.price_curve = self.chart.plot(pen=pg.mkPen('b', width=2))

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.price_label)
        layout.addWidget(self.chart)
        self.setLayout(layout)

