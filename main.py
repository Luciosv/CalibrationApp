import sys

from PySide6.QtWidgets import QApplication, QStyleFactory
from PySide6.QtGui import QPalette, QColor


def main():

    app = QApplication(sys.argv)

    app.setStyle(QStyleFactory.create("Fusion"))

    palette = QPalette()
    palette.setColor(QPalette.Window, QColor("#1B1C22"))
    palette.setColor(QPalette.WindowText, QColor("#E4E5EC"))
    palette.setColor(QPalette.Base, QColor("#2E303A"))
    palette.setColor(QPalette.AlternateBase, QColor("#25262E"))
    palette.setColor(QPalette.ToolTipBase, QColor("#2E303A"))
    palette.setColor(QPalette.ToolTipText, QColor("#E4E5EC"))
    palette.setColor(QPalette.Text, QColor("#E4E5EC"))
    palette.setColor(QPalette.Button, QColor("#25262E"))
    palette.setColor(QPalette.ButtonText, QColor("#E4E5EC"))
    palette.setColor(QPalette.BrightText, QColor("#E53935"))
    palette.setColor(QPalette.Link, QColor("#D4783C"))
    palette.setColor(QPalette.Highlight, QColor("#D4783C"))
    palette.setColor(QPalette.HighlightedText, QColor("#FFFFFF"))
    palette.setColor(QPalette.Disabled, QPalette.Text, QColor("#63657A"))
    palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor("#63657A"))
    app.setPalette(palette)

    app.setStyleSheet("""
        QToolTip {
            background-color: #2E303A;
            color: #E4E5EC;
            border: 1px solid #3A3B48;
            padding: 6px;
            font-size: 12px;
        }

        QSplitter::handle {
            background-color: #3A3B48;
            width: 2px;
        }
    """)

    from ui.main_window import MainWindow

    window = MainWindow()

    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
