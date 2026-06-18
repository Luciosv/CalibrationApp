import json

from PySide6.QtCore import (
    QObject,
    Signal,
    QUrl,
)

from PySide6.QtWebSockets import (
    QWebSocket,
)

from utils.json_manager import JsonManager


class WebSocketClient(QObject):

    connected = Signal()
    disconnected = Signal()
    error_occurred = Signal(str)

    def __init__(
        self,
        url: str = "ws://localhost:8080",
        parent=None,
    ):

        super().__init__(parent)

        self.url = url
        self.socket = QWebSocket()

        self.socket.connected.connect(
            self.connected
        )

        self.socket.disconnected.connect(
            self.disconnected
        )

    def connect_to_unity(self):

        self.socket.open(QUrl(self.url))

    def send_config(self, config):

        if self.socket.state() != QWebSocket.State.Connected:

            self.error_occurred.emit(
                "Not connected to Unity."
            )

            return

        data = JsonManager.export_for_unity(
            config
        )

        self.socket.sendTextMessage(
            json.dumps(data)
        )

    def disconnect(self):

        self.socket.close()
