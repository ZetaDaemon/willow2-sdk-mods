from mods_base import build_mod

from .hooks import (
    close_bank,
    generate_save,
    load_save,
    open_bank,
    post_load_save,
    refresh_vendor,
    validate_definition,
)
from .settings import PROTECT_ITEMS, REFRESH_VENDORS

build_mod(
    hooks=[
        close_bank,
        generate_save,
        load_save,
        validate_definition,
        open_bank,
        refresh_vendor,
        post_load_save,
    ],  # pyright: ignore[reportUnknownArgumentType]
    options=[PROTECT_ITEMS, REFRESH_VENDORS],
)
