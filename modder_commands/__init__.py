import argparse

import unrealsdk
from command_extensions.builtins import obj_name_splitter, parse_object
from drop_loot import drop_loot
from mods_base import build_mod, command, get_pc
from unrealsdk.unreal import UFunction, UObject, WrappedStruct


def get_context_from_path(context: UObject, path: str) -> UObject:
    out_context = context
    for name in path.split(","):
        try:
            new_context = getattr(out_context, name)
        except AttributeError:
            unrealsdk.logging.error(
                f"{name} either does not exist on {out_context}.",
            )
            return None
        if new_context is None:
            unrealsdk.logging.error(
                f"{name} on {out_context} is None.",
            )
            return None
        if isinstance(new_context, UFunction):
            new_context = new_context()
            if not isinstance(new_context, UObject):
                unrealsdk.logging.error(f"{name} on {out_context} does not return a UObject.")
                return None
        elif not isinstance(new_context, UObject):
            unrealsdk.logging.error(f"{name} on {out_context} is not a UObject.")
            return None
        out_context = new_context


@command(
    splitter=obj_name_splitter,
    description="Get the value of an AttributeDefinition, also prints out the resolved context.",
)
def eval_attr(args: argparse.Namespace) -> None:
    attr = parse_object(args.attr)
    if attr is None:
        return
    if not attr.Class._inherits(unrealsdk.find_class("AttributeDefinition")):
        unrealsdk.logging.error(f"{attr} is not an AttributeDefinition.")
        return
    context = args.context
    if context is None:
        context = get_pc()
    else:
        context = parse_object(context)
        if context is None:
            return
    if args.path is not None:
        context = get_context_from_path(context, args.path)
    if context is None:
        return

    unrealsdk.logging.info(attr.GetBaseValue(context) if args.b else attr.GetValue(context))


eval_attr.add_argument("attr", help="The AttributeDefinition to get the value of.")
eval_attr.add_argument(
    "context",
    help="Context to use for evaluating the attribute, defaults to none.",
    nargs="?",
    default=None,
)
eval_attr.add_argument(
    "--path",
    help="A period seperated path on the context to get the final context, defaults to none.",
    default=None,
)
eval_attr.add_argument(
    "--b",
    help="Get the base value of the attribute instead of the full value.",
    action="store_true",
)


@command(
    splitter=obj_name_splitter,
    description="Get the value of an AttributeInitializationDefinition",
)
def eval_initdef(args: argparse.Namespace) -> None:
    initdef = parse_object(args.initdef)
    if initdef is None:
        return
    if not initdef.Class._inherits(unrealsdk.find_class("AttributeInitializationDefinition")):
        unrealsdk.logging.error(f"{initdef} is not an AttributeInitializationDefinition.")
        return
    context = args.context
    if context is None:
        context = get_pc()
    else:
        context = parse_object(context)
        if context is None:
            return
    if args.path is not None:
        context = get_context_from_path(context, args.path)
    if context is None:
        return
    try:
        base = float(args.base)
    except ValueError:
        unrealsdk.logging.error(f"Cannot convert {args.base} to a float.")
        return

    unrealsdk.logging.info(
        initdef.EvaluateInitializationData(
            unrealsdk.make_struct(
                "AttributeInitializationData",
                BaseValueConstant=base,
                BaseValueAttribute=None,
                InitializationDefinition=initdef,
                BaseValueScaleConstant=1,
            ),
            context,
        ),
    )


eval_initdef.add_argument(
    "initdef",
    help="The AttributeInitializationDefinition to get the value of.",
)
eval_initdef.add_argument(
    "context",
    help="Context to use for evaluating the attribute, defaults to none.",
    nargs="?",
    default=None,
)
eval_initdef.add_argument(
    "--path",
    help="A period seperated path on the context to get the final context, defaults to none.",
    default=None,
)
eval_initdef.add_argument(
    "--base",
    help=(
        "Initdefs must be evaluated as an AttributeInitializationData struct, "
        "so depending on the AttributeInitializationDefinition the BaseValueConstant "
        "may matter, this lets you set it, defaults to 0"
    ),
    default="0",
)


@command(description="Find all objects of a specific class")
def findall(args: argparse.Namespace) -> None:
    try:
        cls = unrealsdk.find_class(args.cls)
    except ValueError:
        unrealsdk.logging.error(f"{args.cls} is not a class.")
        return
    all_objects = list(unrealsdk.find_all(cls, exact=False))
    all_objects.sort(key=lambda obj: obj._path_name())
    for obj in all_objects:
        unrealsdk.logging.info(obj)


findall.add_argument("cls", help="The class to use.")


build_mod(commands=[drop_loot, findall, eval_initdef, eval_attr])
