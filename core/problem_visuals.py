from __future__ import annotations

import ast
from html import escape
from math import atan2, cos, hypot, sin
from typing import Any


# These diagrams illustrate the first worked example. Problems whose first
# example is already clear without a spatial model are intentionally omitted.
PROBLEM_VISUALS: dict[str, dict[str, Any]] = {
    "best-stock-profit": {
        "kind": "bars",
        "label": "The prices from example one with the best buy and later sale marked",
        "values": [7, 1, 5, 3, 6, 4],
        "markers": {1: "buy", 4: "sell later"},
        "caption": "Buying at 1 and selling later at 6 produces the expected profit of 5.",
    },
    "maximum-subarray": {
        "kind": "sequence",
        "label": "The first example array with its maximum-sum subarray highlighted",
        "items": [-2, 1, -3, 4, -1, 2, 1, -5, 4],
        "active": [3, 4, 5, 6],
        "caption": "The highlighted block [4, -1, 2, 1] is consecutive and has sum 6.",
    },
    "flood-fill": {
        "kind": "grid_compare",
        "label": "The first example image before and after flood fill",
        "before": [[1, 1, 1], [1, 1, 0], [1, 0, 1]],
        "after": [[2, 2, 2], [2, 2, 0], [2, 0, 1]],
        "before_classes": {
            (0, 0): "connected",
            (0, 1): "connected",
            (0, 2): "connected",
            (1, 0): "connected",
            (1, 1): "source",
            (2, 0): "connected",
            (2, 2): "separate",
        },
        "after_classes": {
            (0, 0): "changed",
            (0, 1): "changed",
            (0, 2): "changed",
            (1, 0): "changed",
            (1, 1): "changed",
            (2, 0): "changed",
            (2, 2): "separate",
        },
        "left_label": "before",
        "right_label": "after",
        "caption": "The lower-right 1 stays unchanged because it only touches the filled region diagonally.",
    },
    "longest-unique-substring": {
        "kind": "sequence",
        "label": "The first example string with its first longest unique substring highlighted",
        "items": list("abcabcbb"),
        "active": [0, 1, 2],
        "warning": [3],
        "annotations": {3: "repeats a"},
        "caption": "The first abc has length 3; the next a repeats a character in that substring.",
    },
    "product-except-self": {
        "kind": "product",
        "label": "The calculation for output index one in the first example",
        "items": [1, 2, 3, 4],
        "excluded": 1,
        "caption": "At output index 1, exclude the input value 2: 1 × 3 × 4 = 12.",
    },
    "container-most-water": {
        "kind": "container",
        "label": "The nine heights from example one with the maximum container highlighted",
        "values": [1, 8, 6, 2, 5, 4, 8, 3, 7],
        "left": 1,
        "right": 8,
        "caption": "The lines at indices 1 and 8 have width 7 and limiting height 7, giving area 49.",
    },
    "minimum-size-subarray-sum": {
        "kind": "sequence",
        "label": "The first example array with its shortest qualifying subarray highlighted",
        "items": [2, 3, 1, 2, 4, 3],
        "active": [4, 5],
        "annotations": {4: "4 + 3", 5: "= 7"},
        "caption": "The neighboring values 4 and 3 reach the target with length 2.",
    },
    "character-replacement": {
        "kind": "sequence",
        "label": "The first example string after using two replacements",
        "items": list("ABAB"),
        "active": [0, 1, 2, 3],
        "changed": {1: "A", 3: "A"},
        "annotations": {1: "B → A", 3: "B → A"},
        "caption": "Replacing both B characters makes all four positions equal.",
    },
    "daily-temperatures": {
        "kind": "bars",
        "label": "The temperatures from example one with one four-day wait marked",
        "values": [73, 74, 75, 71, 69, 72, 76, 73],
        "markers": {2: "75°", 6: "next warmer"},
        "span": [2, 6],
        "caption": "For day 2, the first warmer temperature is 76 on day 6, so the wait is 4.",
    },
    "search-rotated-array": {
        "kind": "sequence",
        "label": "The rotated array from example one with the target at the rotation point",
        "items": [4, 5, 6, 7, 0, 1, 2],
        "break_after": 3,
        "annotations": {3: "rotation", 4: "point"},
        "caption": "The target 0 appears immediately after the rotation break, at index 4.",
    },
    "koko-bananas": {
        "kind": "piles",
        "label": "The first example piles divided into hours at speed four",
        "values": [3, 6, 7, 11],
        "speed": 4,
        "caption": "At speed 4, the four piles take 1 + 2 + 2 + 3 = 8 hours.",
    },
    "merge-intervals": {
        "kind": "intervals",
        "label": "The intervals from example one before and after merging",
        "before": [[1, 3], [2, 6], [8, 10], [15, 18]],
        "after": [[1, 6], [8, 10], [15, 18]],
        "caption": "[1, 3] and [2, 6] overlap; the other two intervals remain separate.",
    },
    "insert-interval": {
        "kind": "intervals",
        "label": "The first example intervals before and after inserting the new interval",
        "before": [[1, 3], [6, 9]],
        "new": [2, 5],
        "after": [[1, 5], [6, 9]],
        "caption": "The new [2, 5] overlaps [1, 3] but does not reach [6, 9].",
    },
    "spiral-matrix": {
        "kind": "grid",
        "label": "The first example matrix numbered in spiral visit order",
        "values": [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
        "order": [1, 2, 3, 8, 9, 4, 7, 6, 5],
        "caption": "The small numbers show the visit order that produces [1, 2, 3, 6, 9, 8, 7, 4, 5].",
    },
    "rotate-matrix": {
        "kind": "grid_compare",
        "label": "A matrix before and after a ninety-degree clockwise rotation",
        "before": [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
        "after": [[7, 4, 1], [8, 5, 2], [9, 6, 3]],
        "left_label": "before",
        "right_label": "90° clockwise",
        "caption": "The first input column [1, 4, 7] becomes the output row [7, 4, 1].",
    },
    "set-matrix-zeroes": {
        "kind": "grid_compare",
        "label": "A matrix whose marked row and column become zero",
        "before": [[1, 1, 1], [1, 0, 1], [1, 1, 1]],
        "after": [[1, 0, 1], [0, 0, 0], [1, 0, 1]],
        "before_classes": {(1, 1): "source"},
        "after_classes": {
            (0, 1): "changed",
            (1, 0): "changed",
            (1, 1): "source",
            (1, 2): "changed",
            (2, 1): "changed",
        },
        "left_label": "original zero",
        "right_label": "affected row + column",
        "caption": "The center zero changes the entire middle row and middle column to zero.",
    },
    "number-of-islands": {
        "kind": "grid",
        "label": "The first example grid with its three islands distinguished",
        "values": [[1, 1, 1], [0, 1, 0], [1, 0, 1]],
        "cell_classes": {
            (0, 0): "group-1",
            (0, 1): "group-1",
            (0, 2): "group-1",
            (1, 1): "group-1",
            (2, 0): "group-2",
            (2, 2): "group-3",
        },
        "display_zero_as": "·",
        "display_land_as": "1",
        "caption": "The two bottom land cells touch the top island only diagonally, so all three are separate.",
    },
    "shortest-unweighted-path": {
        "kind": "graph",
        "label": "The graph from example one with a shortest route from zero to two highlighted",
        "nodes": {0: (8, 50), 1: (35, 20), 2: (70, 22), 3: (35, 82), 4: (72, 76)},
        "edges": [(0, 1), (1, 2), (0, 3), (3, 4), (4, 2)],
        "active_edges": [(0, 1), (1, 2)],
        "active_nodes": [0, 1, 2],
        "caption": "The highlighted route 0 → 1 → 2 uses 2 edges, matching the expected output.",
    },
    "house-robber": {
        "kind": "houses",
        "label": "The first example street with the optimal nonadjacent houses selected",
        "values": [1, 2, 3, 1],
        "active": [0, 2],
        "caption": "Selecting houses 0 and 2 gives 1 + 3 = 4 without choosing adjacent houses.",
    },
    "decode-ways": {
        "kind": "decodings",
        "label": "The two valid decodings of the first example string",
        "digits": "12",
        "rows": [(["1", "2"], ["A", "B"]), (["12"], ["L"])],
        "caption": "12 can be read as 1 + 2 or as the single value 12, giving two decodings.",
    },
    "longest-increasing-subsequence": {
        "kind": "sequence",
        "label": "One longest increasing subsequence from the first example array",
        "items": [10, 9, 2, 5, 3, 7, 101, 18],
        "active": [2, 4, 5, 6],
        "muted": [0, 1, 3, 7],
        "caption": "The highlighted values 2, 3, 7, 101 keep their input order and have length 4.",
    },
}


def _classes(*parts: str | None) -> str:
    return " ".join(part for part in parts if part)


def _sequence(spec: dict[str, Any]) -> str:
    active = set(spec.get("active", []))
    warning = set(spec.get("warning", []))
    muted = set(spec.get("muted", []))
    changed = spec.get("changed", {})
    tones = spec.get("tones", [])
    annotations = spec.get("annotations", {})
    break_after = spec.get("break_after")
    cells: list[str] = []
    for index, original in enumerate(spec["items"]):
        value = changed.get(index, original)
        tone = f"tone-{tones[index]}" if index < len(tones) else None
        class_name = _classes(
            "gc-vis-cell",
            "is-active" if index in active else None,
            "is-warning" if index in warning else None,
            "is-muted" if index in muted else None,
            "is-changed" if index in changed else None,
            tone,
            "has-break" if index == break_after else None,
        )
        annotation = annotations.get(index)
        cells.append(
            f'<div class="gc-vis-cell-wrap">'
            f'<div class="{class_name}">{escape(str(value))}</div>'
            f'{f"<span>{escape(str(annotation))}</span>" if annotation else ""}'
            f"</div>"
        )
    return f'<div class="gc-vis-sequence">{"".join(cells)}</div>'


def _bars(spec: dict[str, Any]) -> str:
    values = spec["values"]
    markers = spec.get("markers", {})
    index_label = spec.get("index_label", "day")
    maximum = max(values) or 1
    bars = []
    for index, value in enumerate(values):
        marker = markers.get(index)
        height = max(14, round(value / maximum * 82))
        bars.append(
            '<div class="gc-vis-bar-column">'
            f'<span class="gc-vis-bar-marker">{escape(marker) if marker else ""}</span>'
            f'<div class="gc-vis-bar {"is-marked" if marker else ""}" '
            f'style="height:{height}px"></div>'
            f'<span class="gc-vis-bar-value">{escape(str(value))}</span>'
            f'<span class="gc-vis-bar-index">{escape(index_label)} {index}</span>'
            "</div>"
        )
    span = ""
    if spec.get("span"):
        left, right = spec["span"]
        count = len(values)
        start = ((left + .5) / count) * 100
        width = ((right - left) / count) * 100
        span = (
            f'<div class="gc-vis-bar-span" style="left:{start:.2f}%;width:{width:.2f}%">'
            f'<span>{right - left} day{"s" if right - left != 1 else ""}</span></div>'
        )
    return f'<div class="gc-vis-bars">{span}{"".join(bars)}</div>'


def _grid_cells(
    values: list[list[Any]],
    classes: dict[tuple[int, int], str] | None = None,
    order: list[int] | None = None,
    display_zero_as: str | None = None,
    display_land_as: str | None = None,
) -> str:
    classes = classes or {}
    columns = max((len(row) for row in values), default=1)
    flat_cells = []
    flat_index = 0
    for row_index, row in enumerate(values):
        for column_index, value in enumerate(row):
            shown = "" if value is None else value
            if display_zero_as is not None and value == 0:
                shown = display_zero_as
            elif display_land_as is not None and value != 0:
                shown = display_land_as
            class_name = _classes(
                "gc-vis-grid-cell",
                classes.get((row_index, column_index)),
            )
            visit = order[flat_index] if order else None
            flat_cells.append(
                f'<div class="{class_name}">'
                f'<span>{escape(str(shown))}</span>'
                f'{f"<small>{visit}</small>" if visit is not None else ""}'
                "</div>"
            )
            flat_index += 1
    return (
        f'<div class="gc-vis-grid" style="--gc-grid-columns:{columns}">'
        f'{"".join(flat_cells)}</div>'
    )


def _grid(spec: dict[str, Any]) -> str:
    return _grid_cells(
        spec["values"],
        spec.get("cell_classes"),
        spec.get("order"),
        spec.get("display_zero_as"),
        spec.get("display_land_as"),
    )


def _grid_compare(spec: dict[str, Any]) -> str:
    before = _grid_cells(spec["before"], spec.get("before_classes"))
    after = _grid_cells(spec["after"], spec.get("after_classes"))
    return (
        '<div class="gc-vis-compare">'
        f'<div><span class="gc-vis-side-label">{escape(spec.get("left_label", "before"))}</span>'
        f"{before}</div>"
        '<div class="gc-vis-arrow" aria-hidden="true">→</div>'
        f'<div><span class="gc-vis-side-label">{escape(spec.get("right_label", "after"))}</span>'
        f"{after}</div>"
        "</div>"
    )


def _product(spec: dict[str, Any]) -> str:
    excluded = spec["excluded"]
    pieces = []
    for index, value in enumerate(spec["items"]):
        pieces.append(
            f'<div class="gc-vis-product-value {"is-excluded" if index == excluded else ""}">'
            f"{escape(str(value))}</div>"
        )
        if index < len(spec["items"]) - 1:
            pieces.append('<span class="gc-vis-times">×</span>')
    return (
        '<div class="gc-vis-product">'
        f'{"".join(pieces)}'
        f'<span class="gc-vis-product-note">exclude index {excluded}</span>'
        "</div>"
    )


def _container(spec: dict[str, Any]) -> str:
    values = spec["values"]
    left = spec["left"]
    right = spec["right"]
    maximum = max(values) or 1
    limiting = min(values[left], values[right])
    water_height = round(limiting / maximum * 96)
    edge_inset = 8.0
    usable_width = 100.0 - edge_inset * 2

    def horizontal_position(index: int) -> float:
        if len(values) == 1:
            return 50.0
        return edge_inset + index / (len(values) - 1) * usable_width

    bars = []
    for index, value in enumerate(values):
        height = max(8, round(value / maximum * 96))
        position = horizontal_position(index)
        bars.append(
            f'<div class="gc-vis-water-line {"is-boundary" if index in (left, right) else ""}" '
            f'style="height:{height}px;left:{position:.2f}%"><span>{value}</span></div>'
        )
    start = horizontal_position(left)
    width = horizontal_position(right) - start
    return (
        f'<div class="gc-vis-water" style="--gc-water-edge:{edge_inset:.2f}%">'
        f'<div class="gc-vis-water-fill" style="left:{start:.2f}%;width:{width:.2f}%;'
        f'height:{water_height}px"></div>'
        f'{"".join(bars)}'
        '<div class="gc-vis-water-baseline"></div>'
        "</div>"
    )


def _staircase(spec: dict[str, Any]) -> str:
    steps = []
    count = int(spec["steps"])
    for index in range(count):
        steps.append(
            f'<div class="gc-vis-step" style="height:{28 + index * 12}px">'
            f"<span>{index + 1}</span></div>"
        )
    return (
        '<div class="gc-vis-staircase">'
        f'{"".join(steps)}'
        '<div class="gc-vis-step-moves"><span>+1</span><span>+2</span></div>'
        "</div>"
    )


def _piles(spec: dict[str, Any]) -> str:
    speed = int(spec["speed"])
    piles = []
    for value in spec["values"]:
        portions = []
        remaining = int(value)
        while remaining > 0:
            portion = min(speed, remaining)
            portions.append(
                f'<span style="--gc-portion:{portion / speed:.3f}">{portion}</span>'
            )
            remaining -= portion
        piles.append(
            '<div class="gc-vis-pile">'
            f'<div class="gc-vis-portions">{"".join(portions)}</div>'
            f"<strong>{value}</strong>"
            f'<small>{len(portions)} hour{"s" if len(portions) != 1 else ""}</small>'
            "</div>"
        )
    return (
        '<div class="gc-vis-piles">'
        f'{"".join(piles)}'
        f'<div class="gc-vis-speed">speed = {speed} per hour</div>'
        "</div>"
    )


def _interval_row(
    intervals: list[list[int]],
    tone: str = "",
    new_interval: list[int] | None = None,
) -> str:
    minimum = min(start for start, _ in intervals)
    maximum = max(end for _, end in intervals)
    spread = max(1, maximum - minimum)
    edge_inset = 7.0
    usable_width = 100.0 - edge_inset * 2
    marks = []
    for start, end in intervals:
        left = edge_inset + (start - minimum) / spread * usable_width
        width = max(6, (end - start) / spread * usable_width)
        width = min(width, 100.0 - edge_inset - left)
        interval_tone = "is-new" if [start, end] == new_interval else tone
        marks.append(
            f'<div class="gc-vis-interval {interval_tone}" '
            f'style="left:{left:.2f}%;width:{width:.2f}%">'
            f"[{start}, {end}]</div>"
        )
    return f'<div class="gc-vis-interval-line">{"".join(marks)}</div>'


def _intervals(spec: dict[str, Any]) -> str:
    before_items = list(spec["before"])
    if spec.get("new"):
        before_items.append(spec["new"])
    before = _interval_row(before_items, new_interval=spec.get("new"))
    after = _interval_row(spec["after"], "is-merged")
    return (
        '<div class="gc-vis-intervals">'
        f'<div><span>before</span>{before}</div>'
        '<div class="gc-vis-interval-down" aria-hidden="true">↓</div>'
        f'<div><span>after</span>{after}</div>'
        "</div>"
    )


def _graph(spec: dict[str, Any]) -> str:
    nodes = spec["nodes"]
    active_edges = {tuple(edge) for edge in spec.get("active_edges", [])}
    active_nodes = set(spec.get("active_nodes", []))
    directed = bool(spec.get("directed"))
    edges = []
    for start, end in spec["edges"]:
        x1, y1 = nodes[start]
        x2, y2 = nodes[end]
        dx = x2 - x1
        # The graph canvas is twice as wide as it is tall, so vertical
        # percentages represent half as many pixels as horizontal percentages.
        dy = (y2 - y1) * .5
        length = hypot(dx, dy)
        angle = atan2(dy, dx) * 180 / 3.141592653589793
        if directed:
            length = max(1, length - 4.5)
        class_name = _classes(
            "gc-vis-graph-edge",
            "is-active" if (start, end) in active_edges or (end, start) in active_edges else None,
            "is-directed" if directed else None,
        )
        edges.append(
            f'<div class="{class_name}" style="left:{x1}%;top:{y1}%;'
            f'width:{length:.2f}%;transform:rotate({angle:.2f}deg)"></div>'
        )
    node_html = []
    for node, (x, y) in nodes.items():
        node_html.append(
            f'<div class="gc-vis-graph-node {"is-active" if node in active_nodes else ""}" '
            f'style="left:{x}%;top:{y}%">{escape(str(node))}</div>'
        )
    return f'<div class="gc-vis-graph">{"".join(edges)}{"".join(node_html)}</div>'


def _houses(spec: dict[str, Any]) -> str:
    active = set(spec["active"])
    houses = []
    for index, value in enumerate(spec["values"]):
        houses.append(
            f'<div class="gc-vis-house {"is-active" if index in active else ""}">'
            '<div class="gc-vis-roof"></div>'
            f'<div class="gc-vis-house-body">{value}</div>'
            f"<small>{index}</small>"
            "</div>"
        )
    return f'<div class="gc-vis-houses">{"".join(houses)}</div>'


def _decodings(spec: dict[str, Any]) -> str:
    rows = []
    for number_parts, letter_parts in spec["rows"]:
        numbers = " | ".join(escape(part) for part in number_parts)
        letters = " + ".join(escape(part) for part in letter_parts)
        rows.append(
            '<div class="gc-vis-decoding-row">'
            f"<span>{numbers}</span><b>→</b><span>{letters}</span>"
            "</div>"
        )
    return (
        '<div class="gc-vis-decodings">'
        f'<strong>{escape(spec["digits"])}</strong>'
        f'<div>{"".join(rows)}</div>'
        "</div>"
    )


def _segments(spec: dict[str, Any]) -> str:
    segments = "".join(
        f'<span class="tone-{index % 3 + 1}">{escape(segment)}</span>'
        for index, segment in enumerate(spec["segments"])
    )
    return f'<div class="gc-vis-segments">{segments}</div>'


def _sequence_compare(spec: dict[str, Any]) -> str:
    before = _sequence({"items": spec["before"]})
    after = _sequence({"items": spec["after"], "active": range(len(spec["after"]))})
    return (
        '<div class="gc-vis-sequence-compare">'
        f'<div><span class="gc-vis-side-label">{escape(spec.get("left_label", "before"))}</span>{before}</div>'
        '<div class="gc-vis-sequence-arrow" aria-hidden="true">↓</div>'
        f'<div><span class="gc-vis-side-label">{escape(spec.get("right_label", "after"))}</span>{after}</div>'
        "</div>"
    )


def _linked_list_row(values: list[Any], tone: str = "") -> str:
    nodes = []
    for index, value in enumerate(values[:14]):
        shown = value[0] if isinstance(value, list) and value else value
        random_target = (
            value[1]
            if isinstance(value, list) and len(value) == 2
            else None
        )
        nodes.append(
            f'<span class="gc-vis-list-node {tone}"><b>{escape(str(shown))}</b>'
            f'{f"<small>r → {escape(str(random_target))}</small>" if random_target is not None else ""}'
            "</span>"
        )
        if index < min(len(values), 14) - 1:
            nodes.append('<span class="gc-vis-list-arrow" aria-hidden="true">→</span>')
    if len(values) > 14:
        nodes.append('<span class="gc-vis-list-more">…</span>')
    return f'<div class="gc-vis-linked-row">{"".join(nodes)}</div>'


def _linked_list(spec: dict[str, Any]) -> str:
    before_values = spec["before"]
    if spec.get("grouped"):
        before = "".join(
            f'<div class="gc-vis-linked-group"><small>list {index + 1}</small>'
            f'{_linked_list_row(values)}</div>'
            for index, values in enumerate(before_values[:4])
        )
    else:
        before = _linked_list_row(before_values)
    after_values = spec.get("after")
    after = ""
    if isinstance(after_values, list):
        after = (
            '<div class="gc-vis-sequence-arrow" aria-hidden="true">↓</div>'
            f'{_linked_list_row(after_values, "is-result")}'
        )
    return f'<div class="gc-vis-linked">{before}{after}</div>'


def _operations(spec: dict[str, Any]) -> str:
    rows = []
    operations = spec["operations"]
    arguments = spec["arguments"]
    results = spec["results"]
    shown = min(len(operations), 8)
    for index in range(shown):
        argument = arguments[index] if index < len(arguments) else []
        result = results[index] if index < len(results) else None
        rows.append(
            '<div class="gc-vis-operation-row">'
            f'<code>{escape(str(operations[index]))}</code>'
            f'<span>{escape(_compact_value(argument))}</span>'
            '<b aria-hidden="true">→</b>'
            f'<span class="gc-vis-operation-result">{escape(_compact_value(result))}</span>'
            "</div>"
        )
    if len(operations) > shown:
        rows.append(
            f'<div class="gc-vis-operation-more">+ {len(operations) - shown} more operations</div>'
        )
    return f'<div class="gc-vis-operations">{"".join(rows)}</div>'


def _compact_value(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return str(value).lower()
    rendered = str(value)
    return rendered if len(rendered) <= 34 else rendered[:31] + "…"


def _tree(spec: dict[str, Any]) -> str:
    values = list(spec["values"])[:31]
    if not values or values[0] is None:
        return '<div class="gc-vis-empty">empty tree</div>'

    nodes: list[dict[str, Any]] = [{"value": values[0], "depth": 0}]
    edges: list[tuple[int, int]] = []
    queue = [0]
    value_index = 1
    while queue and value_index < len(values):
        parent = queue.pop(0)
        for _ in range(2):
            if value_index >= len(values):
                break
            value = values[value_index]
            value_index += 1
            if value is None:
                continue
            child = len(nodes)
            nodes.append({"value": value, "depth": nodes[parent]["depth"] + 1})
            edges.append((parent, child))
            queue.append(child)

    levels: dict[int, list[int]] = {}
    for index, node in enumerate(nodes):
        levels.setdefault(node["depth"], []).append(index)
    max_depth = max(levels)
    positions: dict[int, tuple[float, float]] = {}
    for depth, indexes in levels.items():
        for order, node_index in enumerate(indexes):
            x = 8 + (order + 1) / (len(indexes) + 1) * 84
            y = 9 + depth / max(1, max_depth) * 75
            positions[node_index] = (x, y)

    edge_html = []
    for parent, child in edges:
        x1, y1 = positions[parent]
        x2, y2 = positions[child]
        dx = x2 - x1
        dy = (y2 - y1) * .55
        length = hypot(dx, dy)
        angle = atan2(dy, dx) * 180 / 3.141592653589793
        edge_html.append(
            f'<span class="gc-vis-tree-edge" style="left:{x1:.2f}%;top:{y1:.2f}%;'
            f'width:{length:.2f}%;transform:rotate({angle:.2f}deg)"></span>'
        )
    active_values = set(spec.get("active_values", []))
    node_html = [
        f'<span class="gc-vis-tree-node {"is-active" if node["value"] in active_values else ""}" '
        f'style="left:{positions[index][0]:.2f}%;top:{positions[index][1]:.2f}%">'
        f'{escape(str(node["value"]))}</span>'
        for index, node in enumerate(nodes)
    ]
    height = 92 + max_depth * 30
    return (
        f'<div class="gc-vis-tree" style="height:{height}px">'
        f'{"".join(edge_html)}{"".join(node_html)}</div>'
    )


def _graph_auto(spec: dict[str, Any]) -> str:
    raw_edges = spec["edges"][:24]
    labels = []
    for edge in raw_edges:
        for value in edge[:2]:
            if value not in labels:
                labels.append(value)
    labels = labels[:16]
    count = max(1, len(labels))
    nodes = {}
    for index, label in enumerate(labels):
        angle = -1.5708 + index * 6.283185307179586 / count
        nodes[label] = (
            50 + 39 * cos(angle),
            50 + 36 * sin(angle),
        )
    edges = [
        (edge[0], edge[1])
        for edge in raw_edges
        if edge[0] in nodes and edge[1] in nodes
    ]
    return _graph(
        {
            "nodes": nodes,
            "edges": edges,
            "directed": spec.get("directed", False),
        }
    )


def _intervals_auto(spec: dict[str, Any]) -> str:
    before = _interval_row(spec["before"])
    after_values = spec.get("after")
    after = ""
    if after_values:
        after = (
            '<div class="gc-vis-interval-down" aria-hidden="true">↓</div>'
            f'<div><span>result</span>{_interval_row(after_values, "is-merged")}</div>'
        )
    return (
        '<div class="gc-vis-intervals">'
        f'<div><span>input</span>{before}</div>{after}</div>'
    )


def _points(spec: dict[str, Any]) -> str:
    points = spec["points"][:24]
    active_points = {
        tuple(point[:2]) for point in spec.get("active_points", [])
        if isinstance(point, list) and len(point) >= 2
    }
    if not points:
        return '<div class="gc-vis-empty">no points</div>'
    xs = [float(point[0]) for point in points]
    ys = [float(point[1]) for point in points]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    span_x = max(1.0, max_x - min_x)
    span_y = max(1.0, max_y - min_y)
    point_html = []
    for index, (x, y, *_) in enumerate(points):
        left = 8 + (float(x) - min_x) / span_x * 84
        bottom = 10 + (float(y) - min_y) / span_y * 76
        point_html.append(
            f'<span class="gc-vis-point {"is-active" if (x, y) in active_points else ""}" '
            f'style="left:{left:.2f}%;bottom:{bottom:.2f}%">'
            f'<b>{index}</b><small>({escape(str(x))}, {escape(str(y))})</small></span>'
        )
    return (
        '<div class="gc-vis-points"><span class="gc-vis-axis-x"></span>'
        f'<span class="gc-vis-axis-y"></span>{"".join(point_html)}</div>'
    )


def _string_grid(spec: dict[str, Any]) -> str:
    top = list(spec["top"])[:14]
    side = list(spec["side"])[:10]
    cells = ['<span class="gc-vis-string-corner"></span>']
    cells.extend(f"<b>{escape(value)}</b>" for value in top)
    for side_value in side:
        cells.append(f"<b>{escape(side_value)}</b>")
        cells.extend('<span></span>' for _ in top)
    return (
        '<div class="gc-vis-string-grid" '
        f'style="--gc-string-columns:{len(top) + 1}">{"".join(cells)}</div>'
    )


def _pyramid(spec: dict[str, Any]) -> str:
    rows = []
    for row in spec["rows"][:8]:
        rows.append(
            '<div class="gc-vis-pyramid-row">'
            + "".join(f"<span>{escape(str(value))}</span>" for value in row)
            + "</div>"
        )
    return f'<div class="gc-vis-pyramid">{"".join(rows)}</div>'


def _rectangles(spec: dict[str, Any]) -> str:
    ax1, ay1, ax2, ay2, bx1, by1, bx2, by2 = spec["coordinates"]
    min_x, max_x = min(ax1, bx1), max(ax2, bx2)
    min_y, max_y = min(ay1, by1), max(ay2, by2)
    span_x = max(1, max_x - min_x)
    span_y = max(1, max_y - min_y)

    def box(x1: float, y1: float, x2: float, y2: float, tone: str) -> str:
        left = 7 + (x1 - min_x) / span_x * 86
        bottom = 8 + (y1 - min_y) / span_y * 78
        width = max(5, (x2 - x1) / span_x * 86)
        height = max(8, (y2 - y1) / span_y * 78)
        return (
            f'<span class="gc-vis-rectangle {tone}" style="left:{left:.2f}%;'
            f'bottom:{bottom:.2f}%;width:{width:.2f}%;height:{height:.2f}%"></span>'
        )

    return (
        '<div class="gc-vis-rectangles">'
        f'{box(ax1, ay1, ax2, ay2, "tone-a")}'
        f'{box(bx1, by1, bx2, by2, "tone-b")}</div>'
    )


def _clock(spec: dict[str, Any]) -> str:
    hour = float(spec["hour"]) % 12
    minute = float(spec["minute"]) % 60
    hour_angle = hour * 30 + minute * .5
    minute_angle = minute * 6
    marks = "".join(f"<span>{value}</span>" for value in (12, 3, 6, 9))
    return (
        '<div class="gc-vis-clock">'
        f'{marks}<i class="is-hour" style="transform:rotate({hour_angle:.2f}deg)"></i>'
        f'<i class="is-minute" style="transform:rotate({minute_angle:.2f}deg)"></i>'
        '<b></b></div>'
    )


def _paired_bars(spec: dict[str, Any]) -> str:
    left = spec["left"]
    right = spec["right"]
    left_label = spec.get("left_label", "first")
    right_label = spec.get("right_label", "second")
    maximum = max([*left, *right, 1])
    groups = []
    for index, (left_value, right_value) in enumerate(zip(left[:12], right[:12])):
        groups.append(
            '<div class="gc-vis-paired-group">'
            f'<span class="is-left" style="height:{max(8, left_value / maximum * 74):.2f}px"></span>'
            f'<span class="is-right" style="height:{max(8, right_value / maximum * 74):.2f}px"></span>'
            f"<small>{index}</small></div>"
        )
    return (
        '<div class="gc-vis-paired-bars">'
        f'<div class="gc-vis-paired-legend"><span>{escape(left_label)}</span>'
        f'<span>{escape(right_label)}</span></div>'
        f'<div class="gc-vis-paired-groups">{"".join(groups)}</div></div>'
    )


def _books(spec: dict[str, Any]) -> str:
    books = spec["books"][:14]
    max_height = max((book[1] for book in books), default=1)
    total_width = max(sum(book[0] for book in books), 1)
    rendered = []
    for index, (thickness, height, *_) in enumerate(books):
        rendered.append(
            f'<span style="height:{max(18, height / max_height * 88):.2f}px;'
            f'width:{max(6, thickness / total_width * 100):.2f}%">'
            f'<b>{index}</b><small>{thickness} × {height}</small></span>'
        )
    return f'<div class="gc-vis-books">{"".join(rendered)}</div>'


def _trips(spec: dict[str, Any]) -> str:
    trips = spec["trips"][:12]
    minimum = min((trip[1] for trip in trips), default=0)
    maximum = max((trip[2] for trip in trips), default=1)
    spread = max(1, maximum - minimum)
    rows = []
    for passengers, start, end, *_ in trips:
        left = 6 + (start - minimum) / spread * 88
        width = max(5, (end - start) / spread * 88)
        rows.append(
            '<div class="gc-vis-trip-row">'
            f'<b>{escape(str(passengers))} riders</b>'
            f'<span style="left:{left:.2f}%;width:{width:.2f}%">'
            f"{escape(str(start))} → {escape(str(end))}</span></div>"
        )
    return f'<div class="gc-vis-trips">{"".join(rows)}</div>'


def _buildings(spec: dict[str, Any]) -> str:
    buildings = spec["buildings"][:16]
    min_x = min((building[0] for building in buildings), default=0)
    max_x = max((building[1] for building in buildings), default=1)
    max_height = max((building[2] for building in buildings), default=1)
    span_x = max(1, max_x - min_x)
    rendered = []
    for left, right, height, *_ in buildings:
        x = 4 + (left - min_x) / span_x * 92
        width = max(3, (right - left) / span_x * 92)
        rendered.append(
            f'<span style="left:{x:.2f}%;width:{width:.2f}%;'
            f'height:{max(8, height / max_height * 110):.2f}px">'
            f"<small>{escape(str(height))}</small></span>"
        )
    return f'<div class="gc-vis-buildings">{"".join(rendered)}</div>'


def _matrix_pair(spec: dict[str, Any]) -> str:
    left = _grid_cells(spec["left"])
    right = _grid_cells(spec["right"])
    return (
        '<div class="gc-vis-matrix-pair">'
        f'<div><span class="gc-vis-side-label">matrix A</span>{left}</div>'
        '<b aria-hidden="true">×</b>'
        f'<div><span class="gc-vis-side-label">matrix B</span>{right}</div>'
        "</div>"
    )


def _first_queen_board(size: int) -> list[str]:
    columns: set[int] = set()
    rising: set[int] = set()
    falling: set[int] = set()
    queens: list[int] = []

    def place(row: int) -> bool:
        if row == size:
            return True
        for column in range(size):
            if (
                column in columns
                or row + column in rising
                or row - column in falling
            ):
                continue
            columns.add(column)
            rising.add(row + column)
            falling.add(row - column)
            queens.append(column)
            if place(row + 1):
                return True
            queens.pop()
            columns.remove(column)
            rising.remove(row + column)
            falling.remove(row - column)
        return False

    if size < 1 or size > 10 or not place(0):
        return []
    return [
        "." * column + "Q" + "." * (size - column - 1)
        for column in queens
    ]


def _queens(spec: dict[str, Any]) -> str:
    board = spec["board"]
    classes = {
        (row, column): "source"
        for row, values in enumerate(board)
        for column, value in enumerate(values)
        if value == "Q"
    }
    return _grid_cells([list(row) for row in board], classes)


def _argument_names(problem: dict[str, Any]) -> list[str]:
    try:
        tree = ast.parse(f"{problem['signature']}\n    pass\n")
        function = tree.body[0]
        return [argument.arg for argument in function.args.args]
    except (KeyError, SyntaxError, AttributeError):
        return []


def _result_text(value: Any) -> str:
    return _compact_value(value)


def _auto_visual_spec(problem: dict[str, Any]) -> dict[str, Any] | None:
    decision = problem.get("visualization")
    tests = problem.get("tests", [])
    if not decision or not tests:
        return None

    args = tests[0].get("args", [])
    expected = tests[0].get("expected")
    names = _argument_names(problem)
    title = problem["title"]
    requested_kind = decision["kind"]
    label = f"The first example for {title}"
    result = _result_text(expected)

    def argument(index: int, default: Any = None) -> Any:
        return args[index] if 0 <= index < len(args) else default

    if requested_kind == "grid_dimensions":
        indexes = decision.get("arg_indexes", [0, 1])
        rows = int(argument(indexes[0], 0))
        columns = int(argument(indexes[1], 0))
        if not 1 <= rows <= 12 or not 1 <= columns <= 16:
            return None
        values = [["·" for _ in range(columns)] for _ in range(rows)]
        classes = (
            {(0, 0): "source", (rows - 1, columns - 1): "connected"}
            if title == "Unique Paths"
            else {}
        )
        return {
            "kind": "grid",
            "label": label,
            "values": values,
            "cell_classes": classes,
            "caption": (
                f"The first example uses a {rows} × {columns} grid; "
                f"the expected result is {result}."
            ),
        }

    if requested_kind == "pyramid_input":
        rows = argument(decision.get("arg_index", 0), [])
        return {
            "kind": "pyramid",
            "label": label,
            "rows": rows,
            "caption": (
                "The input rows keep their triangular adjacency visible; "
                f"the expected result is {result}."
            ),
        }

    if requested_kind == "keypad":
        return {
            "kind": "grid",
            "label": label,
            "values": [[1, 2, 3], [4, 5, 6], [7, 8, 9], [None, 0, None]],
            "caption": (
                "Knight moves connect keys on this phone layout. "
                f"For the first example, the expected count is {result}."
            ),
        }

    if requested_kind == "books":
        return {
            "kind": "books",
            "label": label,
            "books": argument(decision.get("arg_index", 0), []),
            "caption": (
                "Each book keeps its input order, width, and relative height; "
                f"the minimum total shelf height is {result}."
            ),
        }

    if requested_kind == "guard_grid":
        if len(args) < 4:
            return None
        rows, columns, guards, walls = args[:4]
        if not 1 <= rows <= 12 or not 1 <= columns <= 16:
            return None
        values = [["·" for _ in range(columns)] for _ in range(rows)]
        classes: dict[tuple[int, int], str] = {}
        for row, column in guards:
            values[row][column] = "G"
            classes[(row, column)] = "source"
        for row, column in walls:
            values[row][column] = "W"
            classes[(row, column)] = "separate"
        return {
            "kind": "grid",
            "label": label,
            "values": values,
            "cell_classes": classes,
            "caption": (
                "G marks guards and W marks walls in the first example; "
                f"{result} cells remain unguarded."
            ),
        }

    if requested_kind == "knight":
        if len(args) < 2:
            return None
        x, y = int(args[0]), int(args[1])
        radius = max(2, min(5, max(abs(x), abs(y))))
        values = [
            [f"{column},{row}" for column in range(-radius, radius + 1)]
            for row in range(radius, -radius - 1, -1)
        ]
        classes = {
            (radius, radius): "source",
            (radius - y, radius + x): "connected",
        }
        return {
            "kind": "grid",
            "label": label,
            "values": values,
            "cell_classes": classes,
            "caption": (
                f"The center is (0, 0) and the marked target is ({x}, {y}); "
                f"the minimum move count is {result}."
            ),
        }

    if requested_kind == "trips":
        return {
            "kind": "trips",
            "label": label,
            "trips": argument(decision.get("arg_index", 0), []),
            "caption": (
                "Each span shows where its passengers are in the car. "
                f"The first example returns {result}."
            ),
        }

    if requested_kind == "buildings":
        return {
            "kind": "buildings",
            "label": label,
            "buildings": argument(decision.get("arg_index", 0), []),
            "caption": (
                "Overlapping building footprints and heights form the first "
                "example's skyline."
            ),
        }

    if requested_kind == "fleet":
        if len(args) < 3:
            return None
        return {
            "kind": "paired_bars",
            "label": label,
            "left": args[1],
            "right": args[2],
            "left_label": "position",
            "right_label": "speed",
            "caption": (
                f"Each pair belongs to one car heading toward target {args[0]}; "
                f"the expected fleet count is {result}."
            ),
        }

    if requested_kind == "tic_tac_toe":
        moves = argument(decision.get("arg_index", 0), [])
        board: list[list[str]] = [["" for _ in range(3)] for _ in range(3)]
        classes: dict[tuple[int, int], str] = {}
        for move_index, (row, column) in enumerate(moves):
            board[row][column] = "A" if move_index % 2 == 0 else "B"
            classes[(row, column)] = (
                "connected" if move_index % 2 == 0 else "separate"
            )
        return {
            "kind": "grid",
            "label": label,
            "values": board,
            "cell_classes": classes,
            "caption": (
                "The moves are applied in order, with A and B alternating; "
                f"the expected result is {result}."
            ),
        }

    if requested_kind == "character_grid":
        rows = argument(decision.get("arg_index", 0), [])
        return {
            "kind": "grid",
            "label": label,
            "values": [list(row) for row in rows],
            "caption": (
                "The first example's start, walls, keys, and locks remain in their "
                f"grid positions. The expected distance is {result}."
            ),
        }

    if requested_kind == "matrix_pair":
        indexes = decision.get("arg_indexes", [0, 1])
        return {
            "kind": "matrix_pair",
            "label": label,
            "left": argument(indexes[0], []),
            "right": argument(indexes[1], []),
            "caption": (
                "The two sparse input matrices are shown side by side; "
                f"their product is {result}."
            ),
        }

    if requested_kind == "timestamp_graph":
        logs = argument(decision.get("arg_index", 0), [])
        active_logs = [
            log for log in logs
            if isinstance(expected, int) and log[0] <= expected
        ]
        return {
            "kind": "graph_auto",
            "label": label,
            "edges": [log[1:3] for log in active_logs],
            "caption": (
                "The edges present by the expected timestamp connect everyone "
                f"for the first time at {result}."
            ),
        }

    if requested_kind == "sequence_auto":
        index = decision.get("arg_index", 0)
        items = argument(index, [])
        active: list[int] = []
        if isinstance(expected, int) and any(
            word in title for word in ("Index", "Peak", "Pivot", "Duplicate")
        ):
            if "Duplicate" in title:
                active = [
                    item_index
                    for item_index, value in enumerate(items)
                    if value == expected
                ]
            elif 0 <= expected < len(items):
                active = [expected]
        relationship = "positions and neighboring values"
        if "Subarray" in title or "Contiguous" in title:
            relationship = "which values are adjacent"
        elif "Subsequence" in title:
            relationship = "the original left-to-right order"
        elif "Jump" in title or "Gas Station" in title:
            relationship = "each value's position along the route"
        return {
            "kind": "sequence",
            "label": label,
            "items": items,
            "active": active,
            "caption": (
                f"The indexed cells make {relationship} visible; "
                f"the expected result is {result}."
            ),
        }

    if requested_kind == "string_sequence":
        index = decision.get("arg_index", 0)
        value = str(argument(index, ""))
        active: list[int] = []
        if isinstance(expected, str) and expected and expected in value:
            start = value.index(expected)
            active = list(range(start, start + len(expected)))
        return {
            "kind": "sequence",
            "label": label,
            "items": list(value),
            "active": active,
            "caption": (
                "Each cell is one character in the first input, preserving exact "
                f"position and order. The expected result is {result}."
            ),
        }

    if requested_kind == "sequence_compare":
        before = argument(decision.get("arg_index", 0), [])
        if not isinstance(expected, list) or any(
            isinstance(value, list) for value in expected
        ):
            return None
        return {
            "kind": "sequence_compare",
            "label": label,
            "before": before,
            "after": expected,
            "caption": (
                "The first row is the example input and the second row is its "
                "required output."
            ),
        }

    if requested_kind == "bars_auto":
        values = argument(decision.get("arg_index", 0), [])
        return {
            "kind": "bars",
            "label": label,
            "values": values,
            "index_label": "i",
            "caption": (
                "Bar height preserves the relative size at every input index; "
                f"the expected result is {result}."
            ),
        }

    if requested_kind in {"grid_auto", "grid_compare_auto", "grid_output"}:
        if requested_kind == "grid_output":
            grid = expected
        else:
            grid = argument(decision.get("arg_index", 0), [])
        if not isinstance(grid, list) or not grid:
            return None
        if requested_kind == "grid_compare_auto":
            return {
                "kind": "grid_compare",
                "label": label,
                "before": grid,
                "after": expected,
                "left_label": "input",
                "right_label": "expected",
                "caption": (
                    "The two grids show the first example before and after the "
                    "required transformation."
                ),
            }
        classes: dict[tuple[int, int], str] = {}
        if (
            isinstance(expected, list)
            and expected
            and all(
                isinstance(cell, list)
                and len(cell) >= 2
                and all(isinstance(value, int) for value in cell[:2])
                for cell in expected
            )
        ):
            classes = {
                (cell[0], cell[1]): "connected"
                for cell in expected
                if 0 <= cell[0] < len(grid)
                and 0 <= cell[1] < len(grid[cell[0]])
            }
        if "target" in names:
            target = argument(names.index("target"))
            for row_index, row in enumerate(grid):
                for column_index, value in enumerate(row):
                    if value == target:
                        classes[(row_index, column_index)] = "source"
        if title == "Find the Celebrity" and isinstance(expected, int):
            for row_index in range(len(grid)):
                if expected < len(grid[row_index]):
                    classes[(row_index, expected)] = "connected"
            if expected < len(grid):
                for column_index in range(len(grid[expected])):
                    classes[(expected, column_index)] = "source"
        return {
            "kind": "grid",
            "label": label,
            "values": grid,
            "cell_classes": classes,
            "caption": (
                "The first example is laid out by row and column; "
                f"its expected result is {result}."
            ),
        }

    if requested_kind == "tree":
        if decision.get("source") == "expected":
            values = expected
        else:
            values = argument(decision.get("arg_index", 0), [])
        if not isinstance(values, list):
            return None
        active_values: list[Any] = []
        if isinstance(expected, (str, int, float, bool)):
            active_values = [expected]
        elif (
            isinstance(expected, list)
            and expected
            and all(not isinstance(value, (list, dict)) for value in expected)
            and decision.get("source") != "expected"
        ):
            active_values = [value for value in expected if value is not None]
        return {
            "kind": "tree",
            "label": label,
            "values": values,
            "active_values": active_values,
            "caption": (
                (
                    "The diagram is the tree required by the first example's output."
                    if decision.get("source") == "expected"
                    else "The nodes follow the first example's level-order representation; "
                    f"the expected result is {result}."
                )
            ),
        }

    if requested_kind == "linked_list":
        index = decision.get("arg_index", 0)
        before = argument(index, [])
        grouped = bool(
            title == "Merge k Sorted Lists"
            or decision.get("grouped")
            or decision.get("all_list_args")
        )
        if decision.get("arg_indexes"):
            before = [
                argument(item_index, [])
                for item_index in decision["arg_indexes"]
            ]
        elif decision.get("all_list_args"):
            before = [
                value for value in args
                if isinstance(value, list)
            ]
        after = None
        if isinstance(expected, list) and (
            grouped or expected != before
        ):
            after = expected
        return {
            "kind": "linked_list",
            "label": label,
            "before": before,
            "after": after,
            "grouped": grouped,
            "caption": (
                "Arrows preserve node order in the first example"
                + (
                    "; the lower row is the expected list."
                    if after is not None
                    else f"; the expected result is {result}."
                )
            ),
        }

    if requested_kind == "operations":
        if len(args) < 2 or not isinstance(expected, list):
            return None
        return {
            "kind": "operations",
            "label": label,
            "operations": args[0],
            "arguments": args[1],
            "results": expected,
            "caption": (
                "Each row pairs an operation and its arguments with the "
                "corresponding expected result."
            ),
        }

    if requested_kind == "graph_auto":
        edges = argument(decision.get("arg_index", 0), [])
        directed = any(
            word in title
            for word in (
                "Course",
                "Flight",
                "Network Delay",
                "Reconstruct Itinerary",
                "Alien Dictionary",
            )
        )
        return {
            "kind": "graph_auto",
            "label": label,
            "edges": edges,
            "directed": directed,
            "caption": (
                "The first example's connections are shown as "
                f"{'directed' if directed else 'undirected'} edges; "
                f"the expected result is {result}."
            ),
        }

    if requested_kind == "intervals_auto":
        before = argument(decision.get("arg_index", 0), [])
        after = (
            expected
            if isinstance(expected, list)
            and all(isinstance(item, list) and len(item) >= 2 for item in expected)
            else None
        )
        return {
            "kind": "intervals_auto",
            "label": label,
            "before": before,
            "after": after,
            "caption": (
                "Horizontal position makes overlap and separation visible in "
                f"the first example. The expected result is {result}."
            ),
        }

    if requested_kind == "points":
        return {
            "kind": "points",
            "label": label,
            "points": argument(decision.get("arg_index", 0), []),
            "active_points": expected if isinstance(expected, list) else [],
            "caption": (
                "The coordinate plane preserves the relative positions from "
                f"the first example. The expected result is {result}."
            ),
        }

    if requested_kind == "string_grid":
        indexes = decision.get("arg_indexes", [0, 1])
        return {
            "kind": "string_grid",
            "label": label,
            "top": str(argument(indexes[0], "")),
            "side": str(argument(indexes[1], "")),
            "caption": (
                "The row and column labels expose the character-pair state space "
                f"for the first example; the expected result is {result}."
            ),
        }

    if requested_kind == "pyramid":
        rows = expected if isinstance(expected, list) else []
        if rows and not isinstance(rows[0], list):
            rows = [rows]
        return {
            "kind": "pyramid",
            "label": label,
            "rows": rows,
            "caption": "The rows show the exact expected structure for the first example.",
        }

    if requested_kind == "queens":
        board: list[str] = []
        if (
            isinstance(expected, list)
            and expected
            and isinstance(expected[0], list)
        ):
            board = expected[0]
        elif args and isinstance(args[0], int):
            board = _first_queen_board(args[0])
        if not board:
            return None
        return {
            "kind": "queens",
            "label": label,
            "board": board,
            "caption": (
                "One valid arrangement for the first example places one queen "
                "in every row without shared columns or diagonals."
            ),
        }

    if requested_kind == "rectangles":
        return {
            "kind": "rectangles",
            "label": label,
            "coordinates": args,
            "caption": (
                "The two coordinate rectangles expose their overlap; "
                f"the combined area is {result}."
            ),
        }

    if requested_kind == "clock":
        if len(args) < 2:
            return None
        return {
            "kind": "clock",
            "label": label,
            "hour": args[0],
            "minute": args[1],
            "caption": (
                "The hands show the first example time; "
                f"their smaller angle is {result} degrees."
            ),
        }

    if requested_kind == "paired_bars":
        indexes = decision.get("arg_indexes", [0, 1])
        return {
            "kind": "paired_bars",
            "label": label,
            "left": argument(indexes[0], []),
            "right": argument(indexes[1], []),
            "left_label": names[indexes[0]] if indexes[0] < len(names) else "first",
            "right_label": names[indexes[1]] if indexes[1] < len(names) else "second",
            "caption": f"The paired values produce the expected result {result}.",
        }

    return None


RENDERERS = {
    "sequence": _sequence,
    "bars": _bars,
    "grid": _grid,
    "grid_compare": _grid_compare,
    "product": _product,
    "container": _container,
    "staircase": _staircase,
    "piles": _piles,
    "intervals": _intervals,
    "graph": _graph,
    "houses": _houses,
    "decodings": _decodings,
    "segments": _segments,
    "sequence_compare": _sequence_compare,
    "linked_list": _linked_list,
    "operations": _operations,
    "tree": _tree,
    "graph_auto": _graph_auto,
    "intervals_auto": _intervals_auto,
    "points": _points,
    "string_grid": _string_grid,
    "pyramid": _pyramid,
    "queens": _queens,
    "rectangles": _rectangles,
    "clock": _clock,
    "paired_bars": _paired_bars,
    "books": _books,
    "trips": _trips,
    "buildings": _buildings,
    "matrix_pair": _matrix_pair,
}


def problem_visual_html(problem: dict[str, Any] | str) -> str | None:
    if isinstance(problem, str):
        spec = PROBLEM_VISUALS.get(problem)
    else:
        spec = PROBLEM_VISUALS.get(problem["id"]) or _auto_visual_spec(problem)
    if spec is None:
        return None
    renderer = RENDERERS.get(spec["kind"])
    if renderer is None:
        return None
    visual = renderer(spec)
    return (
        f'<figure class="gc-problem-visual" aria-label="{escape(spec["label"])}">'
        f'<div class="gc-vis-stage">{visual}</div>'
        f'<figcaption>{escape(spec["caption"])}</figcaption>'
        "</figure>"
    )
