import argparse

import unrealsdk
from command_extensions.builtins import obj_name_splitter, parse_object
from mods_base import command, get_pc
from unrealsdk.unreal import UObject

ITEM_POOL_STATIC = unrealsdk.find_class("ItemPool").ClassDefaultObject


def drop_loot_inner(obj: UObject, quantity: int, level: int) -> None:
    willow_pc = get_pc()
    new_items = []
    if obj.Class._inherits(unrealsdk.find_class("ItemPoolDefinition")):
        for _ in range(quantity):
            _, items = ITEM_POOL_STATIC.SpawnBalancedInventoryFromPool(obj, level, 0, willow_pc, [])
            new_items.extend(items)
    elif obj.Class._inherits(unrealsdk.find_class("InventoryBalanceDefinition")):
        _, items = ITEM_POOL_STATIC.SpawnBalancedInventoryFromInventoryBalanceDefinition(
            obj, quantity, level, 0, willow_pc, []
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
    obj = parse_object(args.obj)
    if obj is None:
        return
    level = args.level
    if level < 0:
        level = get_pc().Pawn.GetGameStage()
    drop_loot_inner(obj, args.quantity, level)


drop_loot.add_argument("obj", help="The balance or pool to drop.")
drop_loot.add_argument("-q", "--quantity", default=1, type=int, help="The number of times to drop")
drop_loot.add_argument(
    "-l",
    "--level",
    default=-1,
    type=int,
    help="The level of the dropped item(s), below 0 users player level.",
)
