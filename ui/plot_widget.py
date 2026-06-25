from PySide6.QtGui import QColor
from PySide6.QtWidgets import QWidget, QVBoxLayout

import pyqtgraph as pg

from maths.curve_generator import CurveGenerator


class PlotWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.plot = pg.PlotWidget()
        self.plot.setBackground("#F5F6FA")

        layout.addWidget(self.plot)

        # Grid
        self.plot.showGrid(
            x=True,
            y=True,
            alpha=0.3
        )

        # Ejes
        for axis_name in ["bottom", "left"]:
            axis = self.plot.getAxis(axis_name)
            axis.setTextPen(QColor("#1B1C22"))
            axis.setPen(QColor("#3A3B48"))

        # Etiquetas
        self.plot.setLabel(
            "bottom",
            "Depth (mm)",
        )

        self.plot.setLabel(
            "left",
            "Force (N)",
        )

        # Leyenda
        legend = self.plot.addLegend(
            brush="#F5F6FA",
            pen=pg.mkPen("#3A3B48", width=1),
        )
        legend.setLabelTextColor("#1B1C22")

        # Borde del viewport
        self.plot.getPlotItem().getViewBox().setBorder(
            pg.mkPen("#3A3B48", width=1)
        )

        # Curva principal
        self.curve_item = self.plot.plot(
            [],
            [],
            name="Fitted curve",
            pen=pg.mkPen(
                "#D4783C",
                width=3
            )
        )

        # Curva de referencia
        self.reference_curve_item = self.plot.plot(
            [],
            [],
            name="Reference curve",
            pen=pg.mkPen(
                "#7A7D8E",
                width=2,
                style=pg.QtCore.Qt.DashLine
            )
        )

        # Elementos dinámicos
        self.region_items = []
        self.text_items = []
        self.line_items = []

    # --------------------------------------------------
    # Limpieza
    # --------------------------------------------------

    def clear_regions(self):

        for item in self.region_items:
            self.plot.removeItem(item)

        for item in self.text_items:
            self.plot.removeItem(item)

        for item in self.line_items:
            self.plot.removeItem(item)

        self.region_items.clear()
        self.text_items.clear()
        self.line_items.clear()

    # --------------------------------------------------
    # Actualización
    # --------------------------------------------------

    def update_plot(self, config, reference_config=None):

        self.clear_regions()

        x, y = CurveGenerator.generate(config)

        max_force = max(
            10,
            float(y.max()) * 1.15
        )

        self.plot.setYRange(
            0,
            max_force
        )

        self.curve_item.setData(x, y)

        self._draw_regions(config, max_force)
        
        if reference_config is not None:
            ref_x, ref_y = (
                CurveGenerator.generate(
                    reference_config
                )
            )
        
            self.reference_curve_item.setData(
                ref_x,
                ref_y
            )       
        
        else: self.reference_curve_item.clear()

    # --------------------------------------------------
    # Regiones anatómicas
    # --------------------------------------------------

    def _draw_regions(self, config, max_force=10):

        regions = CurveGenerator.get_regions(
            config
        )

        for region in regions:

            start = region["start"]
            end = region["end"]

            tissue = config.get_tissue(
                region["name"]
            )

            # Fondo coloreado
            rect = pg.QtWidgets.QGraphicsRectItem(
                start,
                0,
                end - start,
                max_force
            )

            color = pg.mkColor(
                tissue.color
            )

            color.setAlpha(50)

            rect.setBrush(color)

            rect.setPen(
                pg.mkPen(None)
            )

            self.plot.addItem(rect)

            self.region_items.append(rect)

            # Línea divisoria

            line = pg.InfiniteLine(
                pos=end,
                angle=90,
                pen=pg.mkPen(
                    "#4B4D5E",
                    width=1,
                    style=pg.QtCore.Qt.DashLine
                )
            )

            self.plot.addItem(line)

            self.line_items.append(line)

            # Texto

            text = pg.TextItem(
                text=region["name"],
                anchor=(0.5, 0),
                color="#1B1C22",
            )

            text.setRotation(90)

            center_x = (
                start + end
            ) / 2

            text.setPos(
                center_x,
                max_force * 0.97
            )

            self.plot.addItem(text)

            self.text_items.append(text)