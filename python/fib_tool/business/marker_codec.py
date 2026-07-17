"""Canonical conversion between FIB marker objects and plain records."""

from ..config import LAYERS
from ..markers import CutMarker, ConnectMarker, ProbeMarker
from ..multipoint_markers import MultiPointCutMarker, MultiPointConnectMarker


_TYPE_BY_CLASS = (
    (MultiPointCutMarker, "multipoint_cut"),
    (MultiPointConnectMarker, "multipoint_connect"),
    (CutMarker, "cut"),
    (ConnectMarker, "connect"),
    (ProbeMarker, "probe"),
)

_TYPE_BY_ID_PREFIX = {
    "CUT": "cut",
    "CONNECT": "connect",
    "PROBE": "probe",
    "MULTIPOINT": "multipoint",
}


def marker_type_name(marker):
    """Return the canonical type name for a supported marker object."""
    for marker_class, type_name in _TYPE_BY_CLASS:
        if isinstance(marker, marker_class):
            return type_name
    raise TypeError("Unknown marker: %s" % type(marker).__name__)


def _parse_marker_id(marker_id):
    if not isinstance(marker_id, str):
        raise TypeError("Marker ID must be a string")

    prefix, separator, remainder = marker_id.partition("_")
    number_text = remainder.split("_", 1)[0]
    if not separator or prefix not in _TYPE_BY_ID_PREFIX or not number_text.isdigit():
        raise ValueError("Invalid marker ID: %s" % marker_id)
    return _TYPE_BY_ID_PREFIX[prefix], int(number_text)


def marker_id_to_type(marker_id):
    """Return the base marker type encoded in a marker ID."""
    return _parse_marker_id(marker_id)[0]


def marker_id_number(marker_id):
    """Return the numeric sequence encoded in a marker ID."""
    return _parse_marker_id(marker_id)[1]


def marker_to_record(marker):
    """Return a JSON-safe record for a supported marker object."""
    marker_type = marker_type_name(marker)
    record = {
        "id": marker.id,
        "layer": marker.layer,
        "notes": getattr(marker, "notes", ""),
        "screenshots": getattr(marker, "screenshots", []),
        "target_layers": getattr(marker, "target_layers", []),
    }
    if marker_type == "multipoint_cut":
        record.update(type="multipoint_cut", points=[list(p) for p in marker.points],
                      point_layers=marker.point_layers)
    elif marker_type == "multipoint_connect":
        record.update(type="multipoint_connect", points=[list(p) for p in marker.points],
                      point_layers=marker.point_layers)
    elif marker_type == "cut":
        record.update(type="cut", x1=marker.x1, y1=marker.y1,
                      x2=marker.x2, y2=marker.y2,
                      layer1=marker.layer1, layer2=marker.layer2)
    elif marker_type == "connect":
        record.update(type="connect", x1=marker.x1, y1=marker.y1,
                      x2=marker.x2, y2=marker.y2,
                      layer1=marker.layer1, layer2=marker.layer2)
    elif marker_type == "probe":
        record.update(type="probe", x=marker.x, y=marker.y,
                      target_layer=marker.target_layer)
    return record


def marker_from_record(record):
    """Create a marker object from a canonical or older JSON record."""
    marker_type = record["type"]
    marker_id = record["id"]
    base_type = marker_type.replace("multipoint_", "")
    layer = record.get("layer", LAYERS[base_type])

    if marker_type == "cut":
        marker = CutMarker(id=marker_id, x1=record["x1"], y1=record["y1"],
                           x2=record["x2"], y2=record["y2"], layer=layer,
                           layer1=record.get("layer1"), layer2=record.get("layer2"))
    elif marker_type == "connect":
        marker = ConnectMarker(id=marker_id, x1=record["x1"], y1=record["y1"],
                               x2=record["x2"], y2=record["y2"], layer=layer,
                               layer1=record.get("layer1"), layer2=record.get("layer2"))
    elif marker_type == "probe":
        marker = ProbeMarker(id=marker_id, x=record["x"], y=record["y"],
                             layer=layer, target_layer=record.get("target_layer"))
    elif marker_type == "multipoint_cut":
        marker = MultiPointCutMarker(id=marker_id, points=[tuple(p) for p in record["points"]],
                                     layer=layer, point_layers=record.get("point_layers", []))
    elif marker_type == "multipoint_connect":
        marker = MultiPointConnectMarker(id=marker_id, points=[tuple(p) for p in record["points"]],
                                         layer=layer, point_layers=record.get("point_layers", []))
    else:
        raise ValueError("Unknown marker type: %s" % marker_type)

    marker.notes = record.get("notes", "")
    marker.screenshots = record.get("screenshots", [])
    marker.target_layers = record.get("target_layers", [])
    return marker
