import argparse

import unrealsdk
from command_extensions.builtins import obj_name_splitter, parse_object
from mods_base import command, get_pc
from unrealsdk.unreal import UObject


def drop_loot_inner(obj: UObject, quantity: int) -> None:
    item_pool = unrealsdk.find_class("ItemPool").ClassDefaultObject
    willow_pc = get_pc()
    new_items = []
    if obj.Class._inherits(unrealsdk.find_class("ItemPoolDefinition")):
        for _ in range(quantity):
            _, items = item_pool.SpawnBalancedInventoryFromPool(
                obj,
                willow_pc.Pawn.GetGameStage(),
                0,
                willow_pc,
                [],
            )
            new_items.extend(items)
    elif obj.Class._inherits(unrealsdk.find_class("InventoryBalanceDefinition")):
        _, items = item_pool.SpawnBalancedInventoryFromInventoryBalanceDefinition(
            obj,
            quantity,
            willow_pc.Pawn.GetGameStage(),
            0,
            willow_pc,
            [],
        )
        new_items.extend(items)
    else:
        unrealsdk.logging.warning(
            f"{obj} is not an ItemPoolDefinition or InventoryBalanceDefinition"
        )
        return
    for item in new_items:
        item.SetOwner(willow_pc.Pawn)
        item.Instigator = willow_pc.Pawn
        item.DropFrom(willow_pc.Pawn.Location, willow_pc.Pawn.GetItemTossVelocity())


desc = "Drop a number of items from an InventoryBalanceDefinition or ItemPoolDefinition"


@command(description=desc, splitter=obj_name_splitter)
def drop_loot(args: argparse.Namespace) -> None:
    quantity = 0
    try:
        quantity = int(args.quantity)
    except ValueError:
        unrealsdk.logging.error("quantity must be an int.")
        return
    obj = parse_object(args.obj)
    drop_loot_inner(obj, quantity)


drop_loot.add_argument("obj", help="The balance or pool to drop.")
drop_loot.add_argument(
    "quantity",
    nargs="?",
    default="1",
    help="The number of times to drop",
)
