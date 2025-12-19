# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**KLayout FIB Tool** - A practical IC layout annotation tool for FIB (Focused Ion Beam) operations. Built for KLayout (>=0.28) following Linus Torvalds' programming philosophy: "Good data structures make code naturally simple."

**Current Status**: Production ready, undergoing modular refactoring (Phase 2 complete, ~4% code reduction achieved).

## Architecture

### 3-Layer Modular Structure (Version 4.0+)

```
python/fib_tool/
├── core/                       # Core utilities (stateless, pure functions)
│   ├── global_state.py         # Centralized state management (replaces sys.modules)
│   ├── geometry_utils.py       # Distance, direction, bounding box calculations
│   └── validation_utils.py     # Input validation and data verification
│
├── ui/                         # UI components
│   └── dialog_manager.py       # Consolidated dialog operations (QMessageBox wrapper)
│
├── business/                   # Business logic
│   ├── marker_transformer.py   # Marker type conversions (CUT/CONNECT/PROBE)
│   ├── file_manager.py         # JSON save/load operations
│   └── export_manager.py       # PDF/HTML export facade
│
├── fib_plugin.py               # Mouse-based marker creation plugin
├── fib_panel.py                # Main dockable panel UI (2,191 lines, being refactored)
├── klayout_package.py          # SALT package entry point
├── markers.py                  # Basic marker classes (CutMarker, ConnectMarker, ProbeMarker)
├── multipoint_markers.py       # Multi-point marker support
├── layer_manager.py            # Auto layer creation (layers 337, 338, 339)
├── layer_tap.py                # Layer detection at click position
├── marker_menu.py              # Context menu operations
├── screenshot_export.py        # Screenshot capture with 3-level zoom
├── config.py                   # Constants: LAYERS, GEOMETRIC_PARAMS, UI_TIMEOUTS
├── smart_counter.py            # Intelligent marker ID generation
└── __init__.py                 # Package exports (new + legacy modules)
```

### Legacy vs New Architecture

**Legacy (still functional)**: Monolithic modules in root `fib_tool/`
**New (recommended)**: Modular architecture with clear separation:
- **Core**: Pure utilities, no side effects
- **Business**: Domain logic, stateful operations
- **UI**: Presentation layer, user interactions

### Key Design Principles

1. **Data Structures First**: `FibGlobalState` centralizes all marker data
2. **No sys.modules Access**: State injected via dependency injection
3. **Early Returns**: Maximum 2-3 levels of nesting
4. **Single Responsibility**: Each module has one clear purpose
5. **Backward Compatibility**: Old imports still work
6. **1000-Line Limit**: No Python file exceeds 1000 lines (see LinusTorvalds.md for details)

## Development Commands

### Installation & Deployment

```bash
# SALT Package Installation (Production)
./install.sh                    # macOS/Linux - choose symbolic link for dev
./install.bat                   # Windows

# Uninstallation
./uninstall.sh                  # macOS/Linux
./uninstall.bat                 # Windows
```

### Development Mode (KLayout Macro Development - F5)

```python
# Method 1: Set path before exec (RECOMMENDED)
FIB_TOOL_PATH = '/path/to/klayout-fib-tool'
exec(open(FIB_TOOL_PATH + '/load_fib_tool.py', encoding='utf-8').read())

# Method 2: Use full path
exec(open('/path/to/klayout-fib-tool/load_fib_tool.py', encoding='utf-8').read())
# Then enter path when prompted
```

### Testing & Diagnostics

```python
# In KLayout Macro Development (F5):

# Diagnose panel activation
exec(open('/path/to/diagnose_panel_activation.py', encoding='utf-8').read())

# Diagnose layer creation
exec(open('/path/to/diagnose_layer_creation.py', encoding='utf-8').read())

# Test imports
python3 -c "import sys; sys.path.insert(0, 'python'); import fib_tool; print('OK')"
```

### Code Quality Checks

```bash
# Check Python syntax
python3 -m py_compile python/fib_tool/*.py
python3 -m py_compile python/fib_tool/core/*.py
python3 -m py_compile python/fib_tool/business/*.py
python3 -m py_compile python/fib_tool/ui/*.py

# Verify module structure
python3 -c "
import sys
sys.path.insert(0, 'python')
from fib_tool import FibGlobalState, FibDialogManager, FibMarkerTransformer
print('New modules OK')
from fib_tool import markers, fib_panel
print('Legacy modules OK')
"
```

## Usage Workflow

### User Flow (End User)
1. **Install**: Via SALT Package Manager or `./install.sh`
2. **Open GDS**: Load layout file in KLayout
3. **Launch**: `Ctrl+Shift+F` or **Tools → FIB Tool**
4. **Create Markers**: Click CUT/CONNECT/PROBE buttons
5. **Export**: Save XML or generate HTML report with screenshots

### Developer Flow
1. **Setup**: Clone repo, run `./install.sh` with symbolic link
2. **Develop**: Modify code in `python/fib_tool/`
3. **Test**: Use `load_fib_tool.py` in KLayout F5
4. **Reload**: Close/reopen KLayout for changes to take effect
5. **Verify**: Check layers 337, 338, 339 are created automatically

## Key Files & Their Roles

### Entry Points
- **`klayout_package.py`**: SALT package auto-initialization
- **`fib_plugin.py`**: Mouse interaction plugin (toolbar buttons)
- **`fib_panel.py`**: Main UI panel (dockable widget)
- **`load_fib_tool.py`**: Development loader with path detection

### Core Business Logic
- **`FibGlobalState`**: Manages marker counters, lists, screenshots
- **`FibMarkerTransformer`**: Converts between marker types
- **`FibFileManager`**: JSON save/load with validation
- **`FibExportManager`**: PDF/HTML report generation

### Configuration
- **`config.py`**: Layer numbers (337, 338, 339), geometric params, timeouts
- **`grain.xml`**: SALT package descriptor

## Common Issues & Solutions

### Panel Not Appearing
- **Cause**: KLayout not fully restarted
- **Fix**: Close KLayout completely (not just window), reopen, run loader

### Import Errors
- **Cause**: Path not in sys.path
- **Fix**: Ensure `python/` directory is added to sys.path before import

### Layer Creation Fails
- **Cause**: No active layout
- **Fix**: Open a GDS file first, or continue loading (will create layers when layout opened)

### Double Initialization
- **Cause**: Loading via both SALT and exec()
- **Fix**: Use only one method; loader checks for existing initialization

## Refactoring Status

**Current**: Phase 2 complete (97 lines reduced, state management refactored)
**Next**: Phase 3 - MessageBox consolidation, export operations, move to ui/ directory
**Target**: Reduce `fib_panel.py` from 2,191 → ~1,200 lines

**⚠️ Code Quality Issue**: `fib_panel.py` currently at 2,191 lines (exceeds 1000-line limit)
- This violates the 1000-line rule documented in LinusTorvalds.md
- Phase 3 will address this by further modularization

### Recent Changes
- ✅ Created `core/`, `ui/`, `business/` directories
- ✅ Extracted 7 new modules (1,200+ lines moved)
- ✅ Eliminated all `sys.modules` accesses in new code
- ✅ Centralized state management
- ✅ Backward compatibility maintained

## Testing Checklist

When making changes, verify:
- [ ] Marker creation works (CUT, CONNECT, PROBE)
- [ ] Multi-point markers function correctly
- [ ] JSON save/load preserves all data
- [ ] HTML/PDF export generates reports
- [ ] Layer auto-creation works (337, 338, 339)
- [ ] Context menu operations work
- [ ] Keyboard shortcuts function
- [ ] No import errors in new modules
- [ ] Legacy imports still work

## Dependencies

- **KLayout**: >=0.28
- **Python**: 3.8+
- **Standard Library Only**: No external dependencies (uses pya from KLayout)

## Notes for Future Claude Instances

1. **Always check REFACTORING_STATUS.md** before major changes - tracks ongoing modularization
2. **Use new modules** (`FibGlobalState`, etc.) for new features
3. **Maintain backward compatibility** - old imports must continue working
4. **Follow Linus Torvalds principles**: early returns, single responsibility, max 2-3 nesting levels
5. **Test in KLayout F5** - this is the primary development environment
6. **Check layer numbers**: 337=CUT, 338=CONNECT, 339=PROBE (documented in config.py)