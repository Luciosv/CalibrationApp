from PySide6.QtCore import Qt, Signal

from PySide6.QtGui import QStandardItem, QFont

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QCheckBox,
    QDoubleSpinBox,
    QComboBox,
    QGroupBox,
    QFrame,
    QSlider,
    QPushButton,
    QSizePolicy,
)

from config.formulas import FORMULAS, get_default_params

from models.parameter import Parameter
from models.tissue import Tissue


class TissueWidget(QGroupBox):

    configuration_changed = Signal()

    def __init__(
        self,
        tissue: Tissue,
        parent=None
    ):
        super().__init__(parent)

        self.tissue = tissue

        self.setTitle("")

        self.setStyleSheet("""
            TissueWidget {
                border: 1px solid #3A3B48;
                border-radius: 4px;
                background: #2E303A;
                margin: 0px;
            }
            TissueWidget QDoubleSpinBox {
                color: #E4E5EC;
                background: #1B1C22;
                border: 1px solid #3A3B48;
                border-radius: 3px;
                padding: 2px 4px;
                font-family: "Cascadia Code", "JetBrains Mono", "Consolas", "monospace";
                font-size: 12px;
            }
            TissueWidget QDoubleSpinBox:focus {
                border-color: #D4783C;
            }
            TissueWidget QDoubleSpinBox:disabled {
                color: #63657A;
                background: #25262E;
            }
            TissueWidget QDoubleSpinBox::up-button,
            TissueWidget QDoubleSpinBox::down-button {
                width: 0px;
                border: none;
            }
            TissueWidget QDoubleSpinBox::up-arrow,
            TissueWidget QDoubleSpinBox::down-arrow {
                width: 0px;
                border: none;
            }
            TissueWidget QComboBox {
                color: #E4E5EC;
                background: #1B1C22;
                border: 1px solid #3A3B48;
                border-radius: 3px;
                padding: 2px 8px;
                font-size: 12px;
                min-width: 120px;
            }
            TissueWidget QComboBox:focus {
                border-color: #D4783C;
            }
            TissueWidget QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            TissueWidget QComboBox::down-arrow {
                image: none;
            }
            TissueWidget QComboBox QAbstractItemView {
                background: #2E303A;
                color: #E4E5EC;
                border: 1px solid #3A3B48;
                selection-background-color: #D4783C;
                selection-color: #FFFFFF;
                outline: none;
            }
            TissueWidget QSlider::groove:horizontal {
                background: #3A3B48;
                height: 6px;
                border-radius: 3px;
            }
            TissueWidget QSlider::handle:horizontal {
                background: #D4783C;
                width: 14px;
                height: 14px;
                margin: -5px 0;
                border-radius: 7px;
            }
            TissueWidget QSlider::handle:horizontal:hover {
                background: #E0874F;
            }
            TissueWidget QSlider::sub-page:horizontal {
                background: #D4783C;
                border-radius: 3px;
            }
            TissueWidget QSlider::add-page:horizontal {
                background: #3A3B48;
                border-radius: 3px;
            }
            TissueWidget QPushButton {
                color: #E4E5EC;
                background: #1B1C22;
                border: 1px solid #3A3B48;
                border-radius: 3px;
                font-size: 13px;
                font-weight: 600;
                padding: 0;
            }
            TissueWidget QPushButton:hover {
                border-color: #D4783C;
                background: #2E303A;
            }
            TissueWidget QPushButton:pressed {
                background: #3A3B48;
            }
        """)

        self.param_spinboxes = []
        self.param_delta_spinboxes = []
        self.param_sliders = []
        self.param_minus_buttons = []
        self.param_plus_buttons = []

        self._slider_scale = 10000

        self._build_ui()

        self.refresh_from_model()

        self._connect_signals()

    # --------------------------------------------------
    # UI
    # --------------------------------------------------

    def _build_ui(self):

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 6)
        layout.setSpacing(6)

        self._create_header(layout)

        sep1 = QFrame()
        sep1.setFrameShape(QFrame.Shape.HLine)
        sep1.setStyleSheet("color: #3A3B48; margin: 4px 0;")
        layout.addWidget(sep1)

        self._create_family_section(layout)

        self._create_parameters_section(layout)

        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setStyleSheet("color: #3A3B48; margin: 4px 0;")
        layout.addWidget(sep2)

        self._create_depth_section(layout)

    def _create_header(self, layout):

        header_frame = QFrame()
        header_frame.setFixedHeight(36)
        header_frame.setStyleSheet(
            "background-color: #25262E; border-radius: 3px;"
        )

        header = QHBoxLayout(header_frame)
        header.setContentsMargins(8, 6, 8, 6)
        header.setSpacing(8)

        header.addStretch()

        swatch = QFrame()
        swatch.setFixedSize(22, 22)
        swatch.setStyleSheet(
            f"background-color: {self.tissue.color}; "
            "border: 2px solid #4B4D5E; border-radius: 4px;"
        )
        swatch.setToolTip(f"Color: {self.tissue.color}")
        header.addWidget(swatch)

        name_label = QLabel(self.tissue.name)
        name_label.setStyleSheet(
            "font-weight: 600; font-size: 14px; color: #E4E5EC;"
        )
        header.addWidget(name_label)

        header.addStretch()

        layout.addWidget(header_frame)

    def _create_family_section(self, layout):

        section = QVBoxLayout()
        section.setSpacing(4)
        section.setContentsMargins(16, 2, 0, 2)

        family_row = QHBoxLayout()
        family_row.setSpacing(4)

        family_label = QLabel("Family:")
        family_label.setStyleSheet("color: #9395A8; font-size: 12px;")
        family_row.addWidget(family_label)

        self.family_combo = QComboBox()

        model = self.family_combo.model()

        categories = [
            ("Simple", ["constant", "linear"]),
            ("Rupture", ["kv_rupture", "simone_pop"]),
            ("Polynomial", ["polynomial2", "polynomial3"]),
            ("Exponential", [
                "exponential", "sigmoid", "saturating_exp"
            ]),
        ]

        for cat_name, families in categories:
            cat_item = QStandardItem(cat_name)
            cat_item.setEnabled(False)
            font = cat_item.font()
            font.setBold(True)
            font.setPointSize(font.pointSize() - 1)
            cat_item.setFont(font)
            model.appendRow(cat_item)

            for fam in families:
                item = QStandardItem(fam)
                model.appendRow(item)

        self.family_combo.setToolTip(
            "Mathematical model for this tissue's force response"
        )

        family_row.addWidget(self.family_combo)
        family_row.addStretch()
        section.addLayout(family_row)

        layout.addLayout(section)

    def _create_depth_section(self, layout):

        container = QWidget()
        container.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

        section = QVBoxLayout(container)
        section.setSpacing(4)
        section.setContentsMargins(16, 2, 0, 2)

        depth_row = QHBoxLayout()
        depth_row.setSpacing(4)

        depth_label = QLabel("Depth:")
        depth_label.setStyleSheet("color: #9395A8; font-size: 12px;")
        depth_row.addWidget(depth_label)

        self.start_depth_label = QLabel("0.00")
        self.start_depth_label.setStyleSheet("color: #9395A8; font-size: 12px;")
        depth_row.addWidget(self.start_depth_label)

        arrow = QLabel("→")
        arrow.setStyleSheet("color: #63657A;")
        depth_row.addWidget(arrow)

        self.depth_spin = QDoubleSpinBox()
        self.depth_spin.setRange(0.1, 1000)
        self.depth_spin.setDecimals(2)
        self.depth_spin.setSingleStep(0.1)
        self.depth_spin.setFixedWidth(80)
        self.depth_spin.setToolTip(
            "End depth of this tissue (mm)\nThickness = end − start"
        )
        depth_row.addWidget(self.depth_spin)

        mm_label = QLabel("mm")
        mm_label.setStyleSheet("color: #9395A8; font-size: 12px;")
        depth_row.addWidget(mm_label)

        self.thickness_label = QLabel("")
        self.thickness_label.setStyleSheet("color: #63657A; font-size: 11px;")
        depth_row.addWidget(self.thickness_label)

        depth_row.addStretch()
        section.addLayout(depth_row)

        layout.addWidget(container)

    def _create_parameters_section(self, layout):

        self.parameters_layout = QVBoxLayout()
        self.parameters_layout.setSpacing(8)
        layout.addLayout(self.parameters_layout, stretch=1)
        self.rebuild_parameter_widgets()

    @staticmethod
    def _clear_layout(layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget() is not None:
                item.widget().setVisible(False)
                item.widget().deleteLater()
            elif item.layout() is not None:
                TissueWidget._clear_layout(item.layout())
                item.layout().deleteLater()

    @staticmethod
    def _decimals_from_delta(delta: float) -> int:
        delta_str = f"{delta:.10f}"
        if "." in delta_str:
            fractional = delta_str.split(".")[1].rstrip("0")
            return max(1, min(len(fractional), 6))
        return 1

    def rebuild_parameter_widgets(self):
        TissueWidget._clear_layout(
            self.parameters_layout
        )

        self.param_spinboxes.clear()
        self.param_delta_spinboxes.clear()
        self.param_sliders.clear()
        self.param_minus_buttons.clear()
        self.param_plus_buttons.clear()

        formula_class = FORMULAS.get(self.tissue.family)

        if formula_class is not None:
            for i in range(len(formula_class.parameter_names)):
                param = formula_class.parameter_names[i]

                spin_box = QDoubleSpinBox()
                lim_inf, lim_sup = formula_class.bounds[i]
                spin_box.setRange(lim_inf, lim_sup)
                spin_box.setDecimals(
                    self._decimals_from_delta(self.tissue.parameters[i].delta)
                )
                spin_box.setSingleStep(
                    self.tissue.parameters[i].delta
                )

                spin_box.setToolTip(
                    f"{param} ∈ [{lim_inf}, {lim_sup}]"
                )

                current_value = self.tissue.parameters[i].value
                spin_box.setValue(current_value)

                spin_box.editingFinished.connect(
                    lambda p=param, sb=spin_box: self._on_parameter_changed(p, sb.value())
                )

                # Botón −
                minus_btn = QPushButton("−")
                minus_btn.setFixedSize(28, 24)
                minus_btn.setToolTip(f"Decrease by {self.tissue.parameters[i].delta}")

                # Botón +
                plus_btn = QPushButton("+")
                plus_btn.setFixedSize(28, 24)
                plus_btn.setToolTip(f"Increase by {self.tissue.parameters[i].delta}")

                delta_spin = QDoubleSpinBox()
                delta_spin.setRange(0.0001, 10.0)
                delta_spin.setDecimals(4)
                delta_spin.setSingleStep(0.001)
                delta_spin.setPrefix("Δ ")
                delta_spin.setValue(
                    self.tissue.parameters[i].delta
                )
                delta_spin.setToolTip(
                    "Step size for the parameter spinbox arrows"
                )
                delta_spin.valueChanged.connect(
                    lambda value, idx=i: self._on_delta_changed(idx, value)
                )

                slider = QSlider(Qt.Orientation.Horizontal)
                slider.setRange(
                    int(lim_inf * self._slider_scale),
                    int(lim_sup * self._slider_scale),
                )
                slider.setValue(
                    int(current_value * self._slider_scale)
                )
                slider.setToolTip(
                    f"{param}: drag to adjust"
                )

                def make_slider_handler(p_name, spin, scale):
                    def handler(val):
                        new_val = val / scale
                        spin.blockSignals(True)
                        spin.setValue(new_val)
                        spin.blockSignals(False)
                        self._on_parameter_changed(p_name, new_val)
                    return handler

                slider.valueChanged.connect(
                    make_slider_handler(param, spin_box, self._slider_scale)
                )

                def make_step_handler(p_name, spin, step_sign):
                    def handler():
                        step = spin.singleStep()
                        new_val = spin.value() + step * step_sign
                        new_val = max(
                            spin.minimum(),
                            min(spin.maximum(), new_val)
                        )
                        spin.setValue(new_val)
                        self._on_parameter_changed(p_name, new_val)
                    return handler

                minus_btn.clicked.connect(
                    make_step_handler(param, spin_box, -1)
                )
                plus_btn.clicked.connect(
                    make_step_handler(param, spin_box, 1)
                )

                outer = QVBoxLayout()
                outer.setSpacing(4)

                row1 = QHBoxLayout()
                row1.setSpacing(4)
                param_label = QLabel(param)
                param_label.setStyleSheet("color: #9395A8; font-size: 12px;")
                row1.addWidget(param_label)
                row1.addWidget(minus_btn)
                row1.addWidget(spin_box)
                row1.addWidget(plus_btn)
                row1.addWidget(delta_spin)
                row1.addStretch()
                outer.addLayout(row1)

                row2 = QHBoxLayout()
                row2.setContentsMargins(0, 0, 0, 0)
                row2.addWidget(slider)
                outer.addLayout(row2)

                self.parameters_layout.addLayout(outer)

                self.param_spinboxes.append(spin_box)
                self.param_delta_spinboxes.append(delta_spin)
                self.param_sliders.append(slider)
                self.param_minus_buttons.append(minus_btn)
                self.param_plus_buttons.append(plus_btn)

    # --------------------------------------------------
    # Señales
    # --------------------------------------------------

    def _connect_signals(self):

        self.family_combo.currentTextChanged.connect(
            self._on_family_changed_by_user
        )

        self.depth_spin.editingFinished.connect(
            self._on_depth_changed
        )

    # --------------------------------------------------
    # Modelo -> UI
    # --------------------------------------------------

    def refresh_from_model(self):

        old_family = self.family_combo.currentText()
        new_family = self.tissue.family

        self.family_combo.blockSignals(True)
        self.family_combo.setCurrentText(
            new_family
        )
        self.family_combo.blockSignals(False)

        if old_family != new_family or len(self.param_spinboxes) != len(self.tissue.parameters):
            self.blockSignals(True)
            self.rebuild_parameter_widgets()
            self.blockSignals(False)
        else:
            for i, spin_box in enumerate(self.param_spinboxes):
                if i < len(self.tissue.parameters):
                    spin_box.blockSignals(True)
                    spin_box.setValue(
                        self.tissue.parameters[i].value
                    )
                    spin_box.blockSignals(False)

            for i, delta_spin in enumerate(self.param_delta_spinboxes):
                if i < len(self.tissue.parameters):
                    delta_spin.blockSignals(True)
                    delta_spin.setValue(
                        self.tissue.parameters[i].delta
                    )
                    delta_spin.blockSignals(False)

            for i, slider in enumerate(self.param_sliders):
                if i < len(self.tissue.parameters):
                    slider.blockSignals(True)
                    slider.setValue(
                        int(self.tissue.parameters[i].value * self._slider_scale)
                    )
                    slider.blockSignals(False)

        self.depth_spin.setValue(
            self.tissue.end_depth
        )

        self.start_depth_label.setText(
            f"{self.tissue.start_depth:.2f}"
        )

        self.thickness_label.setText(
            f"({self.tissue.thickness:.2f} mm)"
        )

    # --------------------------------------------------
    # UI -> Modelo
    # --------------------------------------------------

    def _on_family_changed_by_user(
        self,
        family: str
    ):

        if family not in FORMULAS:
            return

        self.tissue.family = family
        param_names = FORMULAS[family].parameter_names
        param_values = get_default_params(family)
        self.tissue.parameters = [
            Parameter(name=n, value=v, delta=0.01)
            for n, v in zip(param_names, param_values)
        ]
        self.rebuild_parameter_widgets()
        self.configuration_changed.emit()

    def _on_depth_changed(self):

        start_depth = self.tissue.start_depth

        self.tissue.thickness = max(
            0.1,
            self.depth_spin.value() - start_depth
        )

        self.configuration_changed.emit()

    def _on_parameter_changed(self, param_name: str, value: float):
        for p in self.tissue.parameters:
            if p.name == param_name:
                p.value = value
                break
        self.configuration_changed.emit()

    def _on_delta_changed(self, param_index: int, delta: float):
        if param_index < len(self.tissue.parameters):
            self.tissue.parameters[param_index].delta = delta
            self.param_spinboxes[param_index].setSingleStep(delta)
            self.param_spinboxes[param_index].setDecimals(
                self._decimals_from_delta(delta)
            )
