from __future__ import annotations

import ast
from collections import deque
from html import escape
from heapq import heappop, heappush
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
    active_edges = {tuple(edge[:2]) for edge in spec.get("active_edges", [])}
    active_nodes = set(spec.get("active_nodes", []))
    node_annotations = spec.get("node_annotations", {})
    directed = bool(spec.get("directed"))
    edges = []
    for edge in spec["edges"]:
        start, end = edge[:2]
        edge_label = edge[2] if len(edge) > 2 else None
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
            "is-active"
            if (start, end) in active_edges
            or (not directed and (end, start) in active_edges)
            else None,
            "is-directed" if directed else None,
        )
        edges.append(
            f'<div class="{class_name}" style="left:{x1}%;top:{y1}%;'
            f'width:{length:.2f}%;transform:rotate({angle:.2f}deg)">'
            f'{f"""<span class="gc-vis-graph-edge-label" style="transform:translate(-50%,-50%) rotate({-angle:.2f}deg)">{escape(str(edge_label))}</span>""" if edge_label is not None else ""}'
            "</div>"
        )
    node_html = []
    for node, (x, y) in nodes.items():
        annotation = node_annotations.get(node)
        node_html.append(
            f'<div class="gc-vis-graph-node {"is-active" if node in active_nodes else ""}" '
            f'style="left:{x}%;top:{y}%"><b>{escape(str(node))}</b>'
            f'{f"<small>{escape(str(annotation))}</small>" if annotation is not None else ""}'
            "</div>"
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


def _house_circle(spec: dict[str, Any]) -> str:
    values = spec["values"]
    active = set(spec.get("active", []))
    count = max(1, len(values))
    rendered = []
    for index, value in enumerate(values):
        angle = -1.5708 + index * 6.283185307179586 / count
        x = 50 + 38 * cos(angle)
        y = 50 + 38 * sin(angle)
        rendered.append(
            f'<span class="gc-vis-circle-house {"is-active" if index in active else ""}" '
            f'style="left:{x:.2f}%;top:{y:.2f}%"><b>{escape(str(value))}</b>'
            f"<small>{index}</small></span>"
        )
    return (
        '<div class="gc-vis-house-circle">'
        f'{"".join(rendered)}<span class="gc-vis-circle-link"></span></div>'
    )


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


def _linked_list_row(
    values: list[Any],
    tone: str = "",
    arrow: str = "→",
) -> str:
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
            nodes.append(
                '<span class="gc-vis-list-arrow" aria-hidden="true">'
                f"{escape(arrow)}</span>"
            )
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


def _parse_tree_nodes(values: list[Any]) -> list[dict[str, Any]]:
    values = list(values)[:31]
    if not values or values[0] is None:
        return []
    nodes: list[dict[str, Any]] = [
        {"value": values[0], "depth": 0, "slot": 0, "parent": None}
    ]
    queue = [0]
    value_index = 1
    while queue and value_index < len(values):
        parent_index = queue.pop(0)
        parent = nodes[parent_index]
        for child_offset in range(2):
            if value_index >= len(values):
                break
            value = values[value_index]
            value_index += 1
            if value is None:
                continue
            child_index = len(nodes)
            nodes.append(
                {
                    "value": value,
                    "depth": parent["depth"] + 1,
                    "slot": parent["slot"] * 2 + child_offset + 1,
                    "parent": parent_index,
                }
            )
            queue.append(child_index)
    return nodes


def _tree_value_order(values: list[Any], ordered_values: list[Any]) -> dict[int, int]:
    nodes = _parse_tree_nodes(values)
    unused = set(range(len(nodes)))
    badges: dict[int, int] = {}
    for order, value in enumerate(ordered_values, start=1):
        match = next(
            (
                index
                for index, node in enumerate(nodes)
                if index in unused and node["value"] == value
            ),
            None,
        )
        if match is None:
            continue
        unused.remove(match)
        badges[match] = order
    return badges


def _tree_path_indices(values: list[Any], path_values: list[Any]) -> list[int]:
    nodes = _parse_tree_nodes(values)
    if not nodes or not path_values or nodes[0]["value"] != path_values[0]:
        return []

    children: dict[int, list[int]] = {}
    for index, node in enumerate(nodes):
        if node["parent"] is not None:
            children.setdefault(node["parent"], []).append(index)

    def visit(node_index: int, path_index: int) -> list[int] | None:
        if nodes[node_index]["value"] != path_values[path_index]:
            return None
        if path_index == len(path_values) - 1:
            return [node_index]
        for child in children.get(node_index, []):
            suffix = visit(child, path_index + 1)
            if suffix:
                return [node_index, *suffix]
        return None

    return visit(0, 0) or []


def _tree_index_path(nodes: list[dict[str, Any]], end: int) -> list[int]:
    path = [end]
    while nodes[path[-1]]["parent"] is not None:
        path.append(nodes[path[-1]]["parent"])
    return list(reversed(path))


def _tree_path_between(
    nodes: list[dict[str, Any]],
    first: int,
    second: int,
) -> list[int]:
    first_path = _tree_index_path(nodes, first)
    second_path = _tree_index_path(nodes, second)
    split = 0
    while (
        split < min(len(first_path), len(second_path))
        and first_path[split] == second_path[split]
    ):
        split += 1
    return [
        *reversed(first_path[split:]),
        first_path[split - 1],
        *second_path[split:],
    ]


def _tree_depth_path(values: list[Any], shortest: bool = False) -> list[int]:
    nodes = _parse_tree_nodes(values)
    parent_indexes = {
        node["parent"] for node in nodes if node["parent"] is not None
    }
    leaves = [index for index in range(len(nodes)) if index not in parent_indexes]
    if not leaves:
        return []
    end = min(
        leaves,
        key=lambda index: nodes[index]["depth"],
    ) if shortest else max(
        leaves,
        key=lambda index: nodes[index]["depth"],
    )
    return _tree_index_path(nodes, end)


def _tree_diameter_path(values: list[Any]) -> list[int]:
    nodes = _parse_tree_nodes(values)
    if not nodes:
        return []
    best: list[int] = [0]
    for first in range(len(nodes)):
        for second in range(first, len(nodes)):
            candidate = _tree_path_between(nodes, first, second)
            if len(candidate) > len(best):
                best = candidate
    return best


def _tree_maximum_sum_path(values: list[Any]) -> list[int]:
    nodes = _parse_tree_nodes(values)
    best: list[int] = []
    best_sum: int | float | None = None
    for first in range(len(nodes)):
        for second in range(first, len(nodes)):
            candidate = _tree_path_between(nodes, first, second)
            if not all(
                isinstance(nodes[index]["value"], (int, float))
                for index in candidate
            ):
                continue
            total = sum(nodes[index]["value"] for index in candidate)
            if best_sum is None or total > best_sum:
                best_sum = total
                best = candidate
    return best


def _tree_good_node_indices(values: list[Any]) -> list[int]:
    nodes = _parse_tree_nodes(values)
    good = []
    for index, node in enumerate(nodes):
        path = _tree_index_path(nodes, index)
        if node["value"] >= max(nodes[ancestor]["value"] for ancestor in path):
            good.append(index)
    return good


def _tree_sum_path(
    values: list[Any],
    target: int | float,
    root_to_leaf: bool,
) -> list[int]:
    nodes = _parse_tree_nodes(values)
    parent_indexes = {
        node["parent"] for node in nodes if node["parent"] is not None
    }
    for end in range(len(nodes)):
        if root_to_leaf and end in parent_indexes:
            continue
        path = _tree_index_path(nodes, end)
        candidates = [path] if root_to_leaf else [path[start:] for start in range(len(path))]
        for candidate in candidates:
            if sum(nodes[index]["value"] for index in candidate) == target:
                return candidate
    return []


def _tree_average_match_indices(values: list[Any]) -> list[int]:
    nodes = _parse_tree_nodes(values)
    children: dict[int, list[int]] = {}
    for index, node in enumerate(nodes):
        if node["parent"] is not None:
            children.setdefault(node["parent"], []).append(index)
    matches = []

    def total(node_index: int) -> tuple[int | float, int]:
        subtotal = nodes[node_index]["value"]
        count = 1
        for child in children.get(node_index, []):
            child_total, child_count = total(child)
            subtotal += child_total
            count += child_count
        if subtotal // count == nodes[node_index]["value"]:
            matches.append(node_index)
        return subtotal, count

    if nodes:
        total(0)
    return matches


def _tree_even_grandparent_indices(values: list[Any]) -> list[int]:
    nodes = _parse_tree_nodes(values)
    matches = []
    for index, node in enumerate(nodes):
        parent = node["parent"]
        grandparent = nodes[parent]["parent"] if parent is not None else None
        if (
            grandparent is not None
            and isinstance(nodes[grandparent]["value"], int)
            and nodes[grandparent]["value"] % 2 == 0
        ):
            matches.append(index)
    return matches


def _tree_removal_rounds(values: list[Any]) -> dict[int, int]:
    nodes = _parse_tree_nodes(values)
    children: dict[int, list[int]] = {}
    for index, node in enumerate(nodes):
        if node["parent"] is not None:
            children.setdefault(node["parent"], []).append(index)
    rounds: dict[int, int] = {}

    def visit(node_index: int) -> int:
        round_number = 1 + max(
            (visit(child) for child in children.get(node_index, [])),
            default=0,
        )
        rounds[node_index] = round_number
        return round_number

    if nodes:
        visit(0)
    return rounds


def _tree(spec: dict[str, Any]) -> str:
    values = list(spec["values"])[:31]
    nodes = _parse_tree_nodes(values)
    if not nodes:
        return '<div class="gc-vis-empty">empty tree</div>'

    max_depth = max(node["depth"] for node in nodes)
    positions: dict[int, tuple[float, float]] = {}
    for index, node in enumerate(nodes):
        depth = node["depth"]
        first_slot = 2**depth - 1
        position_in_level = node["slot"] - first_slot
        x = 4 + (position_in_level + .5) / (2**depth) * 92
        y = 10 + depth / max(1, max_depth) * 72
        positions[index] = (x, y)

    edge_html = []
    for child, node in enumerate(nodes):
        parent = node["parent"]
        if parent is None:
            continue
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
    if spec.get("next_links"):
        for depth in range(max_depth + 1):
            level = sorted(
                (
                    index for index, node in enumerate(nodes)
                    if node["depth"] == depth
                ),
                key=lambda index: positions[index][0],
            )
            for first, second in zip(level, level[1:]):
                x1, y1 = positions[first]
                x2, _ = positions[second]
                edge_html.append(
                    '<span class="gc-vis-tree-next-link" '
                    f'style="left:{x1 + 2:.2f}%;top:{y1:.2f}%;'
                    f'width:{max(0, x2 - x1 - 4):.2f}%">→</span>'
                )
    active_values = set(spec.get("active_values", []))
    target_values = set(spec.get("target_values", []))
    active_indices = set(spec.get("active_indices", []))
    target_indices = set(spec.get("target_indices", []))
    badges = spec.get("badges", {})
    node_html = []
    for index, node in enumerate(nodes):
        class_name = _classes(
            "gc-vis-tree-node",
            "is-active"
            if index in active_indices or node["value"] in active_values
            else None,
            "is-target"
            if index in target_indices or node["value"] in target_values
            else None,
        )
        badge = badges.get(index)
        node_html.append(
            f'<span class="{class_name}" '
            f'style="left:{positions[index][0]:.2f}%;top:{positions[index][1]:.2f}%">'
            f'{escape(str(node["value"]))}'
            f'{f"<small>{escape(str(badge))}</small>" if badge is not None else ""}'
            "</span>"
        )
    height = 92 + max_depth * 30
    return (
        f'<div class="gc-vis-tree" style="height:{height}px">'
        f'{"".join(edge_html)}{"".join(node_html)}</div>'
    )


def _tree_collection(spec: dict[str, Any]) -> str:
    panels = []
    for item in spec["trees"]:
        panels.append(
            '<div class="gc-vis-tree-panel">'
            f'<span class="gc-vis-side-label">{escape(item["label"])}</span>'
            f'{_tree(item)}</div>'
        )
    return f'<div class="gc-vis-tree-collection">{"".join(panels)}</div>'


def _tree_list_compare(spec: dict[str, Any]) -> str:
    output = [value for value in spec["output"] if value is not None]
    circular = spec.get("circular", False)
    output_row = _linked_list_row(
        output,
        "is-result",
        "↔" if circular else "→",
    )
    if circular:
        output_row += (
            '<span class="gc-vis-list-loop">'
            "last ↔ first</span>"
        )
    return (
        '<div class="gc-vis-tree-list">'
        '<div class="gc-vis-tree-panel">'
        '<span class="gc-vis-side-label">input tree</span>'
        f'{_tree({"values": spec["input"]})}</div>'
        '<div class="gc-vis-arrow" aria-hidden="true">→</div>'
        '<div><span class="gc-vis-side-label">'
        f'{escape(spec.get("output_label", "expected list"))}</span>'
        f"{output_row}</div>"
        "</div>"
    )


def _graph_auto(spec: dict[str, Any]) -> str:
    raw_edges = spec["edges"][:24]
    labels = list(spec.get("node_labels", []))
    for edge in raw_edges:
        for value in edge[:2]:
            if value not in labels:
                labels.append(value)
    labels = labels[:16]
    edges = [
        tuple(edge)
        for edge in raw_edges
        if edge[0] in labels and edge[1] in labels
    ]
    pair_edges = [(edge[0], edge[1]) for edge in edges]
    directed = spec.get("directed", False)
    nodes: dict[Any, tuple[float, float]] = {}

    adjacency = {label: [] for label in labels}
    for first, second in pair_edges:
        if second not in adjacency[first]:
            adjacency[first].append(second)
        if first not in adjacency[second]:
            adjacency[second].append(first)
    connected = not labels
    if labels:
        visited = {labels[0]}
        stack = [labels[0]]
        while stack:
            node = stack.pop()
            for neighbor in adjacency[node]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    stack.append(neighbor)
        connected = len(visited) == len(labels)
    is_tree = connected and len(pair_edges) == max(0, len(labels) - 1)

    if is_tree and labels:
        directed_roots = (
            [
                label for label in labels
                if all(second != label for _, second in pair_edges)
            ]
            if directed
            else []
        )
        root = (
            directed_roots[0]
            if directed_roots
            else 0 if 0 in labels
            else labels[0]
        )
        children: dict[Any, list[Any]] = {}
        depths = {root: 0}

        def build(node: Any, parent: Any | None) -> None:
            children[node] = [
                neighbor for neighbor in adjacency[node]
                if neighbor != parent
            ]
            for child in children[node]:
                depths[child] = depths[node] + 1
                build(child, node)

        build(root, None)
        raw_x: dict[Any, float] = {}
        next_leaf = 0

        def place(node: Any) -> float:
            nonlocal next_leaf
            child_positions = [place(child) for child in children[node]]
            if child_positions:
                raw_x[node] = sum(child_positions) / len(child_positions)
            else:
                raw_x[node] = float(next_leaf)
                next_leaf += 1
            return raw_x[node]

        place(root)
        x_span = max(1.0, max(raw_x.values()) - min(raw_x.values()))
        max_depth = max(depths.values(), default=0)
        for label in labels:
            nodes[label] = (
                10 + (raw_x[label] - min(raw_x.values())) / x_span * 80,
                12 + depths[label] / max(1, max_depth) * 76,
            )
    elif directed and labels:
        outgoing = {label: [] for label in labels}
        indegree = {label: 0 for label in labels}
        for first, second in pair_edges:
            if second not in outgoing[first]:
                outgoing[first].append(second)
                indegree[second] += 1
        queue = deque(label for label in labels if indegree[label] == 0)
        levels = {label: 0 for label in queue}
        processed = []
        while queue:
            node = queue.popleft()
            processed.append(node)
            for neighbor in outgoing[node]:
                levels[neighbor] = max(levels.get(neighbor, 0), levels[node] + 1)
                indegree[neighbor] -= 1
                if indegree[neighbor] == 0:
                    queue.append(neighbor)
        if len(processed) == len(labels):
            max_level = max(levels.values(), default=0)
            for level in range(max_level + 1):
                level_nodes = [label for label in labels if levels[label] == level]
                for index, label in enumerate(level_nodes):
                    nodes[label] = (
                        50
                        if len(level_nodes) == 1
                        else 10 + index / (len(level_nodes) - 1) * 80,
                        12 + level / max(1, max_level) * 76,
                    )

    if not nodes:
        count = max(1, len(labels))
        for index, label in enumerate(labels):
            angle = -1.5708 + index * 6.283185307179586 / count
            nodes[label] = (
                50 + 39 * cos(angle),
                50 + 36 * sin(angle),
            )
    return _graph(
        {
            "nodes": nodes,
            "edges": edges,
            "directed": directed,
            "active_edges": spec.get("active_edges", []),
            "active_nodes": spec.get("active_nodes", []),
            "node_annotations": spec.get("node_annotations", {}),
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


def _dp_table(spec: dict[str, Any]) -> str:
    top_labels = spec["top_labels"]
    side_labels = spec["side_labels"]
    values = spec["values"]
    active = set(spec.get("active", []))
    header = '<th class="gc-vis-dp-corner"></th>' + "".join(
        f"<th>{escape(str(label))}</th>" for label in top_labels
    )
    rows = []
    for row_index, row in enumerate(values):
        cells = "".join(
            f'<td class="{"is-active" if (row_index, column_index) in active else ""}">'
            f'{escape("✓" if value is True else "·" if value is False else str(value))}</td>'
            for column_index, value in enumerate(row)
        )
        rows.append(
            f"<tr><th>{escape(str(side_labels[row_index]))}</th>{cells}</tr>"
        )
    return (
        '<div class="gc-vis-dp-table-wrap"><table class="gc-vis-dp-table">'
        f"<thead><tr>{header}</tr></thead><tbody>{''.join(rows)}</tbody>"
        "</table></div>"
    )


def _pyramid(spec: dict[str, Any]) -> str:
    active = set(spec.get("active", []))
    rows = []
    for row_index, row in enumerate(spec["rows"][:8]):
        rows.append(
            '<div class="gc-vis-pyramid-row">'
            + "".join(
                f'<span class="{"is-active" if (row_index, column_index) in active else ""}">'
                f"{escape(str(value))}</span>"
                for column_index, value in enumerate(row)
            )
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
    shelves = spec.get("shelves") or [books]
    max_height = max((book[1] for book in books), default=1)
    shelf_width = max(spec.get("shelf_width", 0), 1)
    rendered_shelves = []
    book_index = 0
    for shelf in shelves:
        rendered = []
        for thickness, height, *_ in shelf:
            rendered.append(
                f'<span style="height:{max(18, height / max_height * 62):.2f}px;'
                f'width:{max(6, thickness / shelf_width * 100):.2f}%">'
                f'<b>{book_index}</b><small>{thickness} × {height}</small></span>'
            )
            book_index += 1
        rendered_shelves.append(
            f'<div class="gc-vis-book-shelf">{"".join(rendered)}</div>'
        )
    return f'<div class="gc-vis-books">{"".join(rendered_shelves)}</div>'


def _stair_costs(spec: dict[str, Any]) -> str:
    costs = spec["costs"]
    maximum = max(costs) or 1
    steps = []
    for index, cost in enumerate(costs[:14]):
        steps.append(
            '<div class="gc-vis-cost-step">'
            f'<span style="height:{max(22, cost / maximum * 72):.2f}px">{escape(str(cost))}</span>'
            f"<small>step {index}</small></div>"
        )
    return f'<div class="gc-vis-cost-stairs">{"".join(steps)}</div>'


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
    result = _grid_cells(spec["result"]) if spec.get("result") is not None else ""
    equation = (
        '<div class="gc-vis-matrix-pair">'
        f'<div><span class="gc-vis-side-label">matrix A</span>{left}</div>'
        '<b aria-hidden="true">×</b>'
        f'<div><span class="gc-vis-side-label">matrix B</span>{right}</div>'
    )
    if result:
        equation += (
            '<b aria-hidden="true">=</b>'
            f'<div><span class="gc-vis-side-label">product</span>{result}</div>'
        )
    return f"{equation}</div>"


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


def _string_dp_spec(title: str, first: str, second: str, third: str = "") -> dict[str, Any]:
    columns = len(first) + 1
    rows = len(second) + 1
    values: list[list[Any]] = [[0] * columns for _ in range(rows)]

    if title == "Longest Common Subsequence":
        for row in range(1, rows):
            for column in range(1, columns):
                if second[row - 1] == first[column - 1]:
                    values[row][column] = values[row - 1][column - 1] + 1
                else:
                    values[row][column] = max(
                        values[row - 1][column],
                        values[row][column - 1],
                    )
    elif title == "Edit Distance":
        values[0] = list(range(columns))
        for row in range(rows):
            values[row][0] = row
        for row in range(1, rows):
            for column in range(1, columns):
                if second[row - 1] == first[column - 1]:
                    values[row][column] = values[row - 1][column - 1]
                else:
                    values[row][column] = 1 + min(
                        values[row - 1][column],
                        values[row][column - 1],
                        values[row - 1][column - 1],
                    )
    elif title == "Distinct Subsequences":
        values[0] = [1] * columns
        for row in range(1, rows):
            for column in range(1, columns):
                values[row][column] = values[row][column - 1]
                if second[row - 1] == first[column - 1]:
                    values[row][column] += values[row - 1][column - 1]
    elif title == "Interleaving String":
        bool_values: list[list[bool]] = [
            [False] * columns for _ in range(rows)
        ]
        bool_values[0][0] = True
        for row in range(rows):
            for column in range(columns):
                if row == 0 and column == 0:
                    continue
                output_index = row + column - 1
                from_top = (
                    row > 0
                    and bool_values[row - 1][column]
                    and output_index < len(third)
                    and second[row - 1] == third[output_index]
                )
                from_left = (
                    column > 0
                    and bool_values[row][column - 1]
                    and output_index < len(third)
                    and first[column - 1] == third[output_index]
                )
                bool_values[row][column] = from_top or from_left
        values = bool_values

    return {
        "top_labels": ["∅", *first],
        "side_labels": ["∅", *second],
        "values": values,
        "active": [(rows - 1, columns - 1)],
    }


def _path_count_values(obstacles: list[list[Any]]) -> list[list[Any]]:
    rows = len(obstacles)
    columns = len(obstacles[0])
    counts = [[0] * columns for _ in range(rows)]
    for row in range(rows):
        for column in range(columns):
            if obstacles[row][column] in (1, True):
                counts[row][column] = "×"
                continue
            if row == 0 and column == 0:
                counts[row][column] = 1
                continue
            from_top = counts[row - 1][column] if row else 0
            from_left = counts[row][column - 1] if column else 0
            counts[row][column] = (
                (from_top if isinstance(from_top, int) else 0)
                + (from_left if isinstance(from_left, int) else 0)
            )
    return counts


def _minimum_grid_path(
    grid: list[list[int]],
    falling: bool = False,
) -> tuple[list[tuple[int, int]], int]:
    rows, columns = len(grid), len(grid[0])
    costs = [[float("inf")] * columns for _ in range(rows)]
    parent: dict[tuple[int, int], tuple[int, int]] = {}
    if falling:
        costs[0] = [int(value) for value in grid[0]]
        for row in range(1, rows):
            for column in range(columns):
                candidates = [
                    previous
                    for previous in (column - 1, column, column + 1)
                    if 0 <= previous < columns
                ]
                best = min(candidates, key=lambda previous: costs[row - 1][previous])
                costs[row][column] = costs[row - 1][best] + grid[row][column]
                parent[(row, column)] = (row - 1, best)
        end = (rows - 1, min(range(columns), key=lambda column: costs[-1][column]))
    else:
        costs[0][0] = grid[0][0]
        for row in range(rows):
            for column in range(columns):
                if row == 0 and column == 0:
                    continue
                candidates = []
                if row:
                    candidates.append((row - 1, column))
                if column:
                    candidates.append((row, column - 1))
                best = min(candidates, key=lambda cell: costs[cell[0]][cell[1]])
                costs[row][column] = costs[best[0]][best[1]] + grid[row][column]
                parent[(row, column)] = best
        end = (rows - 1, columns - 1)

    path = [end]
    while path[-1] in parent:
        path.append(parent[path[-1]])
    path.reverse()
    return path, int(costs[end[0]][end[1]])


def _longest_increasing_grid_path(grid: list[list[int]]) -> list[tuple[int, int]]:
    rows, columns = len(grid), len(grid[0])
    memo: dict[tuple[int, int], list[tuple[int, int]]] = {}

    def visit(row: int, column: int) -> list[tuple[int, int]]:
        if (row, column) in memo:
            return memo[(row, column)]
        best: list[tuple[int, int]] = []
        for row_step, column_step in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            next_row, next_column = row + row_step, column + column_step
            if (
                0 <= next_row < rows
                and 0 <= next_column < columns
                and grid[next_row][next_column] > grid[row][column]
            ):
                candidate = visit(next_row, next_column)
                if len(candidate) > len(best):
                    best = candidate
        memo[(row, column)] = [(row, column), *best]
        return memo[(row, column)]

    return max(
        (visit(row, column) for row in range(rows) for column in range(columns)),
        key=len,
    )


def _largest_square_region(matrix: list[list[Any]]) -> list[tuple[int, int]]:
    rows, columns = len(matrix), len(matrix[0])
    dp = [[0] * (columns + 1) for _ in range(rows + 1)]
    best_size = 0
    best_end = (0, 0)
    for row in range(1, rows + 1):
        for column in range(1, columns + 1):
            if str(matrix[row - 1][column - 1]) == "1":
                dp[row][column] = 1 + min(
                    dp[row - 1][column],
                    dp[row][column - 1],
                    dp[row - 1][column - 1],
                )
                if dp[row][column] > best_size:
                    best_size = dp[row][column]
                    best_end = (row - 1, column - 1)
    end_row, end_column = best_end
    return [
        (row, column)
        for row in range(end_row - best_size + 1, end_row + 1)
        for column in range(end_column - best_size + 1, end_column + 1)
    ]


def _largest_rectangle_region(matrix: list[list[Any]]) -> list[tuple[int, int]]:
    rows, columns = len(matrix), len(matrix[0])
    heights = [0] * columns
    best_area = 0
    best = (0, 0, -1)
    for row in range(rows):
        heights = [
            heights[column] + 1 if str(matrix[row][column]) == "1" else 0
            for column in range(columns)
        ]
        stack: list[int] = []
        for column in range(columns + 1):
            height = heights[column] if column < columns else 0
            while stack and heights[stack[-1]] > height:
                top = stack.pop()
                left = stack[-1] + 1 if stack else 0
                area = heights[top] * (column - left)
                if area > best_area:
                    best_area = area
                    best = (row, left, column - 1)
            stack.append(column)
    end_row, left, right = best
    height = best_area // max(1, right - left + 1)
    return [
        (row, column)
        for row in range(end_row - height + 1, end_row + 1)
        for column in range(left, right + 1)
    ]


def _paint_house_path(costs: list[list[int]]) -> list[tuple[int, int]]:
    rows, columns = len(costs), len(costs[0])
    dp = [list(costs[0])]
    parents: list[list[int | None]] = [[None] * columns]
    for row in range(1, rows):
        dp.append([0] * columns)
        parents.append([None] * columns)
        for color in range(columns):
            previous = min(
                (candidate for candidate in range(columns) if candidate != color),
                key=lambda candidate: dp[row - 1][candidate],
            )
            dp[row][color] = costs[row][color] + dp[row - 1][previous]
            parents[row][color] = previous
    color = min(range(columns), key=lambda candidate: dp[-1][candidate])
    path = []
    for row in range(rows - 1, -1, -1):
        path.append((row, color))
        previous = parents[row][color]
        if previous is not None:
            color = previous
    return list(reversed(path))


def _triangle_min_path(triangle: list[list[int]]) -> list[tuple[int, int]]:
    costs = [list(row) for row in triangle]
    choices: dict[tuple[int, int], int] = {}
    for row in range(len(triangle) - 2, -1, -1):
        for column in range(len(triangle[row])):
            next_column = (
                column
                if costs[row + 1][column] <= costs[row + 1][column + 1]
                else column + 1
            )
            choices[(row, column)] = next_column
            costs[row][column] += costs[row + 1][next_column]
    path = []
    column = 0
    for row in range(len(triangle)):
        path.append((row, column))
        if row < len(triangle) - 1:
            column = choices[(row, column)]
    return path


def _dungeon_health_grid(dungeon: list[list[int]]) -> list[list[int]]:
    rows, columns = len(dungeon), len(dungeon[0])
    needed = [[10**9] * columns for _ in range(rows)]
    for row in range(rows - 1, -1, -1):
        for column in range(columns - 1, -1, -1):
            if row == rows - 1 and column == columns - 1:
                onward = 1
            else:
                onward = min(
                    needed[row + 1][column] if row + 1 < rows else 10**9,
                    needed[row][column + 1] if column + 1 < columns else 10**9,
                )
            needed[row][column] = max(1, onward - dungeon[row][column])
    return needed


def _word_search_path(
    board: list[list[str]],
    word: str,
) -> list[tuple[int, int]]:
    rows, columns = len(board), len(board[0])

    def visit(
        row: int,
        column: int,
        index: int,
        used: set[tuple[int, int]],
    ) -> list[tuple[int, int]] | None:
        if board[row][column] != word[index]:
            return None
        if index == len(word) - 1:
            return [(row, column)]
        used.add((row, column))
        for row_step, column_step in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            next_row, next_column = row + row_step, column + column_step
            if (
                0 <= next_row < rows
                and 0 <= next_column < columns
                and (next_row, next_column) not in used
            ):
                suffix = visit(
                    next_row,
                    next_column,
                    index + 1,
                    used,
                )
                if suffix:
                    used.remove((row, column))
                    return [(row, column), *suffix]
        used.remove((row, column))
        return None

    if not word:
        return []
    for row in range(rows):
        for column in range(columns):
            path = visit(row, column, 0, set())
            if path:
                return path
    return []


def _grid_components(
    grid: list[list[Any]],
    land_value: Any,
) -> list[list[tuple[int, int]]]:
    rows, columns = len(grid), len(grid[0])
    remaining = {
        (row, column)
        for row in range(rows)
        for column in range(columns)
        if grid[row][column] == land_value
        or str(grid[row][column]) == str(land_value)
    }
    components = []
    while remaining:
        start = next(iter(remaining))
        remaining.remove(start)
        stack = [start]
        component = []
        while stack:
            row, column = stack.pop()
            component.append((row, column))
            for row_step, column_step in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                neighbor = (row + row_step, column + column_step)
                if neighbor in remaining:
                    remaining.remove(neighbor)
                    stack.append(neighbor)
        components.append(component)
    return components


def _reconstruct_cell_path(
    parent: dict[tuple[int, int], tuple[int, int] | None],
    end: tuple[int, int],
) -> list[tuple[int, int]]:
    path = [end]
    while parent[path[-1]] is not None:
        path.append(parent[path[-1]])  # type: ignore[arg-type]
    return list(reversed(path))


def _binary_grid_shortest_path(
    grid: list[list[int]],
) -> list[tuple[int, int]]:
    rows, columns = len(grid), len(grid[0])
    start, end = (0, 0), (rows - 1, columns - 1)
    if grid[0][0] != 0 or grid[-1][-1] != 0:
        return []
    parent: dict[tuple[int, int], tuple[int, int] | None] = {start: None}
    queue = deque([start])
    while queue:
        row, column = queue.popleft()
        if (row, column) == end:
            return _reconstruct_cell_path(parent, end)
        for row_step in (-1, 0, 1):
            for column_step in (-1, 0, 1):
                if row_step == column_step == 0:
                    continue
                neighbor = (row + row_step, column + column_step)
                if (
                    0 <= neighbor[0] < rows
                    and 0 <= neighbor[1] < columns
                    and grid[neighbor[0]][neighbor[1]] == 0
                    and neighbor not in parent
                ):
                    parent[neighbor] = (row, column)
                    queue.append(neighbor)
    return []


def _obstacle_elimination_path(
    grid: list[list[int]],
    eliminations: int,
) -> list[tuple[int, int]]:
    rows, columns = len(grid), len(grid[0])
    remaining = eliminations - int(grid[0][0])
    if remaining < 0:
        return []
    start = (0, 0, remaining)
    queue = deque([start])
    best_remaining = {(0, 0): remaining}
    parent: dict[
        tuple[int, int, int],
        tuple[int, int, int] | None,
    ] = {start: None}
    end_state: tuple[int, int, int] | None = None
    while queue:
        row, column, remaining = queue.popleft()
        if (row, column) == (rows - 1, columns - 1):
            end_state = (row, column, remaining)
            break
        for row_step, column_step in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            next_row, next_column = row + row_step, column + column_step
            if not (0 <= next_row < rows and 0 <= next_column < columns):
                continue
            next_remaining = remaining - int(grid[next_row][next_column])
            if next_remaining < 0:
                continue
            if next_remaining <= best_remaining.get((next_row, next_column), -1):
                continue
            next_state = (next_row, next_column, next_remaining)
            best_remaining[(next_row, next_column)] = next_remaining
            parent[next_state] = (row, column, remaining)
            queue.append(next_state)
    if end_state is None:
        return []
    states = [end_state]
    while parent[states[-1]] is not None:
        states.append(parent[states[-1]])  # type: ignore[arg-type]
    return [(row, column) for row, column, _ in reversed(states)]


def _priority_grid_path(
    grid: list[list[int]],
    objective: str,
) -> tuple[list[tuple[int, int]], int]:
    rows, columns = len(grid), len(grid[0])
    start, end = (0, 0), (rows - 1, columns - 1)
    parent: dict[tuple[int, int], tuple[int, int] | None] = {start: None}
    if objective == "maximin":
        scores = [[-1] * columns for _ in range(rows)]
        scores[0][0] = int(grid[0][0])
        heap = [(-scores[0][0], 0, 0)]
    else:
        scores = [[10**9] * columns for _ in range(rows)]
        scores[0][0] = int(grid[0][0])
        heap = [(scores[0][0], 0, 0)]

    while heap:
        priority, row, column = heappop(heap)
        score = -priority if objective == "maximin" else priority
        if score != scores[row][column]:
            continue
        if (row, column) == end:
            return _reconstruct_cell_path(parent, end), int(score)
        for row_step, column_step in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            next_row, next_column = row + row_step, column + column_step
            if not (0 <= next_row < rows and 0 <= next_column < columns):
                continue
            if objective == "maximin":
                candidate = min(score, int(grid[next_row][next_column]))
                improves = candidate > scores[next_row][next_column]
            elif objective == "minimax":
                candidate = max(score, int(grid[next_row][next_column]))
                improves = candidate < scores[next_row][next_column]
            else:
                candidate = score + int(grid[next_row][next_column])
                improves = candidate < scores[next_row][next_column]
            if not improves:
                continue
            scores[next_row][next_column] = candidate
            parent[(next_row, next_column)] = (row, column)
            heappush(
                heap,
                (
                    -candidate if objective == "maximin" else candidate,
                    next_row,
                    next_column,
                ),
            )
    return [], -1


def _safest_grid_path(
    grid: list[list[int]],
) -> tuple[list[tuple[int, int]], int]:
    rows, columns = len(grid), len(grid[0])
    distances = [[10**9] * columns for _ in range(rows)]
    queue: deque[tuple[int, int]] = deque()
    for row in range(rows):
        for column in range(columns):
            if int(grid[row][column]) == 1:
                distances[row][column] = 0
                queue.append((row, column))
    while queue:
        row, column = queue.popleft()
        for row_step, column_step in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            next_row, next_column = row + row_step, column + column_step
            if (
                0 <= next_row < rows
                and 0 <= next_column < columns
                and distances[next_row][next_column] > distances[row][column] + 1
            ):
                distances[next_row][next_column] = distances[row][column] + 1
                queue.append((next_row, next_column))
    return _priority_grid_path(distances, "maximin")


def _shortest_bridge_cells(
    grid: list[list[int]],
) -> tuple[list[list[tuple[int, int]]], list[tuple[int, int]]]:
    components = _grid_components(grid, 1)
    if len(components) < 2:
        return components, []
    first = set(components[0])
    queue = deque(components[0])
    parent: dict[tuple[int, int], tuple[int, int] | None] = {
        cell: None for cell in components[0]
    }
    rows, columns = len(grid), len(grid[0])
    while queue:
        row, column = queue.popleft()
        for row_step, column_step in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            neighbor = (row + row_step, column + column_step)
            if not (0 <= neighbor[0] < rows and 0 <= neighbor[1] < columns):
                continue
            if neighbor in first or neighbor in parent:
                continue
            if int(grid[neighbor[0]][neighbor[1]]) == 1:
                bridge = []
                current = (row, column)
                while current not in first:
                    bridge.append(current)
                    previous = parent[current]
                    if previous is None:
                        break
                    current = previous
                return components, list(reversed(bridge))
            parent[neighbor] = (row, column)
            queue.append(neighbor)
    return components, []


def _largest_island_flip(
    grid: list[list[int]],
) -> tuple[list[list[tuple[int, int]]], tuple[int, int] | None]:
    components = _grid_components(grid, 1)
    component_by_cell = {
        cell: index
        for index, component in enumerate(components)
        for cell in component
    }
    best_size = max((len(component) for component in components), default=0)
    best_cell = None
    rows, columns = len(grid), len(grid[0])
    for row in range(rows):
        for column in range(columns):
            if int(grid[row][column]) != 0:
                continue
            adjacent = {
                component_by_cell[(next_row, next_column)]
                for row_step, column_step in ((1, 0), (-1, 0), (0, 1), (0, -1))
                if 0 <= (next_row := row + row_step) < rows
                and 0 <= (next_column := column + column_step) < columns
                and (next_row, next_column) in component_by_cell
            }
            size = 1 + sum(len(components[index]) for index in adjacent)
            if size > best_size:
                best_size = size
                best_cell = (row, column)
    return components, best_cell


def _optimal_book_shelves(
    books: list[list[int]],
    shelf_width: int,
) -> list[list[list[int]]]:
    count = len(books)
    best = [0] + [10**9] * count
    previous = [0] * (count + 1)
    for end in range(1, count + 1):
        width = 0
        height = 0
        for start in range(end, 0, -1):
            width += books[start - 1][0]
            if width > shelf_width:
                break
            height = max(height, books[start - 1][1])
            candidate = best[start - 1] + height
            if candidate < best[end]:
                best[end] = candidate
                previous[end] = start - 1
    shelves = []
    end = count
    while end:
        start = previous[end]
        shelves.append(books[start:end])
        end = start
    return list(reversed(shelves))


def _maximum_product_span(values: list[int]) -> list[int]:
    best_product: int | None = None
    best_span = (0, 0)
    for start in range(len(values)):
        product = 1
        for end in range(start, len(values)):
            product *= values[end]
            if best_product is None or product > best_product:
                best_product = product
                best_span = (start, end)
    return list(range(best_span[0], best_span[1] + 1))


def _linear_robbery(values: list[int], offset: int) -> tuple[int, list[int]]:
    previous_two = (0, [])
    previous_one = (0, [])
    for index, value in enumerate(values):
        take = (
            previous_two[0] + value,
            [*previous_two[1], index + offset],
        )
        skip = previous_one
        current = take if take[0] > skip[0] else skip
        previous_two, previous_one = previous_one, current
    return previous_one


def _circular_robbery_indices(values: list[int]) -> list[int]:
    if len(values) <= 1:
        return [0] if values else []
    without_last = _linear_robbery(values[:-1], 0)
    without_first = _linear_robbery(values[1:], 1)
    return (
        without_last[1]
        if without_last[0] >= without_first[0]
        else without_first[1]
    )


def _minimum_jump_path(values: list[int]) -> list[int]:
    if not values:
        return []
    parents = [-1] * len(values)
    furthest_discovered = 0
    for index, reach in enumerate(values):
        if index > furthest_discovered:
            break
        boundary = min(len(values) - 1, index + reach)
        for child in range(furthest_discovered + 1, boundary + 1):
            parents[child] = index
        furthest_discovered = max(furthest_discovered, boundary)
        if furthest_discovered == len(values) - 1:
            break
    if len(values) > 1 and parents[-1] == -1:
        return [0]
    path = [len(values) - 1]
    while path[-1] > 0:
        path.append(parents[path[-1]])
    return list(reversed(path))


def _split_array_groups(values: list[int], group_count: int) -> list[int]:
    count = len(values)
    prefix = [0]
    for value in values:
        prefix.append(prefix[-1] + value)
    dp = [[float("inf")] * (count + 1) for _ in range(group_count + 1)]
    parent = [[-1] * (count + 1) for _ in range(group_count + 1)]
    dp[0][0] = 0
    for groups in range(1, group_count + 1):
        for end in range(groups, count + 1):
            for split in range(groups - 1, end):
                candidate = max(dp[groups - 1][split], prefix[end] - prefix[split])
                if candidate < dp[groups][end]:
                    dp[groups][end] = candidate
                    parent[groups][end] = split
    boundaries = [count]
    groups, end = group_count, count
    while groups:
        end = parent[groups][end]
        boundaries.append(end)
        groups -= 1
    boundaries.reverse()
    tones = [1] * count
    for group in range(group_count):
        for index in range(boundaries[group], boundaries[group + 1]):
            tones[index] = group % 3 + 1
    return tones


def _palindrome_partition(value: str) -> list[str]:
    count = len(value)
    cuts = [10**9] * (count + 1)
    cuts[0] = -1
    parent = [0] * (count + 1)
    palindrome = [[False] * count for _ in range(count)]
    for end in range(count):
        for start in range(end + 1):
            if value[start] == value[end] and (
                end - start <= 2 or palindrome[start + 1][end - 1]
            ):
                palindrome[start][end] = True
                if cuts[start] + 1 < cuts[end + 1]:
                    cuts[end + 1] = cuts[start] + 1
                    parent[end + 1] = start
    parts = []
    end = count
    while end:
        start = parent[end]
        parts.append(value[start:end])
        end = start
    return list(reversed(parts))


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

    if requested_kind == "stair_costs":
        costs = argument(decision.get("arg_index", 0), [])
        return {
            "kind": "stair_costs",
            "label": label,
            "costs": costs,
            "caption": (
                "Each step shows the cost paid when landing there; "
                f"the least total cost to move beyond the last step is {result}."
            ),
        }

    if requested_kind == "subarray_result":
        values = argument(decision.get("arg_index", 0), [])
        active = _maximum_product_span(values)
        return {
            "kind": "sequence",
            "label": label,
            "items": values,
            "active": active,
            "caption": (
                "The highlighted contiguous block has the maximum product, "
                f"which is {result}."
            ),
        }

    if requested_kind == "house_circle":
        values = argument(decision.get("arg_index", 0), [])
        return {
            "kind": "house_circle",
            "label": label,
            "values": values,
            "active": _circular_robbery_indices(values),
            "caption": (
                "The circular layout makes the first and last houses adjacent. "
                f"The highlighted nonadjacent selection totals {result}."
            ),
        }

    if requested_kind == "jump_path":
        values = argument(decision.get("arg_index", 0), [])
        path = _minimum_jump_path(values)
        annotations = {
            index: (
                "finish"
                if index == len(values) - 1
                else f"jump ≤ {values[index]}"
            )
            for index in path
        }
        return {
            "kind": "sequence",
            "label": label,
            "items": values,
            "active": path,
            "annotations": annotations,
            "caption": (
                "The highlighted indices form a valid shortest route to the final "
                f"position; the expected result is {result}."
            ),
        }

    if requested_kind == "split_array":
        values = argument(decision.get("arg_index", 0), [])
        groups = int(args[1]) if len(args) > 1 else 1
        return {
            "kind": "sequence",
            "label": label,
            "items": values,
            "tones": _split_array_groups(values, groups),
            "caption": (
                "Colors mark one optimal contiguous partition; its largest group "
                f"sum is {result}."
            ),
        }

    if requested_kind == "pal_partition":
        value = str(argument(decision.get("arg_index", 0), ""))
        parts = _palindrome_partition(value)
        return {
            "kind": "segments",
            "label": label,
            "segments": parts,
            "caption": (
                "Each displayed segment is a palindrome. The separators give "
                f"the minimum {result} cut{'s' if expected != 1 else ''}."
            ),
        }

    if requested_kind == "dp_table":
        indexes = decision.get("arg_indexes", [0, 1])
        first = str(argument(indexes[0], ""))
        second = str(argument(indexes[1], ""))
        third = str(args[2]) if len(args) > 2 else ""
        table = _string_dp_spec(title, first, second, third)
        return {
            "kind": "dp_table",
            "label": label,
            **table,
            "caption": (
                "Each cell is the solved value for the two displayed prefixes; "
                f"the highlighted full-prefix cell is {result}."
            ),
        }

    if requested_kind == "path_count_grid":
        if title == "Unique Paths":
            rows, columns = int(args[0]), int(args[1])
            obstacles = [[0] * columns for _ in range(rows)]
        else:
            obstacles = argument(decision.get("arg_index", 0), [])
            rows, columns = len(obstacles), len(obstacles[0])
        counts = _path_count_values(obstacles)
        classes = {
            (row, column): "separate"
            for row in range(rows)
            for column in range(columns)
            if obstacles[row][column] in (1, True)
        }
        classes[(0, 0)] = "source"
        classes[(rows - 1, columns - 1)] = "connected"
        return {
            "kind": "grid",
            "label": label,
            "values": counts,
            "cell_classes": classes,
            "caption": (
                "Each open cell shows how many right-and-down paths reach it; "
                f"the destination contains {result}."
            ),
        }

    if requested_kind == "paint_house":
        costs = argument(decision.get("arg_index", 0), [])
        path = _paint_house_path(costs)
        return {
            "kind": "grid",
            "label": label,
            "values": costs,
            "cell_classes": {cell: "changed" for cell in path},
            "caption": (
                "Rows are houses and columns are colors. The highlighted cells "
                f"form one minimum-cost valid assignment totaling {result}."
            ),
        }

    if requested_kind == "matrix_region":
        matrix = argument(decision.get("arg_index", 0), [])
        region = (
            _largest_square_region(matrix)
            if title == "Maximal Square"
            else _largest_rectangle_region(matrix)
        )
        return {
            "kind": "grid",
            "label": label,
            "values": matrix,
            "cell_classes": {cell: "connected" for cell in region},
            "caption": (
                f"The highlighted all-1 region has the maximum area of {result}."
            ),
        }

    if requested_kind == "matrix_path":
        matrix = argument(decision.get("arg_index", 0), [])
        if title == "Longest Increasing Path in a Matrix":
            path = _longest_increasing_grid_path(matrix)
        else:
            path, _ = _minimum_grid_path(
                matrix,
                falling=title == "Minimum Falling Path Sum",
            )
        classes = {cell: "changed" for cell in path}
        if path:
            classes[path[0]] = "source"
            classes[path[-1]] = "connected"
        return {
            "kind": "grid",
            "label": label,
            "values": matrix,
            "cell_classes": classes,
            "order": [
                next(
                    (
                        order
                        for order, cell in enumerate(path, 1)
                        if cell == (row, column)
                    ),
                    None,
                )
                for row in range(len(matrix))
                for column in range(len(matrix[row]))
            ],
            "caption": (
                "The numbered cells show one optimal path for the first example; "
                f"its expected result is {result}."
            ),
        }

    if requested_kind == "dungeon_dp":
        dungeon = argument(decision.get("arg_index", 0), [])
        needed = _dungeon_health_grid(dungeon)
        return {
            "kind": "grid_compare",
            "label": label,
            "before": dungeon,
            "after": needed,
            "left_label": "room effect",
            "right_label": "health needed",
            "caption": (
                "The right grid gives the minimum health required before entering "
                f"each room; the start cell is {result}."
            ),
        }

    if requested_kind == "triangle_path":
        triangle = argument(decision.get("arg_index", 0), [])
        return {
            "kind": "pyramid",
            "label": label,
            "rows": triangle,
            "active": _triangle_min_path(triangle),
            "caption": (
                f"The highlighted adjacent values form a minimum path totaling {result}."
            ),
        }

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
        books = argument(decision.get("arg_index", 0), [])
        shelf_width = int(args[1]) if len(args) > 1 else sum(
            book[0] for book in books
        )
        return {
            "kind": "books",
            "label": label,
            "books": books,
            "shelf_width": shelf_width,
            "shelves": _optimal_book_shelves(books, shelf_width),
            "caption": (
                "The rows show one optimal shelf arrangement while preserving "
                f"book order; their total height is {result}."
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

    if requested_kind == "snakes_board":
        board = argument(decision.get("arg_index", 0), [])
        size = len(board)
        values: list[list[Any]] = [[""] * size for _ in range(size)]
        classes: dict[tuple[int, int], str] = {}
        for square in range(1, size * size + 1):
            level, offset = divmod(square - 1, size)
            row = size - 1 - level
            column = offset if level % 2 == 0 else size - 1 - offset
            destination = board[row][column]
            values[row][column] = (
                f"{square}→{destination}"
                if destination != -1
                else square
            )
            if destination != -1:
                classes[(row, column)] = "source"
        classes[(size - 1, 0)] = "changed"
        end_column = 0 if (size - 1) % 2 else size - 1
        classes[(0, end_column)] = "connected"
        return {
            "kind": "grid",
            "label": label,
            "values": values,
            "cell_classes": classes,
            "caption": (
                "Cells follow the board's alternating square order; arrows show "
                f"snakes or ladders. The minimum roll count is {result}."
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
            "result": expected if isinstance(expected, list) else None,
            "caption": (
                "The input matrices and their exact product are shown in the "
                "same row-and-column layout."
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
            separators: dict[tuple[int, int], str] = {}
            if title == "Sudoku Solver":
                for row_index, row in enumerate(grid):
                    for column_index, _ in enumerate(row):
                        classes = []
                        if column_index in {2, 5}:
                            classes.append("box-right")
                        if row_index in {2, 5}:
                            classes.append("box-bottom")
                        if classes:
                            separators[(row_index, column_index)] = " ".join(classes)
            return {
                "kind": "grid_compare",
                "label": label,
                "before": grid,
                "after": expected,
                "before_classes": separators,
                "after_classes": separators,
                "left_label": "input",
                "right_label": "expected",
                "caption": (
                    "The two grids show the first example before and after the "
                    "required transformation."
                ),
            }
        classes: dict[tuple[int, int], str] = {}
        order: list[int | None] | None = None
        caption_override: str | None = None
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
        flattened = [value for row in grid for value in row]
        if flattened and all(str(value) in {"0", "1"} for value in flattened):
            obstacle_titles = {
                "Minimum Obstacle Removal to Reach Corner",
                "Shortest Path in Binary Matrix",
                "Shortest Path in a Grid with Obstacles Elimination",
            }
            for row_index, row in enumerate(grid):
                for column_index, value in enumerate(row):
                    if title in obstacle_titles:
                        tone = "separate" if str(value) == "1" else "is-water"
                    elif title == "Find the Safest Path in a Grid":
                        tone = "source" if str(value) == "1" else "is-water"
                    elif title == "Number of Closed Islands":
                        tone = "is-water" if str(value) == "1" else "group-1"
                    else:
                        tone = "group-1" if str(value) == "1" else "is-water"
                    classes.setdefault((row_index, column_index), tone)
            if title == "Max Area of Island":
                components = _grid_components(grid, 1)
                largest = max(components, key=len, default=[])
                for component in components:
                    for cell in component:
                        classes[cell] = (
                            "connected" if component is largest else "group-2"
                        )
            if title == "Number of Closed Islands":
                rows, columns = len(grid), len(grid[0])
                for component in _grid_components(grid, 0):
                    is_closed = all(
                        row not in {0, rows - 1}
                        and column not in {0, columns - 1}
                        for row, column in component
                    )
                    for cell in component:
                        classes[cell] = "connected" if is_closed else "source"
            if title == "Making A Large Island":
                components, best_flip = _largest_island_flip(grid)
                component_tones = ("group-1", "group-2", "group-3")
                for index, component in enumerate(components):
                    for cell in component:
                        classes[cell] = component_tones[index % len(component_tones)]
                if best_flip is not None:
                    classes[best_flip] = "source"
                caption_override = (
                    "Colors separate the existing islands. The orange water cell "
                    f"is one optimal flip, producing area {result}."
                )
            if title == "Shortest Bridge":
                components, bridge = _shortest_bridge_cells(grid)
                for index, component in enumerate(components[:2]):
                    for cell in component:
                        classes[cell] = "group-1" if index == 0 else "group-2"
                for cell in bridge:
                    classes[cell] = "changed"
                order = [
                    next(
                        (
                            step
                            for step, cell in enumerate(bridge, 1)
                            if cell == (row_index, column_index)
                        ),
                        None,
                    )
                    for row_index, row in enumerate(grid)
                    for column_index, _ in enumerate(row)
                ]
                caption_override = (
                    "The two colors are the original islands. The numbered water "
                    f"cells form a shortest bridge using {result} flip"
                    f"{'s' if expected != 1 else ''}."
                )
        if title == "Rotting Oranges":
            for row_index, row in enumerate(grid):
                for column_index, value in enumerate(row):
                    classes[(row_index, column_index)] = (
                        "source" if value == 2
                        else "connected" if value == 1
                        else "is-water"
                    )
        if title == "Shortest Distance from All Buildings":
            for row_index, row in enumerate(grid):
                for column_index, value in enumerate(row):
                    classes[(row_index, column_index)] = (
                        "source" if value == 1
                        else "separate" if value == 2
                        else "is-water"
                    )
        if title in {"Valid Sudoku", "Sudoku Solver"}:
            for row_index, row in enumerate(grid):
                for column_index, _ in enumerate(row):
                    separators = []
                    if column_index in {2, 5}:
                        separators.append("box-right")
                    if row_index in {2, 5}:
                        separators.append("box-bottom")
                    if separators:
                        classes[(row_index, column_index)] = " ".join(separators)
        if "target" in names:
            target = argument(names.index("target"))
            for row_index, row in enumerate(grid):
                for column_index, value in enumerate(row):
                    if value == target:
                        classes[(row_index, column_index)] = "source"
        if title == "Kth Smallest Element in a Sorted Matrix":
            for row_index, row in enumerate(grid):
                for column_index, value in enumerate(row):
                    if value == expected:
                        classes[(row_index, column_index)] = "connected"
        if title == "Word Search" and len(args) > 1 and isinstance(args[1], str):
            path = _word_search_path(grid, args[1])
            for cell in path:
                classes[cell] = "changed"
            order = [
                next(
                    (
                        step
                        for step, cell in enumerate(path, 1)
                        if cell == (row_index, column_index)
                    ),
                    None,
                )
                for row_index, row in enumerate(grid)
                for column_index, _ in enumerate(row)
            ]
        if title == "Robot Room Cleaner" and len(args) >= 3:
            classes[(int(args[1]), int(args[2]))] = "source"
        path: list[tuple[int, int]] = []
        path_metric: int | None = None
        if title == "Shortest Path in Binary Matrix":
            path = _binary_grid_shortest_path(grid)
            path_metric = len(path)
            caption_override = (
                "The numbered open cells form a shortest eight-direction path. "
                f"It contains {result} cells."
            )
        elif title == "Shortest Path in a Grid with Obstacles Elimination":
            eliminations = int(args[1]) if len(args) > 1 else 0
            path = _obstacle_elimination_path(grid, eliminations)
            path_metric = len(path) - 1 if path else -1
            caption_override = (
                "The numbered cells form a shortest route while using no more "
                f"than {eliminations} obstacle elimination"
                f"{'s' if eliminations != 1 else ''}; its length is {result}."
            )
        elif title == "Minimum Obstacle Removal to Reach Corner":
            path, path_metric = _priority_grid_path(grid, "sum")
            caption_override = (
                "The numbered route minimizes the highlighted obstacle cells "
                f"entered, so {result} removal"
                f"{'s are' if expected != 1 else ' is'} required."
            )
        elif title == "Path With Maximum Minimum Value":
            path, path_metric = _priority_grid_path(grid, "maximin")
            caption_override = (
                "The numbered route maximizes its smallest cell value; that "
                f"bottleneck is {result}."
            )
        elif title == "Swim in Rising Water":
            path, path_metric = _priority_grid_path(grid, "minimax")
            caption_override = (
                "The numbered route minimizes its highest elevation, so every "
                f"cell on it is reachable at time {result}."
            )
        elif title == "Find the Safest Path in a Grid":
            path, path_metric = _safest_grid_path(grid)
            caption_override = (
                "The numbered route maximizes its minimum Manhattan distance "
                f"from a thief; its safeness factor is {result}."
            )
        if path:
            for step, cell in enumerate(path, 1):
                classes[cell] = (
                    "source" if step == 1
                    else "connected" if step == len(path)
                    else "changed"
                )
            order = [
                next(
                    (
                        step
                        for step, cell in enumerate(path, 1)
                        if cell == (row_index, column_index)
                    ),
                    None,
                )
                for row_index, row in enumerate(grid)
                for column_index, _ in enumerate(row)
            ]
        if title == "Diagonal Traverse" and isinstance(expected, list):
            positions: dict[Any, list[tuple[int, int]]] = {}
            for row_index, row in enumerate(grid):
                for column_index, value in enumerate(row):
                    positions.setdefault(value, []).append((row_index, column_index))
            used: set[tuple[int, int]] = set()
            ordered_cells: list[tuple[int, int]] = []
            for value in expected:
                match = next(
                    (
                        cell
                        for cell in positions.get(value, [])
                        if cell not in used
                    ),
                    None,
                )
                if match is not None:
                    used.add(match)
                    ordered_cells.append(match)
            order = [
                next(
                    (
                        step
                        for step, cell in enumerate(ordered_cells, 1)
                        if cell == (row_index, column_index)
                    ),
                    None,
                )
                for row_index, row in enumerate(grid)
                for column_index, _ in enumerate(row)
            ]
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
            "order": order,
            "path": path,
            "path_metric": path_metric,
            "caption": (
                caption_override
                or (
                    "The numbered cells spell the requested word in order."
                    if title == "Word Search" and order
                    else "Small numbers give the exact diagonal visit order."
                    if title == "Diagonal Traverse" and order
                    else "The first example is laid out by row and column; "
                    f"its expected result is {result}."
                )
            ),
        }

    if requested_kind in {
        "tree",
        "tree_pair",
        "tree_compare",
        "tree_merge",
        "tree_forest",
        "tree_list",
    }:
        if requested_kind == "tree_pair":
            indexes = decision.get("arg_indexes", [0, 1])
            return {
                "kind": "tree_collection",
                "label": label,
                "trees": [
                    {"label": "first tree", "values": argument(indexes[0], [])},
                    {"label": "second tree", "values": argument(indexes[1], [])},
                ],
                "caption": (
                    "Both trees from the first example are shown with their exact "
                    f"structure; the comparison returns {result}."
                ),
            }

        if requested_kind == "tree_compare":
            return {
                "kind": "tree_collection",
                "label": label,
                "trees": [
                    {"label": "input", "values": argument(decision.get("arg_index", 0), [])},
                    {"label": "expected", "values": expected},
                ],
                "caption": (
                    "The first example's input and expected tree are shown side by side."
                ),
            }

        if requested_kind == "tree_merge":
            indexes = decision.get("arg_indexes", [0, 1])
            return {
                "kind": "tree_collection",
                "label": label,
                "trees": [
                    {"label": "tree 1", "values": argument(indexes[0], [])},
                    {"label": "tree 2", "values": argument(indexes[1], [])},
                    {"label": "merged", "values": expected},
                ],
                "caption": (
                    "Corresponding input nodes combine to produce the displayed "
                    "merged tree."
                ),
            }

        if requested_kind == "tree_forest":
            forest = (
                expected
                if isinstance(expected, list)
                and all(isinstance(tree, list) for tree in expected)
                else []
            )
            return {
                "kind": "tree_collection",
                "label": label,
                "trees": [
                    {
                        "label": "input tree",
                        "values": argument(decision.get("arg_index", 0), []),
                    },
                    *[
                        {"label": f"result {index + 1}", "values": tree}
                        for index, tree in enumerate(forest)
                    ],
                ],
                "caption": (
                    "The input tree and every tree returned by the first example "
                    "are shown with their exact structures."
                ),
            }

        if requested_kind == "tree_list":
            return {
                "kind": "tree_list_compare",
                "label": label,
                "input": argument(decision.get("arg_index", 0), []),
                "output": expected,
                "output_label": (
                    "circular sorted order"
                    if title == "Convert Binary Search Tree to Sorted Doubly Linked List"
                    else "flattened preorder"
                ),
                "circular": title == "Convert Binary Search Tree to Sorted Doubly Linked List",
                "caption": (
                    "The first example's tree is shown beside the exact node order "
                    "required in its transformed output."
                ),
            }

        if decision.get("source") == "expected":
            values = expected
        else:
            values = argument(decision.get("arg_index", 0), [])
        if not isinstance(values, list):
            return None
        active_values: list[Any] = []
        target_values: list[Any] = []
        active_indices: list[int] = []
        target_indices: list[int] = []
        badges: dict[int, int] = {}
        caption_override: str | None = None
        if decision.get("highlight_result") and isinstance(
            expected, (str, int, float)
        ):
            active_values = [expected]
        if decision.get("highlight_result_list") and isinstance(expected, list):
            active_values = [value for value in expected if value is not None]
        for target_index in decision.get("target_arg_indexes", []):
            target = argument(target_index)
            if isinstance(target, (str, int, float)):
                target_values.append(target)
        if decision.get("range_arg_indexes"):
            low_index, high_index = decision["range_arg_indexes"]
            low, high = argument(low_index), argument(high_index)
            active_values = [
                node["value"]
                for node in _parse_tree_nodes(values)
                if isinstance(node["value"], (int, float))
                and low <= node["value"] <= high
            ]
        if decision.get("highlight_first_path") and isinstance(expected, list):
            first_path = expected[0] if expected and isinstance(expected[0], list) else []
            active_indices = _tree_path_indices(values, first_path)
        if decision.get("visit_order") and isinstance(expected, list):
            badges = _tree_value_order(values, expected)
        if title == "Maximum Depth of Binary Tree":
            active_indices = _tree_depth_path(values)
            caption_override = (
                "The highlighted root-to-leaf path contains the maximum depth of "
                f"{result} nodes."
            )
        elif title == "Minimum Depth of Binary Tree":
            active_indices = _tree_depth_path(values, shortest=True)
            caption_override = (
                "The highlighted path reaches the nearest leaf at depth "
                f"{result}."
            )
        elif title == "Diameter of Binary Tree":
            active_indices = _tree_diameter_path(values)
            caption_override = (
                "The highlighted longest node-to-node path contains "
                f"{result} edges."
            )
        elif title == "Binary Tree Maximum Path Sum":
            active_indices = _tree_maximum_sum_path(values)
            caption_override = (
                "The highlighted connected path has the maximum node sum, "
                f"{result}."
            )
        elif title == "Count Good Nodes in Binary Tree":
            active_indices = _tree_good_node_indices(values)
            caption_override = (
                "Highlighted nodes are at least as large as every ancestor on "
                f"their root path; there are {result}."
            )
        elif title in {"Path Sum", "Path Sum III"} and len(args) > 1:
            active_indices = _tree_sum_path(
                values,
                argument(1),
                root_to_leaf=title == "Path Sum",
            )
            caption_override = (
                "The highlighted downward path reaches the example's target sum."
                if active_indices
                else "No qualifying downward path exists in this example."
            )
        elif title == "Count Nodes Equal to Average of Subtree":
            active_indices = _tree_average_match_indices(values)
            caption_override = (
                "Each highlighted node equals the integer average of its own "
                f"subtree; there are {result}."
            )
        elif title == "Sum of Nodes with Even-Valued Grandparent":
            active_indices = _tree_even_grandparent_indices(values)
            caption_override = (
                "Highlighted nodes have an even-valued grandparent and contribute "
                f"to the sum {result}."
            )
        elif title == "Find Leaves of Binary Tree":
            badges = _tree_removal_rounds(values)
            caption_override = (
                "Each badge is the round in which that node becomes a leaf and "
                "is removed."
            )
        if (
            title == "Lowest Common Ancestor of Deepest Leaves"
            and isinstance(expected, list)
            and expected
        ):
            active_values = [expected[0]]
            nodes = _parse_tree_nodes(values)
            deepest = max((node["depth"] for node in nodes), default=0)
            target_indices = [
                index for index, node in enumerate(nodes)
                if node["depth"] == deepest
            ]
            caption_override = (
                "Orange nodes are the deepest leaves; the blue node is their "
                "lowest common ancestor."
            )
        return {
            "kind": "tree",
            "label": label,
            "values": values,
            "active_values": active_values,
            "target_values": target_values,
            "active_indices": active_indices,
            "target_indices": target_indices,
            "badges": badges,
            "next_links": decision.get("next_links", False),
            "caption": (
                caption_override
                or (
                    "The diagram is the tree required by the first example's output."
                    if decision.get("source") == "expected"
                    else (
                        "Numbered badges show the required visit order."
                        if badges
                        else "The diagram preserves the exact parent-child structure "
                        f"from the first example; the expected result is {result}."
                    )
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
        raw_edges = argument(decision.get("arg_index", 0), [])
        edges: list[list[Any]] = []
        node_labels: list[Any] = []
        if decision.get("adjacency_list"):
            node_labels = list(range(1, len(raw_edges) + 1))
            seen: set[tuple[Any, Any]] = set()
            for start, neighbors in enumerate(raw_edges, start=1):
                for end in neighbors:
                    key = tuple(sorted((start, end), key=str))
                    if key not in seen:
                        seen.add(key)
                        edges.append([start, end])
        else:
            external_weights = (
                argument(decision["weight_arg_index"], [])
                if decision.get("weight_arg_index") is not None
                else []
            )
            for edge_index, edge in enumerate(raw_edges):
                start, end = edge[:2]
                if decision.get("reverse_edges"):
                    start, end = end, start
                normalized = [start, end]
                if edge_index < len(external_weights):
                    normalized.append(external_weights[edge_index])
                elif len(edge) > 2:
                    normalized.append(edge[2])
                edges.append(normalized)

        directed = any(
            word in title
            for word in (
                "Course",
                "Flight",
                "Network Delay",
                "Reconstruct Itinerary",
                "Alien Dictionary",
                "Minimum Weighted Subgraph",
            )
        )
        if decision.get("node_count_arg_index") is not None:
            count = int(argument(decision["node_count_arg_index"], 0))
            node_labels = list(range(count))
        elif title == "Network Delay Time" and len(args) > 1:
            node_labels = list(range(1, int(args[1]) + 1))
        elif decision.get("node_value_arg_index") is not None:
            node_labels = list(range(len(argument(decision["node_value_arg_index"], []))))

        active_edges: list[list[Any]] = []
        active_nodes: list[Any] = []
        if title == "Redundant Connection" and isinstance(expected, list):
            active_edges = [expected]
        if title == "Reconstruct Itinerary" and isinstance(expected, list):
            active_edges = [
                [expected[index], expected[index + 1]]
                for index in range(len(expected) - 1)
            ]
            active_nodes = expected
        if decision.get("active_node_arg_index") is not None:
            flags = argument(decision["active_node_arg_index"], [])
            active_nodes = [
                index for index, is_active in enumerate(flags) if is_active
            ]
        if title == "Network Delay Time" and len(args) > 2:
            active_nodes = [args[2]]

        node_annotations: dict[Any, Any] = {}
        if decision.get("node_value_arg_index") is not None:
            node_values = argument(decision["node_value_arg_index"], [])
            node_annotations = {
                index: f"value {value}" for index, value in enumerate(node_values)
            }
        if title == "Minimum Time to Collect All Apples in a Tree":
            node_annotations.update({node: "apple" for node in active_nodes})
        if title == "Network Delay Time" and active_nodes:
            node_annotations[active_nodes[0]] = "source"

        weight_note = (
            " Edge labels are the example's weights."
            if any(len(edge) > 2 for edge in edges)
            else ""
        )
        return {
            "kind": "graph_auto",
            "label": label,
            "edges": edges,
            "node_labels": node_labels,
            "directed": directed,
            "active_edges": active_edges,
            "active_nodes": active_nodes,
            "node_annotations": node_annotations,
            "caption": (
                "The first example's connections are shown as "
                f"{'directed' if directed else 'undirected'} edges; "
                f"the expected result is {result}.{weight_note}"
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
    "house_circle": _house_circle,
    "decodings": _decodings,
    "segments": _segments,
    "sequence_compare": _sequence_compare,
    "linked_list": _linked_list,
    "operations": _operations,
    "tree": _tree,
    "tree_collection": _tree_collection,
    "tree_list_compare": _tree_list_compare,
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
    "dp_table": _dp_table,
    "stair_costs": _stair_costs,
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
