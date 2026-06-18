import os

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QScrollArea,
    QToolBar,
    QFileDialog,
    QMessageBox,
)

from models.simulation_config import (
    SimulationConfig,
)

from ui.plot_widget import (
    PlotWidget,
)

from ui.tissue_widget import (
    TissueWidget,
)

from utils.json_manager import JsonManager
from utils.reference_manager import ReferenceManager

from network.websocket_client import WebSocketClient

from models.parameter import Parameter

DEFAULT_REF_PATH = os.path.join(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    ),
    "data",
    "reference.json",
)


class MainWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        self.config = SimulationConfig()
        self.reference_manager = ReferenceManager()
        self.websocket_client = WebSocketClient()

        self.tissue_widgets = []

        self._load_default_reference()

        self._build_ui()

        self.refresh_everything()

    def _build_ui(self):

        self.setWindowTitle(
            "Needle Calibration"
        )

        self.resize(
            1600,
            900
        )

        self._create_toolbar()

        central = QWidget()

        self.setCentralWidget(
            central
        )

        self.root = QHBoxLayout(
            central
        )

        self._graph()

        self.right_scroll = QScrollArea()
        self.right_scroll.setWidgetResizable(True)
        self.root.addWidget(
            self.right_scroll,
            1
        )

        self._populate_right_panel()

    def _create_toolbar(self):

        toolbar = QToolBar("Tools")

        self.addToolBar(toolbar)

        load_action = toolbar.addAction(
            "Load Reference"
        )

        load_action.triggered.connect(
            self._on_load_reference
        )

        restore_action = toolbar.addAction(
            "Restore Defaults"
        )

        restore_action.triggered.connect(
            self._on_restore_defaults
        )

        toolbar.addSeparator()

        send_action = toolbar.addAction(
            "Send to Unity"
        )

        send_action.triggered.connect(
            self._on_send_to_unity
        )

        toolbar.addSeparator()

        export_json_action = toolbar.addAction(
            "Export JSON"
        )

        export_json_action.triggered.connect(
            self._on_export_json
        )

        export_csv_action = toolbar.addAction(
            "Export CSV"
        )

        export_csv_action.triggered.connect(
            self._on_export_csv
        )

    def _populate_right_panel(self):

        right_panel = QWidget()

        right_layout = QVBoxLayout(
            right_panel
        )

        for tissue in self.config.tissues:

            widget = TissueWidget(
                tissue
            )

            widget.configuration_changed.connect(
                self.on_configuration_changed
            )

            self.tissue_widgets.append(
                widget
            )

            right_layout.addWidget(
                widget
            )

        self.right_scroll.setWidget(
            right_panel
        )

    def _graph(self):
        self.plot_widget = PlotWidget()

        self.root.addWidget(
            self.plot_widget,
            3
        )

    def on_configuration_changed(self):
        self.config.update_depths()

        self.refresh_everything()

    def refresh_everything(self):
        for widget in self.tissue_widgets:

            widget.blockSignals(True)

            widget.refresh_from_model()

            widget.blockSignals(False)

        self.plot_widget.update_plot(
            self.config,
            self.reference_manager.get_reference_config(),
        )

    def _load_default_reference(self):

        if not os.path.exists(DEFAULT_REF_PATH):
            return

        try:
            self.reference_manager.load_reference(
                DEFAULT_REF_PATH
            )

            JsonManager.load_json(
                DEFAULT_REF_PATH,
                self.config,
            )

        except Exception:
            pass

    def _on_load_reference(self):

        path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Reference JSON",
            "",
            "JSON Files (*.json)",
        )

        if not path:
            return

        try:
            self.reference_manager.load_reference(
                path
            )

            JsonManager.load_json(
                path,
                self.config,
            )

            QMessageBox.information(
                self,
                "Reference Loaded",
                "Reference curve loaded successfully.",
            )

            self.refresh_everything()

        except Exception as e:
            QMessageBox.warning(
                self,
                "Load Error",
                f"Could not load reference:\n{e}",
            )

    def _on_restore_defaults(self):

        reply = QMessageBox.question(
            self,
            "Restore Defaults",
            "Reset all parameters to default values?",
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        ref_config = (
            self.reference_manager.get_reference_config()
        )

        if ref_config is not None:

            for tissue in self.config.tissues:

                ref_tissue = ref_config.get_tissue(
                    tissue.name
                )

                if ref_tissue is None:
                    continue

                tissue.family = ref_tissue.family

                tissue.parameters = [
                    Parameter(
                        name=p.name,
                        value=p.value,
                        delta=0.01,
                    )
                    for p in ref_tissue.parameters
                ]

            self.config.update_depths()

        else:

            self.config = SimulationConfig()

            for widget in self.tissue_widgets:
                widget.deleteLater()

            self.tissue_widgets.clear()

            self._populate_right_panel()

        self.refresh_everything()

    def _on_send_to_unity(self):

        try:
            self.websocket_client.send_config(
                self.config
            )

            QMessageBox.information(
                self,
                "Sent",
                "Configuration sent to Unity.",
            )

        except Exception as e:
            QMessageBox.warning(
                self,
                "Send Error",
                f"Could not send to Unity:\n{e}",
            )

    def _on_export_json(self):

        path, _ = QFileDialog.getSaveFileName(
            self,
            "Export JSON",
            "",
            "JSON Files (*.json)",
        )

        if not path:
            return

        try:
            JsonManager.save_json(
                self.config,
                path,
            )

            QMessageBox.information(
                self,
                "Exported",
                f"Configuration exported to:\n{path}",
            )

        except Exception as e:
            QMessageBox.warning(
                self,
                "Export Error",
                f"Could not export JSON:\n{e}",
            )

    def _on_export_csv(self):

        path, _ = QFileDialog.getSaveFileName(
            self,
            "Export CSV",
            "",
            "CSV Files (*.csv)",
        )

        if not path:
            return

        try:
            JsonManager.save_csv(
                self.config,
                path,
            )

            QMessageBox.information(
                self,
                "Exported",
                f"Configuration exported to:\n{path}",
            )

        except Exception as e:
            QMessageBox.warning(
                self,
                "Export Error",
                f"Could not export CSV:\n{e}",
            )
