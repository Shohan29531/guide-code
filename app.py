from __future__ import annotations

# UI build: topics-hints-v2-2026-07-24

import ast
import json
import re
from datetime import datetime
from html import escape
from urllib.parse import quote
from typing import Any

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from code_editor import code_editor

from core.languages import LANGUAGES, LANGUAGE_BY_ID, starter_code
from core.problem_visuals import problem_visual_html
from core.problems import PROBLEM_BY_ID, PROBLEMS
from core.runner import classify_mistake, run_tests
from core.storage import (
    export_progress,
    get_dashboard,
    init_db,
    load_draft,
    load_guide_notes,
    save_attempt,
    save_draft,
    save_guide_note,
)

PROBLEM_TITLE_TO_ID = {
    problem["title"]: problem["id"]
    for problem in PROBLEMS
}
PROBLEM_ID_TO_TITLE = {
    problem["id"]: problem["title"]
    for problem in PROBLEMS
}

PROBLEM_PICKER_KEY = "practice_problem_picker"
RELATED_PROBLEM_LIMIT = 6

NAVIGATION_TO_ROUTE = {
    "Dashboard": "dashboard",
    "Practice": "practice",
    "Problem Library": "problem-set",
}
ROUTE_TO_NAVIGATION = {
    route: navigation
    for navigation, route in NAVIGATION_TO_ROUTE.items()
}
DEFAULT_ROUTE = NAVIGATION_TO_ROUTE["Dashboard"]

RELATED_GENERIC_TOPICS = {
    "array",
    "arrays and hashing",
    "dynamic programming",
    "hash table",
    "math",
    "simulation",
    "sorting",
    "string",
}

RELATED_GENERIC_WORDS = {
    "array",
    "dynamic",
    "hash",
    "math",
    "programming",
    "simulation",
    "sorting",
    "string",
    "table",
}

RELATED_STOP_WORDS = {
    "a",
    "an",
    "and",
    "at",
    "by",
    "for",
    "from",
    "in",
    "into",
    "of",
    "on",
    "or",
    "the",
    "to",
    "with",
    "i",
    "ii",
    "iii",
    "iv",
    "v",
}

RELATED_WORD_ALIASES = {
    "arrays": "array",
    "graphs": "graph",
    "heaps": "heap",
    "intervals": "interval",
    "matrices": "matrix",
    "paths": "path",
    "queues": "queue",
    "stacks": "stack",
    "strings": "string",
    "trees": "tree",
    "tries": "trie",
}

SHOW_GUIDED_SECTIONS = False

st.set_page_config(
    page_title="GuidedCode",
    page_icon="💻",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    :root {
        color-scheme: light;
        --gc-accent: #2563eb;
        --gc-accent-dark: #1d4ed8;
        --gc-accent-soft: #eff6ff;
        --gc-border: #d7deea;
        --gc-muted: #526071;
        --gc-page: #ffffff;
        --gc-panel: #f7f9fc;
        --gc-surface: #ffffff;
        --gc-text: #111827;
        --gc-code-bg: #f3f6fa;
        --gc-disabled-bg: #eef2f7;
        --gc-disabled-text: #475569;
        --gc-focus: #1d4ed8;
    }
    /* Remove the moving blue highlight from searchable dropdown options */
    div[data-baseweb="popover"] [role="option"],
    div[data-baseweb="menu"] [role="option"] {
        outline: none !important;
        box-shadow: none !important;
    }

    div[data-baseweb="popover"] [role="option"][aria-selected="true"],
    div[data-baseweb="popover"] [role="option"]:focus,
    div[data-baseweb="menu"] [role="option"][aria-selected="true"],
    div[data-baseweb="menu"] [role="option"]:focus {
        background-color: transparent !important;
        outline: none !important;
        box-shadow: none !important;
    }

    /* Remove the blue input focus rectangle while typing */
    div[data-baseweb="select"] input:focus,
    div[data-baseweb="select"] [role="combobox"]:focus {
        outline: none !important;
        box-shadow: none !important;
    }

    html, body, .stApp, [data-testid="stAppViewContainer"],
    [data-testid="stMain"], [data-testid="stMainBlockContainer"] {
        background: var(--gc-page) !important;
        color: var(--gc-text) !important;
    }
    ::selection {
        background: #bfdbfe;
        color: #172033;
    }

    /* Streamlit's fixed top header/toolbar must also be forced to light mode. */
    header[data-testid="stHeader"],
    [data-testid="stHeader"] {
        background: transparent !important;
        color: var(--gc-text) !important;
        border: 0 !important;
        box-shadow: none !important;
        height: 0 !important;
        min-height: 0 !important;
        overflow: visible !important;
        pointer-events: none !important;
    }
    [data-testid="stHeader"]::before,
    [data-testid="stHeader"]::after {
        background: transparent !important;
    }
    [data-testid="stDeployButton"],
    [data-testid="stAppDeployButton"],
    [data-testid="stMainMenu"],
    [data-testid="stMainMenuButton"],
    [data-testid="stToolbarActions"],
    .stAppDeployButton {
        display: none !important;
    }
    [data-testid="stToolbar"] {
        background: transparent !important;
        height: 0 !important;
        min-height: 0 !important;
        overflow: visible !important;
        pointer-events: none !important;
    }
    [data-testid="stHeaderActionElements"] {
        background: transparent !important;
        pointer-events: none !important;
    }
    [data-testid="stExpandSidebarButton"] {
        align-items: center !important;
        display: flex !important;
        height: 2rem !important;
        justify-content: center !important;
        left: .7rem !important;
        min-height: 2rem !important;
        pointer-events: auto !important;
        position: fixed !important;
        top: .55rem !important;
        width: 2rem !important;
        z-index: 1000000 !important;
    }
    [data-testid="stToolbar"] > div,
    [data-testid="stStatusWidget"],
    [data-testid="stStatusWidget"] > div {
        background: transparent !important;
        color: var(--gc-text) !important;
    }
    [data-testid="stToolbar"] button,
    [data-testid="stHeader"] button {
        background: #ffffff !important;
        color: var(--gc-text) !important;
        border-color: var(--gc-border) !important;
    }
    [data-testid="stToolbar"] button *,
    [data-testid="stHeader"] button * {
        color: var(--gc-text) !important;
    }
    [data-testid="stToolbar"] button svg,
    [data-testid="stHeader"] button svg {
        color: var(--gc-text) !important;
        fill: var(--gc-text) !important;
    }
    [data-testid="stDecoration"] {
        background: var(--gc-accent) !important;
    }

    body,
    [data-testid="stMarkdownContainer"],
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] li,
    [data-testid="stWidgetLabel"],
    [data-testid="stWidgetLabel"] p,
    [data-testid="stCaptionContainer"],
    [data-testid="stMetricLabel"],
    [data-testid="stMetricValue"],
    [data-testid="stMetricDelta"],
    .stRadio label, .stCheckbox label {
        color: var(--gc-text) !important;
    }

    a, [data-testid="stMarkdownContainer"] a {
        color: var(--gc-accent-dark) !important;
        text-decoration-color: currentColor !important;
    }
    a:hover, [data-testid="stMarkdownContainer"] a:hover {
        color: #1e3a8a !important;
    }

    small, .gc-muted, [data-testid="stCaptionContainer"] p {
        color: var(--gc-muted) !important;
    }

    .block-container {
        padding-top: .55rem !important;
        padding-bottom: 3rem;
        max-width: 1380px;
    }

    .gc-practice-workspace-marker {
        display: none;
    }
    [data-testid="stElementContainer"]:has(.gc-practice-workspace-marker) {
        height: 0 !important;
        margin: 0 !important;
        min-height: 0 !important;
        overflow: hidden !important;
        padding: 0 !important;
    }
    html:has(.gc-practice-workspace-marker),
    body:has(.gc-practice-workspace-marker),
    .stApp:has(.gc-practice-workspace-marker),
    .stApp:has(.gc-practice-workspace-marker) [data-testid="stAppViewContainer"],
    .stApp:has(.gc-practice-workspace-marker) [data-testid="stMain"] {
        height: 100dvh !important;
        max-height: 100dvh !important;
        min-height: 0 !important;
        overflow: hidden !important;
    }
    .stApp:has(.gc-practice-workspace-marker)
    [data-testid="stMainBlockContainer"] {
        box-sizing: border-box !important;
        height: 100dvh !important;
        max-height: 100dvh !important;
        min-height: 0 !important;
        max-width: none !important;
        overflow: hidden !important;
        padding: .55rem .75rem !important;
        width: 100% !important;
    }
    .stApp:has(.gc-practice-workspace-marker)
    [data-testid="stSidebarContent"] {
        overflow: hidden !important;
    }

    [data-testid="stSidebar"],
    [data-testid="stSidebar"] > div,
    [data-testid="stSidebarContent"] {
        background: var(--gc-panel) !important;
        color: var(--gc-text) !important;
    }
    [data-testid="stSidebar"] {
        border-right: 1px solid var(--gc-border);
    }
    .gc-sidebar-problem-label {
        color: #344054 !important;
        font-size: .792rem;
        font-weight: 750;
        letter-spacing: .02em;
        margin: .7rem 0 .28rem;
    }
    [data-testid="stSidebar"] [data-testid="stSelectbox"] {
        margin: 0 !important;
    }
    [data-testid="stSidebar"] .react-aria-ComboBox,
    [data-testid="stSidebar"] .react-aria-ComboBox > [role="group"] {
        background: #ffffff !important;
        border-color: #cbd5e1 !important;
        min-height: 2.1rem !important;
    }
    [data-testid="stSidebar"] .react-aria-ComboBox input[role="combobox"] {
        font-size: .88rem !important;
    }

    .gc-hero {
        padding: .9rem 1rem;
        border: 1px solid var(--gc-border);
        border-radius: 12px;
        background: linear-gradient(135deg, #eff6ff 0%, #ffffff 72%);
        box-shadow: 0 4px 14px rgba(15, 23, 42, 0.035);
        margin-bottom: .55rem;
    }
    .gc-eyebrow {
        font-size: .836rem;
        text-transform: uppercase;
        letter-spacing: .12em;
        color: var(--gc-accent-dark) !important;
        font-weight: 700;
    }
    .gc-title {
        color: var(--gc-text) !important;
        font-size: 1.87rem;
        line-height: 1.1;
        font-weight: 760;
        margin: .15rem 0 .3rem;
    }
    .gc-problem-difficulty {
        align-items: center;
        border: 1px solid transparent;
        border-radius: 999px;
        display: inline-flex;
        font-size: .836rem;
        font-weight: 700;
        line-height: 1.2;
        margin-top: .2rem;
        padding: .2rem .52rem;
    }
    .gc-problem-difficulty.is-easy {
        background: #ecfdf3;
        border-color: #abefc6;
        color: #067647 !important;
    }
    .gc-problem-difficulty.is-medium {
        background: #fffaeb;
        border-color: #fedf89;
        color: #b54708 !important;
    }
    .gc-problem-difficulty.is-hard {
        background: #fef3f2;
        border-color: #fecdca;
        color: #b42318 !important;
    }
    .gc-problem-hero {
        background: transparent;
        border: 0;
        border-radius: 0;
        box-shadow: none;
        margin: 0;
        padding: .2rem 0 .9rem;
    }
    .gc-problem-hero .gc-title {
        font-size: 1.848rem;
        margin: 0 0 .18rem;
    }
    .gc-subtitle {
        color: var(--gc-muted) !important;
        font-size: .968rem;
        line-height: 1.4;
        max-width: 820px;
    }
    .gc-question {
        padding: 1rem 1.1rem;
        border: 1px solid #dbeafe;
        border-left: 4px solid var(--gc-accent);
        background: var(--gc-accent-soft);
        border-radius: 8px;
        color: var(--gc-text) !important;
        font-size: 1.144rem;
    }
    .gc-pass { font-weight: 700; }

    /* Compact problem-contract visualizations */
    .gc-problem-visual {
        color: #172033;
        margin: .9rem 0 1.15rem;
        max-width: 100%;
        padding: 0;
    }
    .gc-vis-stage {
        box-sizing: border-box;
        max-width: 100%;
        min-width: 0;
        overflow: visible;
        padding: .45rem .1rem .65rem;
        width: 100%;
    }
    .gc-vis-legend {
        align-items: center;
        color: #526071;
        display: flex;
        flex-wrap: wrap;
        font-size: .726rem;
        gap: .3rem .75rem;
        line-height: 1.2;
        margin-top: .42rem;
    }
    .gc-vis-legend-item {
        align-items: center;
        display: inline-flex;
        gap: .28rem;
    }
    .gc-vis-legend-item i {
        background: #e7efff;
        border: 1px solid #4c7dd9;
        border-radius: 50%;
        box-sizing: border-box;
        display: inline-block;
        height: .62rem;
        width: .62rem;
    }
    .gc-vis-legend-item i.target {
        background: #fff1e7;
        border-color: #e99554;
    }
    .gc-vis-legend-item i.badge {
        background: #2f6fed;
        border: 2px solid #dbe8ff;
    }
    .gc-vis-legend-item i.next {
        background: transparent;
        border: 0;
        border-radius: 0;
        border-top: 2px dashed #b57616;
        height: 0;
        width: .85rem;
    }
    .gc-vis-legend-item i.path {
        background: #e7efff;
        border-color: #4c7dd9;
        border-radius: 3px;
    }
    .gc-vis-legend-item i.match {
        background: #e8f7ee;
        border-color: #55a977;
        border-radius: 3px;
    }
    .gc-vis-legend-item i.result {
        background: #fff1e7;
        border-color: #e99554;
        border-radius: 3px;
    }
    .gc-vis-legend-item i.tone-1 { background: #e8f0ff; border-color: #6f94d8; }
    .gc-vis-legend-item i.tone-2 { background: #e8f7ee; border-color: #69ad82; }
    .gc-vis-legend-item i.tone-3 { background: #fff1e7; border-color: #dc8c50; }
    .gc-vis-legend-item i.tone-4 { background: #f2eaff; border-color: #9a82ca; }
    .gc-problem-visual figcaption {
        color: #526071;
        font-size: .858rem;
        line-height: 1.35;
        margin-top: .32rem;
    }
    .gc-example-content > .gc-problem-visual {
        box-sizing: border-box;
        margin: .55rem 0 .4rem;
        width: 100%;
    }
    .gc-vis-sequence {
        align-items: flex-start;
        display: flex;
        gap: .24rem;
        max-width: 100%;
        overflow-x: auto;
        overflow-y: visible;
        padding: .06rem .04rem .36rem;
        scrollbar-gutter: stable;
    }
    .gc-vis-cell-wrap {
        flex: 1 0 var(--gc-vis-cell-width, 2.15rem);
        min-width: var(--gc-vis-cell-width, 2.15rem);
        position: relative;
        text-align: center;
    }
    .gc-vis-cell-wrap > span {
        color: #667085;
        display: block;
        font-size: .77rem;
        line-height: 1.1;
        margin-top: .22rem;
        min-height: .8rem;
        white-space: nowrap;
    }
    .gc-vis-cell {
        align-items: center;
        background: #f3f5f8;
        border: 1px solid #d8dee8;
        border-radius: 4px;
        box-sizing: border-box;
        color: #172033;
        display: flex;
        font-family: SFMono-Regular, Consolas, "Liberation Mono", monospace;
        font-size: .88rem;
        font-weight: 700;
        height: 2.1rem;
        justify-content: center;
        min-width: 0;
        overflow: hidden;
        padding: 0 .12rem;
        position: relative;
        text-overflow: ellipsis;
    }
    .gc-vis-cell.is-active {
        background: #e7efff;
        border-color: #7da7f8;
        color: #173b78;
    }
    .gc-vis-cell.is-warning {
        background: #fff1e7;
        border-color: #f0a46b;
        color: #873800;
    }
    .gc-vis-cell.is-muted {
        color: #98a2b3;
        opacity: .66;
    }
    .gc-vis-cell.is-changed {
        background: #e8f7ee;
        border-color: #7bc69a;
        color: #135f35;
    }
    .gc-vis-cell.tone-1,
    .gc-vis-segments .tone-1 {
        background: #e8f0ff;
        border-color: #9fbcf4;
    }
    .gc-vis-cell.tone-2,
    .gc-vis-segments .tone-2 {
        background: #edf8f1;
        border-color: #9bd0ae;
    }
    .gc-vis-cell.tone-3,
    .gc-vis-segments .tone-3 {
        background: #fff3e8;
        border-color: #efbc8f;
    }
    .gc-vis-cell-wrap.has-break-after {
        margin-right: .7rem;
    }
    .gc-vis-cell-wrap.has-break-after::after {
        border-right: 2px dashed #98a2b3;
        bottom: -.05rem;
        content: "";
        position: absolute;
        right: -.42rem;
        top: -.05rem;
    }
    .gc-vis-bars {
        align-items: flex-end;
        box-sizing: border-box;
        display: flex;
        gap: .35rem;
        height: 132px;
        max-width: 100%;
        padding: 1.65rem .65rem 1.35rem;
        position: relative;
        width: 100%;
    }
    .gc-vis-bar-column {
        align-items: center;
        display: flex;
        flex: 1 1 0;
        flex-direction: column;
        height: 100%;
        justify-content: flex-end;
        min-width: 0;
        position: relative;
    }
    .gc-vis-bar {
        background: #cbd3df;
        border-radius: 3px 3px 0 0;
        max-width: 2.2rem;
        min-width: .65rem;
        width: 58%;
    }
    .gc-vis-bar.is-marked {
        background: #4c7dd9;
    }
    .gc-vis-bar-marker {
        color: #344054;
        font-size: .77rem;
        font-weight: 700;
        left: 50%;
        position: absolute;
        top: -1.3rem;
        transform: translateX(-50%);
        white-space: nowrap;
    }
    .gc-vis-bar-value {
        color: #344054;
        font-family: SFMono-Regular, Consolas, monospace;
        font-size: .77rem;
        font-weight: 700;
        margin-top: .1rem;
    }
    .gc-vis-bar-index {
        color: #667085;
        font-size: .77rem;
        white-space: nowrap;
    }
    .gc-vis-bar-span {
        border-top: 2px solid #4c7dd9;
        height: 8px;
        position: absolute;
        top: .8rem;
        z-index: 2;
    }
    .gc-vis-bar-span::before,
    .gc-vis-bar-span::after {
        background: #4c7dd9;
        content: "";
        height: 7px;
        position: absolute;
        top: -2px;
        width: 2px;
    }
    .gc-vis-bar-span::before { left: 0; }
    .gc-vis-bar-span::after { right: 0; }
    .gc-vis-bar-span span {
        color: #344054;
        font-size: .77rem;
        left: 50%;
        position: absolute;
        top: -1.05rem;
        transform: translateX(-50%);
        white-space: nowrap;
    }
    .gc-vis-grid-scroll {
        max-width: 100%;
        overflow-x: auto;
        overflow-y: hidden;
        padding: .08rem .05rem .35rem;
        scrollbar-gutter: stable;
    }
    .gc-vis-grid {
        display: grid;
        gap: .22rem;
        grid-template-columns: repeat(var(--gc-grid-columns), var(--gc-grid-cell-width));
        max-width: none;
        width: max-content;
    }
    .gc-vis-grid-cell {
        align-items: center;
        background: #f3f5f8;
        border: 1px solid #d8dee8;
        border-radius: 4px;
        color: #344054;
        display: flex;
        font-family: SFMono-Regular, Consolas, monospace;
        font-size: .836rem;
        font-weight: 700;
        height: var(--gc-grid-cell-height);
        justify-content: center;
        min-width: 0;
        overflow: visible;
        padding: 0 .2rem;
        position: relative;
        text-overflow: clip;
    }
    .gc-vis-grid-cell small {
        color: #345995;
        font-family: inherit;
        font-size: .77rem;
        position: absolute;
        right: .18rem;
        top: .1rem;
    }
    .gc-vis-grid-cell.source {
        background: #fff0e4;
        border-color: #eea26c;
    }
    .gc-vis-grid-cell.connected,
    .gc-vis-grid-cell.changed,
    .gc-vis-grid-cell.group-1 {
        background: #e5efff;
        border-color: #8eb0ee;
    }
    .gc-vis-grid-cell.separate,
    .gc-vis-grid-cell.group-2 {
        background: #f2eaff;
        border-color: #b6a0e4;
    }
    .gc-vis-grid-cell.group-3 {
        background: #e7f7ed;
        border-color: #91cda8;
    }
    .gc-vis-grid-cell.is-water {
        background: #f8fafc;
        border-color: #e4e8ee;
        color: #98a2b3;
    }
    .gc-vis-grid-cell.box-right {
        border-right: 3px solid #7d8998;
    }
    .gc-vis-grid-cell.box-bottom {
        border-bottom: 3px solid #7d8998;
    }
    .gc-vis-compare {
        align-items: center;
        display: flex;
        flex-wrap: wrap;
        gap: clamp(.45rem, 2vw, 1rem);
        max-width: 100%;
    }
    .gc-vis-compare > div:not(.gc-vis-arrow) {
        min-width: 0;
    }
    .gc-vis-side-label {
        color: #667085;
        display: block;
        font-size: .77rem;
        font-weight: 700;
        margin-bottom: .22rem;
        text-align: center;
        text-transform: uppercase;
    }
    .gc-vis-arrow {
        color: #667085;
        flex: 0 0 auto;
        font-size: 1.265rem;
    }
    .gc-vis-product {
        align-items: center;
        display: flex;
        flex-wrap: wrap;
        gap: .35rem;
    }
    .gc-vis-product-value {
        align-items: center;
        background: #e7efff;
        border: 1px solid #8eb0ee;
        border-radius: 4px;
        display: flex;
        font-family: SFMono-Regular, Consolas, monospace;
        font-size: .902rem;
        font-weight: 700;
        height: 2.15rem;
        justify-content: center;
        width: 2.15rem;
    }
    .gc-vis-product-value.is-excluded {
        background: #f3f5f8;
        border-color: #d8dee8;
        color: #98a2b3;
        text-decoration: line-through;
    }
    .gc-vis-times {
        color: #667085;
        font-weight: 700;
    }
    .gc-vis-product-note {
        color: #667085;
        font-size: .792rem;
        margin-left: .25rem;
    }
    .gc-vis-water {
        align-items: flex-end;
        box-sizing: border-box;
        display: flex;
        height: 126px;
        justify-content: space-between;
        max-width: 100%;
        padding: 0 0 20px;
        position: relative;
        width: 100%;
    }
    .gc-vis-water-line {
        background: #8e99a8;
        bottom: 20px;
        position: absolute;
        transform: translateX(-50%);
        width: 3px;
        z-index: 3;
    }
    .gc-vis-water-line.is-boundary {
        background: #245bb5;
        width: 4px;
    }
    .gc-vis-water-line span {
        color: #526071;
        font-size: .77rem;
        left: 50%;
        position: absolute;
        top: -1rem;
        transform: translateX(-50%);
    }
    .gc-vis-water-fill {
        background: rgba(70, 137, 214, .2);
        border-top: 2px solid #4689d6;
        bottom: 20px;
        position: absolute;
        z-index: 1;
    }
    .gc-vis-water-baseline {
        background: #667085;
        bottom: 19px;
        height: 2px;
        left: var(--gc-water-edge);
        position: absolute;
        right: var(--gc-water-edge);
    }
    .gc-vis-staircase {
        align-items: flex-end;
        box-sizing: border-box;
        display: flex;
        height: 118px;
        max-width: 100%;
        padding-right: 4.6rem;
        position: relative;
        width: 100%;
    }
    .gc-vis-step {
        align-items: flex-start;
        background: #e8edf4;
        border-right: 1px solid #b9c2cf;
        border-top: 1px solid #b9c2cf;
        display: flex;
        flex: 1 1 0;
        justify-content: center;
        max-width: 3.5rem;
        padding-top: .2rem;
    }
    .gc-vis-step span {
        color: #526071;
        font-size: .77rem;
    }
    .gc-vis-step-moves {
        color: #245bb5;
        display: flex;
        flex-direction: column;
        font-size: .792rem;
        font-weight: 700;
        gap: .85rem;
        position: absolute;
        right: .2rem;
        top: 1.8rem;
    }
    .gc-vis-step-moves span::before {
        content: "↗ ";
    }
    .gc-vis-piles {
        align-items: flex-end;
        box-sizing: border-box;
        display: flex;
        gap: .8rem;
        max-width: 100%;
        min-height: 126px;
        padding-bottom: 1.55rem;
        position: relative;
        width: 100%;
    }
    .gc-vis-pile {
        align-items: center;
        display: flex;
        flex: 1 1 0;
        flex-direction: column;
        max-width: 5rem;
    }
    .gc-vis-portions {
        align-items: stretch;
        display: flex;
        flex-direction: column-reverse;
        gap: 2px;
        width: 70%;
    }
    .gc-vis-portions span {
        align-items: center;
        background: #e7efff;
        border: 1px solid #8eb0ee;
        box-sizing: border-box;
        color: #344054;
        display: flex;
        font-family: SFMono-Regular, Consolas, monospace;
        font-size: .77rem;
        height: calc(13px + var(--gc-portion) * 9px);
        justify-content: center;
    }
    .gc-vis-pile strong {
        color: #344054;
        font-size: .836rem;
        margin-top: .18rem;
    }
    .gc-vis-pile small {
        color: #667085;
        font-size: .77rem;
    }
    .gc-vis-speed {
        bottom: 0;
        color: #526071;
        font-family: SFMono-Regular, Consolas, monospace;
        font-size: .77rem;
        left: 0;
        position: absolute;
    }
    .gc-vis-intervals {
        max-width: 28rem;
        width: 100%;
    }
    .gc-vis-intervals > div:not(.gc-vis-interval-down) {
        align-items: center;
        display: grid;
        gap: .45rem;
        grid-template-columns: 2.8rem 1fr;
    }
    .gc-vis-intervals > div > span {
        color: #667085;
        font-size: .77rem;
        font-weight: 700;
        text-transform: uppercase;
    }
    .gc-vis-interval-line {
        background: #d5dbe4;
        height: 2px;
        margin: 1.15rem 0;
        position: relative;
    }
    .gc-vis-interval {
        align-items: center;
        background: #e7efff;
        border: 1px solid #8eb0ee;
        border-radius: 3px;
        box-sizing: border-box;
        color: #173b78;
        display: flex;
        font-family: SFMono-Regular, Consolas, monospace;
        font-size: .77rem;
        height: 1.35rem;
        justify-content: center;
        min-width: 2.8rem;
        position: absolute;
        top: -.68rem;
        white-space: nowrap;
    }
    .gc-vis-interval:nth-child(even) {
        top: .78rem;
    }
    .gc-vis-interval.is-merged {
        background: #e7f7ed;
        border-color: #91cda8;
        color: #135f35;
    }
    .gc-vis-interval.is-new {
        background: #fff0e4;
        border-color: #eea26c;
        color: #873800;
    }
    .gc-vis-interval-down {
        color: #667085;
        font-size: .935rem;
        line-height: .6;
        margin-left: 3.7rem;
    }
    .gc-vis-graph-block {
        max-width: 100%;
        min-width: 0;
    }
    .gc-vis-graph-scroll {
        max-width: 100%;
        overflow-x: auto;
        overflow-y: hidden;
        padding: .45rem .5rem 1.55rem;
        scrollbar-gutter: stable;
    }
    .gc-vis-graph {
        box-sizing: border-box;
        height: var(--gc-graph-height);
        margin: 0 auto;
        min-width: var(--gc-graph-width);
        position: relative;
        width: var(--gc-graph-width);
    }
    .gc-vis-graph-svg {
        height: 100%;
        inset: 0;
        overflow: visible;
        position: absolute;
        width: 100%;
        z-index: 1;
    }
    .gc-vis-graph-edge {
        fill: none;
        stroke: #aeb8c6;
        stroke-linecap: round;
        stroke-width: 2;
        vector-effect: non-scaling-stroke;
    }
    .gc-vis-graph-edge.is-active {
        stroke: #2f6fed;
        stroke-width: 3;
    }
    .gc-vis-graph-edge.tone-1 { stroke: #6f94d8; }
    .gc-vis-graph-edge.tone-2 { stroke: #69ad82; }
    .gc-vis-graph-edge.tone-3 { stroke: #dc8c50; }
    .gc-vis-graph-edge.tone-4 { stroke: #9a82ca; }
    .gc-vis-graph-arrow { fill: #7f8b9c; }
    .gc-vis-graph-arrow-active { fill: #2f6fed; }
    .gc-vis-graph-edge-label {
        background: #fff;
        border: 1px solid #d8dee8;
        border-radius: 3px;
        color: #344054;
        font-family: SFMono-Regular, Consolas, monospace;
        font-size: .66rem;
        line-height: 1;
        padding: .13rem .22rem;
        position: absolute;
        transform: translate(-50%, -50%);
        white-space: nowrap;
        z-index: 3;
    }
    .gc-vis-graph-node {
        align-items: center;
        background: #f3f5f8;
        border: 1px solid #aeb8c6;
        border-radius: 50%;
        box-sizing: border-box;
        color: #344054;
        display: flex;
        font-family: SFMono-Regular, Consolas, monospace;
        font-size: .825rem;
        font-weight: 700;
        height: 1.88rem;
        justify-content: center;
        position: absolute;
        transform: translate(-50%, -50%);
        width: 1.88rem;
        z-index: 2;
    }
    .gc-vis-graph-node.is-active {
        background: #e7efff;
        border-color: #2f6fed;
        box-shadow: 0 0 0 2px rgba(47, 111, 237, .12);
        color: #173b78;
    }
    .gc-vis-graph-node.tone-1 {
        background: #e8f0ff;
        border-color: #6f94d8;
        color: #244b89;
    }
    .gc-vis-graph-node.tone-2 {
        background: #e8f7ee;
        border-color: #69ad82;
        color: #17613a;
    }
    .gc-vis-graph-node.tone-3 {
        background: #fff1e7;
        border-color: #dc8c50;
        color: #873800;
    }
    .gc-vis-graph-node.tone-4 {
        background: #f2eaff;
        border-color: #9a82ca;
        color: #553b86;
    }
    .gc-vis-graph-node.is-active {
        background: #e7efff;
        border-color: #2f6fed;
        color: #173b78;
    }
    .gc-vis-graph-node b {
        font: inherit;
    }
    .gc-vis-graph-node small {
        background: rgba(255, 255, 255, .94);
        border-radius: 3px;
        color: #526071;
        font-size: .638rem;
        font-weight: 650;
        left: 50%;
        line-height: 1.15;
        padding: .08rem .18rem;
        position: absolute;
        top: 1.95rem;
        transform: translateX(-50%);
        white-space: nowrap;
    }
    .gc-vis-houses {
        align-items: flex-end;
        box-sizing: border-box;
        display: flex;
        gap: clamp(.25rem, 1.5vw, .75rem);
        max-width: 100%;
        width: 100%;
    }
    .gc-vis-house {
        align-items: center;
        display: flex;
        flex: 1 1 0;
        flex-direction: column;
        max-width: 3.8rem;
        opacity: .55;
    }
    .gc-vis-house.is-active {
        opacity: 1;
    }
    .gc-vis-roof {
        border-bottom: 15px solid #9da8b7;
        border-left: 22px solid transparent;
        border-right: 22px solid transparent;
        height: 0;
        width: 0;
    }
    .gc-vis-house.is-active .gc-vis-roof {
        border-bottom-color: #4c7dd9;
    }
    .gc-vis-house-body {
        align-items: center;
        background: #e8edf4;
        border: 1px solid #9da8b7;
        color: #344054;
        display: flex;
        font-family: SFMono-Regular, Consolas, monospace;
        font-size: .825rem;
        font-weight: 700;
        height: 2.25rem;
        justify-content: center;
        width: 2.65rem;
    }
    .gc-vis-house.is-active .gc-vis-house-body {
        background: #e7efff;
        border-color: #4c7dd9;
    }
    .gc-vis-house small {
        color: #667085;
        font-size: .715rem;
        margin-top: .16rem;
    }
    .gc-vis-house-circle {
        border: 1px dashed #c5ccd6;
        border-radius: 50%;
        height: 9.5rem;
        margin: .2rem 0 .35rem .3rem;
        position: relative;
        width: 9.5rem;
    }
    .gc-vis-circle-house {
        align-items: center;
        background: #f3f5f8;
        border: 1px solid #aeb8c6;
        border-radius: 50%;
        display: flex;
        flex-direction: column;
        height: 2rem;
        justify-content: center;
        position: absolute;
        transform: translate(-50%, -50%);
        width: 2rem;
    }
    .gc-vis-circle-house.is-active {
        background: #e7efff;
        border-color: #4c7dd9;
        color: #173b78;
    }
    .gc-vis-circle-house b {
        font-family: SFMono-Regular, Consolas, monospace;
        font-size: .77rem;
    }
    .gc-vis-circle-house small {
        color: #667085;
        font-size: .55rem;
    }
    .gc-vis-decodings {
        align-items: center;
        display: flex;
        flex-wrap: wrap;
        gap: 1.15rem;
        max-width: 100%;
    }
    .gc-vis-decodings > strong {
        background: #f3f5f8;
        border: 1px solid #d8dee8;
        border-radius: 4px;
        font-family: SFMono-Regular, Consolas, monospace;
        font-size: 1.1rem;
        padding: .55rem .65rem;
    }
    .gc-vis-decoding-row {
        align-items: center;
        color: #344054;
        display: grid;
        font-family: SFMono-Regular, Consolas, monospace;
        font-size: .836rem;
        gap: .55rem;
        grid-template-columns: minmax(3rem, auto) auto minmax(3rem, auto);
        margin: .2rem 0;
    }
    .gc-vis-decoding-row b {
        color: #667085;
    }
    .gc-vis-segments {
        display: flex;
        flex-wrap: wrap;
        gap: .28rem;
    }
    .gc-vis-segments span {
        border: 1px solid;
        border-radius: 4px;
        color: #344054;
        font-family: SFMono-Regular, Consolas, monospace;
        font-size: .858rem;
        font-weight: 700;
        padding: .42rem .55rem;
    }
    .gc-vis-sequence-compare {
        display: grid;
        gap: .2rem;
        max-width: 100%;
    }
    .gc-vis-sequence-compare > div:not(.gc-vis-sequence-arrow) {
        min-width: 0;
    }
    .gc-vis-sequence-arrow {
        color: #7f8b9c;
        font-size: .99rem;
        line-height: 1;
        padding-left: .65rem;
    }
    .gc-vis-linked {
        display: grid;
        gap: .45rem;
        max-width: 100%;
    }
    .gc-vis-linked-group {
        align-items: center;
        display: grid;
        gap: .45rem;
        grid-template-columns: 2.8rem minmax(0, 1fr);
    }
    .gc-vis-linked-group > small {
        color: #667085;
        font-size: .748rem;
        font-weight: 700;
        text-transform: uppercase;
    }
    .gc-vis-linked-row {
        align-items: center;
        display: flex;
        flex-wrap: wrap;
        gap: .22rem;
        max-width: 100%;
    }
    .gc-vis-list-node {
        align-items: center;
        background: #f3f5f8;
        border: 1px solid #cfd7e3;
        border-radius: 50%;
        box-sizing: border-box;
        color: #26364d;
        display: inline-flex;
        flex-direction: column;
        font-family: SFMono-Regular, Consolas, monospace;
        font-size: .825rem;
        height: 2.1rem;
        justify-content: center;
        min-width: 2.1rem;
        padding: 0 .28rem;
    }
    .gc-vis-list-node.is-result {
        background: #e8f7ee;
        border-color: #7bc69a;
        color: #135f35;
    }
    .gc-vis-list-node small {
        color: #667085;
        font-size: .594rem;
        line-height: .7rem;
    }
    .gc-vis-list-arrow,
    .gc-vis-list-more {
        color: #7f8b9c;
        font-size: .902rem;
    }
    .gc-vis-operations {
        display: grid;
        max-width: 34rem;
        width: 100%;
    }
    .gc-vis-operation-row {
        align-items: center;
        border-bottom: 1px solid #e7eaf0;
        color: #526071;
        display: grid;
        font-size: .792rem;
        gap: .45rem;
        grid-template-columns: minmax(5.8rem, 1fr) minmax(3.6rem, 1fr) auto minmax(3.6rem, 1fr);
        min-width: 0;
        padding: .28rem 0;
    }
    .gc-vis-operation-row code,
    .gc-vis-operation-row span {
        min-width: 0;
        overflow-wrap: anywhere;
    }
    .gc-vis-operation-row code {
        color: #173b78;
        font-weight: 700;
    }
    .gc-vis-operation-row b {
        color: #98a2b3;
    }
    .gc-vis-operation-result {
        color: #135f35;
        font-family: SFMono-Regular, Consolas, monospace;
    }
    .gc-vis-operation-more {
        color: #667085;
        font-size: .77rem;
        padding-top: .3rem;
    }
    .gc-vis-tree-block {
        max-width: 100%;
        min-width: 0;
    }
    .gc-vis-tree-scroll {
        max-width: 100%;
        overflow-x: auto;
        overflow-y: hidden;
        padding: .55rem .5rem .75rem;
        scrollbar-gutter: stable;
    }
    .gc-vis-tree {
        margin: 0 auto;
        position: relative;
    }
    .gc-vis-tree-svg {
        height: 100%;
        inset: 0;
        overflow: visible;
        position: absolute;
        width: 100%;
        z-index: 1;
    }
    .gc-vis-tree-edge {
        fill: none;
        stroke: #b9c2cf;
        stroke-linecap: round;
        stroke-width: 2;
        vector-effect: non-scaling-stroke;
    }
    .gc-vis-tree-edge.is-active {
        stroke: #2f6fed;
        stroke-width: 3;
    }
    .gc-vis-tree-next-link {
        fill: none;
        stroke: #b57616;
        stroke-dasharray: 5 4;
        stroke-width: 1.5;
        vector-effect: non-scaling-stroke;
    }
    #gc-vis-tree-next-arrow path {
        fill: #b57616;
    }
    .gc-vis-list-loop {
        color: #667085;
        display: block;
        font-size: .748rem;
        font-weight: 700;
        margin-top: .35rem;
    }
    .gc-vis-tree-node {
        align-items: center;
        background: #f3f5f8;
        border: 1px solid #aeb8c6;
        border-radius: 50%;
        box-sizing: border-box;
        color: #344054;
        display: flex;
        font-family: SFMono-Regular, Consolas, monospace;
        font-size: .792rem;
        font-weight: 700;
        height: 1.9rem;
        justify-content: center;
        position: absolute;
        transform: translate(-50%, -50%);
        width: 1.9rem;
        z-index: 2;
    }
    .gc-vis-tree-node.is-active {
        background: #e7efff;
        border-color: #2f6fed;
        box-shadow: 0 0 0 2px rgba(47, 111, 237, .12);
        color: #173b78;
    }
    .gc-vis-tree-node.is-target {
        background: #fff1e7;
        border-color: #e99554;
        color: #873800;
    }
    .gc-vis-tree-node.is-active.is-target {
        box-shadow: 0 0 0 3px #f7c49d;
    }
    .gc-vis-tree-node > small {
        align-items: center;
        background: #2f6fed;
        border: 1px solid #fff;
        border-radius: 50%;
        color: #fff;
        display: flex;
        font-size: .55rem;
        height: .9rem;
        justify-content: center;
        position: absolute;
        right: -.42rem;
        top: -.44rem;
        width: .9rem;
    }
    .gc-vis-tree-collection {
        align-items: start;
        display: grid;
        gap: .9rem;
        grid-template-columns: repeat(auto-fit, minmax(min(100%, 16rem), 1fr));
        max-width: 100%;
    }
    .gc-vis-tree-list {
        align-items: center;
        display: flex;
        flex-wrap: wrap;
        gap: .8rem;
        max-width: 100%;
    }
    .gc-vis-tree-list > div {
        min-width: 0;
    }
    .gc-vis-tree-panel {
        min-width: 0;
        width: 100%;
    }
    .gc-vis-tree-panel .gc-vis-tree-scroll {
        border: 1px solid #edf0f4;
        border-radius: 6px;
        padding-left: .35rem;
        padding-right: .35rem;
    }
    .gc-vis-empty {
        color: #667085;
        font-size: .825rem;
    }
    .gc-vis-points {
        height: 145px;
        max-width: 28rem;
        position: relative;
        width: 100%;
    }
    .gc-vis-axis-x,
    .gc-vis-axis-y {
        background: #c3cad5;
        position: absolute;
    }
    .gc-vis-axis-x {
        height: 1px;
        left: 4%;
        right: 4%;
        top: 50%;
    }
    .gc-vis-axis-y {
        bottom: 4%;
        left: 50%;
        top: 4%;
        width: 1px;
    }
    .gc-vis-point {
        background: #667085;
        border: 2px solid #fff;
        border-radius: 50%;
        height: .62rem;
        position: absolute;
        transform: translate(-50%, 50%);
        width: .62rem;
        z-index: 2;
    }
    .gc-vis-point.is-active {
        background: #2f6fed;
        box-shadow: 0 0 0 2px #a9c5fb;
    }
    .gc-vis-point b {
        display: none;
    }
    .gc-vis-point small {
        color: #526071;
        font-family: SFMono-Regular, Consolas, monospace;
        font-size: .682rem;
        left: .58rem;
        position: absolute;
        top: -.55rem;
        white-space: nowrap;
    }
    .gc-vis-string-grid {
        display: grid;
        gap: 2px;
        grid-template-columns: repeat(var(--gc-string-columns), minmax(1.1rem, 2rem));
        max-width: 100%;
    }
    .gc-vis-string-grid > span,
    .gc-vis-string-grid > b {
        align-items: center;
        aspect-ratio: 1;
        display: flex;
        font-family: SFMono-Regular, Consolas, monospace;
        font-size: .77rem;
        justify-content: center;
    }
    .gc-vis-string-grid > b {
        color: #344054;
    }
    .gc-vis-string-grid > span:not(.gc-vis-string-corner) {
        background: #f3f5f8;
        border: 1px solid #e0e5ec;
    }
    .gc-vis-dp-block {
        max-width: 100%;
        min-width: 0;
    }
    .gc-vis-dp-table-wrap {
        max-width: 100%;
        overflow-x: auto;
        overflow-y: visible;
        padding: .15rem .1rem .5rem;
        scrollbar-gutter: stable;
    }
    .gc-vis-dp-table {
        border-collapse: separate;
        border-spacing: 2px;
        font-family: SFMono-Regular, Consolas, monospace;
        table-layout: fixed;
        width: auto;
    }
    .gc-vis-dp-table th,
    .gc-vis-dp-table td {
        border: 0;
        font-size: .715rem;
        height: 1.65rem;
        min-width: 1.65rem;
        padding: 0 .15rem;
        text-align: center;
    }
    .gc-vis-dp-table th {
        background: #fff;
        color: #526071;
        font-weight: 700;
    }
    .gc-vis-dp-table tbody th {
        left: 0;
        position: sticky;
        z-index: 2;
    }
    .gc-vis-dp-table td {
        background: #f3f5f8;
        border: 1px solid #e0e5ec;
        color: #344054;
    }
    .gc-vis-dp-table td.is-path {
        background: #e7efff;
        border-color: #4c7dd9;
        color: #173b78;
        font-weight: 750;
    }
    .gc-vis-dp-table td.is-match {
        background: #e8f7ee;
        border-color: #55a977;
        color: #135f35;
        font-weight: 800;
    }
    .gc-vis-dp-table td.is-result {
        background: #fff1e7;
        border-color: #e99554;
        box-shadow: inset 0 0 0 1px #e99554;
        color: #873800;
        font-weight: 850;
    }
    .gc-vis-pyramid {
        display: grid;
        gap: .22rem;
        justify-content: start;
        max-width: 100%;
    }
    .gc-vis-pyramid-row {
        display: flex;
        gap: .22rem;
        justify-content: center;
    }
    .gc-vis-pyramid-row span {
        align-items: center;
        background: #f3f5f8;
        border: 1px solid #d8dee8;
        border-radius: 4px;
        display: flex;
        font-family: SFMono-Regular, Consolas, monospace;
        font-size: .77rem;
        height: 1.7rem;
        justify-content: center;
        min-width: 1.7rem;
        padding: 0 .18rem;
    }
    .gc-vis-pyramid-row span.is-active {
        background: #e7efff;
        border-color: #4c7dd9;
        color: #173b78;
        font-weight: 800;
    }
    .gc-vis-rectangles {
        height: 145px;
        max-width: 27rem;
        position: relative;
        width: 100%;
    }
    .gc-vis-rectangle {
        border: 2px solid;
        box-sizing: border-box;
        position: absolute;
    }
    .gc-vis-rectangle.tone-a {
        background: rgba(76, 125, 217, .18);
        border-color: #4c7dd9;
    }
    .gc-vis-rectangle.tone-b {
        background: rgba(235, 146, 75, .18);
        border-color: #d8732c;
    }
    .gc-vis-clock {
        border: 2px solid #b9c2cf;
        border-radius: 50%;
        height: 8.4rem;
        margin-left: .2rem;
        position: relative;
        width: 8.4rem;
    }
    .gc-vis-clock > span {
        color: #526071;
        font-size: .715rem;
        position: absolute;
        transform: translate(-50%, -50%);
    }
    .gc-vis-clock > span:nth-of-type(1) { left: 50%; top: 8%; }
    .gc-vis-clock > span:nth-of-type(2) { left: 92%; top: 50%; }
    .gc-vis-clock > span:nth-of-type(3) { left: 50%; top: 92%; }
    .gc-vis-clock > span:nth-of-type(4) { left: 8%; top: 50%; }
    .gc-vis-clock > i {
        background: #344054;
        bottom: 50%;
        left: calc(50% - 1px);
        position: absolute;
        transform-origin: 50% 100%;
        width: 2px;
    }
    .gc-vis-clock > i.is-hour { height: 30%; }
    .gc-vis-clock > i.is-minute {
        background: #2f6fed;
        height: 40%;
    }
    .gc-vis-clock > b {
        background: #172033;
        border-radius: 50%;
        height: .42rem;
        left: 50%;
        position: absolute;
        top: 50%;
        transform: translate(-50%, -50%);
        width: .42rem;
    }
    .gc-vis-paired-bars {
        max-width: 32rem;
        width: 100%;
    }
    .gc-vis-paired-legend {
        color: #667085;
        display: flex;
        font-size: .748rem;
        gap: 1rem;
        margin-bottom: .3rem;
    }
    .gc-vis-paired-legend span::before {
        background: #8290a3;
        border-radius: 2px;
        content: "";
        display: inline-block;
        height: .55rem;
        margin-right: .25rem;
        width: .55rem;
    }
    .gc-vis-paired-legend span:last-child::before {
        background: #4c7dd9;
    }
    .gc-vis-paired-groups {
        align-items: end;
        display: flex;
        gap: .35rem;
        height: 92px;
    }
    .gc-vis-paired-group {
        align-items: end;
        display: grid;
        flex: 1 1 0;
        gap: 2px;
        grid-template-columns: 1fr 1fr;
        height: 100%;
        max-width: 2.5rem;
        position: relative;
    }
    .gc-vis-paired-group > span {
        background: #8290a3;
        border-radius: 2px 2px 0 0;
    }
    .gc-vis-paired-group > span.is-right {
        background: #4c7dd9;
    }
    .gc-vis-paired-group small {
        bottom: -1rem;
        color: #667085;
        font-size: .682rem;
        grid-column: 1 / -1;
        left: 50%;
        position: absolute;
        transform: translateX(-50%);
    }
    .gc-vis-books {
        display: grid;
        gap: .45rem;
        max-width: 34rem;
        width: 100%;
    }
    .gc-vis-book-shelf {
        align-items: end;
        border-bottom: 3px solid #98a2b3;
        display: flex;
        gap: 2px;
        min-height: 68px;
        padding: 0 .2rem;
    }
    .gc-vis-book-shelf > span {
        align-items: center;
        background: #e7efff;
        border: 1px solid #8eb0ee;
        box-sizing: border-box;
        display: flex;
        flex-direction: column;
        justify-content: center;
        min-width: .65rem;
        position: relative;
    }
    .gc-vis-book-shelf b {
        color: #173b78;
        font-size: .682rem;
    }
    .gc-vis-book-shelf small {
        bottom: -1rem;
        color: #667085;
        font-size: .572rem;
        left: 50%;
        position: absolute;
        transform: translateX(-50%);
        white-space: nowrap;
    }
    .gc-vis-cost-stairs {
        align-items: end;
        display: flex;
        gap: .28rem;
        max-width: 32rem;
        min-height: 96px;
        width: 100%;
    }
    .gc-vis-cost-step {
        align-items: center;
        display: flex;
        flex: 1 1 0;
        flex-direction: column;
        max-width: 3.2rem;
    }
    .gc-vis-cost-step > span {
        align-items: center;
        background: #e7efff;
        border: 1px solid #8eb0ee;
        border-radius: 3px 3px 0 0;
        color: #173b78;
        display: flex;
        font-family: SFMono-Regular, Consolas, monospace;
        font-size: .748rem;
        justify-content: center;
        width: 72%;
    }
    .gc-vis-cost-step small {
        color: #667085;
        font-size: .616rem;
        margin-top: .15rem;
        white-space: nowrap;
    }
    .gc-vis-trips {
        display: grid;
        gap: .32rem;
        max-width: 32rem;
        width: 100%;
    }
    .gc-vis-trip-row {
        background: linear-gradient(#d8dee8, #d8dee8) center / 100% 2px no-repeat;
        height: 1.55rem;
        position: relative;
    }
    .gc-vis-trip-row > b {
        color: #526071;
        font-size: .682rem;
        left: 0;
        position: absolute;
        top: -.08rem;
    }
    .gc-vis-trip-row > span {
        align-items: center;
        background: #e7efff;
        border: 1px solid #8eb0ee;
        border-radius: 3px;
        box-sizing: border-box;
        color: #173b78;
        display: flex;
        font-family: SFMono-Regular, Consolas, monospace;
        font-size: .682rem;
        height: 1.15rem;
        justify-content: center;
        min-width: 3.2rem;
        position: absolute;
        top: .35rem;
        white-space: nowrap;
    }
    .gc-vis-buildings {
        border-bottom: 2px solid #98a2b3;
        height: 125px;
        max-width: 34rem;
        position: relative;
        width: 100%;
    }
    .gc-vis-buildings > span {
        background: rgba(76, 125, 217, .17);
        border: 1px solid #6f94d8;
        border-bottom: 0;
        bottom: 0;
        box-sizing: border-box;
        position: absolute;
    }
    .gc-vis-buildings small {
        color: #344054;
        font-size: .616rem;
        left: 50%;
        position: absolute;
        top: .12rem;
        transform: translateX(-50%);
    }
    .gc-vis-matrix-pair {
        align-items: center;
        display: flex;
        flex-wrap: wrap;
        gap: .7rem;
        max-width: 100%;
    }
    .gc-vis-matrix-pair > div {
        min-width: 0;
    }
    .gc-vis-matrix-pair > b {
        color: #667085;
        font-size: 1.1rem;
    }

    /* Worked examples */
    .gc-io-label {
        color: #526071 !important;
        font-size: .792rem;
        font-weight: 750;
        letter-spacing: .095em;
        text-transform: uppercase;
    }
    .gc-example-card {
        background: transparent;
        border: 0;
        border-radius: 0;
        box-shadow: none;
        box-sizing: border-box;
        margin: 0 0 1.35rem;
        overflow: visible;
        padding: .12rem 0 .25rem;
        width: 100%;
    }
    .gc-example-card.is-first {
        padding-top: 3.75rem;
    }
    .gc-example-header {
        align-items: center;
        display: flex;
        padding: 0 0 .32rem;
    }
    .gc-example-title {
        color: var(--gc-text) !important;
        font-size: 1.012rem;
        font-weight: 700;
        line-height: 1.2;
        margin: 0;
    }
    .gc-example-content {
        margin-left: 1rem;
    }
    .gc-io-grid {
        display: block;
        padding: 0;
    }
    .gc-io-panel {
        margin: 0 !important;
        min-width: 0;
        padding: 0;
    }
    .gc-io-panel + .gc-io-panel {
        margin-top: .28rem !important;
    }
    .gc-io-value {
        background: transparent !important;
        border: 0;
        border-radius: 0;
        box-sizing: border-box;
        color: #172033 !important;
        font-size: 1.001rem;
        line-height: 1.4;
        margin: .06rem 0 0 !important;
        max-width: 100%;
        min-width: 0;
        overflow-wrap: anywhere !important;
        padding: 0;
        white-space: pre-wrap !important;
        width: 100%;
        word-break: break-word !important;
    }
    .gc-io-value code {
        background: transparent !important;
        color: #172033 !important;
        font-family: SFMono-Regular, Consolas, "Liberation Mono", monospace;
        font-size: inherit !important;
        overflow-wrap: anywhere !important;
        padding: 0;
        white-space: inherit !important;
        word-break: inherit !important;
    }
    .gc-explanation {
        background: transparent;
        border: 0;
        border-radius: 0;
        margin: .28rem 0 0;
        min-width: 0;
        padding: 0;
        width: 100%;
    }
    .gc-explanation-body {
        display: grid;
        gap: .34rem;
        margin: .08rem 0 0;
        min-width: 0;
        width: 100%;
    }
    .gc-explanation-line {
        color: #172033 !important;
        font-size: 1.001rem;
        line-height: 1.48;
        min-width: 0;
        overflow-wrap: anywhere;
        white-space: normal;
        word-break: normal;
    }
    .gc-explanation-line.is-bullet {
        padding-left: 1rem;
        position: relative;
    }
    .gc-explanation-line.is-bullet::before {
        color: #526071;
        content: "•";
        left: .1rem;
        position: absolute;
        top: 0;
    }
    .gc-explanation code,
    .gc-explanation-token {
        -webkit-box-decoration-break: clone;
        background: var(--gc-code-bg) !important;
        border-radius: 4px;
        box-decoration-break: clone;
        color: #172033 !important;
        font-family: SFMono-Regular, Consolas, "Liberation Mono", monospace;
        font-size: .946em;
        overflow-wrap: anywhere;
        padding: .08rem .28rem;
        white-space: pre-wrap;
        word-break: break-word;
    }
    .gc-explanation-trace {
        border: 1px solid #e1e7f0;
        border-radius: 10px;
        display: grid;
        margin-top: .14rem;
        max-width: 100%;
        min-width: 0;
        overflow: hidden;
        width: min(100%, 46rem);
    }
    .gc-explanation-trace-row {
        align-items: start;
        display: grid;
        gap: .7rem;
        grid-template-columns: minmax(0, 1fr) minmax(4.5rem, auto);
        min-width: 0;
        padding: .52rem .65rem;
    }
    .gc-explanation-trace-row + .gc-explanation-trace-row {
        border-top: 1px solid #e6ebf2;
    }
    .gc-explanation-trace-row.is-header {
        background: #f7f9fc;
        color: #526071 !important;
        font-size: .748rem;
        font-weight: 750;
        letter-spacing: .075em;
        text-transform: uppercase;
    }
    .gc-explanation-trace-window,
    .gc-explanation-trace-result {
        min-width: 0;
    }
    .gc-explanation-trace-result {
        text-align: right;
    }
    @media (max-width: 650px) {
        .gc-explanation-trace-row {
            grid-template-columns: minmax(0, 1fr);
        }
        .gc-explanation-trace-result {
            text-align: left;
        }
    }

    /* Constraints and output rules */
    .gc-constraints {
        margin: .45rem 0 .2rem;
    }
    .gc-constraints-title {
        color: var(--gc-text) !important;
        font-size: 1.32rem;
        font-weight: 700;
        line-height: 1.25;
        margin: .12rem 0 .4rem;
    }
    .gc-constraint-list {
        list-style: disc;
        margin: 0;
        padding-left: 1.25rem;
    }
    .gc-constraint-item {
        color: #344054 !important;
        display: list-item;
        font-size: 1.001rem;
        line-height: 1.4;
        margin: 0 0 .3rem;
        padding-left: .15rem;
    }
    .gc-constraint-number,
    .gc-constraint-operator,
    .gc-constraint-code {
        border: 1px solid;
        border-radius: 5px;
        display: inline-block;
        font-family: SFMono-Regular, Consolas, "Liberation Mono", monospace;
        font-size: .935em;
        font-weight: 650;
        line-height: 1.35;
        margin: 0 .05rem;
        padding: .08rem .32rem;
    }
    .gc-constraint-number {
        background: #eff6ff;
        border-color: #bfdbfe;
        color: #1d4ed8 !important;
    }
    .gc-constraint-operator {
        background: #f4f3ff;
        border-color: #d9d6fe;
        color: #5925dc !important;
    }
    .gc-constraint-code {
        background: #ecfdf3;
        border-color: #abefc6;
        color: #05603a !important;
    }

    /* Folded topics and separately leveled hints after the constraints */
    .gc-after-constraints-space {
        display: block;
        width: 100%;
    }
    .gc-after-constraints-space .gc-gap-line {
        display: block;
        height: 1.45rem;
        line-height: 1.45rem;
        width: 100%;
    }
    .gc-topic-list {
        align-items: center;
        display: flex;
        flex-wrap: wrap;
        gap: .42rem;
        padding: .16rem 0 .35rem;
    }
    .gc-topic-pill {
        align-items: center;
        background: transparent;
        border: 1px solid #b8c3d4;
        border-radius: 999px;
        color: #344054 !important;
        display: inline-flex;
        font-size: .836rem;
        font-weight: 700;
        line-height: 1.2;
        padding: .2rem .52rem;
    }
    .gc-hint-body {
        color: #344054 !important;
        font-size: 1.001rem;
        line-height: 1.5;
        margin: .04rem 0 .28rem;
    }
    .gc-hint-body code {
        background: #f3f4f6 !important;
        border: 1px solid #e1e5eb;
        border-radius: 4px;
        color: #172033 !important;
        font-size: .946em;
        padding: .06rem .25rem;
    }

    /* Compact problem picker */
    [data-testid="stVerticalBlock"][class*="st-key-problem_picker_bar"] {
        gap: 0 !important;
        max-width: 44rem;
        padding: 0 !important;
    }
    [data-testid="stElementContainer"]:has(
        > [data-testid="stVerticalBlock"][class*="st-key-problem_picker_bar"]
    ) {
        margin-bottom: -.7rem !important;
    }
    [data-testid="stHorizontalBlock"]:has(.gc-problem-picker-label) {
        align-items: center !important;
        gap: .55rem !important;
        margin: 0 !important;
        min-height: 2rem !important;
    }
    [data-testid="stHorizontalBlock"]:has(.gc-problem-picker-label)
    > [data-testid="stColumn"] {
        background: transparent !important;
        border: 0 !important;
        min-width: 0 !important;
        padding: 0 !important;
    }
    [data-testid="stHorizontalBlock"]:has(.gc-problem-picker-label)
    > [data-testid="stColumn"]:has(.gc-problem-picker-label)
    > [data-testid="stVerticalBlock"],
    [data-testid="stElementContainer"]:has(.gc-problem-picker-label) {
        align-items: center !important;
        display: flex !important;
        height: 2rem !important;
        justify-content: flex-start !important;
        min-height: 2rem !important;
    }
    .gc-problem-picker-label {
        align-items: center;
        box-sizing: border-box;
        color: #344054;
        display: flex;
        font-size: .88rem;
        font-weight: 700;
        height: 2rem;
        line-height: 1;
        margin: 0;
        padding-left: 3rem;
        transform: translateY(-.45rem);
        white-space: nowrap;
    }
    [data-testid="stHorizontalBlock"]:has(.gc-problem-picker-label)
    [data-testid="stSelectbox"] {
        margin: 0 !important;
    }
    [data-testid="stHorizontalBlock"]:has(.gc-problem-picker-label)
    .react-aria-ComboBox,
    [data-testid="stHorizontalBlock"]:has(.gc-problem-picker-label)
    .react-aria-ComboBox > [role="group"] {
        height: 2rem !important;
        min-height: 2rem !important;
    }
    [data-testid="stHorizontalBlock"]:has(.gc-problem-picker-label)
    .react-aria-ComboBox input[role="combobox"] {
        font-size: .88rem !important;
        height: 1.9rem !important;
        min-height: 0 !important;
        padding: .25rem .45rem !important;
    }
    [data-testid="stHorizontalBlock"]:has(.gc-problem-picker-label)
    .react-aria-ComboBox button[aria-label="Open"] {
        height: 1.9rem !important;
        min-height: 0 !important;
        padding: 0 .3rem !important;
        width: 1.65rem !important;
    }

    /* LeetCode-style split solve workspace */
    [data-testid="stHorizontalBlock"]:has(.gc-problem-pane-marker):has(.gc-code-pane-marker) {
        align-items: stretch;
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 0 !important;
        min-width: 0 !important;
        overflow: hidden !important;
        width: 100% !important;
    }
    [data-testid="stHorizontalBlock"]:has(.gc-problem-pane-marker):has(.gc-code-pane-marker)
    > [data-testid="stColumn"] {
        background: #ffffff;
        border: 0;
        border-radius: 0;
        box-shadow: none;
        min-width: 0;
        overflow-x: hidden;
        padding: 0 .75rem .75rem;
    }
    [data-testid="stHorizontalBlock"]:has(.gc-problem-pane-marker):has(.gc-code-pane-marker)
    > [data-testid="stColumn"]:has(.gc-column-resizer-marker) {
        background: #e7eaf0;
        flex: 0 0 12px !important;
        max-width: 12px !important;
        min-width: 12px !important;
        overflow: hidden !important;
        padding: 0 !important;
        width: 12px !important;
    }
    [data-testid="stColumn"]:has(.gc-column-resizer-marker)
    > [data-testid="stVerticalBlock"] {
        gap: 0 !important;
        height: 100%;
        padding: 0 !important;
    }
    .gc-column-resizer-marker {
        height: 0;
        margin: 0;
        width: 0;
    }
    .gc-pane-bar {
        align-items: center;
        background: rgba(255, 255, 255, .97);
        box-sizing: border-box;
        display: flex;
        height: 2.35rem;
        justify-content: space-between;
        margin: 0 -.75rem .55rem;
        padding: 0 .75rem;
        position: sticky;
        top: 0;
        z-index: 5;
    }
    .gc-pane-bar::after {
        background: #dbe3ef;
        bottom: 0;
        content: "";
        height: 1px;
        left: .75rem;
        position: absolute;
        right: .75rem;
    }
    .gc-pane-title {
        color: #172033 !important;
        font-size: .946rem;
        font-weight: 750;
        line-height: 1;
    }
    [data-testid="stHorizontalBlock"]:has(.gc-code-bar-marker):not(:has(.gc-problem-pane-marker)),
    [data-testid="stHorizontalBlock"]:has(.gc-problem-bar-marker):not(:has(.gc-code-pane-marker)) {
        align-items: center;
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        background: rgba(255, 255, 255, .97);
        box-sizing: border-box;
        gap: 0 !important;
        height: 2.35rem !important;
        min-height: 2.35rem !important;
        margin: 0 -.75rem .2rem;
        padding: 0 .45rem 0 .75rem;
        position: sticky;
        top: 0;
        z-index: 5;
    }
    [data-testid="stHorizontalBlock"]:has(.gc-code-bar-marker):not(:has(.gc-problem-pane-marker))::after,
    [data-testid="stHorizontalBlock"]:has(.gc-problem-bar-marker):not(:has(.gc-code-pane-marker))::after {
        background: #cbd5e1;
        bottom: 0;
        content: "";
        height: 1px;
        left: .75rem;
        position: absolute;
        right: .45rem;
    }
    [data-testid="stHorizontalBlock"]:has(.gc-code-bar-marker):not(:has(.gc-problem-pane-marker))
    > [data-testid="stColumn"],
    [data-testid="stHorizontalBlock"]:has(.gc-problem-bar-marker):not(:has(.gc-code-pane-marker))
    > [data-testid="stColumn"] {
        background: transparent !important;
        border: 0 !important;
        border-radius: 0 !important;
        box-shadow: none !important;
        min-height: 0 !important;
        overflow: visible !important;
        padding: 0 !important;
    }
    [data-testid="stHorizontalBlock"]:has(.gc-code-bar-marker):not(:has(.gc-problem-pane-marker))
    > [data-testid="stColumn"]:has(.gc-code-bar-marker) {
        flex: 1 1 auto !important;
        max-width: none !important;
        min-width: 0 !important;
        width: auto !important;
    }
    [data-testid="stHorizontalBlock"]:has(.gc-code-bar-marker):not(:has(.gc-problem-pane-marker))
    > [data-testid="stColumn"]:has([data-testid="stSelectbox"]) {
        flex: 0 0 7.75rem !important;
        max-width: 7.75rem !important;
        min-width: 7.75rem !important;
        width: 7.75rem !important;
    }
    .gc-code-bar-marker,
    .gc-problem-bar-marker {
        align-items: center;
        display: flex;
        height: 2.35rem;
    }
    .gc-code-bar-marker .gc-pane-title {
        transform: translateY(-3px);
    }
    .gc-problem-bar-spacer {
        height: 1.65rem;
    }
    .gc-problem-pane-anchor {
        display: none;
    }
    [data-testid="stElementContainer"]:has(.gc-problem-pane-anchor) {
        height: 0 !important;
        margin: 0 !important;
        min-height: 0 !important;
        padding: 0 !important;
    }
    [data-testid="stHorizontalBlock"]:has(.gc-code-bar-marker):not(:has(.gc-problem-pane-marker))
    [data-testid="stSelectbox"] {
        margin: 0 0 0 auto;
        max-width: 7.75rem;
        width: 100%;
    }
    [data-testid="stHorizontalBlock"]:has(.gc-code-bar-marker):not(:has(.gc-problem-pane-marker))
    .react-aria-ComboBox,
    [data-testid="stHorizontalBlock"]:has(.gc-code-bar-marker):not(:has(.gc-problem-pane-marker))
    .react-aria-ComboBox > [role="group"] {
        background: #f8fafc !important;
        border: 1px solid #d0d5dd !important;
        border-radius: 5px !important;
        box-shadow: none !important;
        font-size: .858rem !important;
        height: 1.65rem !important;
        min-height: 1.65rem !important;
    }
    [data-testid="stHorizontalBlock"]:has(.gc-code-bar-marker):not(:has(.gc-problem-pane-marker))
    .react-aria-ComboBox > [role="group"] {
        overflow: hidden;
    }
    [data-testid="stHorizontalBlock"]:has(.gc-code-bar-marker):not(:has(.gc-problem-pane-marker))
    .react-aria-ComboBox input[role="combobox"] {
        font-size: .858rem !important;
        height: 1.55rem !important;
        min-height: 0 !important;
        padding: .2rem .38rem !important;
    }
    [data-testid="stHorizontalBlock"]:has(.gc-code-bar-marker):not(:has(.gc-problem-pane-marker))
    .react-aria-ComboBox button[aria-label="Open"] {
        height: 1.55rem !important;
        min-height: 0 !important;
        padding: 0 .28rem !important;
        width: 1.45rem !important;
    }
    [data-testid="stHorizontalBlock"]:has(.gc-code-bar-marker):not(:has(.gc-problem-pane-marker))
    .react-aria-ComboBox button[aria-label="Open"] svg {
        height: .72rem !important;
        width: .72rem !important;
    }
    [data-testid="stVerticalBlockBorderWrapper"]:has(.gc-judge-panel-marker),
    [data-testid="stLayoutWrapper"]:has(
        > [data-testid="stVerticalBlock"][class*="st-key-judge_panel--"]
    ) {
        background: transparent !important;
        border: 0 !important;
        border-radius: 0 !important;
        box-shadow: none !important;
        margin-top: 0;
        padding: 0 !important;
    }
    [data-testid="stVerticalBlockBorderWrapper"]:has(.gc-judge-panel-marker)
    > [data-testid="stVerticalBlock"],
    [data-testid="stVerticalBlock"][class*="st-key-judge_panel--"] {
        gap: .25rem !important;
        padding: 0 !important;
    }
    [data-testid="stColumn"]:has(.gc-code-pane-marker):not(:has(.gc-problem-pane-marker))
    > [data-testid="stVerticalBlock"] {
        gap: 0 !important;
        height: 100% !important;
        min-height: 0 !important;
        overflow: hidden !important;
    }
    [data-testid="stColumn"]:has(.gc-code-pane-marker):not(:has(.gc-problem-pane-marker))
    > [data-testid="stVerticalBlock"] > [data-testid="stElementContainer"] {
        min-height: 0 !important;
    }
    .gc-judge-panel-marker {
        height: 0;
        margin: 0;
    }
    [data-testid="stVerticalBlock"][class*="st-key-resize_handle--"] {
        gap: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    [data-testid="stElementContainer"]:has(
        [data-testid="stVerticalBlock"][class*="st-key-resize_handle--"]
    ) {
        margin-left: -.75rem !important;
        margin-right: -.75rem !important;
        width: auto !important;
    }
    [data-testid="stVerticalBlock"][class*="st-key-resize_handle--"] iframe {
        display: block;
        margin: 0 !important;
        width: 100% !important;
    }
    [data-testid="stVerticalBlock"][class*="st-key-testcase_region--"] {
        display: flex !important;
        flex-direction: column !important;
        gap: .25rem !important;
        min-height: 0 !important;
        overflow: hidden !important;
        padding: .35rem 0 0 !important;
    }
    [data-testid="stVerticalBlock"][class*="st-key-testcase_region--"]
    > [data-testid="stElementContainer"]:has(.gc-judge-panel-marker) {
        flex: 0 0 auto !important;
        min-height: 0 !important;
        overflow: visible !important;
    }
    [data-testid="stVerticalBlock"][class*="st-key-testcase_region--"]
    > [data-testid="stElementContainer"]:has(.gc-console-actions-marker) {
        flex: 0 0 auto !important;
    }
    [data-testid="stVerticalBlock"][class*="st-key-testcase_region--"]
    [data-testid="stVerticalBlock"][class*="st-key-judge_panel--"] {
        height: auto !important;
        min-height: 0 !important;
        overflow: visible !important;
    }
    [data-testid="stVerticalBlock"][class*="st-key-testcase_region--"].gc-console-collapsed {
        gap: 0 !important;
        padding-top: .2rem !important;
    }
    [data-testid="stVerticalBlock"][class*="st-key-testcase_region--"].gc-console-collapsed
    > [data-testid="stElementContainer"]:has(.gc-judge-panel-marker) {
        display: none !important;
    }
    [data-testid="stVerticalBlock"][class*="st-key-testcase_region--"].gc-console-overflow
    > [data-testid="stElementContainer"]:has(.gc-judge-panel-marker) {
        flex: 1 1 auto !important;
        overflow: hidden !important;
    }
    [data-testid="stVerticalBlock"][class*="st-key-testcase_region--"].gc-console-overflow
    [data-testid="stVerticalBlock"][class*="st-key-judge_panel--"] {
        height: 100% !important;
        overflow-y: auto !important;
        overscroll-behavior: contain;
        scrollbar-gutter: stable;
    }
    .gc-console-empty {
        color: #667085 !important;
        font-size: .902rem;
        padding: .65rem .1rem;
    }
    [data-testid="stVerticalBlock"][class*="st-key-judge_panel--"]
    [data-testid="stCodeBlock"] {
        margin: 0 0 .32rem !important;
    }
    [data-testid="stVerticalBlock"][class*="st-key-judge_panel--"]
    [data-testid="stCodeBlock"] pre {
        background: #f7f7f8 !important;
        border: 0 !important;
        border-radius: 5px !important;
        color: #172033 !important;
        font-size: .88rem !important;
        line-height: 1.35 !important;
        min-height: 2.1rem;
        padding: .38rem .5rem !important;
        white-space: pre-wrap !important;
    }
    [data-testid="stVerticalBlock"][class*="st-key-judge_panel--"]
    [data-testid="stCodeBlock"] button {
        display: none !important;
    }
    .gc-console-status {
        align-items: baseline;
        display: flex;
        flex-wrap: wrap;
        gap: .2rem .45rem;
        line-height: 1.3;
        margin: .15rem 0 0;
        min-height: 1.55rem;
        padding-bottom: .55rem;
    }
    [data-testid="stElementContainer"]:has(.gc-console-status) {
        margin-bottom: .12rem !important;
    }
    .gc-console-status strong {
        font-size: 1.034rem;
        line-height: 1.3;
    }
    .gc-console-status.is-pass strong {
        color: #16803a !important;
    }
    .gc-console-status.is-fail strong {
        color: #d92d20 !important;
    }
    .gc-console-status span {
        color: #667085 !important;
        font-size: .836rem;
    }
    .gc-console-error {
        background: #fef3f2;
        border-radius: 5px;
        color: #b42318 !important;
        font-family: SFMono-Regular, Consolas, "Liberation Mono", monospace;
        font-size: .836rem;
        margin-top: .4rem;
        padding: .5rem .55rem;
        white-space: pre-wrap;
    }
    [data-testid="stHorizontalBlock"]:has(.gc-console-actions-marker):not(:has(.gc-code-pane-marker))
    > [data-testid="stColumn"]:has(.gc-run-action-marker) button {
        background: #f2f3f5 !important;
        border-color: #d0d5dd !important;
        color: #344054 !important;
        font-size: .88rem !important;
        height: 2.25rem !important;
        min-height: 2.25rem !important;
        padding: 0 .5rem !important;
    }
    [data-testid="stHorizontalBlock"]:has(.gc-console-actions-marker):not(:has(.gc-code-pane-marker))
    > [data-testid="stColumn"]:has(.gc-submit-action-marker) button {
        background: #2cbb5d !important;
        border-color: #2cbb5d !important;
        color: #ffffff !important;
        font-size: .88rem !important;
        height: 2.25rem !important;
        min-height: 2.25rem !important;
        padding: 0 .5rem !important;
        white-space: nowrap !important;
    }
    [data-testid="stHorizontalBlock"]:has(.gc-console-actions-marker):not(:has(.gc-code-pane-marker))
    > [data-testid="stColumn"] button:disabled {
        background: #f2f3f5 !important;
        border-color: #d0d5dd !important;
        color: #98a2b3 !important;
        cursor: not-allowed !important;
        opacity: 1 !important;
    }
    [data-testid="stHorizontalBlock"]:has(.gc-console-actions-marker):not(:has(.gc-code-pane-marker))
    > [data-testid="stColumn"] button:disabled * {
        color: #98a2b3 !important;
        fill: #98a2b3 !important;
    }
    [data-testid="stHorizontalBlock"]:has(.gc-console-actions-marker):not(:has(.gc-code-pane-marker)) {
        align-items: center;
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        background: #ffffff;
        gap: .4rem !important;
        margin-top: 0;
        position: relative;
        z-index: 2;
    }
    [data-testid="stHorizontalBlock"]:has(.gc-console-actions-marker):not(:has(.gc-code-pane-marker))
    > [data-testid="stColumn"] > [data-testid="stVerticalBlock"] {
        gap: 0 !important;
    }
    .gc-console-actions-marker,
    .gc-run-action-marker,
    .gc-submit-action-marker {
        height: 0;
        margin: 0;
    }
    .gc-code-intro {
        margin: .1rem 0 .75rem;
    }
    .gc-code-intro-title {
        color: var(--gc-text) !important;
        font-size: 1.232rem;
        font-weight: 720;
        margin: 0 0 .18rem;
    }
    .gc-code-intro-copy {
        color: var(--gc-muted) !important;
        font-size: .924rem;
        line-height: 1.45;
        margin: 0;
    }

    .gc-tool-kicker,
    .gc-coach-kicker {
        color: #93370d !important;
        font-size: .748rem;
        font-weight: 780;
        letter-spacing: .09em;
        text-transform: uppercase;
    }
    .gc-tool-heading {
        margin: 0 0 .7rem;
    }
    .gc-tool-kicker {
        color: #1d4ed8 !important;
    }
    .gc-tool-title {
        color: #172033 !important;
        font-size: 1.1rem;
        font-weight: 720;
        margin: .1rem 0 .16rem;
    }
    .gc-tool-copy {
        color: #526071 !important;
        font-size: .88rem;
        line-height: 1.45;
        margin: 0;
    }
    .gc-plan-progress {
        align-items: center;
        display: flex;
        gap: .55rem;
        margin: 0 0 .65rem;
    }
    .gc-plan-count {
        color: #344054 !important;
        font-size: .825rem;
        font-weight: 700;
        white-space: nowrap;
    }
    .gc-attempt-coach {
        border: 1px solid #dbeafe;
        border-radius: 10px;
        margin: .85rem 0;
        overflow: hidden;
    }
    .gc-coach-head {
        background: #eff6ff;
        border-bottom: 1px solid #dbeafe;
        padding: .72rem .82rem;
    }
    .gc-coach-head.is-success {
        background: #ecfdf3;
        border-color: #abefc6;
    }
    .gc-coach-head.is-success .gc-coach-kicker {
        color: #067647 !important;
    }
    .gc-coach-title {
        color: #172033 !important;
        font-size: 1.1rem;
        font-weight: 730;
        margin: .12rem 0 0;
    }
    .gc-coach-body {
        background: #ffffff;
        color: #344054 !important;
        font-size: .924rem;
        line-height: 1.5;
        padding: .78rem .82rem;
    }
    .gc-coach-body p {
        color: #344054 !important;
        margin: 0 0 .55rem;
    }
    .gc-coach-body p:last-child {
        margin-bottom: 0;
    }
    .gc-coach-case {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 7px;
        font-family: SFMono-Regular, Consolas, "Liberation Mono", monospace;
        font-size: .825rem;
        margin-top: .55rem;
        overflow-wrap: anywhere;
        padding: .58rem .65rem;
        white-space: pre-wrap;
    }
    .gc-mode-badge {
        border: 1px solid #abefc6;
        border-radius: 999px;
        color: #05603a !important;
        display: inline-block;
        font-size: .77rem;
        font-weight: 750;
        margin-top: .35rem;
        padding: .18rem .48rem;
    }
    [data-testid="stHorizontalBlock"]:has(.gc-problem-pane-marker):has(.gc-code-pane-marker)
    > [data-testid="stColumn"] {
        box-sizing: border-box;
        height: calc(100dvh - 1.1rem);
        max-height: calc(100dvh - 1.1rem);
        min-height: 0;
    }
    [data-testid="stHorizontalBlock"]:has(.gc-problem-pane-marker):has(.gc-code-pane-marker)
    > [data-testid="stColumn"]:has(.gc-problem-pane-marker):not(:has(.gc-code-pane-marker)) {
        overflow: hidden !important;
    }
    [data-testid="stVerticalBlock"][class*="st-key-problem_scroll--"] {
        height: 100% !important;
        max-height: 100% !important;
        min-height: 0 !important;
        overflow-y: auto !important;
        overscroll-behavior-y: contain;
        scroll-padding-bottom: 1.5rem;
        scrollbar-color: #cbd5e1 transparent;
        scrollbar-gutter: stable;
        scrollbar-width: thin;
        -webkit-overflow-scrolling: touch;
    }
    [data-testid="stHorizontalBlock"]:has(.gc-problem-pane-marker):has(.gc-code-pane-marker)
    > [data-testid="stColumn"]:has(.gc-code-pane-marker):not(:has(.gc-problem-pane-marker)),
    [data-testid="stHorizontalBlock"]:has(.gc-problem-pane-marker):has(.gc-code-pane-marker)
    > [data-testid="stColumn"]:has(.gc-column-resizer-marker) {
        overflow: hidden !important;
    }
    .gc-problem-pane-end {
        height: 1.25rem;
        width: 100%;
    }
    @media (max-width: 900px) {
        /* Browser zoom reduces the CSS viewport width. Keep the solve workspace
           as a two-pane IDE instead of activating Streamlit's stacked layout. */
        [data-testid="stHorizontalBlock"]:has(.gc-problem-pane-marker):has(.gc-code-pane-marker) {
            display: flex !important;
            flex-direction: row !important;
            flex-wrap: nowrap !important;
            min-width: 0 !important;
            overflow: hidden !important;
            width: 100% !important;
        }
        [data-testid="stHorizontalBlock"]:has(.gc-problem-pane-marker):has(.gc-code-pane-marker)
        > [data-testid="stColumn"]:has(.gc-problem-pane-marker):not(:has(.gc-code-pane-marker)) {
            flex: 1 1 0 !important;
            max-width: none !important;
            min-width: 0 !important;
            width: 0 !important;
        }
        [data-testid="stHorizontalBlock"]:has(.gc-problem-pane-marker):has(.gc-code-pane-marker)
        > [data-testid="stColumn"]:has(.gc-column-resizer-marker) {
            display: block !important;
            flex: 0 0 12px !important;
            max-width: 12px !important;
            min-width: 12px !important;
            width: 12px !important;
        }
        [data-testid="stHorizontalBlock"]:has(.gc-problem-pane-marker):has(.gc-code-pane-marker)
        > [data-testid="stColumn"]:has(.gc-code-pane-marker):not(:has(.gc-problem-pane-marker)) {
            flex: 1.08 1 0 !important;
            max-width: none !important;
            min-width: 0 !important;
            width: 0 !important;
        }
        [data-testid="stHorizontalBlock"]:has(.gc-code-bar-marker):not(:has(.gc-problem-pane-marker)),
        [data-testid="stHorizontalBlock"]:has(.gc-console-actions-marker):not(:has(.gc-code-pane-marker)) {
            display: flex !important;
            flex-direction: row !important;
            flex-wrap: nowrap !important;
        }
    }
    @media (max-width: 700px) {
        .block-container {
            padding-top: .55rem !important;
        }
        .gc-example-header {
            align-items: flex-start;
        }
    }

    /* Cards, metrics, expanders, bordered containers */
    div[data-testid="stMetric"],
    div[data-testid="stVerticalBlockBorderWrapper"],
    details[data-testid="stExpander"] {
        background: var(--gc-surface) !important;
        border-color: var(--gc-border) !important;
        color: var(--gc-text) !important;
    }
    div[data-testid="stMetric"] {
        border: 1px solid var(--gc-border);
        padding: .9rem;
        border-radius: 14px;
        box-shadow: 0 4px 16px rgba(15, 23, 42, 0.035);
    }
    details[data-testid="stExpander"] summary,
    details[data-testid="stExpander"] summary p,
    details[data-testid="stExpander"] svg {
        color: var(--gc-text) !important;
        fill: var(--gc-text) !important;
    }
    [data-testid="stMain"] h3 {
        font-size: 1.32rem !important;
        font-weight: 700 !important;
        line-height: 1.25 !important;
    }
    [data-testid="stMain"] details[data-testid="stExpander"] summary p {
        font-size: 1.045rem !important;
        font-weight: 600 !important;
        line-height: 1.25 !important;
    }
    [data-testid="stMain"] details[data-testid="stExpander"] {
        background: transparent !important;
        border: 0 !important;
        border-bottom: 1px solid #e5eaf1 !important;
        border-radius: 0 !important;
        box-shadow: none !important;
    }
    [data-testid="stMain"] details[data-testid="stExpander"] summary {
        min-height: 0;
        padding: .5rem 0 !important;
    }
    [data-testid="stColumn"]:has(.gc-problem-pane-marker)
    [data-testid="stVerticalBlock"] {
        gap: .4rem;
    }
    [data-testid="stColumn"]:has(.gc-problem-pane-marker)
    [data-testid="stMarkdownContainer"] > p {
        line-height: 1.42;
        margin-bottom: .4rem;
    }
    .gc-before-predict {
        height: .8rem;
    }

    /* Inputs and selectors */
    input, textarea,
    div[data-baseweb="input"] > div,
    div[data-baseweb="textarea"] > div,
    div[data-baseweb="select"] > div,
    div[data-baseweb="base-input"],
    [data-testid="stTextInput"] input,
    [data-testid="stTextArea"] textarea {
        background: #ffffff !important;
        color: var(--gc-text) !important;
        -webkit-text-fill-color: var(--gc-text) !important;
        border-color: #cbd5e1 !important;
    }
    input::placeholder, textarea::placeholder {
        color: #64748b !important;
        opacity: 1 !important;
        -webkit-text-fill-color: #64748b !important;
    }
    input:disabled, textarea:disabled,
    [aria-disabled="true"] input, [aria-disabled="true"] textarea {
        background: var(--gc-disabled-bg) !important;
        color: var(--gc-disabled-text) !important;
        -webkit-text-fill-color: var(--gc-disabled-text) !important;
        opacity: 1 !important;
    }
    /* Problem-library search, select, multiselect, and dropdown popovers */
    [data-testid="stTextInputRootElement"],
    [data-testid="stTextInputRootElement"] > div,
    div[data-baseweb="input"],
    div[data-baseweb="input"] > div,
    div[data-baseweb="base-input"],
    [data-testid="stSelectbox"] div[data-baseweb="select"],
    [data-testid="stSelectbox"] div[data-baseweb="select"] > div,
    [data-testid="stSelectbox"] div[data-baseweb="select"] > div > div,
    [data-testid="stMultiSelect"] div[data-baseweb="select"],
    [data-testid="stMultiSelect"] div[data-baseweb="select"] > div,
    [data-testid="stMultiSelect"] div[data-baseweb="select"] > div > div,
    div[data-baseweb="select"],
    div[data-baseweb="select"] > div,
    div[data-baseweb="select"] > div > div {
        background: #ffffff !important;
        border-color: #b8c3d4 !important;
        color: var(--gc-text) !important;
        box-shadow: none !important;
    }
    [data-testid="stTextInputRootElement"]:focus-within,
    [data-testid="stSelectbox"] div[data-baseweb="select"] > div:focus-within,
    [data-testid="stMultiSelect"] div[data-baseweb="select"] > div:focus-within,
    div[data-baseweb="select"] > div:focus-within {
        border-color: var(--gc-accent) !important;
        box-shadow: 0 0 0 1px var(--gc-accent) !important;
    }
    [data-testid="stTextInput"] input,
    [data-testid="stSelectbox"] input,
    [data-testid="stMultiSelect"] input,
    div[data-baseweb="select"] input {
        background: transparent !important;
        color: var(--gc-text) !important;
        -webkit-text-fill-color: var(--gc-text) !important;
        caret-color: var(--gc-text) !important;
    }
    [data-testid="stSelectbox"] div[data-baseweb="select"] *,
    [data-testid="stMultiSelect"] div[data-baseweb="select"] *,
    div[data-baseweb="select"] span,
    div[data-baseweb="select"] svg {
        color: var(--gc-text) !important;
        fill: var(--gc-text) !important;
    }
    [data-testid="stMultiSelect"] span[data-baseweb="tag"],
    span[data-baseweb="tag"] {
        background: #e8f0ff !important;
        border: 1px solid #bfd3ff !important;
        color: #173b7a !important;
    }
    [data-testid="stMultiSelect"] span[data-baseweb="tag"] span,
    [data-testid="stMultiSelect"] span[data-baseweb="tag"] svg,
    span[data-baseweb="tag"] span,
    span[data-baseweb="tag"] svg {
        color: #173b7a !important;
        fill: #173b7a !important;
    }
    /* BaseWeb renders dropdown menus in a body-level portal, outside .stApp. */
    body > div[data-baseweb="popover"],
    div[data-baseweb="popover"],
    div[data-baseweb="popover"] > div,
    div[data-baseweb="popover"] [data-baseweb="menu"],
    div[data-baseweb="menu"],
    div[data-baseweb="menu"] > ul,
    ul[role="listbox"],
    [data-testid*="VirtualDropdown"] {
        background: #ffffff !important;
        background-color: #ffffff !important;
        color: var(--gc-text) !important;
        border-color: var(--gc-border) !important;
        box-shadow: 0 10px 30px rgba(15, 23, 42, 0.14) !important;
        color-scheme: light !important;
    }
    [data-testid*="VirtualDropdown"] > div,
    [data-testid*="VirtualDropdown"] ul,
    [data-testid*="VirtualDropdown"] li,
    [data-baseweb="menu"] ul,
    [data-baseweb="menu"] li,
    [role="listbox"] li,
    [role="option"] {
        background: #ffffff !important;
        background-color: #ffffff !important;
        color: var(--gc-text) !important;
        -webkit-text-fill-color: var(--gc-text) !important;
    }
    [data-testid*="VirtualDropdown"] span,
    [data-testid*="VirtualDropdown"] p,
    [data-baseweb="menu"] span,
    [data-baseweb="menu"] p,
    [role="option"] *,
    [role="listbox"] li * {
        color: var(--gc-text) !important;
        -webkit-text-fill-color: var(--gc-text) !important;
    }
    [data-testid*="VirtualDropdown"] li:hover,
    [data-testid*="VirtualDropdown"] li[aria-selected="true"],
    [data-baseweb="menu"] li:hover,
    [data-baseweb="menu"] li[aria-selected="true"],
    [role="option"]:hover,
    [role="option"][aria-selected="true"] {
        background: var(--gc-accent-soft) !important;
        background-color: var(--gc-accent-soft) !important;
        color: #163d7a !important;
    }

    /* Buttons */
    .stButton > button,
    .stDownloadButton > button {
        background: #ffffff !important;
        color: #172033 !important;
        border-color: #cbd5e1 !important;
    }
    .stButton > button:hover,
    .stDownloadButton > button:hover {
        background: #f8fafc !important;
        color: #111827 !important;
        border-color: #94a3b8 !important;
    }
    .stButton > button[kind="primary"] {
        background: var(--gc-accent) !important;
        color: #ffffff !important;
        border-color: var(--gc-accent) !important;
    }
    .stButton > button[kind="primary"] p,
    .stButton > button[kind="primary"] span,
    .stButton > button[kind="primary"] svg {
        color: #ffffff !important;
        fill: #ffffff !important;
    }
    .stButton > button[kind="primary"]:hover {
        background: var(--gc-accent-dark) !important;
        color: #ffffff !important;
        border-color: var(--gc-accent-dark) !important;
    }
    .stButton > button:disabled,
    .stDownloadButton > button:disabled {
        background: var(--gc-disabled-bg) !important;
        border-color: #cbd5e1 !important;
        color: var(--gc-disabled-text) !important;
        opacity: 1 !important;
    }
    .stButton > button:disabled *,
    .stDownloadButton > button:disabled * {
        color: var(--gc-disabled-text) !important;
        fill: var(--gc-disabled-text) !important;
        opacity: 1 !important;
    }
    .stButton > button[kind="primary"]:disabled {
        background: #dbeafe !important;
        border-color: #bfdbfe !important;
        color: #1e3a8a !important;
    }
    .stButton > button[kind="primary"]:disabled * {
        color: #1e3a8a !important;
        fill: #1e3a8a !important;
    }
    button:focus-visible, input:focus-visible, textarea:focus-visible,
    [role="tab"]:focus-visible, [role="radio"]:focus-visible {
        outline: 3px solid #93c5fd !important;
        outline-offset: 2px !important;
    }

    /* Tabs and radio navigation */
    button[data-baseweb="tab"] {
        color: #475569 !important;
        background: transparent !important;
    }
    button[data-baseweb="tab"] *,
    button[data-baseweb="tab"] p {
        color: inherit !important;
    }
    button[data-baseweb="tab"]:hover {
        background: #f8fafc !important;
        color: #1e3a8a !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: var(--gc-accent-dark) !important;
    }
    [data-testid="stSidebar"] [role="radiogroup"] label {
        color: var(--gc-text) !important;
    }

    /* Alerts */
    [data-testid="stAlert"] {
        color: var(--gc-text) !important;
    }
    [data-testid="stAlert"] p,
    [data-testid="stAlert"] li,
    [data-testid="stAlert"] span {
        color: #172033 !important;
    }

    /* Tooltips and transient notifications sit outside the main app tree. */
    [data-baseweb="tooltip"],
    [role="tooltip"] {
        background: #172033 !important;
        color: #ffffff !important;
        border-color: #172033 !important;
    }
    [data-baseweb="tooltip"] *,
    [role="tooltip"] * {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }
    [data-testid="stToast"],
    [data-testid="stNotification"] {
        background: #ffffff !important;
        color: var(--gc-text) !important;
        border: 1px solid var(--gc-border) !important;
    }
    [data-testid="stToast"] *,
    [data-testid="stNotification"] * {
        color: var(--gc-text) !important;
    }

    /* Code blocks */
    [data-testid="stCodeBlock"], pre,
    [data-testid="stMarkdownContainer"] code {
        background: var(--gc-code-bg) !important;
        color: #172033 !important;
    }
    [data-testid="stCodeBlock"] span {
        color: inherit !important;
        -webkit-text-fill-color: inherit !important;
    }

    /* Tables and dataframes */
    [data-testid="stDataFrame"],
    [data-testid="stDataFrameResizable"] {
        background: #ffffff !important;
        color: var(--gc-text) !important;
    }

    /* Dividers and progress */
    hr { border-color: var(--gc-border) !important; }
    [data-testid="stProgress"] > div {
        background-color: #e2e8f0 !important;
    }
    [data-testid="stProgress"] > div > div {
        background-color: var(--gc-accent) !important;
    }

    /* Related-problem links */
    .gc-related-problem-list {
        margin: 0;
        padding: 0.15rem 0 0.25rem 1.5rem;
    }

    .gc-related-problem-list li {
        margin-bottom: 0.48rem;
        padding-left: 0.2rem;
    }

    .gc-related-problem-list li::marker {
        color: #667085;
        font-weight: 500;
    }

    .gc-related-problem-row {
        align-items: center;
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        min-width: 0;
    }

    .gc-related-problem-difficulty {
        flex: 0 0 auto;
        font-size: 0.792rem;
        margin-top: 0;
        padding: 0.16rem 0.46rem;
    }

    .gc-related-problem-link {
        color: #2563eb !important;
        font-size: 1.045rem;
        font-weight: 500;
        line-height: 1.35;
        text-decoration: none !important;
    }

    .gc-related-problem-link:visited {
        color: #2563eb !important;
    }

    .gc-related-problem-link:hover {
        color: #1d4ed8 !important;
        text-decoration: underline !important;
    }

    /* Prevent browser/OS dark mode from recoloring controls */
    input, textarea, select, button { color-scheme: light !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

init_db()


def initialize_state() -> None:
    defaults = {
        "navigation": "Dashboard",
        "username": "learner",
        "current_problem_id": PROBLEMS[0]["id"],
        PROBLEM_PICKER_KEY: PROBLEMS[0]["title"],
        "problem_view_nonce": 0,
    }

    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


initialize_state()


def query_value(name: str) -> str | None:
    """Return one normalized value from Streamlit's query parameters."""
    value = st.query_params.get(name)

    if isinstance(value, list):
        value = value[-1] if value else None

    if value is None:
        return None

    normalized = str(value).strip()
    return normalized or None


def route_parameters(
    navigation: str,
    problem_id: str | None = None,
) -> dict[str, str]:
    """Build the canonical URL parameters for one application view."""
    route = NAVIGATION_TO_ROUTE.get(navigation, DEFAULT_ROUTE)
    parameters = {"page": route}

    if navigation == "Practice":
        active_problem_id = (
            problem_id
            if problem_id in PROBLEM_BY_ID
            else st.session_state.current_problem_id
        )
        parameters["problem"] = active_problem_id

    return parameters


def set_route(
    navigation: str,
    problem_id: str | None = None,
) -> None:
    """Update the address bar without discarding the active app state."""
    desired = route_parameters(navigation, problem_id)
    current = {
        key: query_value(key)
        for key in ("page", "problem")
        if query_value(key) is not None
    }

    if current == desired:
        return

    # from_dict performs one atomic URL update. This avoids the temporary
    # empty URL created by clear() followed by separate assignments.
    st.query_params.from_dict(desired)


def activate_problem(
    problem_id: str,
    *,
    update_url: bool = True,
) -> None:
    """
    Open a problem as a fresh Practice view.

    This resets the problem-pane scroll position and gives all expanders
    new widget identities so they start folded.
    """
    if problem_id not in PROBLEM_BY_ID:
        return

    problem_changed = (
        problem_id != st.session_state.current_problem_id
        or st.session_state.navigation != "Practice"
    )

    st.session_state.current_problem_id = problem_id
    st.session_state[PROBLEM_PICKER_KEY] = PROBLEM_ID_TO_TITLE[
        problem_id
    ]
    st.session_state.navigation = "Practice"

    if problem_changed:
        st.session_state.problem_view_nonce = (
            int(st.session_state.get("problem_view_nonce", 0)) + 1
        )

    if update_url:
        set_route("Practice", problem_id)


def load_route_from_query_parameters() -> None:
    """Restore the exact page/problem encoded in the current URL."""
    requested_route = query_value("page")
    requested_problem_id = query_value("problem")

    # A valid problem parameter is itself an unambiguous Practice route.
    # This also keeps old shared links such as ?problem=two-sum working.
    if requested_problem_id in PROBLEM_BY_ID:
        activate_problem(
            requested_problem_id,
            update_url=False,
        )
        set_route("Practice", requested_problem_id)
        return

    requested_navigation = ROUTE_TO_NAVIGATION.get(requested_route)

    if requested_navigation == "Practice":
        fallback_problem_id = st.session_state.current_problem_id
        if fallback_problem_id not in PROBLEM_BY_ID:
            fallback_problem_id = PROBLEMS[0]["id"]

        activate_problem(
            fallback_problem_id,
            update_url=False,
        )
        set_route("Practice", fallback_problem_id)
        return

    if requested_navigation is None:
        requested_navigation = "Dashboard"

    st.session_state.navigation = requested_navigation
    set_route(requested_navigation)


load_route_from_query_parameters()


def sync_navigation_to_url() -> None:
    """Handle sidebar page changes and persist them in the address bar."""
    navigation = st.session_state.navigation

    if navigation == "Practice":
        set_route(
            navigation,
            st.session_state.current_problem_id,
        )
    else:
        set_route(navigation)


def open_problem(problem_id: str) -> None:
    activate_problem(problem_id)


def select_problem_from_picker() -> None:
    selected_title = st.session_state.get(PROBLEM_PICKER_KEY)
    selected_id = PROBLEM_TITLE_TO_ID.get(selected_title)

    if not selected_id:
        return

    if selected_id == st.session_state.current_problem_id:
        set_route("Practice", selected_id)
        return

    activate_problem(selected_id)


def render_problem_scroll_reset(view_nonce: int) -> None:
    """Initialize the newly keyed problem pane at the top exactly once."""
    pane_class = f"st-key-problem_scroll--{view_nonce}"

    components.html(
        f"""
        <script>
        (() => {{
            const parentWindow = window.parent;
            const parentDocument = parentWindow.document;
            const paneClass = {json.dumps(pane_class)};
            const selector =
                `[data-testid="stVerticalBlock"].${{paneClass}}`;

            let observer = null;
            let observerTimeout = null;

            function resetOnce() {{
                const pane = parentDocument.querySelector(selector);
                if (!pane) {{
                    return false;
                }}

                // This container has a new Streamlit key for each problem.
                // Set only its initial position; never keep overriding user
                // scrolling after the pane has mounted.
                pane.scrollTo({{
                    top: 0,
                    left: 0,
                    behavior: "auto"
                }});

                observer?.disconnect();
                if (observerTimeout !== null) {{
                    parentWindow.clearTimeout(observerTimeout);
                }}
                return true;
            }}

            if (!resetOnce()) {{
                observer = new MutationObserver(() => {{
                    resetOnce();
                }});
                observer.observe(parentDocument.body, {{
                    childList: true,
                    subtree: true
                }});

                // The observer only waits for the newly keyed pane to mount.
                // It never continues resetting an already visible pane.
                observerTimeout = parentWindow.setTimeout(() => {{
                    observer?.disconnect();
                }}, 500);
            }}
        }})();
        </script>
        """,
        height=0,
        width=0,
    )



def normalize_related_topic(value: Any) -> str:
    return " ".join(
        re.findall(r"[a-z0-9]+", str(value).casefold())
    )


def canonical_related_word(word: str) -> str:
    return RELATED_WORD_ALIASES.get(word, word)


def extract_related_words(values: list[Any]) -> set[str]:
    words: set[str] = set()

    for value in values:
        raw_words = re.findall(
            r"[a-z0-9]+",
            str(value).casefold(),
        )

        for raw_word in raw_words:
            if len(raw_word) <= 1:
                continue

            if raw_word in RELATED_STOP_WORDS:
                continue

            words.add(canonical_related_word(raw_word))

    return words


def get_related_problems(
    problem: dict[str, Any],
    limit: int = RELATED_PROBLEM_LIMIT,
) -> list[tuple[dict[str, Any], str]]:
    """
    Return closely related problems ordered by relevance.

    Generic overlap such as only Array is not enough. Problems must share a
    specific topic, multiple topics, a specific topic word, or title terms.
    """
    source_tag_labels: dict[str, str] = {}

    for tag in problem.get("tags", []):
        normalized_tag = normalize_related_topic(tag)

        if normalized_tag:
            source_tag_labels[normalized_tag] = str(tag)

    source_tags = set(source_tag_labels)

    source_topic_words = extract_related_words(
        list(problem.get("tags", []))
    )

    source_title_words = extract_related_words(
        [problem.get("title", "")]
    )

    ranked: list[
        tuple[float, str, dict[str, Any], str]
    ] = []

    for candidate in PROBLEMS:
        if candidate["id"] == problem["id"]:
            continue

        candidate_tags: set[str] = set()

        for tag in candidate.get("tags", []):
            normalized_tag = normalize_related_topic(tag)

            if normalized_tag:
                candidate_tags.add(normalized_tag)

        candidate_topic_words = extract_related_words(
            list(candidate.get("tags", []))
        )

        candidate_title_words = extract_related_words(
            [candidate.get("title", "")]
        )

        shared_tags = source_tags.intersection(candidate_tags)

        shared_topic_words = source_topic_words.intersection(
            candidate_topic_words
        )

        shared_title_words = source_title_words.intersection(
            candidate_title_words
        )

        specific_shared_tags = shared_tags.difference(
            RELATED_GENERIC_TOPICS
        )

        specific_shared_topic_words = (
            shared_topic_words.difference(
                RELATED_GENERIC_WORDS
            )
        )

        is_closely_related = bool(
            specific_shared_tags
            or specific_shared_topic_words
            or len(shared_tags) >= 2
            or shared_title_words
        )

        if not is_closely_related:
            continue

        score = (
            10 * len(specific_shared_tags)
            + 5 * len(specific_shared_topic_words)
            + 3 * len(shared_tags)
            + 4 * len(shared_title_words)
        )

        if (
            candidate.get("difficulty")
            == problem.get("difficulty")
        ):
            score = score + 0.25

        shared_topic_labels = sorted(
            source_tag_labels[tag]
            for tag in shared_tags
            if tag in source_tag_labels
        )

        if shared_topic_labels:
            displayed_topics = shared_topic_labels[:3]
            reason = (
                "Shared topics: "
                + ", ".join(displayed_topics)
            )

        elif specific_shared_topic_words:
            displayed_words = sorted(
                word.upper()
                if word in {"bfs", "dfs", "dp"}
                else word.title()
                for word in specific_shared_topic_words
            )[:3]

            reason = (
                "Shared pattern: "
                + ", ".join(displayed_words)
            )

        else:
            displayed_words = sorted(
                word.title()
                for word in shared_title_words
            )[:3]

            reason = (
                "Similar problem idea: "
                + ", ".join(displayed_words)
            )

        ranked.append(
            (
                score,
                str(candidate["title"]).casefold(),
                candidate,
                reason,
            )
        )

    ranked.sort(
        key=lambda item: (
            -item[0],
            item[1],
        )
    )

    return [
        (candidate, reason)
        for _, _, candidate, reason in ranked[:limit]
    ]


def recommend_problem(dashboard: dict[str, Any]) -> dict[str, Any]:
    solved = set(dashboard.get("solved_ids", []))
    unsolved = [problem for problem in PROBLEMS if problem["id"] not in solved]
    if not unsolved:
        return PROBLEMS[0]

    mastery = dashboard.get("mastery", [])
    if mastery:
        weakest_tag = min(mastery, key=lambda row: float(row["score"]))["tag"]
        matching = [problem for problem in unsolved if weakest_tag in problem["tags"]]
        if matching:
            return sorted(matching, key=lambda p: (p["difficulty"] != "Easy", p["title"]))[0]
    return unsolved[0]


def render_problem_header(problem: dict[str, Any]) -> None:
    difficulty_class = str(problem["difficulty"]).strip().lower()
    st.markdown(
        f"""
        <div class="gc-hero gc-problem-hero">
            <div class="gc-title">{escape(str(problem['title']))}</div>
            <div class="gc-problem-difficulty is-{escape(difficulty_class)}">
                {escape(str(problem['difficulty']))}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def inline_code_html(text: str) -> str:
    """Escape curated copy while preserving its Markdown-style inline code."""
    chunks = text.split("`")
    return "".join(
        f"<code>{escape(chunk)}</code>" if index % 2 else escape(chunk)
        for index, chunk in enumerate(chunks)
    )


EXPLANATION_TOKEN_PATTERN = re.compile(
    r"(`[^`]+`|\"(?:\\.|[^\"\\])*\"|"
    r"(?<![A-Za-z0-9])'(?:\\.|[^'\\\n])*'(?![A-Za-z0-9])|"
    r"\[[^\[\]\n]{1,180}\]|\{[^{}\n]{1,180}\}|"
    r"(?<![A-Za-z_])-?\d+(?:\.\d+)?(?:st|nd|rd|th)?%?)"
)


def explanation_token_html(text: str) -> str:
    """Style numbers and compact code-like literals inside explanations."""
    rendered: list[str] = []
    for token in EXPLANATION_TOKEN_PATTERN.split(text):
        if not token:
            continue

        if token.startswith("`") and token.endswith("`"):
            value = token[1:-1]
            rendered.append(
                f'<code class="gc-explanation-token">{escape(value)}</code>'
            )
        elif EXPLANATION_TOKEN_PATTERN.fullmatch(token):
            rendered.append(
                f'<code class="gc-explanation-token">{escape(token)}</code>'
            )
        else:
            rendered.append(escape(token))

    return "".join(rendered)


def explanation_lines(text: str) -> list[tuple[str, bool]]:
    """Recover readable lines from explanations flattened by imported data."""
    normalized = re.sub(r"[ \t]+", " ", str(text).replace("\r\n", "\n")).strip()
    if not normalized:
        return []

    # Restore common structures that source imports flattened into one paragraph.
    normalized = re.sub(r"\s+(?=Step\s+\d+\s*:)", "\n", normalized, flags=re.I)
    normalized = re.sub(
        r"\s+(?=(?:First|Second|Third|Fourth|Fifth|Final)\s+operation\s*:)",
        "\n",
        normalized,
        flags=re.I,
    )
    normalized = re.sub(
        r"\s+(?=\d+(?:st|nd|rd|th)\s+day\s*:)",
        "\n",
        normalized,
        flags=re.I,
    )
    normalized = re.sub(
        r"\s+(?=\[[^\]\n]+\]\s*,\s*range\s*=)",
        "\n",
        normalized,
        flags=re.I,
    )
    normalized = re.sub(
        r"\s+(?=\[\s*-?\d+\s*,\s*-?\d+\s*\]\s*:)",
        "\n",
        normalized,
    )
    normalized = re.sub(r";\s+(?=[A-Za-z_][A-Za-z0-9_]*(?:\.|\s))", ";\n", normalized)
    normalized = re.sub(
        r"\s+(?=[A-Za-z_][A-Za-z0-9_]*\.[A-Za-z_][A-Za-z0-9_]*\()",
        "\n",
        normalized,
    )
    normalized = re.sub(r"\s+-\s+(?=[A-Z0-9\"'`])", "\n- ", normalized)
    normalized = re.sub(r"\s+(?=The\s+power\s+of\s+-?\d+\s+is\s+)", "\n", normalized)
    normalized = re.sub(
        r"\s+(?=(?:First|Second|Third|Fourth|Fifth|Finally),\s+)",
        "\n",
        normalized,
        flags=re.I,
    )
    normalized = re.sub(r"\s+then,\s+", "\nThen, ", normalized, flags=re.I)

    # Put ordinary sentences on separate lines when a long explanation contains
    # several independent steps. Short prose remains a normal wrapped line.
    if len(normalized) > 135:
        normalized = re.sub(
            r"(?<=[.!?])\s+(?=[A-Z\"'`\[])",
            "\n",
            normalized,
        )

    lines: list[tuple[str, bool]] = []
    for raw_line in normalized.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        is_bullet = line.startswith("- ")
        if is_bullet:
            line = line[2:].strip()
        lines.append((line, is_bullet))

    return lines


def window_trace_html(example: dict[str, Any], explanation: str) -> str:
    """Render flattened sliding-window traces as a real row-by-row table."""
    if not re.search(r"\bWindow\s+position\b", explanation, flags=re.I):
        return ""

    nums_match = re.search(r"\bnums\s*=\s*(\[[^\]]*\])", str(example.get("input", "")))
    k_match = re.search(r"\bk\s*=\s*(-?\d+)", str(example.get("input", "")))
    if not nums_match or not k_match:
        return ""

    try:
        nums = ast.literal_eval(nums_match.group(1))
        k = int(k_match.group(1))
        results = ast.literal_eval(str(example.get("output", "")))
    except (SyntaxError, ValueError, TypeError):
        return ""

    if (
        not isinstance(nums, list)
        or not isinstance(results, list)
        or k <= 0
        or len(results) != max(0, len(nums) - k + 1)
    ):
        return ""

    metric = "Median" if re.search(r"\bMedian\b", explanation, flags=re.I) else "Max"
    rows = [
        (
            '<div class="gc-explanation-trace-row is-header">'
            '<div>Window</div>'
            f'<div class="gc-explanation-trace-result">{escape(metric)}</div>'
            '</div>'
        )
    ]

    for start, result in enumerate(results):
        window = nums[start : start + k]
        rows.append(
            '<div class="gc-explanation-trace-row">'
            '<div class="gc-explanation-trace-window">'
            f'<code class="gc-explanation-token">{escape(str(window))}</code>'
            '</div>'
            '<div class="gc-explanation-trace-result">'
            f'<code class="gc-explanation-token">{escape(str(result))}</code>'
            '</div>'
            '</div>'
        )

    return '<div class="gc-explanation-trace">' + "".join(rows) + "</div>"


def example_explanation_html(example: dict[str, Any], explanation: str) -> str:
    """Create readable, wrapping explanation markup for every problem."""
    trace = window_trace_html(example, explanation)
    if trace:
        return trace

    lines = explanation_lines(explanation)
    if not lines:
        return ""

    return (
        '<div class="gc-explanation-body">'
        + "".join(
            (
                '<div class="gc-explanation-line'
                + (" is-bullet" if is_bullet else "")
                + '">'
                + explanation_token_html(line)
                + "</div>"
            )
            for line, is_bullet in lines
        )
        + "</div>"
    )


CONSTRAINT_TOKEN_PATTERN = re.compile(
    r"(`[^`]+`|O\([^)]*\)|-?\d[\d,]*(?:\.\d+)?%?|<=|>=|==|!=|<|>)"
)
CONSTRAINT_OPERATORS = {
    "<=": "&le;",
    ">=": "&ge;",
    "==": "=",
    "!=": "&ne;",
    "<": "&lt;",
    ">": "&gt;",
}


def constraint_html(text: str) -> str:
    """Encode and visually distinguish numeric and technical constraint tokens."""
    rendered: list[str] = []
    for token in CONSTRAINT_TOKEN_PATTERN.split(text):
        if not token:
            continue
        if token.startswith("`") and token.endswith("`"):
            rendered.append(
                f'<code class="gc-constraint-code">{escape(token[1:-1])}</code>'
            )
        elif token.startswith("O("):
            rendered.append(
                f'<code class="gc-constraint-code">{escape(token)}</code>'
            )
        elif token in CONSTRAINT_OPERATORS:
            rendered.append(
                f'<span class="gc-constraint-operator">'
                f'{CONSTRAINT_OPERATORS[token]}</span>'
            )
        elif re.fullmatch(r"-?\d[\d,]*(?:\.\d+)?%?", token):
            rendered.append(
                f'<span class="gc-constraint-number">{escape(token)}</span>'
            )
        else:
            rendered.append(escape(token))
    return "".join(rendered)


def render_constraints(problem: dict[str, Any]) -> None:
    items = "".join(
        f"""
        <li class="gc-constraint-item">
            <span>{constraint_html(constraint)}</span>
        </li>
        """
        for constraint in problem["constraints"]
    )
    st.markdown(
        f"""
        <section class="gc-constraints" aria-labelledby="constraint-heading">
            <h3 class="gc-constraints-title" id="constraint-heading">
                Constraints and output rules
            </h3>
            <ul class="gc-constraint-list">{items}</ul>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_topics_and_hints(
    problem: dict[str, Any],
) -> None:
    """
    Render topics, related problems, and each hint in a separate fold.
    """
    view_nonce = int(
    st.session_state.get("problem_view_nonce", 0)
    )

    topics = [
        str(topic)
        for topic in problem.get("tags", [])
        if str(topic).strip()
    ]

    hints = [
        str(hint)
        for hint in problem.get("hints", [])
        if str(hint).strip()
    ]

    related_problems = get_related_problems(problem)

    st.markdown(
        """
        <div
            class="gc-after-constraints-space"
            aria-hidden="true"
        >
            <span class="gc-gap-line">&nbsp;</span>
            <span class="gc-gap-line">&nbsp;</span>
            <span class="gc-gap-line">&nbsp;</span>
            <span class="gc-gap-line">&nbsp;</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander(
        "Topics",
        expanded=False,
        key=(
            f"topics::{problem['id']}::{view_nonce}"
        ),
    ):
        topic_pills = "".join(
            (
                '<span class="gc-topic-pill">'
                + escape(topic)
                + "</span>"
            )
            for topic in topics
        )

        st.markdown(
            (
                '<div class="gc-topic-list">'
                + topic_pills
                + "</div>"
            ),
            unsafe_allow_html=True,
        )

    if related_problems:
        with st.container(
            key="related_problems_section",
        ):
            with st.expander(
                "Related Problems",
                expanded=False,
                key=(
                    f"related::{problem['id']}::{view_nonce}"
                ),
            ):
                related_links = []

                for related_problem, _ in related_problems:
                    problem_id = quote(
                        str(related_problem["id"]),
                        safe="",
                    )

                    problem_title = escape(
                        str(related_problem["title"])
                    )

                    related_difficulty = escape(
                        str(related_problem["difficulty"])
                    )
                    related_difficulty_class = escape(
                        str(related_problem["difficulty"])
                        .strip()
                        .lower()
                    )

                    related_links.append(
                        (
                            '<div class="gc-related-problem-row">'
                            '<a class="gc-related-problem-link" '
                            f'href="?page=practice&amp;problem={problem_id}" '
                            'target="_self">'
                            f"{problem_title}"
                            "</a>"
                            '<span class="gc-problem-difficulty '
                            'gc-related-problem-difficulty '
                            f'is-{related_difficulty_class}">'
                            f"{related_difficulty}"
                            "</span>"
                            "</div>"
                        )
                    )

                st.markdown(
                    (
                        '<ol class="gc-related-problem-list">'
                        + "".join(
                            f"<li>{related_link}</li>"
                            for related_link in related_links
                        )
                        + "</ol>"
                    ),
                    unsafe_allow_html=True,
                )




    for hint_number, hint in enumerate(
        hints,
        start=1,
    ):
        with st.expander(
            f"Hint {hint_number}",
            expanded=False,
            key=(
                f"hint::{problem['id']}::"
                f"{hint_number}::{view_nonce}"
            ),
        ):
            st.markdown(
                (
                    '<div class="gc-hint-body">'
                    + inline_code_html(hint)
                    + "</div>"
                ),
                unsafe_allow_html=True,
            )


def render_examples(problem: dict[str, Any]) -> None:
    for index, example in enumerate(problem["examples"], start=1):
        explanation = example.get("explanation") or (
            "Compare the returned value with the problem rules and verify that every "
            "part of the input is handled."
        )
        visual_markup = ""
        if index == 1:
            visual_html = problem_visual_html(problem)
            if visual_html:
                visual_markup = f"\n                    {visual_html}"
        example_class = "gc-example-card is-first" if index == 1 else "gc-example-card"
        st.markdown(
            f"""
            <article class="{example_class}" aria-labelledby="example-{index}">
                <header class="gc-example-header">
                    <div class="gc-example-title" id="example-{index}">Example {index}</div>
                </header>
                <div class="gc-example-content">
                    <div class="gc-io-grid">
                        <section class="gc-io-panel" aria-label="Example {index} input">
                            <div class="gc-io-label">Input</div>
                            <div class="gc-io-value"><code>{escape(str(example["input"]))}</code></div>
                        </section>
                        <section class="gc-io-panel" aria-label="Example {index} output">
                            <div class="gc-io-label">Expected output</div>
                            <div class="gc-io-value"><code>{escape(str(example["output"]))}</code></div>
                        </section>
                    </div>{visual_markup}
                    <section class="gc-explanation" aria-label="Example {index} explanation">
                        <div class="gc-io-label">Explanation</div>
                        {example_explanation_html(example, explanation)}
                    </section>
                </div>
            </article>
            """,
            unsafe_allow_html=True,
        )


def normalized_prediction(value: str) -> Any:
    try:
        return ast.literal_eval(value.strip())
    except (SyntaxError, ValueError):
        return re.sub(r"\s+", "", value).lower()


def render_active_recall(username: str, problem: dict[str, Any]) -> None:
    with st.container():
        st.caption("Trace one input yourself before reading the worked examples.")
        selected_index = st.selectbox(
            "Example to trace",
            options=list(range(len(problem["examples"]))),
            format_func=lambda index: f"Example {index + 1}",
            key=f"prediction_example::{username}::{problem['id']}",
        )
        selected = problem["examples"][selected_index]
        st.caption("Input")
        st.code(selected["input"], language="text", wrap_lines=True)
        prediction_key = (
            f"prediction::{username}::{problem['id']}::{selected_index}"
        )
        status_key = (
            f"prediction_status::{username}::{problem['id']}::{selected_index}"
        )
        prediction = st.text_input(
            "Your predicted output",
            key=prediction_key,
            placeholder="Type the return value before reading the worked case.",
        )
        if st.button(
            "Check prediction",
            key=f"check_prediction::{username}::{problem['id']}::{selected_index}",
            type="primary",
            disabled=not prediction.strip(),
        ):
            st.session_state[status_key] = (
                normalized_prediction(prediction)
                == normalized_prediction(str(selected["output"]))
            )

        if status_key in st.session_state:
            if st.session_state[status_key]:
                st.success(
                    "Prediction matched. Now explain why the output satisfies "
                    "every rule before you read the worked explanation."
                )
            else:
                st.warning(
                    "Not yet. Re-read the output rule and trace one state change "
                    "at a time—the expected value stays hidden here."
                )


def render_test_results(result: dict[str, Any]) -> None:
    passed = int(result.get("passed", 0))
    total = int(result.get("total", 0))
    status = result.get("status", "unknown")

    if status == "completed" and total > 0 and passed == total:
        st.success(f"Accepted — {passed}/{total} tests passed.")
    elif status == "completed":
        st.error(f"{passed}/{total} tests passed.")
    else:
        st.error(result.get("error") or status.replace("_", " ").title())

    if result.get("stdout"):
        with st.expander("Program output"):
            st.code(result["stdout"], language="text")

    for item in result.get("results", []):
        label = "Passed" if item.get("passed") else "Failed"
        with st.expander(f"Test {item['test']} — {label}", expanded=not item.get("passed")):
            st.write("**Input**")
            st.code(repr(item.get("input")), language="python")
            st.write("**Expected**")
            st.code(repr(item.get("expected")), language="python")
            st.write("**Your output**")
            st.code(repr(item.get("actual")), language="python")
            if item.get("error"):
                st.code(item["error"], language="text")


def render_attempt_coach(
    username: str,
    problem: dict[str, Any],
    language_id: str,
) -> None:
    state_suffix = f"{username}::{problem['id']}::{language_id}"
    result_key = f"result::{state_suffix}"
    if result_key not in st.session_state:
        return

    result = st.session_state[result_key]
    diagnosis = st.session_state.get(
        f"diagnosis::{state_suffix}",
        {"type": "Review", "message": "Review the first failing case."},
    )
    passed = int(result.get("passed", 0))
    total = int(result.get("total", 0))
    success = (
        result.get("status") == "completed"
        and total > 0
        and passed == total
    )

    if success:
        mode = st.session_state.get(
            f"independence::{state_suffix}",
            "Independent",
        )
        mode_copy = {
            "Independent": (
                "You passed without revealing a hint. That is stronger evidence "
                "of recall than an accepted answer alone."
            ),
            "Guided": (
                "You passed with a small amount of guidance. Revisit the problem "
                "later and aim to solve it without hints."
            ),
            "Assisted": (
                "You reached a correct solution with substantial guidance. The "
                "next learning win is reproducing the approach from memory."
            ),
        }.get(str(mode), "You passed the available tests.")
        st.markdown(
            f"""
            <section class="gc-attempt-coach">
                <div class="gc-coach-head is-success">
                    <div class="gc-coach-kicker">Learning evidence</div>
                    <div class="gc-coach-title">Accepted is not the finish line</div>
                </div>
                <div class="gc-coach-body">
                    <p>{escape(mode_copy)}</p>
                    <p>
                        This problem will enter your recall queue after three
                        quiet days so you can prove the pattern still sticks.
                    </p>
                    <span class="gc-mode-badge">{escape(str(mode))} solve</span>
                </div>
            </section>
            """,
            unsafe_allow_html=True,
        )
        notes = load_guide_notes(username, problem["id"])
        reflection_key = f"reflection::{username}::{problem['id']}"
        if reflection_key not in st.session_state:
            st.session_state[reflection_key] = notes.get(100, "")
        reflection = st.text_area(
            "Retrieval check: explain the invariant and complexity from memory",
            key=reflection_key,
            height=105,
            placeholder=(
                "What stayed true during the algorithm, and what are the time "
                "and space costs?"
            ),
        )
        if st.button(
            "Save reflection",
            key=f"save_reflection::{username}::{problem['id']}",
            disabled=not reflection.strip(),
        ):
            save_guide_note(username, problem["id"], 100, reflection)
            st.success("Reflection saved. This solve now includes retrieval evidence.")
        return

    failed = [
        item for item in result.get("results", [])
        if not item.get("passed")
    ]
    first = failed[0] if failed else {}
    case_text = (
        f"Input: {first.get('input')!r}\n"
        f"Expected: {first.get('expected')!r}\n"
        f"Your output: {first.get('actual')!r}"
    )
    st.markdown(
        f"""
        <section class="gc-attempt-coach">
            <div class="gc-coach-head">
                <div class="gc-coach-kicker">Failure → lesson</div>
                <div class="gc-coach-title">{escape(str(diagnosis["type"]))}</div>
            </div>
            <div class="gc-coach-body">
                <p>{escape(str(diagnosis["message"]))}</p>
                <div class="gc-coach-case">{escape(case_text)}</div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    hint_key = f"hint_level::{username}::{problem['id']}"
    st.session_state.setdefault(hint_key, 0)
    revealed = int(st.session_state[hint_key])
    if revealed > 0:
        hint_index = min(revealed - 1, len(problem["hints"]) - 1)
        st.info(f"Smallest next nudge: {problem['hints'][hint_index]}")
    if st.button(
        "Reveal one small nudge",
        key=f"coach_hint::{username}::{problem['id']}",
        disabled=revealed >= len(problem["hints"]),
    ):
        st.session_state[hint_key] += 1


def render_guided_reasoning(username: str, problem: dict[str, Any]) -> None:
    notes = load_guide_notes(username, problem["id"])
    completed_steps = sum(
        bool(notes.get(index, "").strip())
        for index in range(len(problem["guide"]))
    )
    st.markdown(
        f"""
        <div class="gc-plan-progress">
            <span class="gc-plan-count">
                {completed_steps} of {len(problem["guide"])} checkpoints saved
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.progress(completed_steps / max(len(problem["guide"]), 1))
    selected_step = st.radio(
        "Reasoning step",
        options=list(range(len(problem["guide"]))),
        format_func=lambda index: f"Step {index + 1}",
        horizontal=True,
        key=f"guide_step::{username}::{problem['id']}",
    )
    st.markdown(
        f'<div class="gc-question">{problem["guide"][selected_step]}</div>',
        unsafe_allow_html=True,
    )
    note_key = f"guide_note::{username}::{problem['id']}::{selected_step}"
    if note_key not in st.session_state:
        st.session_state[note_key] = notes.get(selected_step, "")
    answer = st.text_area(
        "Your reasoning",
        key=note_key,
        height=150,
        placeholder="Write your reasoning in your own words.",
    )
    if st.button(
        "Save checkpoint",
        key=f"save_note::{username}::{problem['id']}::{selected_step}",
    ):
        save_guide_note(username, problem["id"], selected_step, answer)
        st.success("Checkpoint saved.")

    hint_key = f"hint_level::{username}::{problem['id']}"
    st.session_state.setdefault(hint_key, 0)
    hint_cols = st.columns([1, 3])
    if hint_cols[0].button(
        "Reveal next hint",
        key=f"hint_button::{username}::{problem['id']}",
        disabled=st.session_state[hint_key] >= len(problem["hints"]),
        width="stretch",
    ):
        st.session_state[hint_key] += 1
    if st.session_state[hint_key] == 0:
        hint_cols[1].caption("Hints are progressive. Reveal only what you need.")
    for index, hint in enumerate(
        problem["hints"][: st.session_state[hint_key]],
        start=1,
    ):
        st.info(f"Hint {index}: {hint}")


LEETCODE_EDITOR_CSS = """
.ace_editor,
.ace-streamlit-light,
.ace-streamlit-light.ace_editor {
    background: #ffffff !important;
    color: #1f2328 !important;
    font-family: Menlo, Monaco, Consolas, "Liberation Mono", monospace !important;
    line-height: 20px !important;
}
.ace_editor .ace_gutter {
    background: #f7f7f7 !important;
    border-right: 1px solid #e5e7eb !important;
    color: #858585 !important;
}
.ace_editor .ace_gutter-active-line {
    background: #ededed !important;
    color: #333333 !important;
}
.ace_editor .ace_marker-layer .ace_active-line {
    background: #f5f5f5 !important;
}
.ace_editor .ace_marker-layer .ace_selection {
    background: #add6ff !important;
}
.ace_editor .ace_marker-layer .ace_selected-word {
    background: transparent !important;
    border: 1px solid #add6ff !important;
}
.ace_editor .ace_cursor {
    color: #000000 !important;
}
/* Long source lines use Ace soft wrapping. Hide the horizontal scrollbar so
   the editor always stays within the available workspace width. */
.ace_editor .ace_scrollbar-h {
    display: none !important;
    height: 0 !important;
}
.ace_editor .ace_storage,
.ace_editor .ace_storage.ace_type,
.ace_editor .ace_keyword {
    color: #0000ff !important;
}
.ace_editor .ace_keyword.ace_operator,
.ace_editor .ace_punctuation,
.ace_editor .ace_paren {
    color: #1f2328 !important;
}
.ace_editor .ace_string,
.ace_editor .ace_string.ace_regexp {
    color: #a31515 !important;
}
.ace_editor .ace_comment {
    color: #008000 !important;
    font-style: normal !important;
}
.ace_editor .ace_constant.ace_numeric {
    color: #098658 !important;
}
.ace_editor .ace_constant.ace_language,
.ace_editor .ace_support.ace_constant {
    color: #0000ff !important;
}
.ace_editor .ace_entity.ace_name.ace_function,
.ace_editor .ace_support.ace_function {
    color: #795e26 !important;
}
.ace_editor .ace_support.ace_class,
.ace_editor .ace_support.ace_type {
    color: #267f99 !important;
}
.ace_editor .ace_variable,
.ace_editor .ace_variable.ace_parameter {
    color: #001080 !important;
}
.ace_editor .ace_indent-guide {
    position: relative !important;
    display: inline-block !important;
    height: 100% !important;
    vertical-align: top !important;
    box-sizing: border-box !important;
    overflow: visible !important;
    background: none !important;
}
.ace_editor .ace_indent-guide::after {
    content: "";
    position: absolute;
    top: -1px;
    right: 0;
    bottom: -1px;
    width: 1px;
    background: rgba(148, 163, 184, 0.45);
    pointer-events: none;
}
.ace_editor .ace_indent-guide-active::after {
    background: rgba(71, 85, 105, 0.72);
}
/* Cross-language token palette. Ace assigns these semantic classes for
   Python, JavaScript, Java, C, C++, C#, and Go modes. */
.ace_editor .ace_meta,
.ace_editor .ace_meta.ace_tag,
.ace_editor .ace_meta.ace_preprocessor {
    color: #AF00DB !important;
}
.ace_editor .ace_entity.ace_name.ace_tag,
.ace_editor .ace_entity.ace_other.ace_attribute-name {
    color: #800000 !important;
}
.ace_editor .ace_entity.ace_name.ace_type,
.ace_editor .ace_entity.ace_name.ace_class,
.ace_editor .ace_storage.ace_type,
.ace_editor .ace_support.ace_type,
.ace_editor .ace_support.ace_class {
    color: #267F99 !important;
}
.ace_editor .ace_entity.ace_name.ace_function,
.ace_editor .ace_support.ace_function,
.ace_editor .ace_meta.ace_function-call {
    color: #795E26 !important;
}
.ace_editor .ace_variable.ace_language,
.ace_editor .ace_variable.ace_instance,
.ace_editor .ace_variable.ace_other,
.ace_editor .ace_variable.ace_parameter {
    color: #001080 !important;
}
.ace_editor .ace_constant,
.ace_editor .ace_constant.ace_numeric,
.ace_editor .ace_constant.ace_language,
.ace_editor .ace_support.ace_constant {
    color: #098658 !important;
}
.ace_editor .ace_invalid {
    color: #ffffff !important;
    background: #e51400 !important;
}
"""


def set_console_view(view_key: str, view: str) -> None:
    st.session_state[view_key] = view


def problem_parameter_names(problem: dict[str, Any]) -> list[str]:
    tree = ast.parse(f"{problem['signature']}\n    pass\n")
    function = tree.body[0]
    if not isinstance(function, ast.FunctionDef):
        return []
    return [argument.arg for argument in function.args.args]


def console_value(value: Any) -> str:
    try:
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    except TypeError:
        return repr(value)


def render_console_field(label: str, value: Any) -> None:
    st.code(
        f"{label}\n{console_value(value)}",
        language="json",
        wrap_lines=True,
    )


def render_testcase_fields(problem: dict[str, Any], args: list[Any]) -> None:
    names = problem_parameter_names(problem)
    for index, value in enumerate(args):
        label = names[index] if index < len(names) else f"arg{index + 1}"
        render_console_field(f"{label} =", value)


def render_console_result(
    problem: dict[str, Any],
    payload: dict[str, Any] | None,
) -> None:
    if not payload:
        st.markdown(
            '<div class="gc-console-empty">Run a testcase to see its result.</div>',
            unsafe_allow_html=True,
        )
        return

    result = payload["result"]
    passed = int(result.get("passed", 0))
    total = int(result.get("total", 0))
    completed = result.get("status") == "completed"
    success = completed and total > 0 and passed == total
    title = "Accepted" if success else (
        "Wrong Answer" if completed else str(result.get("status", "Error")).replace("_", " ").title()
    )
    mode = "is-pass" if success else "is-fail"
    st.markdown(
        f"""
        <div class="gc-console-status {mode}">
            <strong>{escape(title)}</strong>
            <span>{passed} / {total} testcases passed</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    failed = [item for item in result.get("results", []) if not item.get("passed")]
    items = failed or result.get("results", [])
    if items:
        item = items[0]
        render_testcase_fields(problem, list(item.get("input") or []))
        render_console_field("Output", item.get("actual"))
        render_console_field("Expected", item.get("expected"))
        if item.get("error"):
            st.markdown(
                f'<div class="gc-console-error">{escape(str(item["error"]))}</div>',
                unsafe_allow_html=True,
            )
    elif result.get("error"):
        st.markdown(
            f'<div class="gc-console-error">{escape(str(result["error"]))}</div>',
            unsafe_allow_html=True,
        )

    if result.get("stdout"):
        render_console_field("Stdout", str(result["stdout"]))


def render_column_resizer(username: str) -> None:
    storage_key = json.dumps(f"guidedcode-column-ratio::{username}")
    handle_html = """
    <!doctype html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            html, body {
                background: transparent;
                height: 100%;
                margin: 0;
                overflow: hidden;
                user-select: none;
                width: 12px;
            }
            #gc-column-handle {
                background: #e7eaf0;
                cursor: col-resize;
                height: 100%;
                outline: none;
                position: relative;
                touch-action: none;
                width: 12px;
            }
            #gc-column-handle::before {
                background: #b6bfcc;
                bottom: 0;
                content: "";
                left: 5px;
                position: absolute;
                top: 0;
                transition: background .12s ease, width .12s ease;
                width: 2px;
            }
            #gc-column-handle::after {
                background: #8f9bad;
                border-radius: 999px;
                content: "";
                height: 42px;
                left: 4px;
                position: absolute;
                top: calc(50% - 21px);
                transition: background .12s ease, left .12s ease, width .12s ease;
                width: 4px;
            }
            #gc-column-handle:hover,
            #gc-column-handle:focus-visible,
            #gc-column-handle.is-dragging {
                background: #edf3ff;
            }
            #gc-column-handle:hover::before,
            #gc-column-handle:focus-visible::before,
            #gc-column-handle.is-dragging::before,
            #gc-column-handle:hover::after,
            #gc-column-handle:focus-visible::after,
            #gc-column-handle.is-dragging::after {
                background: #2f6fed;
            }
            #gc-column-handle:hover::after,
            #gc-column-handle:focus-visible::after,
            #gc-column-handle.is-dragging::after {
                left: 3px;
                width: 6px;
            }
        </style>
    </head>
    <body>
        <div
            id="gc-column-handle"
            role="separator"
            aria-label="Resize problem and code columns"
            aria-orientation="vertical"
            aria-valuemin="25"
            aria-valuemax="75"
            tabindex="0"
        ></div>
        <script>
        (() => {
            const DIVIDER_WIDTH = 12;
            const DEFAULT_RATIO = 0.48;
            const STORAGE_KEY = __STORAGE_KEY__;
            const handle = document.getElementById("gc-column-handle");
            let splitRatio = DEFAULT_RATIO;
            let startLeftWidth = 0;
            let startX = 0;
            let rowObserver = null;

            const forceHeight = (element, pixels) => {
                if (!element) return;
                const value = `${pixels}px`;
                element.style.setProperty("height", value, "important");
                element.style.setProperty("min-height", value, "important");
                element.style.setProperty("max-height", value, "important");
            };

            const setWidth = (element, pixels) => {
                if (!element) return;
                const value = `${pixels}px`;
                element.style.setProperty("flex", `0 0 ${value}`, "important");
                element.style.setProperty("width", value, "important");
                element.style.setProperty("min-width", "0", "important");
                element.style.setProperty("max-width", value, "important");
            };

            const locateColumns = () => {
                try {
                    const frame = window.frameElement;
                    const host = frame.closest('[data-testid="stElementContainer"]');
                    const divider = host.closest('[data-testid="stColumn"]');
                    const row = divider.closest('[data-testid="stHorizontalBlock"]');
                    const columns = [...row.children].filter(
                        (child) => child.dataset.testid === "stColumn"
                    );
                    const dividerIndex = columns.indexOf(divider);
                    if (dividerIndex <= 0 || dividerIndex >= columns.length - 1) {
                        return null;
                    }
                    return {
                        frame,
                        host,
                        divider,
                        row,
                        left: columns[dividerIndex - 1],
                        right: columns[dividerIndex + 1],
                    };
                } catch (_) {
                    return null;
                }
            };

            const applyRatio = (nextRatio, persist = false) => {
                const workspace = locateColumns();
                if (!workspace) return;
                const { frame, host, divider, row, left, right } = workspace;
                const available = Math.max(1, row.clientWidth - DIVIDER_WIDTH);
                const minimumLeft = Math.min(340, available * .38);
                const minimumRight = Math.min(420, available * .42);
                const minimumRatio = minimumLeft / available;
                const maximumRatio = 1 - minimumRight / available;
                splitRatio = Math.max(
                    minimumRatio,
                    Math.min(maximumRatio, nextRatio)
                );
                const leftWidth = Math.round(available * splitRatio);
                const rightWidth = available - leftWidth;
                setWidth(left, leftWidth);
                setWidth(divider, DIVIDER_WIDTH);
                setWidth(right, rightWidth);

                const rowHeight = Math.round(row.getBoundingClientRect().height);
                forceHeight(frame, rowHeight);
                forceHeight(host, rowHeight);

                const percent = Math.round(splitRatio * 100);
                handle.setAttribute("aria-valuenow", String(percent));
                handle.setAttribute(
                    "aria-valuetext",
                    `Problem ${percent}%, code ${100 - percent}%`
                );
                if (persist) {
                    try {
                        window.localStorage.setItem(
                            STORAGE_KEY,
                            String(splitRatio)
                        );
                    } catch (_) {}
                }
            };

            try {
                const saved = Number.parseFloat(
                    window.localStorage.getItem(STORAGE_KEY)
                );
                if (Number.isFinite(saved)) splitRatio = saved;
            } catch (_) {}

            handle.addEventListener("pointerdown", (event) => {
                const workspace = locateColumns();
                if (!workspace) return;
                startX = event.screenX;
                startLeftWidth = workspace.left.getBoundingClientRect().width;
                handle.classList.add("is-dragging");
                handle.setPointerCapture(event.pointerId);
                window.parent.document.body.style.setProperty(
                    "cursor",
                    "col-resize",
                    "important"
                );
                window.parent.document.body.style.setProperty(
                    "user-select",
                    "none",
                    "important"
                );
                event.preventDefault();
            });
            handle.addEventListener("pointermove", (event) => {
                if (!handle.hasPointerCapture(event.pointerId)) return;
                const workspace = locateColumns();
                if (!workspace) return;
                const available = Math.max(
                    1,
                    workspace.row.clientWidth - DIVIDER_WIDTH
                );
                applyRatio(
                    (startLeftWidth + event.screenX - startX) / available
                );
            });
            const finishDrag = (event) => {
                if (handle.hasPointerCapture(event.pointerId)) {
                    handle.releasePointerCapture(event.pointerId);
                }
                handle.classList.remove("is-dragging");
                window.parent.document.body.style.removeProperty("cursor");
                window.parent.document.body.style.removeProperty("user-select");
                applyRatio(splitRatio, true);
            };
            handle.addEventListener("pointerup", finishDrag);
            handle.addEventListener("pointercancel", finishDrag);
            handle.addEventListener("keydown", (event) => {
                if (!["ArrowLeft", "ArrowRight"].includes(event.key)) return;
                const delta = event.key === "ArrowLeft" ? -.02 : .02;
                applyRatio(splitRatio + delta, true);
                event.preventDefault();
            });

            const workspace = locateColumns();
            if (workspace && "ResizeObserver" in window) {
                rowObserver = new ResizeObserver(() => {
                    window.requestAnimationFrame(() => applyRatio(splitRatio));
                });
                rowObserver.observe(workspace.row);
            }
            requestAnimationFrame(() => applyRatio(splitRatio));
            window.setTimeout(() => applyRatio(splitRatio), 120);
            window.setTimeout(() => applyRatio(splitRatio), 400);
        })();
        </script>
    </body>
    </html>
    """
    st.iframe(
        handle_html.replace("__STORAGE_KEY__", storage_key),
        width="stretch",
        height=900,
    )


def render_workspace_resizer(username: str, force_expand: bool = False) -> None:
    ratio_storage_key = json.dumps(f"guidedcode-code-ratio::{username}")
    collapsed_storage_key = json.dumps(f"guidedcode-console-collapsed::{username}")
    force_expand_js = "true" if force_expand else "false"
    handle_html = """
    <!doctype html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            html, body {
                background: #eef1f5;
                height: 28px;
                margin: 0;
                overflow: hidden;
                user-select: none;
            }
            #gc-resize-handle {
                align-items: center;
                border-bottom: 1px solid #cbd2dc;
                border-top: 1px solid #cbd2dc;
                box-sizing: border-box;
                cursor: row-resize;
                display: flex;
                height: 28px;
                justify-content: space-between;
                outline: none;
                padding: 0 7px 0 10px;
                touch-action: none;
                width: 100%;
            }
            #gc-resize-handle.is-dragging {
                background: #edf3ff;
            }
            .gc-console-handle-label {
                align-items: center;
                color: #344054;
                display: flex;
                font: 700 13.2px/1 -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
                gap: 8px;
                pointer-events: none;
            }
            .gc-console-grip {
                background: #8f9bad;
                border-radius: 999px;
                height: 4px;
                transition: background .12s ease, width .12s ease;
                width: 34px;
            }
            #gc-resize-handle:hover .gc-console-grip,
            #gc-resize-handle:focus-visible .gc-console-grip,
            #gc-resize-handle.is-dragging .gc-console-grip {
                background: #2f6fed;
                width: 46px;
            }
            #gc-console-toggle {
                align-items: center;
                background: transparent;
                border: 0;
                border-radius: 5px;
                color: #475467;
                cursor: pointer;
                display: flex;
                font: 700 17.6px/1 -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
                height: 22px;
                justify-content: center;
                padding: 0;
                width: 26px;
            }
            #gc-console-toggle:hover,
            #gc-console-toggle:focus-visible {
                background: #dfe7f2;
                color: #1d4ed8;
                outline: none;
            }
            #gc-console-toggle svg {
                display: block;
                flex: 0 0 auto;
                height: 16px;
                overflow: visible;
                transform: rotate(0deg);
                transform-origin: 50% 50%;
                transition: transform .14s ease;
                width: 16px;
            }
            #gc-console-toggle[aria-expanded="false"] svg {
                transform: rotate(180deg);
            }
        </style>
    </head>
    <body>
        <div
            id="gc-resize-handle"
            role="separator"
            aria-label="Resize code editor and testcase panel"
            aria-orientation="horizontal"
            aria-valuemin="20"
            aria-valuemax="88"
            tabindex="0"
        >
            <div class="gc-console-handle-label">
                <span class="gc-console-grip"></span>
                <span>Console</span>
            </div>
            <button
                id="gc-console-toggle"
                type="button"
                aria-label="Minimize testcase panel"
                aria-expanded="true"
                title="Minimize testcase panel"
            >
                <svg viewBox="0 0 16 16" aria-hidden="true" focusable="false">
                    <path
                        d="M3.25 5.75 8 10.5l4.75-4.75"
                        fill="none"
                        stroke="currentColor"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="1.8"
                    />
                </svg>
            </button>
        </div>
        <script>
        (() => {
            const DEFAULT_RATIO = .66;
            const MIN_CODE_HEIGHT = 150;
            const MIN_EXPANDED_TESTCASE_HEIGHT = 118;
            const COLLAPSED_TESTCASE_HEIGHT = 52;
            const RATIO_STORAGE_KEY = __RATIO_STORAGE_KEY__;
            const COLLAPSED_STORAGE_KEY = __COLLAPSED_STORAGE_KEY__;
            const FORCE_EXPAND = __FORCE_EXPAND__;
            const handle = document.getElementById("gc-resize-handle");
            const toggle = document.getElementById("gc-console-toggle");
            let splitRatio = DEFAULT_RATIO;
            let codeHeight = 0;
            let collapsed = false;
            let startHeight = 0;
            let startY = 0;
            let columnObserver = null;
            let applying = false;

            const forceHeight = (element, pixels) => {
                if (!element) return;
                const value = `${Math.max(0, Math.round(pixels))}px`;
                element.style.setProperty("height", value, "important");
                element.style.setProperty("min-height", value, "important");
                element.style.setProperty("max-height", value, "important");
            };

            const locateWorkspace = () => {
                try {
                    const frame = window.frameElement;
                    const host = frame.closest('[data-testid="stElementContainer"]');
                    const column = host.closest('[data-testid="stColumn"]');
                    const editorFrame = [...column.querySelectorAll("iframe")]
                        .find((candidate) => (
                            candidate !== frame
                            && !candidate.closest('[class*="st-key-resize_handle--"]')
                            && candidate.getBoundingClientRect().height > 80
                        ));
                    const editorHost = editorFrame
                        ? editorFrame.closest('[data-testid="stElementContainer"]')
                        : null;
                    const testcaseRegion = column.querySelector(
                        '[data-testid="stVerticalBlock"][class*="st-key-testcase_region--"]'
                    );
                    const testcaseHost = testcaseRegion
                        ? testcaseRegion.closest('[data-testid="stElementContainer"]')
                        : null;
                    const judgeHost = testcaseRegion
                        ? [...testcaseRegion.children].find(
                            (child) => child.querySelector?.(".gc-judge-panel-marker")
                        )
                        : null;
                    const actionsHost = testcaseRegion
                        ? [...testcaseRegion.children].find(
                            (child) => child.querySelector?.(".gc-console-actions-marker")
                        )
                        : null;
                    return {
                        frame,
                        host,
                        column,
                        editorFrame,
                        editorHost,
                        testcaseRegion,
                        testcaseHost,
                        judgeHost,
                        actionsHost,
                    };
                } catch (_) {
                    return null;
                }
            };

            const availableHeight = (workspace) => {
                if (!workspace?.editorHost || !workspace?.column) return 0;
                const columnRect = workspace.column.getBoundingClientRect();
                const editorRect = workspace.editorHost.getBoundingClientRect();
                const handleRect = workspace.host.getBoundingClientRect();
                const styles = window.parent.getComputedStyle(workspace.column);
                const bottomPadding = Number.parseFloat(styles.paddingBottom) || 0;
                return Math.max(
                    1,
                    Math.floor(
                        columnRect.bottom
                        - bottomPadding
                        - editorRect.top
                        - handleRect.height
                    )
                );
            };

            const naturalTestcaseHeight = (workspace) => {
                if (!workspace?.testcaseRegion) return MIN_EXPANDED_TESTCASE_HEIGHT;
                const regionStyles = window.parent.getComputedStyle(workspace.testcaseRegion);
                const paddingTop = Number.parseFloat(regionStyles.paddingTop) || 0;
                const paddingBottom = Number.parseFloat(regionStyles.paddingBottom) || 0;
                const gap = Number.parseFloat(regionStyles.rowGap) || 0;
                const judgeHeight = workspace.judgeHost
                    ? Math.max(
                        workspace.judgeHost.scrollHeight,
                        workspace.judgeHost.getBoundingClientRect().height
                    )
                    : 0;
                const actionsHeight = (
                    workspace.actionsHost
                    && workspace.actionsHost !== workspace.judgeHost
                )
                    ? Math.max(
                        workspace.actionsHost.scrollHeight,
                        workspace.actionsHost.getBoundingClientRect().height
                    )
                    : 0;
                return Math.ceil(
                    paddingTop
                    + paddingBottom
                    + judgeHeight
                    + actionsHeight
                    + (judgeHeight && actionsHeight ? gap : 0)
                    + 4
                );
            };

            const setToggleState = () => {
                toggle.setAttribute("aria-expanded", String(!collapsed));
                toggle.setAttribute(
                    "aria-label",
                    collapsed ? "Expand testcase panel" : "Minimize testcase panel"
                );
                toggle.setAttribute(
                    "title",
                    collapsed ? "Expand testcase panel" : "Minimize testcase panel"
                );
            };

            const applyTestcaseHeight = (
                requestedTestcaseHeight,
                persistRatio = false,
                allowOverflow = false
            ) => {
                const workspace = locateWorkspace();
                if (!workspace || applying) return;
                if (!collapsed && workspace.testcaseRegion) {
                    workspace.testcaseRegion.classList.remove("gc-console-collapsed");
                }
                const totalHeight = availableHeight(workspace);
                if (totalHeight <= 1) return;
                applying = true;
                try {
                    const maximumTestcase = Math.max(
                        COLLAPSED_TESTCASE_HEIGHT,
                        totalHeight - Math.min(MIN_CODE_HEIGHT, totalHeight * .55)
                    );
                    const testcaseHeight = collapsed
                        ? Math.min(COLLAPSED_TESTCASE_HEIGHT, totalHeight)
                        : Math.max(
                            Math.min(MIN_EXPANDED_TESTCASE_HEIGHT, maximumTestcase),
                            Math.min(maximumTestcase, Math.round(requestedTestcaseHeight))
                        );
                    codeHeight = Math.max(1, totalHeight - testcaseHeight);
                    splitRatio = codeHeight / totalHeight;

                    const {
                        editorFrame,
                        editorHost,
                        testcaseRegion,
                        testcaseHost,
                    } = workspace;
                    if (editorFrame && editorHost) {
                        let current = editorFrame;
                        while (current && current !== editorHost) {
                            forceHeight(current, codeHeight);
                            current = current.parentElement;
                        }
                        forceHeight(editorHost, codeHeight);
                    }
                    if (testcaseRegion && testcaseHost) {
                        const needsOverflow = !collapsed && (
                            allowOverflow
                            || naturalTestcaseHeight(workspace) > testcaseHeight + 1
                        );
                        testcaseRegion.classList.toggle("gc-console-collapsed", collapsed);
                        testcaseRegion.classList.toggle(
                            "gc-console-overflow",
                            needsOverflow
                        );
                        let current = testcaseRegion;
                        while (current && current !== testcaseHost) {
                            forceHeight(current, testcaseHeight);
                            current = current.parentElement;
                        }
                        forceHeight(testcaseHost, testcaseHeight);
                    }

                    const percent = Math.round(splitRatio * 100);
                    handle.setAttribute("aria-valuenow", String(percent));
                    handle.setAttribute(
                        "aria-valuetext",
                        collapsed
                            ? "Testcase panel minimized"
                            : `Code ${percent}%, testcases ${100 - percent}%`
                    );
                    setToggleState();
                    if (persistRatio && !collapsed) {
                        try {
                            window.localStorage.setItem(
                                RATIO_STORAGE_KEY,
                                String(splitRatio)
                            );
                        } catch (_) {}
                    }
                } finally {
                    applying = false;
                }
            };

            const autoFit = (preferSavedSize = true) => {
                const workspace = locateWorkspace();
                if (!workspace) return;
                if (!collapsed && workspace.testcaseRegion) {
                    workspace.testcaseRegion.classList.remove("gc-console-collapsed");
                }
                const totalHeight = availableHeight(workspace);
                if (totalHeight <= 1) return;
                if (collapsed) {
                    applyTestcaseHeight(COLLAPSED_TESTCASE_HEIGHT);
                    return;
                }
                const naturalHeight = naturalTestcaseHeight(workspace);
                const savedHeight = preferSavedSize
                    ? totalHeight * (1 - splitRatio)
                    : 0;
                const maximumTestcase = Math.max(
                    COLLAPSED_TESTCASE_HEIGHT,
                    totalHeight - Math.min(MIN_CODE_HEIGHT, totalHeight * .55)
                );
                const desiredHeight = Math.max(
                    MIN_EXPANDED_TESTCASE_HEIGHT,
                    naturalHeight,
                    savedHeight
                );
                applyTestcaseHeight(
                    desiredHeight,
                    false,
                    naturalHeight > maximumTestcase
                );
            };

            const setCollapsed = (nextCollapsed) => {
                collapsed = Boolean(nextCollapsed);
                try {
                    window.localStorage.setItem(
                        COLLAPSED_STORAGE_KEY,
                        collapsed ? "1" : "0"
                    );
                } catch (_) {}
                if (collapsed) {
                    applyTestcaseHeight(COLLAPSED_TESTCASE_HEIGHT);
                } else {
                    autoFit(false);
                }
            };

            try {
                const saved = Number.parseFloat(
                    window.localStorage.getItem(RATIO_STORAGE_KEY)
                );
                if (Number.isFinite(saved) && saved > .15 && saved < .95) {
                    splitRatio = saved;
                }
                collapsed = window.localStorage.getItem(COLLAPSED_STORAGE_KEY) === "1";
            } catch (_) {}

            if (FORCE_EXPAND) {
                collapsed = false;
                try {
                    window.localStorage.setItem(COLLAPSED_STORAGE_KEY, "0");
                } catch (_) {}
            }

            toggle.addEventListener("click", (event) => {
                event.stopPropagation();
                setCollapsed(!collapsed);
            });
            toggle.addEventListener("pointerdown", (event) => {
                event.stopPropagation();
            });
            handle.addEventListener("dblclick", (event) => {
                if (event.target.closest("button")) return;
                setCollapsed(!collapsed);
            });
            handle.addEventListener("pointerdown", (event) => {
                if (event.target.closest("button")) return;
                if (collapsed) setCollapsed(false);
                startY = event.screenY;
                const workspace = locateWorkspace();
                if (!workspace?.editorHost) return;
                startHeight = workspace.editorHost.getBoundingClientRect().height;
                handle.classList.add("is-dragging");
                handle.setPointerCapture(event.pointerId);
                window.parent.document.body.style.setProperty(
                    "cursor",
                    "row-resize",
                    "important"
                );
                window.parent.document.body.style.setProperty(
                    "user-select",
                    "none",
                    "important"
                );
                event.preventDefault();
            });
            handle.addEventListener("pointermove", (event) => {
                if (!handle.hasPointerCapture(event.pointerId)) return;
                const workspace = locateWorkspace();
                if (!workspace) return;
                const totalHeight = availableHeight(workspace);
                const nextCodeHeight = startHeight + event.screenY - startY;
                applyTestcaseHeight(totalHeight - nextCodeHeight);
            });
            const finishDrag = (event) => {
                if (handle.hasPointerCapture(event.pointerId)) {
                    handle.releasePointerCapture(event.pointerId);
                }
                handle.classList.remove("is-dragging");
                window.parent.document.body.style.removeProperty("cursor");
                window.parent.document.body.style.removeProperty("user-select");
                const workspace = locateWorkspace();
                if (workspace) {
                    applyTestcaseHeight(
                        availableHeight(workspace) - codeHeight,
                        true
                    );
                }
            };
            handle.addEventListener("pointerup", finishDrag);
            handle.addEventListener("pointercancel", finishDrag);
            handle.addEventListener("keydown", (event) => {
                if (event.key === "Enter" || event.key === " ") {
                    setCollapsed(!collapsed);
                    event.preventDefault();
                    return;
                }
                if (!["ArrowUp", "ArrowDown"].includes(event.key)) return;
                if (collapsed) setCollapsed(false);
                const workspace = locateWorkspace();
                if (!workspace) return;
                const totalHeight = availableHeight(workspace);
                const delta = event.key === "ArrowUp" ? 24 : -24;
                applyTestcaseHeight(totalHeight - codeHeight + delta, true);
                event.preventDefault();
            });

            const workspace = locateWorkspace();
            if (workspace && "ResizeObserver" in window) {
                columnObserver = new ResizeObserver(() => {
                    if (applying) return;
                    window.requestAnimationFrame(() => autoFit(true));
                });
                columnObserver.observe(workspace.column);
            }
            requestAnimationFrame(() => autoFit(true));
            window.setTimeout(() => autoFit(true), 120);
            window.setTimeout(() => autoFit(true), 400);
            window.setTimeout(() => autoFit(true), 900);
        })();
        </script>
    </body>
    </html>
    """
    st.iframe(
        handle_html.replace("__RATIO_STORAGE_KEY__", ratio_storage_key).replace(
            "__COLLAPSED_STORAGE_KEY__",
            collapsed_storage_key,
        ).replace("__FORCE_EXPAND__", force_expand_js),
        width="stretch",
        height=28,
    )

def render_code_workspace(
    username: str,
    problem: dict[str, Any],
    language_id: str,
    editor_font_size: int,
) -> None:
    language = LANGUAGE_BY_ID[language_id]
    state_suffix = f"{username}::{problem['id']}::{language_id}"
    draft_key = f"code::{state_suffix}"
    view_key = f"console_view::{state_suffix}"
    case_key = f"console_case::{state_suffix}"
    result_key = f"console_result::{state_suffix}"
    expand_key = f"console_force_expand::{state_suffix}"
    st.session_state.setdefault(view_key, "Testcase")
    st.session_state.setdefault(case_key, 0)
    generated_starter = starter_code(problem, language_id)
    if draft_key not in st.session_state:
        saved_draft = load_draft(username, problem["id"], language_id)
        is_legacy_default = bool(
            saved_draft
            and (
                (
                    language_id == "python"
                    and saved_draft.strip() == str(problem["starter_code"]).strip()
                )
                or (
                    language_id == "javascript"
                    and re.fullmatch(
                        r"\s*function\s+solve\([^)]*\)\s*\{\s*"
                        r"//\s*Write your solution here\s*\}\s*",
                        saved_draft,
                    )
                    is not None
                )
            )
        )
        st.session_state[draft_key] = (
            generated_starter if is_legacy_default else (saved_draft or generated_starter)
        )

    editor_response = code_editor(
        st.session_state[draft_key],
        lang=language.editor_mode,
        theme="light",
        shortcuts="vscode",
        height="480px",
        focus=False,
        allow_reset=True,
        # Debounce caused the full Streamlit script to rerun while typing,
        # which recreated the editor and made the cursor/text flicker.
        response_mode="blur",
        options={
            "fontSize": editor_font_size,
            "tabSize": 4,
            "useSoftTabs": True,
            "navigateWithinSoftTabs": True,
            "showPrintMargin": False,
            "showGutter": True,
            "showLineNumbers": True,
            "fixedWidthGutter": True,
            # Wrap long lines at the visible editor width instead of creating
            # a horizontal scroll area.
            "wrap": True,
            "indentedSoftWrap": False,
            "hScrollBarAlwaysVisible": False,
            "displayIndentGuides": True,
            "cursorStyle": "line",
            "enableBasicAutocompletion": True,
            "enableLiveAutocompletion": False,
            "highlightActiveLine": True,
            "highlightSelectedWord": True,
        },
        props={
            "style": {
                "border": "0",
                "borderRadius": "0",
                "fontFamily": (
                    "Menlo, Monaco, Consolas, Liberation Mono, monospace"
                ),
            },
        },
        component_props={"globalCSS": LEETCODE_EDITOR_CSS},
        key=f"editor::{state_suffix}",
    )
    editor_response = editor_response or {}
    response_id = editor_response.get("id")
    response_text = editor_response.get("text")

    # The component returns an empty response dictionary on first render.
    # Never let that blank response overwrite the starter code or saved draft.
    if response_id and response_text is not None:
        st.session_state[draft_key] = response_text
        save_draft(username, problem["id"], response_text, language_id)

    code = st.session_state[draft_key]
    force_expand = bool(st.session_state.pop(expand_key, False))
    with st.container(key=f"resize_handle::{username}"):
        render_workspace_resizer(username, force_expand=force_expand)

    visible_case_count = min(3, len(problem["tests"]))
    run_clicked = False
    submit_clicked = False

    with st.container(key=f"testcase_region::{state_suffix}"):
        with st.container(
            border=False,
            key=f"judge_panel::{state_suffix}",
        ):
            st.markdown(
                '<div class="gc-judge-panel-marker" aria-hidden="true"></div>',
                unsafe_allow_html=True,
            )

            tabs_col, run_col, submit_col = st.columns([2.5, 1.15, 1.35])
            with tabs_col:
                st.markdown(
                    '<div class="gc-console-actions-marker" aria-hidden="true"></div>',
                    unsafe_allow_html=True,
                )
                console_view = st.segmented_control(
                    "Console",
                    ["Testcase", "Test Result"],
                    key=view_key,
                    label_visibility="collapsed",
                )
            with run_col:
                st.markdown(
                    '<div class="gc-run-action-marker" aria-hidden="true"></div>',
                    unsafe_allow_html=True,
                )
                run_clicked = st.button(
                    "Run",
                    key=f"run::{state_suffix}",
                    width="stretch",
                    on_click=set_console_view,
                    args=(view_key, "Test Result"),
                )
            with submit_col:
                st.markdown(
                    '<div class="gc-submit-action-marker" aria-hidden="true"></div>',
                    unsafe_allow_html=True,
                )
                submit_clicked = st.button(
                    "Submit",
                    type="primary",
                    key=f"submit::{state_suffix}",
                    width="stretch",
                    on_click=set_console_view,
                    args=(view_key, "Test Result"),
                )

            if console_view == "Testcase":
                selected_case = st.pills(
                    "Testcases",
                    options=list(range(visible_case_count)),
                    format_func=lambda index: f"Case {index + 1}",
                    key=case_key,
                    label_visibility="collapsed",
                )
                if selected_case is None:
                    selected_case = 0
                render_testcase_fields(
                    problem,
                    list(problem["tests"][int(selected_case)]["args"]),
                )
            else:
                render_console_result(
                    problem,
                    st.session_state.get(result_key),
                )

    if run_clicked:
        save_draft(username, problem["id"], code, language_id)
        selected_case = int(st.session_state.get(case_key, 0))
        with st.spinner("Running testcase..."):
            result = run_tests(
                code,
                [problem["tests"][selected_case]],
                language=language_id,
                problem=problem,
            )
        st.session_state[result_key] = {
            "kind": "run",
            "case_index": selected_case,
            "result": result,
        }
        st.session_state[expand_key] = True
        st.rerun()

    if submit_clicked:
        save_draft(username, problem["id"], code, language_id)
        with st.spinner("Submitting..."):
            result = run_tests(
                code,
                problem["tests"],
                language=language_id,
                problem=problem,
            )
        mistake_type, _ = classify_mistake(result, code)
        notes = load_guide_notes(username, problem["id"])
        planning_steps = sum(
            bool(notes.get(index, "").strip())
            for index in range(len(problem["guide"]))
        )
        hint_level = int(
            st.session_state.get(
                f"hint_level::{username}::{problem['id']}",
                0,
            )
        )
        independence = save_attempt(
            username,
            problem["id"],
            code,
            result,
            mistake_type,
            problem["tags"],
            hint_level=hint_level,
            planning_steps=planning_steps,
            language=language_id,
        )
        st.session_state[result_key] = {
            "kind": "submit",
            "result": result,
        }
        st.session_state[
            f"independence::{state_suffix}"
        ] = independence
        st.session_state[expand_key] = True
        st.rerun()


with st.sidebar:
    st.markdown("## GuidedCode")
    st.caption(f"Learn the reasoning, not only the answer. · {len(PROBLEMS)} problems")
    username = st.text_input("Learner profile", key="username", max_chars=40).strip() or "learner"
    st.radio(
        "Navigation",
        ["Dashboard", "Practice", "Problem Library"],
        key="navigation",
        on_change=sync_navigation_to_url,
        label_visibility="collapsed",
    )
    if st.session_state.navigation == "Practice":
        problem_ids = [
            problem["id"]
            for problem in PROBLEMS
        ]

        if (
            st.session_state.current_problem_id
            not in problem_ids
        ):
            st.session_state.current_problem_id = problem_ids[0]

        active_title = PROBLEM_ID_TO_TITLE[
            st.session_state.current_problem_id
        ]

        picker_title = st.session_state.get(
            PROBLEM_PICKER_KEY
        )

        if (
            picker_title not in PROBLEM_TITLE_TO_ID
            or PROBLEM_TITLE_TO_ID[picker_title]
            != st.session_state.current_problem_id
        ):
            st.session_state[
                PROBLEM_PICKER_KEY
            ] = active_title

        st.markdown(
            (
                '<div class="gc-sidebar-problem-label">'
                "Problem"
                "</div>"
            ),
            unsafe_allow_html=True,
        )

        st.selectbox(
            "Choose a problem",
            options=list(PROBLEM_TITLE_TO_ID),
            key=PROBLEM_PICKER_KEY,
            on_change=select_problem_from_picker,
            placeholder="Search or choose a problem",
            label_visibility="collapsed",
        )

    st.divider()
    st.caption("Local MVP runner. Use isolated execution infrastructure before public deployment.")

page = st.session_state.navigation

if page == "Dashboard":
    dashboard = get_dashboard(username)
    recommendation = recommend_problem(dashboard)

    st.markdown(
        """
        <div class="gc-hero">
            <div class="gc-eyebrow">Personal learning dashboard</div>
            <div class="gc-title">Measure learning, not submissions.</div>
            <div class="gc-subtitle">
                Track which patterns you can recall independently, where your
                reasoning breaks, and what to revisit next.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    metric_cols = st.columns(4)
    metric_cols[0].metric("Solved", dashboard["solved"])
    metric_cols[1].metric("Attempts", dashboard["attempts"])
    metric_cols[2].metric(
        "Independent solves",
        dashboard["independent_solves"],
        help="Problems passed without revealing a hint.",
    )
    average_mastery = (
        sum(float(row["score"]) for row in dashboard["mastery"]) / len(dashboard["mastery"])
        if dashboard["mastery"]
        else 0
    )
    metric_cols[3].metric("Average mastery", f"{average_mastery:.0f}%")

    left, right = st.columns([1.15, 1], gap="large")
    with left:
        st.subheader("Recommended next")
        with st.container(border=True):
            st.markdown(f"### {recommendation['title']}")
            st.write(recommendation["summary"])
            st.caption(f"{recommendation['difficulty']} · {' · '.join(recommendation['tags'])}")
            st.button(
                "Start guided practice",
                type="primary",
                on_click=open_problem,
                args=(recommendation["id"],),
                width="stretch",
            )

        st.subheader("Recent attempts")
        if dashboard["recent"]:
            recent_rows = []
            for row in dashboard["recent"]:
                problem = PROBLEM_BY_ID.get(row["problem_id"], {"title": row["problem_id"]})
                recent_rows.append(
                    {
                        "Problem": problem["title"],
                        "Language": LANGUAGE_BY_ID.get(
                            str(row.get("language", "python")),
                            LANGUAGE_BY_ID["python"],
                        ).label,
                        "Result": f"{row['passed']}/{row['total']}",
                        "Diagnosis": row["mistake_type"],
                        "Learning mode": row.get("independence", "Unrated"),
                        "When": datetime.fromisoformat(row["created_at"]).strftime("%b %d, %H:%M"),
                    }
                )
            st.dataframe(pd.DataFrame(recent_rows), width="stretch", hide_index=True)
        else:
            st.info("Run your first solution to populate the dashboard.")

        st.subheader("Recall queue")
        if dashboard["review_due"]:
            st.caption(
                "Problems return after three quiet days. Solve them from memory "
                "to turn short-term recognition into durable recall."
            )
            for row in dashboard["review_due"]:
                review_problem = PROBLEM_BY_ID.get(row["problem_id"])
                if not review_problem:
                    continue
                last_practiced = datetime.fromisoformat(row["last_practiced"])
                days_ago = max(
                    3,
                    (datetime.now(last_practiced.tzinfo) - last_practiced).days,
                )
                with st.container(border=True):
                    recall_info, recall_action = st.columns([3, 1])
                    recall_info.markdown(f"**{review_problem['title']}**")
                    recall_info.caption(
                        f"Last practiced {days_ago} days ago · "
                        f"{' · '.join(review_problem['tags'])}"
                    )
                    recall_action.button(
                        "Recall now",
                        key=f"recall::{username}::{review_problem['id']}",
                        on_click=open_problem,
                        args=(review_problem["id"],),
                        width="stretch",
                    )
        else:
            st.caption(
                "Accepted problems will reappear here after three quiet days "
                "for a memory-first replay."
            )

    with right:
        st.subheader("Concept mastery")
        if dashboard["mastery"]:
            mastery_df = pd.DataFrame(dashboard["mastery"])[["tag", "score"]].rename(
                columns={"tag": "Concept", "score": "Mastery"}
            )
            st.bar_chart(mastery_df.set_index("Concept"))
            weakest = mastery_df.sort_values("Mastery").head(3)
            for _, row in weakest.iterrows():
                st.write(f"**{row['Concept']}** — {row['Mastery']:.0f}%")
                st.progress(min(float(row["Mastery"]) / 100.0, 1.0))
        else:
            st.info("Mastery estimates appear after your first submission.")

        st.subheader("Recurring mistakes")
        if dashboard["mistakes"]:
            st.dataframe(
                pd.DataFrame(dashboard["mistakes"]).rename(
                    columns={"mistake_type": "Mistake", "count": "Occurrences"}
                ),
                width="stretch",
                hide_index=True,
            )
        else:
            st.caption("No recurring mistake pattern detected yet.")

        st.download_button(
            "Export progress",
            data=export_progress(username),
            file_name=f"{username}_guidedcode_progress.json",
            mime="application/json",
            width="stretch",
        )

elif page == "Problem Library":
    st.title("Problem Library")
    st.caption(f"{len(PROBLEMS)} curated problems with guided reasoning, progressive hints, and personalized feedback.")

    filter_cols = st.columns([1, 1.4, 2])
    difficulties = ["All", *sorted({problem["difficulty"] for problem in PROBLEMS}, key=lambda value: ["Easy", "Medium", "Hard"].index(value) if value in ["Easy", "Medium", "Hard"] else 99)]
    difficulty = filter_cols[0].selectbox("Difficulty", difficulties)
    all_tags = sorted({tag for problem in PROBLEMS for tag in problem["tags"]})
    selected_tags = filter_cols[1].multiselect("Concepts", all_tags)
    search = filter_cols[2].text_input("Search", placeholder="Search titles or concepts").strip().lower()

    filtered = []
    for problem in PROBLEMS:
        if difficulty != "All" and problem["difficulty"] != difficulty:
            continue
        if selected_tags and not set(selected_tags).intersection(problem["tags"]):
            continue
        haystack = " ".join([problem["title"], problem["summary"], *problem["tags"]]).lower()
        if search and search not in haystack:
            continue
        filtered.append(problem)

    page_size = 24
    page_count = max(1, (len(filtered) + page_size - 1) // page_size)
    result_col, page_col = st.columns([4, 1])
    with result_col:
        st.write(f"{len(filtered)} problem{'s' if len(filtered) != 1 else ''}")
    with page_col:
        page_number = st.selectbox(
            "Page",
            options=list(range(1, page_count + 1)),
            format_func=lambda value: f"Page {value} of {page_count}",
            label_visibility="collapsed",
        )
    page_start = (int(page_number) - 1) * page_size
    page_end = min(page_start + page_size, len(filtered))
    if filtered:
        st.caption(f"Showing {page_start + 1}–{page_end}")

    for problem in filtered[page_start:page_end]:
        with st.container(border=True):
            info_col, action_col = st.columns([5, 1])
            with info_col:
                st.markdown(f"### {problem['title']}")
                st.write(problem["summary"])
                st.caption(f"{problem['difficulty']} · {' · '.join(problem['tags'])}")
            with action_col:
                st.button(
                    "Practice",
                    key=f"library_{problem['id']}",
                    on_click=open_problem,
                    args=(problem["id"],),
                    width="stretch",
                )

else:
    st.markdown(
        '<div class="gc-practice-workspace-marker" aria-hidden="true"></div>',
        unsafe_allow_html=True,
    )
    problem = PROBLEM_BY_ID[st.session_state.current_problem_id]

    problem_col, divider_col, code_col = st.columns(
        [1, 0.025, 1.08],
        gap=None,
    )

    with problem_col:
        # The left pane itself is recreated whenever a problem is activated.
        # A fresh DOM node always starts at scrollTop = 0, so Streamlit cannot
        # carry the previous problem's internal scroll position into this one.
        problem_view_nonce = int(
            st.session_state.get("problem_view_nonce", 0)
        )
        with st.container(
            key=f"problem_scroll::{problem_view_nonce}",
            height="stretch",
        ):
            st.markdown(
                (
                    '<div class="gc-problem-pane-marker '
                    'gc-problem-pane-anchor" aria-hidden="true"></div>'
                ),
                unsafe_allow_html=True,
            )
            render_problem_scroll_reset(problem_view_nonce)
            render_problem_header(problem)
            st.markdown(problem["description"])
            if SHOW_GUIDED_SECTIONS:
                st.markdown(
                    '<div class="gc-before-predict" '
                    'aria-hidden="true"></div>',
                    unsafe_allow_html=True,
                )

                st.markdown("### Predict before you peek")
                with st.expander(
                    "Open prediction exercise",
                    expanded=False,
                ):
                    render_active_recall(username, problem)

                st.markdown("### Plan checkpoint")
                with st.expander(
                    "Open planning prompts",
                    expanded=False,
                ):
                    render_guided_reasoning(username, problem)

            render_examples(problem)
            render_constraints(problem)
            render_topics_and_hints(problem)
            st.markdown(
                '<div class="gc-problem-pane-end" '
                'aria-hidden="true"></div>',
                unsafe_allow_html=True,
            )

    with divider_col:
        st.markdown(
            '<div class="gc-column-resizer-marker" aria-hidden="true"></div>',
            unsafe_allow_html=True,
        )
        render_column_resizer(username)

    with code_col:
        language_key = f"language::{username}::{problem['id']}"
        if st.session_state.get(language_key) not in LANGUAGE_BY_ID:
            st.session_state[language_key] = "python"
        font_size_key = f"editor_font_size::{username}"
        st.session_state.setdefault(font_size_key, 16)
        code_bar_title, code_bar_font_size, code_bar_language = st.columns(
            [4.15, 0.7, 1.2],
            gap=None,
            vertical_alignment="center",
        )
        with code_bar_title:
            st.markdown(
                """
                <div class="gc-code-bar-marker gc-code-pane-marker">
                    <span class="gc-pane-title">Code</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with code_bar_font_size:
            editor_font_size = st.selectbox(
                "Editor font size",
                options=[12, 14, 16, 18, 20, 22, 24],
                key=font_size_key,
                format_func=lambda size: f"{size}px",
                label_visibility="collapsed",
            )
        with code_bar_language:
            language_id = st.selectbox(
                "Coding language",
                options=[language.id for language in LANGUAGES],
                format_func=lambda value: LANGUAGE_BY_ID[value].label,
                key=language_key,
                label_visibility="collapsed",
            )
        render_code_workspace(
            username,
            problem,
            language_id,
            editor_font_size,
        )
