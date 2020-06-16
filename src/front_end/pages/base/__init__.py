import dash_bootstrap_components as dbc
import dash_html_components as html

from ..enums import Element as El
from . import components


def BASE_LAYOUT():
    return html.Div(
        [
            components.make_header_bar(),
            components.make_navigation_bar(),
            dbc.Container(id=El.PAGE_CONTENT.value),
        ]
    )
