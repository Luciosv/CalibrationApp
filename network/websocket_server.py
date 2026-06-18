import json
import logging

from PySide6.QtCore import (
    QObject,
    Signal,
)

from PySide6.QtNetwork import (
    QAbstractSocket,
    QHostAddress,
)

from PySide6.QtWebSockets import (
    QWebSocket,
    QWebSocketServer,
)

from utils.json_manager import JsonManager


logger = logging.getLogger(__name__)


class WebSocketServer(QObject):

    client_connected = Signal()
    client_disconnected = Signal()
    error_occurred = Signal(str)

    def __init__(
        self,
        port: int = 8765,
        parent=None,
    ):

        super().__init__(parent)

        self.port = port

        self._server = QWebSocketServer(
            "CalibrationApp",
            QWebSocketServer.NonSecureMode,
            self,
        )

        self._clients: list[QWebSocket] = []

        self._server.newConnection.connect(
            self._on_new_connection
        )

    # --------------------------------------------------
    # Ciclo de vida
    # --------------------------------------------------

    def start(self) -> bool:

        result = self._server.listen(
            QHostAddress.LocalHost,
            self.port,
        )

        if result:
            logger.info(
                "Server listening on "
                f"ws://localhost:{self.port}"
            )
        else:
            logger.error(
                f"Failed to start: "
                f"{self._server.errorString()}"
            )

        return result

    def stop(self):

        for client in list(self._clients):
            client.close()
            client.deleteLater()

        self._clients.clear()
        self._server.close()

    # --------------------------------------------------
    # Estado
    # --------------------------------------------------

    @property
    def is_connected(self) -> bool:

        return any(
            c.state()
            == QAbstractSocket.SocketState.ConnectedState
            for c in self._clients
        )

    # --------------------------------------------------
    # Envío
    # --------------------------------------------------

    def send_config(self, config):

        data = JsonManager.export_for_unity(config)
        message = json.dumps(data)

        dead = []

        for client in self._clients:

            if (
                client.state()
                == QAbstractSocket.SocketState.ConnectedState
            ):
                client.sendTextMessage(message)
            else:
                dead.append(client)

        for client in dead:
            self._clients.remove(client)
            client.deleteLater()
            self.client_disconnected.emit()

        if not self._clients:
            self.error_occurred.emit(
                "No connected clients."
            )

    # --------------------------------------------------
    # Conexiones
    # --------------------------------------------------

    def _on_new_connection(self):

        client = self._server.nextPendingConnection()

        if client is None:
            return

        self._clients.append(client)

        client.disconnected.connect(
            lambda: self._on_client_disconnected(
                client
            )
        )

        logger.info(
            f"Client connected "
            f"({len(self._clients)} total)"
        )

        self.client_connected.emit()

    def _on_client_disconnected(
        self,
        client: QWebSocket,
    ):

        if client in self._clients:
            self._clients.remove(client)

        try:
            client.deleteLater()
        except RuntimeError:
            pass

        logger.info(
            f"Client disconnected "
            f"({len(self._clients)} remaining)"
        )

        self.client_disconnected.emit()
