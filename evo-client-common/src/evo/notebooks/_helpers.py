from pathlib import Path
from typing import TypeAlias

import ipywidgets as widgets

from evo.common.utils import Cache

from . import assets
from ._consts import DEFAULT_CACHE_LOCATION

FileName: TypeAlias = str | Path


def init_cache(cache_location: FileName = DEFAULT_CACHE_LOCATION) -> Cache:
    """Initialise the storage location for the notebook environment.

    Configures the cache location and creates a `.gitignore` file in the root of the cache directory.

    :param cache_location: The location for the cache directory.

    :returns: A Cache instance.
    """
    cache = Cache(cache_location, mkdir=True)
    ignorefile = cache.root / ".gitignore"
    ignorefile.write_text("*\n")
    return cache


def build_img_widget(filename: str) -> widgets.Image:
    image = assets.get(filename).read_bytes()
    return widgets.Image(
        value=image,
        format="png",
        layout=widgets.Layout(max_height="26px", margin="3px", align_self="center"),
    )


def build_button_widget(text: str) -> widgets.Button:
    widget = widgets.Button(
        description=text,
        button_style="info",
        layout=widgets.Layout(margin="5px 5px 5px 5px", align_self="center"),
    )
    widget.style.button_color = "#265C7F"
    return widget
