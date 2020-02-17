import operator
from io import BytesIO

import cairosvg
import leather


def _tick_formatter(value, _index, _tick_count):
    """Just convert to string"""
    return f"{value}"


def make(values, title=None, x_name: str = None,
         y_name: str = None) -> BytesIO:
    """Make chart image from values and return as stream"""

    if not isinstance(values, list):
        values = list(values)

    # sort by x
    values = sorted(values, key=operator.itemgetter(0))

    bio = BytesIO()
    bio.name = 'chart.jpeg'

    chart = leather.Chart(title)

    chart.add_x_axis(name=x_name, tick_formatter=_tick_formatter)
    chart.add_y_axis(name=y_name, tick_formatter=_tick_formatter)

    chart.add_line(values)

    svg_data = chart.to_svg(width=1200, height=800)
    bio.write(cairosvg.svg2png(svg_data))
    bio.seek(0)
    return bio
