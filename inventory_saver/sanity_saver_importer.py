"""Import Sanity Saver inventory records at character load or bank open."""

from __future__ import annotations

import base64
import gzip
import json
import os
import sys
from copy import deepcopy
from functools import cache
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import TYPE_CHECKING, Any

import unrealsdk
from mods_base import MODS_DIR

from .item_codes import (
    INTEGER_OVERRIDE_FIELDS,
    ITEM_CODE_FIELDS,
    WEAPON_CODE_FIELDS,
    WILLOW_ITEM_CLASS,
    WILLOW_WEAPON_CLASS,
    ZDICT_BYTES,
    encode_modded_code,
    pack_serial,
    validate_serial,
)
from .saves import PlayerSaveData, get_save_path

if TYPE_CHECKING:
    from bl2.WillowGame import PlayerSaveGame, WillowInventoryStorage

LegacyRecord = dict[str, Any]


@cache
def find_sanity_saver_saves() -> Path | None:
    roots = [MODS_DIR, MODS_DIR.parent / "Mods", *(Path(p) for p in sys.path if p)]
    candidates: set[Path] = set()

    for root in roots:
        saves = root / "SanitySaver" / "Saves"
        if saves.is_dir():
            candidates.add(saves.resolve())

    if len(candidates) > 1:
        msg = "Multiple Sanity Saver save directories found"
        raise ValueError(msg)

    return next(iter(candidates), None)


def _atomic_write(path: Path, contents: bytes) -> None:
    temporary: Path | None = None
    try:
        with NamedTemporaryFile(dir=path.parent, delete=False) as file:
            temporary = Path(file.name)
            file.write(contents)
            file.flush()
            os.fsync(file.fileno())
        temporary.replace(path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def _json_bytes(data: object) -> bytes:
    return (json.dumps(data, indent=2) + "\n").encode("utf-8")


def _read_legacy(saves_dir: Path, stem: str) -> tuple[Path, bytes, dict[str, LegacyRecord]] | None:
    candidates: list[tuple[int, Path]] = []
    for extension in (".json.gz", ".json"):
        path = saves_dir / f"{stem}{extension}"
        try:
            candidates.append((path.stat().st_mtime_ns, path))
        except FileNotFoundError:
            continue
    if not candidates:
        return None

    # Prefer the newest copy, matching Sanity Saver's compression handling.
    _, path = max(candidates, key=lambda candidate: candidate[0])
    original = path.read_bytes()
    payload = gzip.decompress(original) if path.suffix == ".gz" else original
    document = json.loads(payload)
    if not isinstance(document, dict):
        msg = f"Invalid Sanity Saver save at {path}"
        raise ValueError(msg)  # noqa: TRY004

    version = document.get("save_version", 1)
    if version == 2 and isinstance(document.get("items"), dict):
        records = {
            item_id: record
            for item_id, record in document["items"].items()
            if isinstance(record, dict)
        }
    elif version == 1 and all(
        isinstance(document.get(section), dict) for section in ("replacements", "new_items")
    ):
        records = {}
        replacements = document["replacements"]
        snapshots = document["new_items"]
        for item_id in replacements.keys() | snapshots.keys():
            # Leave ambiguous IDs in the source instead of guessing between copies.
            if item_id in replacements and item_id in snapshots:
                continue
            entries = snapshots.get(item_id, replacements.get(item_id))
            if isinstance(entries, list) and len(entries) == 1 and isinstance(entries[0], dict):
                records[item_id] = entries[0].copy()
                if item_id in snapshots:
                    records[item_id]["_inital"] = True
    else:
        msg = f"Unsupported Sanity Saver save format at {path}"
        raise ValueError(msg)

    return path, original, records


def _convert_code(definition: Any, record: LegacyRecord, *, is_weapon: bool) -> str | None:
    fields = WEAPON_CODE_FIELDS if is_weapon else ITEM_CODE_FIELDS
    inventory_class = WILLOW_WEAPON_CLASS if is_weapon else WILLOW_ITEM_CLASS
    overrides: dict[str, str | int | None] = {}

    for field in fields:
        if field not in record:
            continue

        value = record[field]
        if field in INTEGER_OVERRIDE_FIELDS:
            if type(value) is not int:
                msg = f"Invalid integer for {field}"
                raise ValueError(msg)
        elif value == "None":
            value = None
        elif value is not None and not isinstance(value, str):
            msg = f"Invalid object path for {field}"
            raise ValueError(msg)

        if "_inital" in record:
            if isinstance(value, str) and value.startswith("Transient"):
                continue
            current = getattr(definition, field)
            if field not in INTEGER_OVERRIDE_FIELDS and current is not None:
                current = current._path_name()
            if current == value:
                continue

        overrides[field] = value

    if not overrides:
        return None

    serial, _ = inventory_class.ClassDefaultObject.PackSerialNumber(definition)
    base = pack_serial(serial)
    validate_serial(base64.b64decode(base, validate=True))
    return encode_modded_code(base, overrides, fields, ZDICT_BYTES)


def _commit_import(
    save_id: int,
    save_data: PlayerSaveData,
    updated: PlayerSaveData,
    path: Path,
    original: bytes,
    imported: set[str],
) -> int:
    if not imported:
        return 0

    backup = path.with_name(f"{path.name}.bak")
    if not backup.exists():
        _atomic_write(backup, original)

    if updated != save_data:
        _atomic_write(get_save_path(save_id), _json_bytes(updated))
        save_data.update(updated)

    try:
        if path.read_bytes() != original:
            unrealsdk.logging.warning(f"Sanity Saver file changed during import: {path}")
        else:
            path.unlink()
    except OSError as exc:
        unrealsdk.logging.warning(f"Could not clean up Sanity Saver file {path}: {exc}")

    return len(imported)


def import_inventory(
    save: PlayerSaveGame, save_data: PlayerSaveData, sanity_saver_saves: Path
) -> int:
    """Import matching character records before the normal inventory restore pass."""
    save_id = save.SaveGameId
    if save_id < 0:
        return 0
    stem = f"Save{save_id & 0xFFFF:04X}"
    source = _read_legacy(sanity_saver_saves, stem)
    if source is None:
        return 0

    path, original, legacy = source
    updated = deepcopy(save_data)
    imported: set[str] = set()

    for entry in save.WeaponData:
        if entry is None or entry.WeaponDefinitionData is None:
            continue
        definition = entry.WeaponDefinitionData
        item_id = str(definition.UniqueId)
        record = legacy.get(item_id)
        if record is None or item_id in imported:
            continue

        code = _try_convert(definition, record, item_id, is_weapon=True)
        if code is None:
            continue

        existing = updated["weapons"].get(item_id) or updated["backup"]["weapons"].get(item_id)
        if existing is None:
            updated["weapons"][item_id] = {
                "code": code,
                "mark": int(entry.Mark),
                "quantity": 1,
                "quick_slot": int(entry.QuickSlot),
            }
        elif existing["code"] != code:
            continue
        imported.add(item_id)

    for entry in save.ItemData:
        if entry is None or entry.DefinitionData is None:
            continue
        definition = entry.DefinitionData
        item_id = str(definition.UniqueId)
        record = legacy.get(item_id)
        if record is None or item_id in imported:
            continue

        code = _try_convert(definition, record, item_id, is_weapon=False)
        if code is None:
            continue

        existing = updated["items"].get(item_id) or updated["backup"]["items"].get(item_id)
        if existing is None:
            updated["items"][item_id] = {
                "code": code,
                "mark": int(entry.Mark),
                "quantity": entry.Quantity,
                "readied": entry.bEquipped,
            }
        elif existing["code"] != code:
            continue
        imported.add(item_id)

    return _commit_import(save_id, save_data, updated, path, original, imported)


def import_bank(
    bank: WillowInventoryStorage, save_id: int, save_data: PlayerSaveData, sanity_saver_saves: Path
) -> int:
    """Import matching live bank entries after Open and before the bank restore pass."""
    if save_id < 0 or not bank.ChestIsOpen:
        return 0
    stem = f"Save{save_id & 0xFFFF:04X}_Bank"
    source = _read_legacy(sanity_saver_saves, stem)
    if source is None:
        return 0

    path, original, legacy = source
    updated = deepcopy(save_data)
    imported: set[str] = set()

    for entry in bank.TheChest:
        item = entry.Inventory
        if item is None:
            continue
        is_weapon = item.Class._inherits(WILLOW_WEAPON_CLASS)
        if not is_weapon and not item.Class._inherits(WILLOW_ITEM_CLASS):
            continue

        item_id = str(item.GetUniqueID())
        record = legacy.get(item_id)
        if record is None or item_id in imported:
            continue

        code = _try_convert(item.DefinitionData, record, item_id, is_weapon=is_weapon)
        if code is None:
            continue

        existing = updated["bank"].get(item_id) or updated["backup"]["bank"].get(item_id)
        if existing is None:
            updated["bank"][item_id] = {
                "code": code,
                "mark": int(item.GetMark()),
                "quantity": 1 if is_weapon else item.Quantity,
            }
        elif existing["code"] != code:
            continue
        imported.add(item_id)

    return _commit_import(save_id, save_data, updated, path, original, imported)


def _try_convert(
    definition: Any, record: LegacyRecord, item_id: str, *, is_weapon: bool
) -> str | None:
    try:
        return _convert_code(definition, record, is_weapon=is_weapon)
    except (AttributeError, OverflowError, TypeError, ValueError) as exc:
        unrealsdk.logging.warning(f"Could not import Sanity Saver item {item_id}: {exc}")
        return None
