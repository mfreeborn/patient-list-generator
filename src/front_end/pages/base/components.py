import dash_bootstrap_components as dbc
import dash_html_components as html

from ....version import __version__
from ..enums import Element as El


def make_header_bar():
    return dbc.Row(
        [
            dbc.Col(),
            dbc.Col(html.H3("Patient List Generator", className="app-title")),
            dbc.Col(html.P(f"v{__version__}", className="version-string")),
        ],
        className="header-bar",
    )


def make_navigation_bar():
    return dbc.Row(
        [
            dbc.Col(),
            dbc.Col(
                dbc.Tabs(
                    [dbc.Tab(label="Generate List", tab_id=El.GENERATE_LIST_TAB.value)],
                    id=El.NAV_TABS.value,
                    active_tab=El.GENERATE_LIST_TAB.value,
                    persistence=True,
                    persistence_type="session",
                )
            ),
            dbc.Col(),
        ],
        className="navigation-bar",
    )
