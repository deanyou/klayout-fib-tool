import ast
import unittest
from pathlib import Path
from types import SimpleNamespace


FIB_PANEL_PATH = (
    Path(__file__).resolve().parents[1] / "python" / "fib_tool" / "fib_panel.py"
)


def load_docking_helpers():
    source = FIB_PANEL_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    helper_names = {
        "_find_right_dock_split_target",
        "_dock_fib_panel",
        "_schedule_fib_panel_redock",
    }
    helpers = [
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name in helper_names
    ]
    if {node.name for node in helpers} != helper_names:
        raise AssertionError("missing FIB panel docking helpers")

    module = ast.Module(body=helpers, type_ignores=[])
    namespace = {
        "pya": SimpleNamespace(
            Qt=SimpleNamespace(
                RightDockWidgetArea="right",
                Vertical="vertical",
            ),
            QTimer=FakeTimer,
        ),
        "print": lambda *args, **kwargs: None,
    }
    exec(compile(module, str(FIB_PANEL_PATH), "exec"), namespace)
    return (
        namespace["_find_right_dock_split_target"],
        namespace["_dock_fib_panel"],
        namespace["_schedule_fib_panel_redock"],
    )


class FakeTimer:
    def __init__(self, parent):
        self.parent = parent
        self.interval = None
        self.single_shot = False
        self.timeout = None
        self.started = False

    def setInterval(self, interval):
        self.interval = interval

    def setSingleShot(self, single_shot):
        self.single_shot = single_shot

    def start(self):
        self.started = True


class FakeDock:
    def __init__(self, name, area, height, visible=True):
        self.name = name
        self.area = area
        self.height = height
        self.visible = visible
        self.shown = False

    def inherits(self, class_name):
        return class_name == "QDockWidget"

    def isVisible(self):
        return self.visible

    def show(self):
        self.shown = True


class FakeMainWindow:
    def __init__(self, docks, tabified=None):
        self.docks = docks
        self.tabified = tabified or {}
        self.calls = []

    def findChildren(self):
        return self.docks

    def findChild(self, name):
        return next(
            (dock for dock in self.docks if getattr(dock, "object_name", "") == name),
            None,
        )

    def dockWidgetArea(self, dock):
        return dock.area

    def tabifiedDockWidgets(self, dock):
        return self.tabified.get(dock.name, [])

    def addDockWidget(self, area, dock):
        self.calls.append(("add", area, dock.name))

    def splitDockWidget(self, target, dock, orientation):
        self.calls.append(("split", target.name, dock.name, orientation))

    def resizeDocks(self, docks, sizes, orientation):
        self.calls.append(
            ("resize", [dock.name for dock in docks], sizes, orientation)
        )


class FibPanelDockingTests(unittest.TestCase):
    def test_only_marker_region_absorbs_vertical_resize(self):
        source = FIB_PANEL_PATH.read_text(encoding="utf-8")

        self.assertNotIn("self.scroll_area = pya.QScrollArea()", source)
        self.assertEqual(
            3,
            source.count(
                "pya.QSizePolicy.Preferred, pya.QSizePolicy.Fixed"
            ),
        )
        self.assertIn(
            "pya.QSizePolicy.Preferred, pya.QSizePolicy.Expanding",
            source,
        )
        self.assertIn(
            "pya.QSizePolicy.Expanding, pya.QSizePolicy.Ignored",
            source,
        )
        self.assertIn("self.marker_list.setMinimumHeight(0)", source)
        self.assertIn("self.setWidget(self.container)", source)

    def test_prefers_klayout_named_right_dock(self):
        find_target, _, _ = load_docking_helpers()
        layers = FakeDock("layers", "right", 300)
        layers.object_name = "lp_dock_widget"
        main_window = FakeMainWindow([layers])
        main_window.findChildren = lambda: []

        self.assertIs(find_target(main_window, None), layers)

    def test_selects_largest_visible_right_dock(self):
        find_target, _, _ = load_docking_helpers()
        panel = FakeDock("fib", "right", 400)
        small = FakeDock("small", "right", 150)
        large = FakeDock("large", "right", 500)
        hidden = FakeDock("hidden", "right", 900, visible=False)
        left = FakeDock("left", "left", 1000)
        main_window = FakeMainWindow([panel, small, large, hidden, left])

        self.assertIs(find_target(main_window, panel), large)

    def test_splits_below_existing_right_dock_and_sets_initial_ratio(self):
        _, dock_panel, _ = load_docking_helpers()
        target = FakeDock("layers", "right", 500)
        panel = FakeDock("fib", "right", 400)
        main_window = FakeMainWindow([target])

        self.assertTrue(dock_panel(main_window, panel))
        self.assertTrue(panel.shown)
        self.assertEqual(
            [
                ("add", "right", "fib"),
                ("split", "layers", "fib", "vertical"),
                ("resize", ["layers", "fib"], [2, 1], "vertical"),
            ],
            main_window.calls,
        )

    def test_ignores_tabified_right_dock(self):
        find_target, _, _ = load_docking_helpers()
        tabbed = FakeDock("tabbed", "right", 500)
        plain = FakeDock("plain", "right", 300)
        main_window = FakeMainWindow(
            [tabbed, plain],
            tabified={"tabbed": [FakeDock("other-tab", "right", 500)]},
        )

        self.assertIs(find_target(main_window, None), plain)

    def test_falls_back_to_standard_right_dock_without_target(self):
        _, dock_panel, _ = load_docking_helpers()
        panel = FakeDock("fib", "right", 400)
        main_window = FakeMainWindow([])

        self.assertFalse(dock_panel(main_window, panel))
        self.assertTrue(panel.shown)
        self.assertEqual([("add", "right", "fib")], main_window.calls)

    def test_schedules_redock_after_klayout_restores_window_state(self):
        _, _, schedule_redock = load_docking_helpers()
        target = FakeDock("layers", "right", 500)
        target.object_name = "lp_dock_widget"
        panel = FakeDock("fib", "right", 400)
        main_window = FakeMainWindow([target])

        timer = schedule_redock(main_window, panel)

        self.assertTrue(timer.single_shot)
        self.assertEqual(0, timer.interval)
        self.assertTrue(timer.started)
        self.assertIs(panel._fib_dock_timer, timer)

        timer.timeout()
        self.assertIn(("split", "layers", "fib", "vertical"), main_window.calls)


if __name__ == "__main__":
    unittest.main()
