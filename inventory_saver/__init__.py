from mods_base import build_mod

from .hooks import (
    close_storage,
    generate_save,
    load_save,
    open_storage,
    post_load_save,
    refresh_vendor,
    validate_definition,
)
from .settings import PROTECT_ITEMS, REFRESH_VENDORS

build_mod(
    hooks=[
        close_storage,
        generate_save,
        load_save,
        validate_definition,
        open_storage,
        refresh_vendor,
        post_load_save,
    ],
    options=[PROTECT_ITEMS, REFRESH_VENDORS],
)
