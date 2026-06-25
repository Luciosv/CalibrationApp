from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QCheckBox,
    QFrame,
    QScrollArea,
    QSizePolicy,
)


class _TissueRow(QFrame):

    clicked = Signal(int)
    toggled = Signal(int, bool)

    def __init__(self, index: int, name: str, color: str,
                 start_depth: float, end_depth: float, enabled: bool):
        super().__init__()

        self._index = index
        self._selected = False
        self._hovered = False

        self.setFixedHeight(38)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setObjectName("TissueRow")

        row = QHBoxLayout(self)
        row.setContentsMargins(6, 2, 6, 2)
        row.setSpacing(8)

        self.swatch = QFrame()
        self.swatch.setFixedSize(14, 14)
        self.swatch.setStyleSheet(
            f"background-color: {color}; "
            "border: 1px solid #4B4D5E; border-radius: 3px;"
        )
        row.addWidget(self.swatch)

        self.checkbox = QCheckBox("")
        self.checkbox.setChecked(enabled)
        self.checkbox.setToolTip("Enable/disable this tissue")
        row.addWidget(self.checkbox)

        self.name_label = QLabel(name)
        self.name_label.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Preferred
        )
        row.addWidget(self.name_label)

        self.depth_label = QLabel(
            f"{start_depth:.1f}–{end_depth:.1f}"
        )
        self.depth_label.setStyleSheet("color: #63657A; font-size: 11px;")
        row.addWidget(self.depth_label)

        self.checkbox.toggled.connect(self._on_toggled)

    def _on_toggled(self, checked: bool):
        self.toggled.emit(self._index, checked)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.clicked.emit(self._index)

    def enterEvent(self, event):
        super().enterEvent(event)
        self._hovered = True
        self._update_style()

    def leaveEvent(self, event):
        super().leaveEvent(event)
        self._hovered = False
        self._update_style()

    def _update_style(self):
        if self._selected:
            self.setStyleSheet(
                "#TissueRow { background: #D4783C; border-radius: 4px; }"
            )
            self.name_label.setStyleSheet(
                "color: #FFFFFF; font-weight: 600;"
            )
        elif self._hovered:
            self.setStyleSheet(
                "#TissueRow { background: #2E303A; border-radius: 4px; }"
            )
            self.name_label.setStyleSheet("color: #E4E5EC;")
        else:
            self.setStyleSheet("")
            self.name_label.setStyleSheet("color: #E4E5EC;")

    def set_selected(self, selected: bool):
        self._selected = selected
        self._update_style()

    def update_depth(self, start: float, end: float):
        self.depth_label.setText(f"{start:.1f}–{end:.1f}")


class TissueListWidget(QWidget):

    tissue_selected = Signal(int)
    tissue_toggled = Signal(int, bool)

    def __init__(self, tissues: list, parent=None):
        super().__init__(parent)

        self._rows: list[_TissueRow] = []
        self._selected_index = 0

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(1)

        header = QLabel("TISSUES")
        header.setStyleSheet(
            "font-weight: 600; padding: 6px 12px; "
            "background: #25262E; color: #9395A8; font-size: 11px;"
        )
        layout.addWidget(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        self._container = QWidget()
        self._rows_layout = QVBoxLayout(self._container)
        self._rows_layout.setContentsMargins(2, 2, 2, 2)
        self._rows_layout.setSpacing(1)
        self._rows_layout.addStretch()

        scroll.setWidget(self._container)
        layout.addWidget(scroll)

        self.build_rows(tissues)

    def build_rows(self, tissues: list):
        for row in self._rows:
            row.setVisible(False)
            row.deleteLater()
        self._rows.clear()

        # Remove stretch, rebuild, re-add stretch
        stretch = self._rows_layout.takeAt(
            self._rows_layout.count() - 1
        )

        for i, tissue in enumerate(tissues):
            row = _TissueRow(
                index=i,
                name=tissue.name,
                color=tissue.color,
                start_depth=tissue.start_depth,
                end_depth=tissue.end_depth,
                enabled=tissue.enabled,
            )
            row.clicked.connect(self._on_row_clicked)
            row.toggled.connect(self.tissue_toggled.emit)
            self._rows_layout.addWidget(row)
            self._rows.append(row)

        self._rows_layout.addStretch()

        self._update_selection()

    def _on_row_clicked(self, index: int):
        self._selected_index = index
        self._update_selection()
        self.tissue_selected.emit(index)

    def set_selected(self, index: int):
        if 0 <= index < len(self._rows):
            self._selected_index = index
            self._update_selection()

    def _update_selection(self):
        for i, row in enumerate(self._rows):
            row.set_selected(i == self._selected_index)

    def refresh_rows(self, tissues: list):
        for i, tissue in enumerate(tissues):
            if i < len(self._rows):
                self._rows[i].update_depth(
                    tissue.start_depth, tissue.end_depth
                )
                self._rows[i].checkbox.blockSignals(True)
                self._rows[i].checkbox.setChecked(tissue.enabled)
                self._rows[i].checkbox.blockSignals(False)
