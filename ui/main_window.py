import os

from PySide6.QtGui import QShortcut, QKeySequence

from PySide6.QtCore import Qt

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QScrollArea,
    QToolBar,
    QFileDialog,
    QMessageBox,
    QLabel,
    QSizePolicy,
    QSplitter,
    QStackedWidget,
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

from ui.tissue_list_widget import (
    TissueListWidget,
)

from ui.depth_bar_widget import (
    DepthBarWidget,
)

from utils.json_manager import JsonManager
from utils.reference_manager import ReferenceManager

from network.websocket_server import WebSocketServer

from models.parameter import Parameter

from maths.curve_generator import CurveGenerator

import numpy as np

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

        self.websocket_server = WebSocketServer(
            parent=self
        )

        self.websocket_server.client_connected.connect(
            self._update_connection_status
        )
        self.websocket_server.client_disconnected.connect(
            self._update_connection_status
        )

        self.websocket_server.start()

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

        right_container = QWidget()
        right_container.setObjectName("rightPanel")
        right_container.setStyleSheet(
            "#rightPanel { border-left: 1px solid #3A3B48; "
            "background: #25262E; }"
        )
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(4)

        self.totals_label = QLabel("")
        self.totals_label.setFixedHeight(36)
        self.totals_label.setStyleSheet(
            "padding: 0 12px; "
            "color: #E4E5EC; "
            "font-size: 12px; "
            "font-weight: 600; "
            "background: transparent;"
        )
        self.totals_label.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )
        right_layout.addWidget(self.totals_label)

        self.depth_bar = DepthBarWidget(
            self.config.tissues
        )
        self.depth_bar.tissue_clicked.connect(
            self._on_tissue_selected
        )
        right_layout.addWidget(self.depth_bar)

        self.mid_splitter = QSplitter(Qt.Orientation.Horizontal)

        self.tissue_list = TissueListWidget(
            self.config.tissues
        )
        self.tissue_list.tissue_selected.connect(
            self._on_tissue_selected
        )
        self.tissue_list.tissue_toggled.connect(
            self._on_tissue_toggled
        )
        self.mid_splitter.addWidget(self.tissue_list)

        self.detail_stack = QStackedWidget()
        self.mid_splitter.addWidget(self.detail_stack)

        self.mid_splitter.setSizes([180, 380])

        right_layout.addWidget(self.mid_splitter)

        self.root.addWidget(
            right_container,
            1
        )

        self._populate_right_panel()

        self._create_shortcuts()

    def _create_shortcuts(self):

        QShortcut(QKeySequence("Ctrl+S"), self).activated.connect(
            self._on_send_to_unity
        )
        QShortcut(QKeySequence("Ctrl+E"), self).activated.connect(
            self._on_export_json
        )
        QShortcut(QKeySequence("Ctrl+R"), self).activated.connect(
            self._on_restore_defaults
        )
        QShortcut(QKeySequence("Ctrl+L"), self).activated.connect(
            self._on_load_reference
        )

    def _create_toolbar(self):

        toolbar = QToolBar("Tools")

        self.addToolBar(toolbar)

        toolbar.setToolButtonStyle(
            Qt.ToolButtonStyle.ToolButtonTextOnly
        )

        toolbar.setStyleSheet("""
            QToolBar {
                background: #1B1C22;
                border-bottom: 1px solid #3A3B48;
                spacing: 2px;
                padding: 2px 4px;
            }
            QToolButton {
                color: #E4E5EC;
                background: transparent;
                border: 1px solid transparent;
                border-radius: 4px;
                padding: 4px 10px;
                font-size: 12px;
                font-weight: 500;
            }
            QToolButton:hover {
                background: #2E303A;
                border: 1px solid #3A3B48;
            }
            QToolButton:pressed {
                background: #3A3B48;
            }
            QToolBar::separator {
                color: #3A3B48;
                width: 1px;
                margin: 4px 4px;
            }
        """)

        load_action = toolbar.addAction("Load Reference")

        load_action.triggered.connect(
            self._on_load_reference
        )

        restore_action = toolbar.addAction("Restore Defaults")

        restore_action.triggered.connect(
            self._on_restore_defaults
        )

        toolbar.addSeparator()

        send_action = toolbar.addAction("Send to Unity")

        send_action.triggered.connect(
            self._on_send_to_unity
        )

        toolbar.addSeparator()

        export_json_action = toolbar.addAction("Export JSON")

        export_json_action.triggered.connect(
            self._on_export_json
        )

        export_csv_action = toolbar.addAction("Export CSV")

        export_csv_action.triggered.connect(
            self._on_export_csv
        )

        spacer = QWidget()
        spacer.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Preferred,
        )
        toolbar.addWidget(spacer)

        self.connection_status = QLabel(
            "● Disconnected"
        )
        self.connection_status.setStyleSheet(
            "color: #E53935; "
            "font-weight: 600; "
            "padding: 4px 10px; "
            "font-size: 12px; "
            "background: transparent;"
        )
        toolbar.addWidget(self.connection_status)

    def _populate_right_panel(self):

        for widget in self.tissue_widgets:
            widget.setVisible(False)
            widget.deleteLater()
        self.tissue_widgets.clear()

        while self.detail_stack.count():
            self.detail_stack.removeWidget(
                self.detail_stack.widget(0)
            )

        for tissue in self.config.tissues:
            widget = TissueWidget(tissue)
            widget.configuration_changed.connect(
                self.on_configuration_changed
            )
            self.tissue_widgets.append(widget)
            self.detail_stack.addWidget(widget)

        if self.tissue_widgets:
            self.detail_stack.setCurrentIndex(0)

    def _graph(self):
        self.plot_widget = PlotWidget()

        self.root.addWidget(
            self.plot_widget,
            2
        )

    def on_configuration_changed(self):
        self.config.update_depths()

        self.refresh_everything()

    def _on_tissue_selected(self, index: int):
        if 0 <= index < self.detail_stack.count():
            self.detail_stack.setCurrentIndex(index)

    def _on_tissue_toggled(self, index: int, enabled: bool):
        if 0 <= index < len(self.config.tissues):
            self.config.tissues[index].enabled = enabled
            self.on_configuration_changed()

    def refresh_everything(self):
        for i, widget in enumerate(self.tissue_widgets):

            widget.blockSignals(True)

            widget.refresh_from_model()

            widget.blockSignals(False)

        self.tissue_list.refresh_rows(self.config.tissues)
        self.tissue_list.set_selected(
            self.detail_stack.currentIndex()
        )

        self.depth_bar.update_tissues(self.config.tissues)

        self.reference_manager.sync_from_config(
            self.config
        )

        self.plot_widget.update_plot(
            self.config,
            self.reference_manager.get_reference_config(),
        )

        total_depth = self.config.total_depth
        total = len(self.config.tissues)
        active = len(self.config.active_tissues)

        mse_text = ""
        ref_config = self.reference_manager.get_reference_config()
        if ref_config is not None:
            try:
                _, fitted_y = CurveGenerator.generate(self.config)
                _, ref_y = CurveGenerator.generate(ref_config)
                min_len = min(len(fitted_y), len(ref_y))
                if min_len > 0:
                    mse = float(
                        np.mean((fitted_y[:min_len] - ref_y[:min_len]) ** 2)
                    )
                    mse_text = f"MSE: {mse:.4f} N²"
            except Exception:
                mse_text = "MSE: ---"

        totals_parts = [
            f"Total: {total_depth:.2f}mm",
            f"{active}/{total} active"
        ]
        if mse_text:
            totals_parts.append(mse_text)
        self.totals_label.setText("   |   ".join(totals_parts))

    def _update_connection_status(self):

        if self.websocket_server.is_connected:
            self.connection_status.setText(
                "● Connected"
            )
            self.connection_status.setStyleSheet(
                "color: #4CAF50; "
                "font-weight: 600; "
                "padding: 4px 10px; "
                "font-size: 12px; "
                "background: transparent;"
            )
        else:
            self.connection_status.setText(
                "● Disconnected"
            )
            self.connection_status.setStyleSheet(
                "color: #E53935; "
                "font-weight: 600; "
                "padding: 4px 10px; "
                "font-size: 12px; "
                "background: transparent;"
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
                disable_missing=True,
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

                original_thickness = self.reference_manager.get_original_thickness(tissue.name)
                if original_thickness is not None:
                    tissue.thickness = original_thickness
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

        if not self.websocket_server.is_connected:
            QMessageBox.warning(
                self,
                "No Connection",
                "No client connected to Unity.\n"
                "Start Play Mode in Unity "
                "to establish a connection.",
            )
            return

        try:
            self.websocket_server.send_config(
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
