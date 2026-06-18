import sys

from PySide6.QtWidgets import QApplication

import pyqtgraph as pg

from models.simulation_config import (
    SimulationConfig
)

from math.curve_generator import (
    CurveGenerator
)


app = QApplication(sys.argv)

config = SimulationConfig()

x, y = CurveGenerator.generate(config)

window = pg.GraphicsLayoutWidget(
    show=True,
    title="Curve Test"
)

window.resize(1200, 700)

plot = window.addPlot()

plot.showGrid(
    x=True,
    y=True
)

plot.setLabel(
    "bottom",
    "Depth (mm)"
)

plot.setLabel(
    "left",
    "Force (N)"
)

plot.plot(
    x,
    y,
    pen=pg.mkPen(
        width=3
    )
)

sys.exit(app.exec())