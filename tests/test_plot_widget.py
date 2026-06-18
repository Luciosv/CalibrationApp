import sys

from PySide6.QtWidgets import QApplication

from models.simulation_config import (
    SimulationConfig
)

from ui.plot_widget import PlotWidget


app = QApplication(sys.argv)

config = SimulationConfig()

widget = PlotWidget()

widget.resize(1400, 800)

widget.update_plot(config)

widget.show()

sys.exit(app.exec())