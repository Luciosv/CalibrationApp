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
                border: 1px solid #d4d6d9;
                border-radius: 4px;
                background: #f6f7f9;
                margin: 0px;
            }
            TissueWidget QDoubleSpinBox {
                color: #1a1d23;
                background: #ffffff;
            }
        """)

        self.param_spinboxes = []
        self.param_delta_spinboxes = []
        self.param_sliders = []

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
        layout.setSpacing(5)

        self._create_header(layout)

        self._create_properties(layout)

        self._create_parameters_section(layout)

    def _create_header(self, layout):

        header = QHBoxLayout()
        header.setSpacing(6)

        swatch = QFrame()
        swatch.setFixedSize(14, 14)
        swatch.setStyleSheet(
            f"background-color: {self.tissue.color}; "
            "border: 1px solid #999; border-radius: 3px;"
        )
        swatch.setToolTip(f"Color: {self.tissue.color}")
        header.addWidget(swatch)

        name_label = QLabel(self.tissue.name)
        name_label.setStyleSheet(
            "font-weight: bold; font-size: 13px; color: #1a1d23;"
        )
        header.addWidget(name_label)

        header.addStretch()

        self.enable_checkbox = QCheckBox("Enabled")
        self.enable_checkbox.setToolTip(
            "Disable this tissue to exclude it from the simulation"
        )
        header.addWidget(self.enable_checkbox)

        layout.addLayout(header)

    def _create_properties(self, layout):

        props = QVBoxLayout()
        props.setSpacing(4)
        props.setContentsMargins(16, 2, 0, 2)

        depth_row = QHBoxLayout()
        depth_row.setSpacing(4)

        depth_label = QLabel("Depth:")
        depth_label.setStyleSheet("color: #4a505c;")
        depth_row.addWidget(depth_label)

        self.start_depth_label = QLabel("0.00")
        self.start_depth_label.setStyleSheet("color: #4a505c;")
        depth_row.addWidget(self.start_depth_label)

        arrow = QLabel("→")
        arrow.setStyleSheet("color: #8b92a0;")
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
        mm_label.setStyleSheet("color: #4a505c;")
        depth_row.addWidget(mm_label)

        self.thickness_label = QLabel("")
        self.thickness_label.setStyleSheet("color: #8b92a0; font-size: 11px;")
        depth_row.addWidget(self.thickness_label)

        depth_row.addStretch()
        props.addLayout(depth_row)

        family_row = QHBoxLayout()
        family_row.setSpacing(4)

        family_label = QLabel("Family:")
        family_label.setStyleSheet("color: #4a505c;")
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
        props.addLayout(family_row)

        layout.addLayout(props)

    def _create_parameters_section(self, layout):

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color: #d4d6d9; margin: 2px 0;")
        layout.addWidget(sep)

        self.parameters_layout = QVBoxLayout()
        self.parameters_layout.setSpacing(3)
        layout.addLayout(self.parameters_layout)
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

                outer = QVBoxLayout()
                outer.setSpacing(1)

                row1 = QHBoxLayout()
                row1.setSpacing(4)
                param_label = QLabel(param)
                param_label.setStyleSheet("color: #4a505c;")
                row1.addWidget(param_label)
                row1.addWidget(spin_box)
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

    # --------------------------------------------------
    # Señales
    # --------------------------------------------------

    def _connect_signals(self):

        self.enable_checkbox.toggled.connect(
            self._on_enabled_changed
        )

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

        self.enable_checkbox.setChecked(
            self.tissue.enabled
        )

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

    def _on_enabled_changed(
        self,
        checked: bool
    ):

        self.tissue.enabled = checked

        self.configuration_changed.emit()

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
