# AGENTS.md — CalibrationApp

## Project

PySide6 desktop app to calibrate mechanical parameters of biological tissues for a Unity lumbar-puncture simulator. Internal development tool, not user-facing.

## Structure

```
App/
├── main.py                   # Entry point: python main.py
├── config/
│   ├── formulas.py           # Formula definitions + FORMULAS registry
│   └── tissues.py            # DEFAULT_TISSUES (10 tissues)
├── models/
│   ├── parameter.py          # Parameter dataclass (name, value, delta)
│   ├── tissue.py             # Tissue dataclass (name, thickness, family, parameters[])
│   └── simulation_config.py  # Full state: list[Tissue], depth calculation
├── maths/
│   └── curve_generator.py    # Generate force-depth curve from config
├── network/
│   └── websocket_server.py   # QWebSocketServer on localhost:8765
├── ui/
│   ├── main_window.py        # QMainWindow: toolbar, plot (left), params (right)
│   ├── plot_widget.py        # PyQtGraph plot: curve + reference + regions
│   └── tissue_widget.py      # Per-tissue parameter editor (QGroupBox)
├── utils/
│   ├── json_manager.py       # JSON/CSV load/save/export
│   └── reference_manager.py  # Loads reference.json as SimulationConfig
├── data/
│   └── reference.json        # Auto-loaded reference curve on startup
└── tests/                    # Manual test scripts (no test framework)
    ├── test_model.py
    ├── test_plot_widget.py
    └── test_pyqtgraph.py
```

## Run

```powershell
.venv\Scripts\python.exe main.py
```

Dependencies: PySide6, PyQtGraph, numpy (see requirements.txt).

## Architecture rules

- **Adding a formula**: create the function in `config/formulas.py`, register a `FormulaDefinition` in `FORMULAS`. UI auto-generates from the definition. No UI code changes needed.
- **Parameters live in `tissue.parameters[]`** (list of `Parameter` objects), NOT as `tissue` attributes. Never use `getattr(tissue, param_name)`.
- **`rebuild_parameter_widgets()`** destroys and recreates spinboxes. Called on user family change (`_on_family_changed_by_user`) or by `refresh_from_model()` when `len(param_spinboxes) != len(tissue.parameters)`. Always wrap in `blockSignals(True)` on the widget when calling programmatically to prevent `configuration_changed` loops.
- **Family change flow**: `_on_family_changed_by_user` is connected to the combo box signal and **resets parameters to defaults**. Loading from JSON goes through `JsonManager.load_json()` which sets `tissue.parameters` directly. `refresh_from_model()` always uses `blockSignals(True)` on `family_combo` to prevent triggering `_on_family_changed_by_user`, and compares spinbox count vs param count to decide rebuild vs in-place update.
- **WebSocket**: Python is server (QWebSocketServer), Unity is client. Listens on `localhost:8765`. No handshake, no ACK, no keepalive. Send-only from Python.
- **Reference**: `data/reference.json` loads automatically on startup and populates the editing config.
- **`SimulationConfig`** uses `@dataclass(slots=True)`. Default tissues built in `_build_default_tissues()`. Depths recalculated via `update_depths()`.
- **Plot regions**: drawn from `CurveGenerator.get_regions()` — colored backgrounds, dashed lines, rotated labels per tissue.

## Critical pitfalls

- `QWebSocket.State.Connected` does not exist in PySide6. Use `QAbstractSocket.SocketState.ConnectedState` from `PySide6.QtNetwork`.
- `blockSignals(True)` on a parent widget does NOT block child widget signals. Block each QDoubleSpinBox individually when setting values from model.
- `deleteLater()` is deferred. Call `setVisible(False)` before `deleteLater()` to prevent visual overlap during cleanup.
- `blockSignals(True)` on `family_combo` in `refresh_from_model()` is required; otherwise `setCurrentText()` triggers `_on_family_changed_by_user` and overwrites loaded parameters with defaults.
- Name mismatch between `reference.json` and `DEFAULT_TISSUES` caused silent load failures. Names must match exactly.
- `_clear_layout()` must recursively handle sub-layouts (QHBoxLayout inside QVBoxLayout) because `item.widget()` is None for layout items.

## Extension points

| What | Where | How |
|------|-------|-----|
| New formula | `config/formulas.py` | Create evaluator fn + add `FormulaDefinition` to `FORMULAS` |
| New tissue | `config/tissues.py` | Add `TissueDefinition` to `DEFAULT_TISSUES` |
| New export format | `utils/json_manager.py` | Add static method, wire button in `ui/main_window.py` |

## Testing

No test framework (no pytest). Test scripts are standalone Python files run directly:
```powershell
.venv\Scripts\python.exe tests\test_model.py
```
To verify a change: create `QApplication`, instantiate the class, exercise it, call `app.processEvents()` or use `QEventLoop` for async operations.
