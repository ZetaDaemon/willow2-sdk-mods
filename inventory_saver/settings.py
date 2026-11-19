from mods_base.options import BoolOption

PROTECT_ITEMS = BoolOption(
    "Protect Items",
    True,
    description="Protect items with unknown parts from breaking by not loading.",
)

IGNORE_LOAD_WARNING = BoolOption(
    "Ignore Load Warning",
    False,
    description="Ignore the warning popup that occurs when unable to load all items.",
)

REFRESH_VENDORS = BoolOption(
    "Refresh Vendors",
    False,
    description="Automatically refresh vendors on map load to remove broken items.",
)


REMOVE_MODDED_GROUND_ITEMS = BoolOption(
    "Remove Ground Items",
    False,
    description="Remove ground items with modded parts on map transition.",
)
