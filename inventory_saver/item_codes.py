from __future__ import annotations

import base64
import struct
import zlib
from pathlib import Path
from typing import TYPE_CHECKING, cast

import unrealsdk
from mods_base import Game
from unrealsdk import logging
from unrealsdk.unreal import UClass, WrappedStruct

from inventory_saver.object_cache import find_object

if TYPE_CHECKING:
    from bl2.Engine import WillowInventory
    from bl2.WillowGame import WillowItem, WillowItemTypes, WillowWeapon, WillowWeaponTypes

    ItemDefinitionData = WillowItemTypes.ItemDefinitionData
    WeaponDefinitionData = WillowWeaponTypes.WeaponDefinitionData
    DefinitionData = ItemDefinitionData | WeaponDefinitionData

    InventorySerialNumber = WillowInventory.InventorySerialNumber

    SerialNumberState = WillowInventory.SerialNumberState
else:
    SerialNumberState = unrealsdk.find_enum("SerialNumberState")

WILLOW_WEAPON_CLASS = unrealsdk.find_class("WillowWeapon")
WILLOW_ITEM_CLASS = unrealsdk.find_class("WillowItem")


GAME_PREFIX = {Game.BL2: "BL2MODDED", Game.TPS: "BLOZMODDED", Game.AoDK: "AODKMODDED"}.get(
    _game := Game.get_current(), _game.name or ""
)

ZDICT = Path(__file__).parent / "zdict"
ZDICT_BYTES = ZDICT.read_bytes()

WEAPON_CODE_FIELDS = (
    "WeaponTypeDefinition",
    "BalanceDefinition",
    "ManufacturerDefinition",
    "ManufacturerGradeIndex",
    "BodyPartDefinition",
    "GripPartDefinition",
    "BarrelPartDefinition",
    "SightPartDefinition",
    "StockPartDefinition",
    "ElementalPartDefinition",
    "Accessory1PartDefinition",
    "Accessory2PartDefinition",
    "MaterialPartDefinition",
    "PrefixPartDefinition",
    "TitlePartDefinition",
    "GameStage",
)

ITEM_CODE_FIELDS = (
    "ItemDefinition",
    "BalanceDefinition",
    "ManufacturerDefinition",
    "ManufacturerGradeIndex",
    "AlphaItemPartDefinition",
    "BetaItemPartDefinition",
    "GammaItemPartDefinition",
    "DeltaItemPartDefinition",
    "EpsilonItemPartDefinition",
    "ZetaItemPartDefinition",
    "EtaItemPartDefinition",
    "ThetaItemPartDefinition",
    "MaterialItemPartDefinition",
    "PrefixItemNamePartDefinition",
    "TitleItemNamePartDefinition",
    "GameStage",
)

SERIAL_MIN_LENGTH = 8
SERIAL_BUFFER_LENGTH = 40
SERIAL_TYPE_OFFSET = 0
WEAPON_SERIAL_FLAG = 0x80

SERIAL_SEED = slice(1, 5)
SERIAL_CHECKSUM = slice(5, 7)
ZERO_SERIAL_SEED = b"\x00" * (SERIAL_SEED.stop - SERIAL_SEED.start)
ALL_BITS_SET_BYTE = 0xFF
CHECKSUM_PLACEHOLDER = b"\xff\xff"
CHECKSUM_WORD_BITS = 16
CHECKSUM_WORD_MASK = 0xFFFF

PRIMARY_DEFINITION_OFFSET = 8
WEAPON_DEFINITION_HIGH_BITS_MASK = 0x1F
ITEM_DEFINITION_HIGH_BITS_MASK = 0x01

REPLACEMENT_VERSION_OFFSET = 0
REPLACEMENT_DATA_OFFSET = 1
REPLACEMENT_FORMAT_VERSION = 0
MAX_REPLACEMENT_PAYLOAD_SIZE = 65_536
REPLACEMENT_MASK = struct.Struct("<H")
REPLACEMENT_INTEGER = struct.Struct("<i")
HIGHEST_REPLACEMENT_BIT = 15
OBJECT_PATH_TERMINATOR = b"\x00"
INTEGER_OVERRIDE_FIELDS = {"ManufacturerGradeIndex", "GameStage"}


class ItemCodeDecodeError(ValueError):
    """An item code is malformed or cannot be unpacked by the game."""


def _definition_overrides(
    original: DefinitionData, regenerated: DefinitionData
) -> dict[str, str | int | None]:
    if original._type != regenerated._type:
        msg = "Regenerated item has a different definition type"
        raise ItemCodeDecodeError(msg)

    overrides: dict[str, str | int | None] = {}
    for field in original._type._fields():
        if field.Name == "UniqueId":
            continue

        value = original._get_field(field)
        if value == regenerated._get_field(field):
            continue

        overrides[field.Name] = (
            value if value is None or isinstance(value, int) else value._path_name()
        )

    return overrides


def encode_modded_code(
    base_b64: str, overrides: dict[str, str | int | None], fields: tuple[str, ...], zdict: bytes
) -> str:
    """Encode a BL2 modded code using the format's 16 fields in wire order."""
    if not overrides or overrides.keys() - set(fields):
        msg = "Expected overrides for known definition fields"
        raise ItemCodeDecodeError(msg)

    mask = 0
    values = bytearray()

    for index, name in enumerate(fields):
        if name not in overrides:
            continue

        mask |= 1 << (15 - index)
        value = overrides[name]

        if name in {"ManufacturerGradeIndex", "GameStage"}:
            if type(value) is not int:
                msg = f"{name} requires an integer"
                raise ItemCodeDecodeError(msg)

            values.extend(struct.pack("<i", value))
        elif value is None:
            values.append(0)
        elif isinstance(value, str) and value and "\0" not in value:
            values.extend(value.encode("utf-8"))
            values.append(0)
        else:
            msg = f"{name} requires an object path or None"
            raise ItemCodeDecodeError(msg)

    payload = struct.pack("<H", mask) + values
    compressor = zlib.compressobj(level=zlib.Z_BEST_COMPRESSION, zdict=zdict)
    compressed = compressor.compress(payload) + compressor.flush()
    replacements_b64 = base64.b64encode(b"\x00" + compressed).decode("ascii")

    return f"BL2MODDED[{base_b64}|{replacements_b64}]"


def pack_serial(serial: InventorySerialNumber) -> str:
    buffer = bytearray(serial.Buffer)

    # PackSerialNumber returns an unscrambled buffer. A zero seed keeps it that way.
    buffer[1:5] = b"\x00" * 4
    buffer[5:7] = b"\xff" * 2

    crc = zlib.crc32(buffer.ljust(40, b"\xff"))
    checksum = (crc >> 16) ^ (crc & 0xFFFF)
    buffer[5:7] = checksum.to_bytes(2, "big")

    return base64.b64encode(buffer.rstrip(b"\xff")).decode("ascii")


def _get_base_item_code(item: WillowWeapon | WillowItem) -> str:
    serial, _ = item.PackSerialNumber(item.DefinitionData)  # pyright: ignore[reportArgumentType]
    return pack_serial(serial)


def _full_encode_item(item: WillowWeapon | WillowItem) -> str:
    serial, _ = item.PackSerialNumber(item.DefinitionData)  # pyright: ignore[reportArgumentType]
    *_, definition = item.UnpackSerialNumber(
        serial,
        unrealsdk.make_struct(item.DefinitionData._type.Name),  # pyright: ignore[reportArgumentType]
    )

    overrides = _definition_overrides(item.DefinitionData, definition)
    fields = WEAPON_CODE_FIELDS if item.Class._inherits(WILLOW_WEAPON_CLASS) else ITEM_CODE_FIELDS
    b64 = pack_serial(serial)
    return encode_modded_code(b64, overrides, fields, ZDICT_BYTES)


def get_item_code(item: WillowInventory) -> str | None:
    if not (item.Class._inherits(WILLOW_WEAPON_CLASS) or item.Class._inherits(WILLOW_ITEM_CLASS)):
        return None
    item = cast("WillowWeapon | WillowItem", item)
    def_data = item.DefinitionData
    if def_data is None:
        return None

    primary_field = (
        "WeaponTypeDefinition" if item.Class._inherits(WILLOW_WEAPON_CLASS) else "ItemDefinition"
    )
    if getattr(def_data, primary_field) is None:
        return None

    serial_string = item.GetSerialNumberString()

    gen_item, _ = item.CreateInventoryFromSerialNumberString(serial_string, None)
    if gen_item is None:
        return _full_encode_item(item)
    if not (
        gen_item.Class._inherits(WILLOW_WEAPON_CLASS) or gen_item.Class._inherits(WILLOW_ITEM_CLASS)
    ):
        return None
    gen_item = cast("WillowWeapon | WillowItem", gen_item)

    gen_def_data = gen_item.DefinitionData
    if gen_def_data is None:
        return None

    overrides = _definition_overrides(def_data, gen_def_data)
    if not overrides:
        return None

    base_code = _get_base_item_code(item)
    fields = WEAPON_CODE_FIELDS if item.Class._inherits(WILLOW_WEAPON_CLASS) else ITEM_CODE_FIELDS

    return encode_modded_code(base_code, overrides, fields, ZDICT_BYTES)


def _split_modded_code(code: str) -> tuple[bytes, bytes]:
    prefix = f"{GAME_PREFIX}["
    code = code.strip()
    if not code.startswith(prefix) or not code.endswith("]"):
        msg = f"Expected a {GAME_PREFIX} code"
        raise ItemCodeDecodeError(msg)

    try:
        base_text, replacements_text = code[len(prefix) : -1].split("|")
        return (
            base64.b64decode(base_text, validate=True),
            base64.b64decode(replacements_text, validate=True),
        )
    except ValueError as exc:
        msg = "Invalid modded item code payload"
        raise ItemCodeDecodeError(msg) from exc


def validate_serial(base: bytes) -> bytearray:
    if not SERIAL_MIN_LENGTH <= len(base) <= SERIAL_BUFFER_LENGTH:
        msg = "Invalid inventory serial length"
        raise ItemCodeDecodeError(msg)

    if base[SERIAL_SEED] != ZERO_SERIAL_SEED:
        msg = "Expected a zero-seed inventory serial"
        raise ItemCodeDecodeError(msg)

    padding = bytes([ALL_BITS_SET_BYTE])
    buffer = bytearray(base.ljust(SERIAL_BUFFER_LENGTH, padding))
    expected_checksum = int.from_bytes(buffer[SERIAL_CHECKSUM], "big")
    buffer[SERIAL_CHECKSUM] = CHECKSUM_PLACEHOLDER

    crc = zlib.crc32(buffer)
    checksum = (crc >> CHECKSUM_WORD_BITS) ^ (crc & CHECKSUM_WORD_MASK)
    if checksum != expected_checksum:
        msg = "Invalid inventory serial checksum"
        raise ItemCodeDecodeError(msg)

    return buffer


def _decode_overrides(replacements: bytes, fields: tuple[str, ...]) -> dict[str, str | int | None]:
    if not replacements or replacements[REPLACEMENT_VERSION_OFFSET] != REPLACEMENT_FORMAT_VERSION:
        msg = "Unsupported replacement payload version"
        raise ItemCodeDecodeError(msg)

    try:
        decompressor = zlib.decompressobj(zdict=ZDICT_BYTES)
        payload = decompressor.decompress(
            replacements[REPLACEMENT_DATA_OFFSET:], max_length=MAX_REPLACEMENT_PAYLOAD_SIZE
        )
    except zlib.error as exc:
        msg = "Invalid compressed replacement payload"
        raise ItemCodeDecodeError(msg) from exc

    if not decompressor.eof or decompressor.unused_data:
        msg = "Incomplete, oversized, or invalid replacement payload"
        raise ItemCodeDecodeError(msg)

    if len(payload) < REPLACEMENT_MASK.size:
        msg = "Truncated replacement mask"
        raise ItemCodeDecodeError(msg)

    (mask,) = REPLACEMENT_MASK.unpack_from(payload)
    if not mask:
        msg = "Modded item code has no replacements"
        raise ItemCodeDecodeError(msg)

    overrides: dict[str, str | int | None] = {}
    offset = REPLACEMENT_MASK.size

    for index, name in enumerate(fields):
        if not mask & (1 << (HIGHEST_REPLACEMENT_BIT - index)):
            continue

        if name in INTEGER_OVERRIDE_FIELDS:
            if offset + REPLACEMENT_INTEGER.size > len(payload):
                msg = f"Truncated integer for {name}"
                raise ItemCodeDecodeError(msg)

            (overrides[name],) = REPLACEMENT_INTEGER.unpack_from(payload, offset)
            offset += REPLACEMENT_INTEGER.size
        else:
            end = payload.find(OBJECT_PATH_TERMINATOR, offset)
            if end < 0:
                msg = f"Unterminated object path for {name}"
                raise ItemCodeDecodeError(msg)

            try:
                overrides[name] = payload[offset:end].decode("utf-8") or None
            except UnicodeDecodeError as exc:
                msg = f"Invalid UTF-8 in object path for {name}"
                raise ItemCodeDecodeError(msg) from exc

            offset = end + len(OBJECT_PATH_TERMINATOR)

    if offset != len(payload):
        msg = "Unexpected trailing replacement data"
        raise ItemCodeDecodeError(msg)

    return overrides


def _serial_has_no_primary_definition(buffer: bytearray, is_weapon: bool) -> bool:
    offset = PRIMARY_DEFINITION_OFFSET
    if is_weapon:
        mask = WEAPON_DEFINITION_HIGH_BITS_MASK
        return buffer[offset] == ALL_BITS_SET_BYTE and (buffer[offset + 1] & mask) == mask

    mask = ITEM_DEFINITION_HIGH_BITS_MASK
    return (
        buffer[offset] == buffer[offset + 1] == ALL_BITS_SET_BYTE
        and (buffer[offset + 2] & mask) == mask
    )


def _apply_overrides(
    definition: DefinitionData, overrides: dict[str, str | int | None]
) -> dict[str, str]:
    missing: dict[str, str] = {}

    for name, value in overrides.items():
        if isinstance(value, str):
            try:
                part = find_object(value)
            except ValueError:
                logging.warning(f"Could not find object {value!r} for {name}")
                missing[name] = value
                continue
            setattr(definition, name, part)
        else:
            setattr(definition, name, value)

    return missing


def decode_modded_item_code(
    code: str, inventory_class: UClass | None = None
) -> tuple[DefinitionData, dict[str, str]]:
    base, replacements = _split_modded_code(code)
    buffer = validate_serial(base)

    is_weapon = bool(buffer[SERIAL_TYPE_OFFSET] & WEAPON_SERIAL_FLAG)
    fields = WEAPON_CODE_FIELDS if is_weapon else ITEM_CODE_FIELDS
    base_class = WILLOW_WEAPON_CLASS if is_weapon else WILLOW_ITEM_CLASS

    if inventory_class is None:
        inventory_class = base_class
    elif inventory_class != base_class and not inventory_class._inherits(base_class):
        msg = "Inventory class does not match serial type"
        raise ItemCodeDecodeError(msg)

    overrides = _decode_overrides(replacements, fields)

    unpacker = inventory_class.ClassDefaultObject.UnpackSerialNumber
    args = WrappedStruct(unpacker.func)
    args.SerialNumber.Buffer = buffer
    args.SerialNumber.State = SerialNumberState.SNS_Full
    success, _, definition = unpacker(args)

    primary_field = fields[0]
    if not success and not (
        _serial_has_no_primary_definition(buffer, is_weapon)
        and getattr(definition, primary_field) is None
        and isinstance(overrides.get(primary_field), str)
    ):
        msg = "The game could not unpack the inventory serial"
        raise ItemCodeDecodeError(msg)

    return definition, _apply_overrides(definition, overrides)
