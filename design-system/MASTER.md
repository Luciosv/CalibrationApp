# Needle Calibration App — Design System MASTER

> Internal tool — PySide6 desktop app for calibrating mechanical parameters of biological tissues for a Unity lumbar-puncture simulator.

---

## Design Philosophy: Instrument Panel

A precision calibration workbench. The UI takes inspiration from materials testing machines and lab oscilloscopes: a high-contrast illuminated display (the plot) surrounded by a dark, focused control surface. The copper accent (#D4783C) replaces generic blue — it recalls analog chart recorders and precision measurement equipment. All numerical values render in monospace, signaling that every decimal matters. The visual hierarchy privileges the force-depth curve above all else; controls are present but recede into the dark panel.

### Design decisions
- **Dark UI, light plot**: The plot is the instrument reading. It gets the highest contrast (#F5F6FA canvas, dark grid/ticks) while the surrounding controls recede into a dark surface (#1B1C22/#25262E).
- **Copper accent**: Not a typical UI color. Avoids the three AI-generated defaults (cream+terracotta, dark+acid, broadsheet). Evokes analog measurement equipment.
- **Monospace for all numbers**: Every spinbox, depth label, and data point uses a monospace font. In a calibration tool where users compare decimal values, proportional numbers of different widths are harder to scan. Monospace makes "1.23" and "12.30" instantly distinguishable by width.
- **No icon dependencies**: Toolbar uses text-only buttons instead of platform `QStyle.StandardPixmap`, ensuring identical appearance across Windows/macOS/Linux.

---

## 1. Layout Architecture

```
┌──────────────────────────────────────────────────┐
│  Toolbar  Load   Restore │ Send │ Export.. │ ● C  │  bg: #1B1C22
├────────────────────────────┬─────────────────────┤
│                            │  Totals info (36px) │
│                            │  Depth bar   (36px) │
│       Plot (2/3 width)     ├────────┬────────────┤
│       bg: #F5F6FA          │ Tissue │ Detail     │
│                            │ List   │ (Stacked)  │
│                            │ bg:    │ bg:        │
│                            │inherits │ #2E303A   │
└──────────────────────────────────────────────────┘
```

### Backgrounds
- **Main canvas** (window background): `#1B1C22`
- **Right panel**: `#25262E` (via objectName `#rightPanel`), left border `1px solid #3A3B48`
- **Plot canvas**: `#F5F6FA`
- **TissueWidget cards**: `#2E303A` background, `1px solid #3A3B48` border, 4px border-radius
- **TissueList**: inherits `#25262E` from right panel; rows use custom selection/hover

### Ratios
- **Plot : Right panel** = 2 : 1 (stretch factors in `QHBoxLayout`)
- **TissueList : DetailStack** = 180 : 380 px (initial `QSplitter` sizes)

### Files
| File | Role |
|------|------|
| `ui/main_window.py` | QMainWindow: orchestrates toolbar, plot, right panel |
| `ui/plot_widget.py` | PyQtGraph plot: curve + reference + regions |
| `ui/tissue_widget.py` | Per-tissue editor (depth, family, params, sliders) |
| `ui/tissue_list_widget.py` | Compact row list of all tissues (swatch + name + depth) |
| `ui/depth_bar_widget.py` | Horizontal colored bar, equal-width segments, clickable |

---

## 2. Color System

### Theme Source
Applied via `QPalette` in `main.py` with Fusion style, plus targeted QSS overrides. The palette drives ~80% of widget colors; QSS handles the rest (borders, spinboxes, sliders, combos).

### Canvas & Surface

| Token | Hex | Usage |
|-------|-----|-------|
| Canvas | `#1B1C22` | Main window background, toolbar background, spinbox input bg |
| Surface | `#25262E` | Right panel, header frames, tissue list header, toolbar |
| Card | `#2E303A` | TissueWidget body, tooltip background, combo dropdown |
| Border subtle | `#3A3B48` | Card borders, separators, toolbar border-bottom, slider groove |
| Border stroke | `#4B4D5E` | Swatch borders, plot viewport border, region dividers |

### Text

| Token | Hex | Usage |
|-------|-----|-------|
| Primary | `#E4E5EC` | Tissue names, spinbox values, totals, connection status |
| Secondary | `#9395A8` | Labels (family, depth, parameter names) |
| Muted | `#63657A` | Units, thickness hints, depth bar labels, disabled text |
| On-selection | `#FFFFFF` | Text on selected row, highlighted text |

### Accents

| Token | Hex | Usage |
|-------|-----|-------|
| Copper | `#D4783C` | Fitted curve, selection highlight, slider handle, focus ring |
| Copper hover | `#E0874F` | Slider handle hover |
| Ref curve | `#7A7D8E` | Reference curve dashed line |
| Grid | `#D8DAE3` | Plot grid lines |
| Success | `#4CAF50` | Connection status "Connected" |
| Error | `#E53935` | Connection status "Disconnected" |

### Tissue Colors (unchanged, from `config/tissues.py`)

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
- No pure white (`#FFFFFF`)—invisible on light plot background
- All colors must be distinguishable in both full opacity and alpha=40 on #F5F6FA
- When adding a new tissue, pick a hue not already used

### Plot Regions
- Region backgrounds use tissue color at `alpha=50`
- Dividing lines: `#4B4D5E` dashed
- Text labels: `#1B1C22`, rotated 90°, positioned at top of region

---

## 3. Typography

### Font Stack
| Role | Faces | Fallback |
|------|-------|----------|
| UI labels & body | System default | Qt resolves per-platform (Segoe UI / SF Pro) |
| **Numerical values** | `"Cascadia Code", "JetBrains Mono", "Consolas"` | `"monospace"` |

### Type Scale

| Context | Size | Weight | Color | Face |
|---------|------|--------|-------|------|
| Tissue name in widget | 14px | 600 (Semibold) | `#E4E5EC` | System |
| Totals bar | 12px | 600 (Semibold) | `#E4E5EC` | System |
| Toolbar buttons | 12px | 500 (Medium) | `#E4E5EC` | System |
| Labels (family, depth, param) | 12px | 400 (Regular) | `#9395A8` | System |
| TissueList header | 11px | 600 (Semibold) | `#9395A8` | System |
| Muted text / units | 11px | 400 (Regular) | `#63657A` | System |
| **Spinbox values** | **12px** | **400 (Regular)** | **`#E4E5EC`** | **Monospace** |
| Delta spinbox prefix "Δ " | 12px | 400 | `#E4E5EC` | Monospace |
| Depth bar segment labels | 8pt | 400 | `#1B1C22` | System |
| Depth bar depth labels | 8pt | 400 | `#63657A` | System |
| Connection status | 12px | 600 | `#4CAF50` / `#E53935` | System |

### Signature: Monospace for Numbers
All QDoubleSpinBox instances use a monospace font stack. This is the system's most distinctive typographic decision: in a calibration tool where users read and compare decimal values constantly, monospace makes every digit width-predictable, dramatically improving scannability of parameter values.

---

## 4. Component Library

### 4.1 Toolbar
- **File**: `main_window.py:_create_toolbar()`
- **Style**: `ToolButtonTextOnly` (no icons)
- **Background**: `#1B1C22`, border-bottom `1px solid #3A3B48`
- **Buttons**: Text `#E4E5EC`, transparent bg, 4px border-radius, hover → `#2E303A` + `#3A3B48` border, pressed → `#3A3B48`
- **Separator**: `#3A3B48`, 1px, margin 4px
- **Connection status**: Right-aligned, `● Connected` / `● Disconnected`
- **Shortcuts**: Ctrl+S (Send), Ctrl+E (Export), Ctrl+R (Restore), Ctrl+L (Load)

### 4.2 Totals Info Bar
- **File**: `main_window.py` (as `self.totals_label`)
- **Height**: 36px fixed
- **Content**: `Total: X.XXmm  |  A/B active  |  MSE: X.XXXX N²`
- **Style**: QLabel `padding: 0 12px; color: #E4E5EC; font-size: 12px; font-weight: 600; background: transparent;`
- **Alignment**: Left-aligned, vertically centered

### 4.3 Depth Bar
- **File**: `depth_bar_widget.py`
- **Height**: 36px fixed, background filled with `#25262E`
- **Content**: Colored segments of **equal width** (1/N per active tissue)
- **Interaction**: Click → selects tissue. Hover → lighter segment + popup label for narrow segments
- **Segment border**: `#3A3B48`, 1px
- **Segment text**: `#1B1C22` (dark, readable on tissue colors)
- **Depth labels**: `#63657A` at bottom of each segment boundary
- **Hover popup**: Rect `#3A3B48` border, text `#1B1C22`

### 4.4 Tissue List
- **File**: `tissue_list_widget.py`
- **Row height**: 38px fixed
- **Row content**: [color swatch 14×14] [checkbox] [name] [start–end depth]
- **Selection**: `background: #D4783C`, text `#FFFFFF` weight 600
- **Hover**: `background: #2E303A`, text `#E4E5EC`
- **Default**: transparent, text `#E4E5EC`
- **Header**: "TISSUES", `#25262E` bg, `#9395A8` text, 11px semibold, padding 6px 12px
- **Swatch border**: `1px solid #4B4D5E`, border-radius 3px
- **Depth label**: `#63657A`, 11px

### 4.5 Tissue Widget (Detail View)
- **File**: `tissue_widget.py`
- **Parent**: QGroupBox styled as card (`bg: #2E303A`, `border: 1px solid #3A3B48`, `border-radius: 4px`)
- **Children**:
  1. **Header row**: bg `#25262E`, [color swatch 22×22, border `#4B4D5E`] [name, 14px semibold `#E4E5EC`]
  2. **Properties** (indented 16px):
     - Depth: `0.00 → [end spinbox monospace] mm (thickness)` — labels `#9395A8`, units `#63657A`
     - Family: dropdown (categorized: Simple / Rupture / Polynomial / Exponential)
  3. **Separator line** (HLine, `color: #3A3B48`)
  4. **Parameters**: Per-param 2 rows
     - Row 1: `[label #9395A8] [spinbox monospace #E4E5EC bg #1B1C22] [Δ delta spinbox]`
     - Row 2: `[===== slider =====]`
- **QDoubleSpinBox**: bg `#1B1C22`, border `#3A3B48`, 3px radius, monospace font, up/down arrows hidden
- **QComboBox**: bg `#1B1C22`, border `#3A3B48`, 3px radius, dropdown bg `#2E303A`, selection `#D4783C`
- **QSlider**: groove `#3A3B48` height 6px, handle `#D4783C` 14px circle, sub-page `#D4783C`

### 4.6 Plot
- **File**: `plot_widget.py`
- **Library**: PyQtGraph
- **Background**: `#F5F6FA`
- **Fitted curve**: Copper `#D4783C`, 3px solid
- **Reference curve**: `#7A7D8E`, 2px dashed
- **Regions**: Tissue color alpha=50 bg, `#4B4D5E` dashed dividers, `#1B1C22` rotated labels
- **Grid**: Both axes, `#D8DAE3`, 1px
- **Axes**: Ticks/labels `#1B1C22`, axis lines `#3A3B48`
- **Legend**: bg `#F5F6FA`, border `#3A3B48`, text `#1B1C22`
- **Viewport border**: `#3A3B48`, 1px

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
- No duplicated events (depth bar ignores disabled tissues)

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
- **Right panel width** controlled by `mid_splitter.setSizes([180, 380])`
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
5. Dark mode toggle (system-wide CSS switch) — now the default theme

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
| `main.py` | Entry point + global theme (Fusion, QPalette, QSS) | — |
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
