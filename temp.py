from __future__ import annotations

import re
from pathlib import Path


SOURCE_CANDIDATES = [
    Path("app(40).py"),
    Path("app.py"),
]

source_path = next(
    (path for path in SOURCE_CANDIDATES if path.exists()),
    None,
)

if source_path is None:
    raise FileNotFoundError(
        "Could not find app(40).py or app.py in this folder."
    )

text = source_path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# 1. Add the pending-navigation state key.
# ---------------------------------------------------------------------------

old_constants = '''PROBLEM_PICKER_KEY = "practice_problem_picker"
RELATED_PROBLEM_LIMIT = 6
'''

new_constants = '''PROBLEM_PICKER_KEY = "practice_problem_picker"
PENDING_PROBLEM_REDIRECT_KEY = "pending_problem_redirect"
RELATED_PROBLEM_LIMIT = 6
'''

if "PENDING_PROBLEM_REDIRECT_KEY" not in text:
    if old_constants not in text:
        raise RuntimeError(
            "Could not locate the problem-picker constants."
        )

    text = text.replace(
        old_constants,
        new_constants,
        1,
    )


# ---------------------------------------------------------------------------
# 2. Remove the unsuccessful in-place scroll-reset state.
# ---------------------------------------------------------------------------

text = text.replace(
    '        "reset_problem_view": False,\n',
    "",
)


# ---------------------------------------------------------------------------
# 3. Replace all existing problem-navigation and scroll-reset functions.
# ---------------------------------------------------------------------------

navigation_pattern = re.compile(
    r"def activate_problem\(problem_id: str\) -> None:"
    r".*?"
    r"(?=def normalize_related_topic)",
    flags=re.DOTALL,
)

new_navigation = '''def activate_problem(problem_id: str) -> None:
    """
    Activate a problem after a fresh browser navigation.
    """
    if problem_id not in PROBLEM_BY_ID:
        return

    st.session_state.current_problem_id = problem_id
    st.session_state[PROBLEM_PICKER_KEY] = PROBLEM_ID_TO_TITLE[
        problem_id
    ]
    st.session_state.navigation = "Practice"

    # New expander keys ensure Topics, Related Problems, and Hints
    # all begin folded for the newly opened problem.
    st.session_state.problem_view_nonce = (
        int(st.session_state.get("problem_view_nonce", 0)) + 1
    )


def queue_problem_navigation(problem_id: str) -> None:
    """
    Queue a full browser navigation.

    A full navigation prevents Streamlit from preserving the previous
    problem pane's scroll position and open expander state.
    """
    if problem_id not in PROBLEM_BY_ID:
        return

    if problem_id == st.session_state.current_problem_id:
        return

    st.session_state[
        PENDING_PROBLEM_REDIRECT_KEY
    ] = problem_id


def load_problem_from_query_parameter() -> None:
    requested_problem_id = st.query_params.get("problem")

    if not requested_problem_id:
        return

    if requested_problem_id not in PROBLEM_BY_ID:
        return

    if (
        requested_problem_id
        != st.session_state.current_problem_id
    ):
        activate_problem(requested_problem_id)


load_problem_from_query_parameter()


def open_problem(problem_id: str) -> None:
    queue_problem_navigation(problem_id)


def select_problem_from_picker() -> None:
    selected_title = st.session_state.get(
        PROBLEM_PICKER_KEY
    )

    selected_id = PROBLEM_TITLE_TO_ID.get(
        selected_title
    )

    if not selected_id:
        return

    queue_problem_navigation(selected_id)


'''

text, replacement_count = navigation_pattern.subn(
    lambda _: new_navigation,
    text,
    count=1,
)

if replacement_count != 1:
    raise RuntimeError(
        "Could not replace the existing problem-navigation block."
    )


# ---------------------------------------------------------------------------
# 4. Redirect before rendering the sidebar or workspace.
# ---------------------------------------------------------------------------

redirect_block = '''pending_problem_id = st.session_state.pop(
    PENDING_PROBLEM_REDIRECT_KEY,
    None,
)

if pending_problem_id:
    encoded_problem_id = quote(
        str(pending_problem_id),
        safe="",
    )

    redirect_path = (
        f"?problem={encoded_problem_id}"
        "#problem-top"
    )

    redirect_path_json = json.dumps(
        redirect_path
    )

    components.html(
        f"""
        <script>
        (() => {{
            const redirectPath = {redirect_path_json};
            const parentWindow = window.parent;

            if (
                "scrollRestoration"
                in parentWindow.history
            ) {{
                parentWindow.history.scrollRestoration = "manual";
            }}

            const destination = new URL(
                redirectPath,
                parentWindow.location.href
            );

            parentWindow.location.replace(
                destination.toString()
            );
        }})();
        </script>
        """,
        height=0,
        width=0,
    )

    st.stop()


'''

if "pending_problem_id = st.session_state.pop(" not in text:
    sidebar_marker = "\nwith st.sidebar:\n"

    if sidebar_marker not in text:
        raise RuntimeError(
            "Could not locate the sidebar section."
        )

    text = text.replace(
        sidebar_marker,
        "\n" + redirect_block + "with st.sidebar:\n",
        1,
    )


# ---------------------------------------------------------------------------
# 5. Remove the old JavaScript scroll-reset call.
# ---------------------------------------------------------------------------

text = text.replace(
    "        reset_problem_pane_scroll()\n",
    "",
)


# ---------------------------------------------------------------------------
# 6. Add a reliable destination anchor at the top of the problem pane.
# ---------------------------------------------------------------------------

old_problem_pane_start = '''    with problem_col:
        st.markdown(
            (
                '<div class="gc-problem-pane-marker gc-problem-pane-anchor" '
                'aria-hidden="true"></div>'
            ),
            unsafe_allow_html=True,
        )
'''

new_problem_pane_start = '''    with problem_col:
        st.markdown(
            (
                '<div id="problem-top" '
                'class="gc-problem-top-anchor" '
                'aria-hidden="true"></div>'
            ),
            unsafe_allow_html=True,
        )

        st.markdown(
            (
                '<div class="gc-problem-pane-marker gc-problem-pane-anchor" '
                'aria-hidden="true"></div>'
            ),
            unsafe_allow_html=True,
        )
'''

if "id=\"problem-top\"" not in text:
    if old_problem_pane_start not in text:
        raise RuntimeError(
            "Could not locate the beginning of the problem pane."
        )

    text = text.replace(
        old_problem_pane_start,
        new_problem_pane_start,
        1,
    )


# ---------------------------------------------------------------------------
# 7. Make Related Problems use the same top-reset navigation.
# ---------------------------------------------------------------------------

text = text.replace(
    'f\'href="?problem={problem_id}" \'',
    'f\'href="?problem={problem_id}#problem-top" \'',
)


# ---------------------------------------------------------------------------
# 8. Add styling for the zero-height top anchor.
# ---------------------------------------------------------------------------

anchor_css = '''    .gc-problem-top-anchor {
        display: block;
        height: 0;
        margin: 0;
        padding: 0;
        scroll-margin-top: 0;
    }

'''

if ".gc-problem-top-anchor {" not in text:
    css_marker = (
        "    /* Prevent browser/OS dark mode "
        "from recoloring controls */"
    )

    if css_marker not in text:
        raise RuntimeError(
            "Could not locate the end of the global CSS section."
        )

    text = text.replace(
        css_marker,
        anchor_css + css_marker,
        1,
    )


# ---------------------------------------------------------------------------
# 9. Validate and write the updated application.
# ---------------------------------------------------------------------------

compile(
    text,
    "app.py",
    "exec",
)

output_path = Path("app.py")
output_path.write_text(
    text,
    encoding="utf-8",
)

print(f"Created: {output_path.resolve()}")