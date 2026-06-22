from PySide6.QtCore import Signal

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QCheckBox,
    QDoubleSpinBox,
    QComboBox,
    QGroupBox,
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

        self.setTitle(tissue.name)

        self.param_spinboxes = []

        self._build_ui()

        self.refresh_from_model()

        self._connect_signals()

    # --------------------------------------------------
    # UI
    # --------------------------------------------------

    def _build_ui(self):

        layout = QVBoxLayout(self)

        # Enable

        self._create_enabled_checkbox(layout)

        # Depth

        self._create_depth_spinbox(layout)

        # Family

        self._create_family_combobox(layout)
        
        # Parameters
        self._create_parameters_widgets(layout)
        
    
    def _create_enabled_checkbox(self, layout):

        self.enable_checkbox = QCheckBox(
            "Enabled"
        )

        layout.addWidget(
            self.enable_checkbox
        )
    
    
    def _create_depth_spinbox(self, layout):

        depth_layout = QHBoxLayout()

        depth_layout.addWidget(
            QLabel("End Depth (mm)")
        )

        self.depth_spin = QDoubleSpinBox()

        self.depth_spin.setRange(0.1, 1000)
        self.depth_spin.setDecimals(6)
        self.depth_spin.setSingleStep(0.1)

        depth_layout.addWidget(
            self.depth_spin
        )

        layout.addLayout(
            depth_layout
        )
    
    
    def _create_family_combobox(self, layout):
        family_layout = QHBoxLayout()

        family_layout.addWidget(
            QLabel("Family")
        )

        self.family_combo = QComboBox()

        self.family_combo.addItems(
            sorted(FORMULAS.keys())
        )

        family_layout.addWidget(
            self.family_combo
        )

        layout.addLayout(
            family_layout
        )
    
    
    def _create_parameters_widgets(self, layout):
        self.parameters_layout = QVBoxLayout()
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
                sub = item.layout()
                while sub.count():
                    sub_item = sub.takeAt(0)
                    if sub_item.widget() is not None:
                        sub_item.widget().setVisible(False)
                        sub_item.widget().deleteLater()
                sub.deleteLater()

    def rebuild_parameter_widgets(self):
        TissueWidget._clear_layout(
            self.parameters_layout
        )

        self.param_spinboxes.clear()

        # Add new widgets based on the selected family
        formula_class = FORMULAS.get(self.tissue.family)

        if formula_class is not None:
            for i in range(len(formula_class.parameter_names)):
                param_layout = QHBoxLayout()
                param = formula_class.parameter_names[i]

                param_layout.addWidget(
                    QLabel(param)
                )

                spin_box = QDoubleSpinBox()
                lim_inf, lim_sup = formula_class.bounds[i]
                spin_box.setRange(lim_inf, lim_sup)
                spin_box.setDecimals(6)
                spin_box.setSingleStep(0.1)

                # Set current value from the tissue model
                current_value = self.tissue.parameters[i].value
                spin_box.setValue(current_value)

                # Connect signal to update the tissue model when changed
                spin_box.valueChanged.connect(
                    lambda value, p=param: self._on_parameter_changed(p, value)
                )

                param_layout.addWidget(spin_box)

                self.parameters_layout.addLayout(param_layout)

                self.param_spinboxes.append(spin_box)

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

        self.depth_spin.valueChanged.connect(
            self._on_depth_changed
        )

    # --------------------------------------------------
    # Modelo -> UI
    # --------------------------------------------------

    def refresh_from_model(self):

        self.enable_checkbox.setChecked(
            self.tissue.enabled
        )

        self.family_combo.blockSignals(True)
        self.family_combo.setCurrentText(
            self.tissue.family
        )
        self.family_combo.blockSignals(False)

        if len(self.param_spinboxes) != len(self.tissue.parameters):
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

        self.depth_spin.setValue(
            self.tissue.end_depth
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

        self.tissue.family = family
        param_names = FORMULAS[family].parameter_names
        param_values = get_default_params(family)
        self.tissue.parameters = [
            Parameter(name=n, value=v, delta=0.01)
            for n, v in zip(param_names, param_values)
        ]
        self.rebuild_parameter_widgets()
        self.configuration_changed.emit()

    def _on_depth_changed(
        self,
        new_end_depth: float
    ):

        start_depth = self.tissue.start_depth

        self.tissue.thickness = max(
            0.1,
            new_end_depth - start_depth
        )

        self.configuration_changed.emit()

    def _on_parameter_changed(self, param_name: str, value: float):
        for p in self.tissue.parameters:
            if p.name == param_name:
                p.value = value
                break
        self.configuration_changed.emit()