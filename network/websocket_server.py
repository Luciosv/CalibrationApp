import json
import logging
import socket
import threading

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

DISCOVERY_PORT = 8766


def _get_local_ip() -> str:
    """Return the LAN IP used for outbound traffic (not 127.0.0.1)."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


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
        self._broadcast_stop = threading.Event()

        self._server.newConnection.connect(
            self._on_new_connection
        )

    # --------------------------------------------------
    # Ciclo de vida
    # --------------------------------------------------

    def start(self) -> bool:

        result = self._server.listen(
            QHostAddress.AnyIPv4,
            self.port,
        )

        if result:
            ip = _get_local_ip()
            logger.info(
                f"Server listening on ws://{ip}:{self.port} (all interfaces)"
            )
            self._start_broadcaster()
        else:
            logger.error(
                f"Failed to start: "
                f"{self._server.errorString()}"
            )

        return result

    def stop(self):

        self._broadcast_stop.set()

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

    def _start_broadcaster(self):
        """Broadcast UDP beacons so Unity auto-discovers this server's IP and port."""
        self._broadcast_stop.clear()
        payload = json.dumps(
            {"service": "CalibrationApp", "port": self.port}
        ).encode()

        def _loop():
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            while not self._broadcast_stop.wait(2.0):
                try:
                    sock.sendto(payload, ("255.255.255.255", DISCOVERY_PORT))
                except Exception:
                    pass
            sock.close()

        threading.Thread(target=_loop, daemon=True, name="WSBroadcaster").start()

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
