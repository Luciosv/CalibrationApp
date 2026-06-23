# Needle Calibration App — Design System MASTER

> Internal tool — PySide6 desktop app for calibrating mechanical parameters of biological tissues for a Unity lumbar-puncture simulator.

---

## 1. Layout Architecture

```
┌──────────────────────────────────────────────────┐
│  Toolbar  [Load] [Restore] │ [Send] │ [Export..] │ ● Connected  │
├────────────────────────────┬─────────────────────┤
│                            │  Depth bar (36px)   │
│                            │  Total: 31.1mm 9/10 │
│       Plot (2/3 width)     ├────────┬────────────┤
│                            │ Tissue │ Detail     │
│                            │ List   │ (Stacked)  │
│                            │        │            │
└──────────────────────────────────────────────────┘
```

### Colors & Backgrounds
- **Right panel**: `#eef0f2` background (via objectName `#rightPanel`)
- **TissueWidget cards**: `#f6f7f9` background, `1px solid #d4d6d9` border, 4px border-radius
- **TissueList**: no background (inherits `#eef0f2`); rows use system palette selection

### Ratios
- **Plot : Right panel** = 2 : 1 (stretch factors in `QHBoxLayout`)
- **TissueList : DetailStack** = 150 : 350 px (initial `QSplitter` sizes)

### Files
| File | Role |
|------|------|
| `ui/main_window.py` | QMainWindow: orchestrates toolbar, plot, right panel |
| `ui/plot_widget.py` | PyQtGraph plot: curve + reference + regions |
| `ui/tissue_widget.py` | Per-tissue editor (depth, family, params, sliders) |
| `ui/tissue_list_widget.py` | Compact row list of all tissues (swatch + name + depth) |
| `ui/depth_bar_widget.py` | Horizontal colored bar, proportional to thickness, clickable |

---

## 2. Color System

### Tissue Colors (config/tissues.py)

Each tissue has a distinct color used in:
- **Depth bar** (full opacity on white background)
- **Plot regions** (alpha=40 overlay)
- **Tissue list swatch** (12×12 QFrame)

```
Outside          #E8E0D0  warm beige
Skin             #F4C2C2  pink
Fat              #FFE066  golden yellow
Muscle           #7FB8E0  steel blue
Supraspinous Lig #FDBF6F  orange
Interspinous Lig #B2DF8A  green
Ligamentum Flav  #CAB2D6  lavender
Epidural Space   #A6CEE3  sky blue
Dura Mater       #FB9A99  salmon
Subarachnoid     #D9D9F0  periwinkle
```

**Rules:**
- No two tissues share the same color
- No pure white (`#FFFFFF`) — invisible on light backgrounds
- All colors must be distinguishable in both full opacity and alpha=40
- When adding a new tissue, pick a hue not already used in the list

### Semantic Colors (inline)

| Element | Hex | Usage | Where |
|---------|-----|-------|-------|
| Panel bg | `#eef0f2` | Right panel background | `main_window.py` |
| Card bg | `#f6f7f9` | TissueWidget card background | `tissue_widget.py` |
| Header bg | `#dce0e5` | TissueList header | `tissue_list_widget.py` |
| Hover bg | `#e2e4e8` | TissueList row hover | `tissue_list_widget.py` |
| Card border | `#d4d6d9` | Dividers, panel borders | various |
| Accent blue | `#2563eb` | Fitted curve line in plot | `plot_widget.py` |
| Ref curve | `#9ca3af` | Reference curve line | `plot_widget.py` |
| Primary text | `#1a1d23` | Tissue names, labels | `tissue_widget.py` |
| Secondary text | `#4a505c` | Depth labels, property labels | various |
| Muted text | `#8b92a0` | Units, thickness hints | `tissue_widget.py` |
| Spinbox text | `#1a1d23` | QDoubleSpinBox values | `tissue_widget.py` |

### Plot Regions
- Region backgrounds use tissue color at `alpha=50`
- Dividing lines: gray dashed at `alpha=100`
- Text labels: rotated 90°, positioned at top of region

---

## 3. Typography

| Context | Size | Weight | Color | Where |
|---------|------|--------|-------|-------|
| Body text | default (QWidget) | Normal | `#1a1d23` | All labels |
| Depth bar labels | 8pt | Normal | `#4a505c` | `depth_bar_widget.py` |
| Depth totals | 8pt | Normal | `#1a1d23` | `depth_bar_widget.py` |
| TissueList header | 12px | Bold | `#1a1d23` | `tissue_list_widget.py` |
| Tissue name in widget | 13px | Bold | `#1a1d23` | `tissue_widget.py` |
| Connection status | default | Bold | green/red | `main_window.py` |
| Property labels | default | Normal | `#4a505c` | `tissue_widget.py` |
| Parameter labels | default | Normal | `#4a505c` | `tissue_widget.py` |
| Muted text | 11px | Normal | `#8b92a0` | `tissue_widget.py` |
| Depth bar labels | 8pt | Normal | `#4a505c` | `depth_bar_widget.py` |

- **Font**: System default (Qt resolves per-platform)
- **No custom fonts** loaded

---

## 4. Component Library

### 4.1 Toolbar
- **File**: `main_window.py:_create_toolbar()`
- **Style**: `ToolButtonTextBesideIcon` (icons + text)
- **Icons**: `QStyle.StandardPixmap` (system theme)
  - Load Reference → `SP_DialogOpenButton`
  - Restore Defaults → `SP_RestoreDefaultsButton`
  - Send to Unity → `SP_ArrowForward`
  - Export JSON → `SP_DialogSaveButton`
  - Export CSV → `SP_FileDialogDetailedView`
- **Shortcuts**: Ctrl+S (Send), Ctrl+E (Export), Ctrl+R (Restore), Ctrl+L (Load)

### 4.2 Depth Bar (replaces old Totals Bar)
- **File**: `depth_bar_widget.py`
- **Height**: 36px fixed
- **Content**: Colored segments of **equal width** (1/N per active tissue, regardless of thickness)
- **Interaction**: Click → selects tissue. Hover → tooltip + label popup for narrow segments
- **Labels**: Depth values at each segment boundary (bottom, `#4a505c`)
- **Total overlay**: Right-aligned text `Total: X.XXmm  A/B  MSE: ...` drawn in `#1a1d23` at bottom of bar (via `set_totals()`)
- **Small segments** (<30px): show name only on hover, as a label above the bar

### 4.4 Tissue List
- **File**: `tissue_list_widget.py`
- **Row height**: 38px fixed
- **Row content**: [color swatch 14×14] [checkbox] [name] [start–end depth]
- **Selection**: Click row → highlighted (system palette). Only one selected at a time.
- **Hover**: `background: #e2e4e8` on non-selected rows
- **Header bg**: `#dce0e5`
- **Signal**: `tissue_selected(int)`, `tissue_toggled(int, bool)`

### 4.5 Tissue Widget (Detail View)
- **File**: `tissue_widget.py`
- **Parent**: QGroupBox styled as card (`border: 1px solid #d4d6d9; border-radius: 4px; background: #f6f7f9;`)
- **Children**:
  1. **Header row**: [color swatch 14×14] [tissue name (bold, `#1a1d23`)] ── [Enabled checkbox]
  2. **Properties** (indented 16px):
     - Depth: `0.00 → [end spinbox] mm (thickness mm)` — labels `#4a505c`, units `#8b92a0`
     - Family: dropdown (categorized: Simple / Rupture / Polynomial / Exponential)
  3. **Separator line** (HLine, `#d4d6d9`)
  4. **Parameters**: Per-param 2 rows
     - Row 1: `[label `#4a505c`] [value spinbox `#1a1d23`] [Δ delta]`
     - Row 2: `[============ slider ============]`
- **Slider**: Scaled by ×10000, range = formula bounds. Updates model on drag.
- **Signals**: `editingFinished` on spinbox (not `valueChanged`) to avoid recalculation while typing
- **QDoubleSpinBox**: Explicitly styled `color: #1a1d23; background: #ffffff;`

### 4.6 Plot
- **File**: `plot_widget.py`
- **Library**: PyQtGraph
- **Content**: Fitted curve (blue, 3px), Reference curve (gray dashed, 2px)
- **Regions**: Colored backgrounds + dashed dividing lines + rotated tissue labels
- **Grid**: Both axes, alpha=0.2
- **Labels**: Depth (mm) on X, Force (N) on Y

---

## 5. Interaction Patterns

### Editing Parameters
1. User types in spinbox → **no curve update while typing**
2. User presses Enter or clicks elsewhere → `editingFinished` fires
3. → Model updates → `configuration_changed` emitted → `refresh_everything` called
4. **Sliders**: `valueChanged` fires on every drag → real-time curve feedback
5. **Delta spinbox**: `valueChanged` → adjusts step size AND decimal places of the value spinbox

### Family Change
1. User selects formula from categorized combo
2. `_on_family_changed_by_user` checks `family in FORMULAS` (ignores category headers)
3. Resets parameters to defaults → `rebuild_parameter_widgets()`
4. Emits `configuration_changed`

### Tissue Selection Flow
```
DepthBar click  ─┐
                  ├──→ _on_tissue_selected(index) → detail_stack.setCurrentIndex(index)
TissueList click ─┘
```

### Enable/Disable Toggle
- From TissueList checkbox → `_on_tissue_toggled(index, bool)` → model update → `update_depths()` → `refresh_everything()`
- From TissueWidget checkbox → `_on_enabled_changed(bool)` → same chain
- No duplicated events (deep bar ignores disabled tissues)

---

## 6. Data Flow

```
User input → TissueWidget signal
  → MainWindow.on_configuration_changed()
    → SimulationConfig.update_depths()
    → refresh_everything()
      → [each widget].refresh_from_model()   [sync UI ← model]
      → TissueList.refresh_rows()
      → DepthBar.update_tissues()
      → ReferenceManager.sync_from_config()
      → PlotWidget.update_plot()
      → TotalsBar update
```

### Key Rule: Signal Blocking
- `refresh_from_model()` is always wrapped in `blockSignals(True/False)` on the widget
- Individual spinboxes/sliders are also blocked individually inside `refresh_from_model`
- Exception: **`blockSignals` on a parent does NOT block child widgets** — each child must be blocked individually

---

## 7. Responsive Behavior

- **Window**: Default 1600×900
- **Plot resizes** with window (stretch factor 2)
- **Right panel width** controlled by `mid_splitter.setSizes([150, 350])`
- **No mobile/responsive breakpoints** (desktop-only internal tool)

---

## 8. Known Issues & Future Work

### Open Issues
1. **Depth bar segment collision**: Very small tissues (1mm) produce tiny segments. Current fix: hover label. Future: minimum segment width?
2. **MSE comparison**: Currently compares curves point-by-point at same length. Should interpolate reference at fitted x-points for accurate MSE.
3. **Color contrast in plot regions**: With alpha=40, light colors are barely visible as region backgrounds. Consider increasing alpha or adding pattern fills.
4. **Slider performance**: Continuous slider drag triggers full curve regeneration. For complex formulas with many tissues, this could be slow. Consider debounce-off.
5. **Undo/Redo**: Not implemented. Any parameter change is permanent until "Restore Defaults".
6. **Keyboard navigation in TissueList**: Currently only mouse click. No arrow-key navigation between rows.

### Future UI Improvements
1. Sparkline per tissue in the detail view (mini graph of individual force curve)
2. "Compare mode" — overlay two configs
3. Snapshot save/load (named configs)
4. Fitting assistant — auto-tune parameters to match reference
5. Dark mode toggle (system-wide CSS switch)

---

## 9. Rules for Extension

### Adding a New Formula
1. Create evaluator function in `config/formulas.py`
2. Add `FormulaDefinition` to `FORMULAS` dict
3. Add formula to the categorized combo in `tissue_widget.py:_create_family_combobox()`
4. Done — UI auto-generates spinboxes from `parameter_names` and `bounds`

### Adding a New Tissue
1. Add `TissueDefinition` to `DEFAULT_TISSUES` in `config/tissues.py`
2. Choose a **unique color** not used by any other tissue (see color list in §2)
3. Ensure the tissue name matches exactly between `reference.json` and `DEFAULT_TISSUES`

### Adding a New UI Component
1. Place file in `ui/` directory
2. Follow signal naming: custom signals use `snake_case`, connected in `main_window.py`
3. If adding new spinbox/slider: use `editingFinished` for typed inputs, `valueChanged` for drag inputs
4. Always wrap `setValue()` calls in `blockSignals(True/False)` if called from `refresh_from_model()`

---

## 10. File Index

| Path | Purpose | Key Classes/Functions |
|------|---------|----------------------|
| `main.py` | Entry point | — |
| `config/formulas.py` | Formula definitions + registry | `FormulaDefinition`, `FORMULAS` |
| `config/tissues.py` | Default tissue definitions | `TissueDefinition`, `DEFAULT_TISSUES` |
| `models/parameter.py` | Parameter dataclass | `Parameter` |
| `models/tissue.py` | Tissue dataclass | `Tissue` |
| `models/simulation_config.py` | Full app state | `SimulationConfig` |
| `maths/curve_generator.py` | Force-depth curve generation | `CurveGenerator` |
| `network/websocket_server.py` | QWebSocket server | `WebSocketServer` |
| `ui/main_window.py` | Main window + toolbar + layout | `MainWindow` |
| `ui/plot_widget.py` | PyQtGraph plot | `PlotWidget` |
| `ui/tissue_widget.py` | Per-tissue editor | `TissueWidget` |
| `ui/tissue_list_widget.py` | Compact tissue list | `TissueListWidget`, `_TissueRow` |
| `ui/depth_bar_widget.py` | Depth visualization bar | `DepthBarWidget` |
| `utils/json_manager.py` | JSON/CSV load/save | `JsonManager` |
| `utils/reference_manager.py` | Reference curve handling | `ReferenceManager` |
