from PySide6.QtCore import Qt, Signal, QRectF
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QColor, QFontMetrics, QPen, QFont


class DepthBarWidget(QWidget):

    tissue_clicked = Signal(int)

    def __init__(self, tissues: list, parent=None):
        super().__init__(parent)

        self._tissues = tissues
        self.setFixedHeight(36)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMouseTracking(True)

        self._hovered_index = -1

    def update_tissues(self, tissues: list):
        self._tissues = tissues
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)

        painter = QPainter(self)
        rect = self.rect()
        bar_rect = rect.adjusted(8, 4, -8, -14)

        active = [t for t in self._tissues if t.enabled]

        if not active:
            painter.setPen(QColor("#4a505c"))
            painter.drawText(
                rect, Qt.AlignmentFlag.AlignCenter,
                "No active tissues"
            )
            return

        total_depth = sum(t.thickness for t in active)
        if total_depth <= 0:
            return

        x = bar_rect.x()
        y = bar_rect.y()
        h = bar_rect.height()
        bw = bar_rect.width()

        font = QFont()
        font.setPointSize(8)
        painter.setFont(font)
        fm = QFontMetrics(font)

        num_active = len(active)
        seg_w = bw / num_active

        for i, tissue in enumerate(active):
            w = seg_w
            is_hovered = (i == self._hovered_index)

            color = QColor(tissue.color)

            r = QRectF(x, y, w, h)

            if is_hovered:
                painter.fillRect(r, color.lighter(140))
            else:
                painter.fillRect(r, color)

            painter.setPen(QPen(QColor("#444"), 1))
            painter.drawRect(r)

            show_label = is_hovered and w < 30
            if w > 30 or show_label:
                painter.setPen(QColor("#222"))
                text = tissue.name

                max_text_w = w - 4 if w > 30 else 200
                while (
                    fm.horizontalAdvance(text) > max_text_w
                    and len(text) > 2
                ):
                    text = text[:-1]
                if (
                    fm.horizontalAdvance(text + "…") < max_text_w
                    and text != tissue.name
                ):
                    text += "…"

                if show_label:
                    label_w = fm.horizontalAdvance(text) + 4
                    label_x = max(
                        bar_rect.x(),
                        min(
                            x + w / 2 - label_w / 2,
                            bar_rect.right() - label_w,
                        ),
                    )
                    painter.setPen(QPen(QColor("#444"), 1))
                    painter.drawRect(
                        int(label_x), int(y - fm.height() - 4),
                        int(label_w), fm.height()
                    )
                    painter.drawText(
                        int(label_x), int(y - fm.height() - 4),
                        int(label_w), fm.height(),
                        Qt.AlignmentFlag.AlignCenter,
                        text,
                    )
                else:
                    painter.drawText(
                        r.adjusted(2, 0, -2, 0),
                        Qt.AlignmentFlag.AlignLeft
                        | Qt.AlignmentFlag.AlignVCenter,
                        text,
                    )

            depth_label = f"{tissue.start_depth:.1f}"
            label_w = fm.horizontalAdvance(depth_label)
            label_x = max(bar_rect.x(), x - label_w // 2)

            painter.setPen(QColor("#4a505c"))
            painter.drawText(
                int(label_x), y + h + 2,
                int(label_w), fm.height(),
                Qt.AlignmentFlag.AlignLeft,
                depth_label,
            )

            x += w

        last_depth = f"{active[-1].end_depth:.1f}"
        lw = fm.horizontalAdvance(last_depth)
        lx = min(bar_rect.right() - lw, x - lw // 2)
        painter.setPen(QColor("#4a505c"))
        painter.drawText(
            int(lx), y + h + 2,
            int(lw), fm.height(),
            Qt.AlignmentFlag.AlignLeft,
            last_depth,
        )

        painter.end()

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        idx = self._index_at_pos(event.position().x())
        if idx != self._hovered_index:
            self._hovered_index = idx
            self.update()
            if idx >= 0:
                active = [t for t in self._tissues if t.enabled]
                if idx < len(active):
                    t = active[idx]
                    self.setToolTip(
                        f"{t.name}: {t.start_depth:.1f}–"
                        f"{t.end_depth:.1f} mm "
                        f"({t.thickness:.1f} mm)"
                    )
            else:
                self.setToolTip("")

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if event.button() == Qt.MouseButton.LeftButton:
            index = self._index_at_pos(event.position().x())
            if index >= 0:
                active_count = 0
                for i, t in enumerate(self._tissues):
                    if t.enabled:
                        if active_count == index:
                            self.tissue_clicked.emit(i)
                            return
                        active_count += 1

    def leaveEvent(self, event):
        super().leaveEvent(event)
        self._hovered_index = -1
        self.setToolTip("")
        self.update()

    def _index_at_pos(self, px: float) -> int:
        bar_left = 8
        bar_width = self.width() - 16
        if bar_width <= 0:
            return -1

        active = [t for t in self._tissues if t.enabled]
        if not active:
            return -1

        rel_x = px - bar_left
        if rel_x < 0:
            return -1

        seg_w = bar_width / len(active)
        idx = int(rel_x / seg_w)
        return min(idx, len(active) - 1)
