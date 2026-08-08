from __future__ import annotations

import argparse
from io import TextIOWrapper
from pathlib import Path
from typing import TYPE_CHECKING

import unrealsdk
from command_extensions.builtins import obj_name_splitter
from mods_base import command
import importlib
from bpd_grapher.bpd_helper import bpd_helper

importlib.reload(bpd_helper)
if TYPE_CHECKING:
    from bl2.Engine import BehaviorBase
    from bl2.GearboxFramework import BehaviorProviderDefinition

outfile = Path(__file__).parent / "bpd_dump.py"


class VarIndex:
    """Wrapper type for variable indexes to make dumping easier."""

    idx: int
    name: str

    def __init__(self, idx: int, name: str) -> VarIndex:  # noqa: D107
        self.idx = idx
        self.name = name

    def __repr__(self) -> str:
        """Return the name."""
        return self.name


def get_var_name(sequence: BehaviorProviderDefinition.BehaviorSequenceData, idx: int) -> str:
    variable_data = sequence.VariableData[idx]
    name = f"{variable_data.Name.upper()}_" if variable_data.Name != "None" else ""
    t = variable_data.Type.name.upper().split("_")[-1]
    return f"VAR_{name}{t}_{idx}"


def get_behavior_name(behavior_path: str, idx: int) -> str:
    return behavior_path.rsplit(".", maxsplit=1)[-1] + f"_{idx}"


def get_event_name(event_name: str, idx: int) -> str:
    event_name = event_name.split(" ")
    if len(event_name) > 1:
        event_name = [s[0].upper() + (s[1:].lower() if len(s) > 1 else "") for s in event_name]
    return "".join(event_name) + f"_{idx}"


HANDLED_BEHAVIORS = []


def handle_output_links(
    data: BehaviorProviderDefinition.BehaviorEventData2
    | BehaviorProviderDefinition.BehaviorSequenceActionData2,
    data_idx: int,
    sequence: BehaviorProviderDefinition.BehaviorSequenceData,
    file: TextIOWrapper,
):
    idx, length = bpd_helper.parse_arrayindexandlength(data.OutputLinks.ArrayIndexAndLength)
    behaviors: list[tuple(int, BehaviorProviderDefinition.BehaviorSequenceActionData2)] = []
    for link in sequence.ConsolidatedOutputLinkData[idx : idx + length]:
        l_id, i = bpd_helper.parse_linkidandlinkedbehavior(link.LinkIdAndLinkedBehavior)
        linked_behavior = sequence.BehaviorData2[i].Behavior
        if linked_behavior not in HANDLED_BEHAVIORS:
            behaviors.append((i, sequence.BehaviorData2[i]))
            HANDLED_BEHAVIORS.append(linked_behavior)
        if data._type.Name == "BehaviorEventData2":
            name = get_event_name(data.UserData.EventName, data_idx)
        else:
            name = get_behavior_name(data.Behavior._path_name(), data_idx)
        b_link = bpd_helper.BehaviorLink(
            bpd_helper.Behavior(get_behavior_name(linked_behavior._path_name(), i)),
            l_id,
            link.ActivateDelay,
        )
        file.write(f"{name} += {b_link}\n")
    for idx, behavior in behaviors:
        handle_output_links(behavior, idx, sequence, file)


def dump_bpd_sequence(sequence: BehaviorProviderDefinition.BehaviorSequenceData) -> None:
    events: list[bpd_helper.EventData] = []
    behaviors: list[bpd_helper.Behavior] = []
    for event in sequence.EventData2:
        event_data = bpd_helper.EventData(event.UserData.EventName)
        idx, length = bpd_helper.parse_arrayindexandlength(
            event.OutputVariables.ArrayIndexAndLength,
        )
        for var_link in sequence.ConsolidatedVariableLinkData[idx : idx + length]:
            i, l = bpd_helper.parse_arrayindexandlength(
                var_link.LinkedVariables.ArrayIndexAndLength,
            )
            link_data = bpd_helper.VariableLinkData(
                [],
                var_link.PropertyName,
                bpd_helper.EBehaviorVariableLinkType(var_link.VariableLinkType.value),
                var_link.ConnectionIndex,
            )
            link_data.variable_indexes = [
                VarIndex(
                    (vi := sequence.ConsolidatedLinkedVariables[x]),
                    get_var_name(sequence, vi),
                )
                for x in range(i, i + l)
            ]
            event_data.output_variables.append(link_data)
        events.append(event_data)
    for behavior in sequence.BehaviorData2:
        behavior_data = bpd_helper.Behavior(behavior.Behavior._path_name())
        idx, length = bpd_helper.parse_arrayindexandlength(
            behavior.LinkedVariables.ArrayIndexAndLength,
        )
        for var_link in sequence.ConsolidatedVariableLinkData[idx : idx + length]:
            i, l = bpd_helper.parse_arrayindexandlength(
                var_link.LinkedVariables.ArrayIndexAndLength,
            )
            link_data = bpd_helper.VariableLinkData(
                [],
                var_link.PropertyName,
                bpd_helper.EBehaviorVariableLinkType(var_link.VariableLinkType.value),
                var_link.ConnectionIndex,
            )
            link_data.variable_indexes = [
                VarIndex(
                    (vi := sequence.ConsolidatedLinkedVariables[x]),
                    get_var_name(sequence, vi),
                )
                for x in range(i, i + l)
            ]
            behavior_data.linked_variables.append(link_data)
        behaviors.append(behavior_data)

    with outfile.open("w") as file:
        file.write(f"generate_variables({len(sequence.VariableData)})\n\n")
        for idx, var in enumerate(sequence.VariableData):
            print(f"{get_var_name(sequence, idx)} = {idx}", file=file)
        file.write("\n\n")
        for idx, event in enumerate(events):
            print(f"{get_event_name(event.event_name, idx)} = {event}", file=file)
        file.write("\n\n")
        for idx, behavior in enumerate(behaviors):
            print(f"{get_behavior_name(behavior.behavior, idx)} = {behavior}", file=file)
        file.write("\n\n")

        for idx, event in enumerate(sequence.EventData2):
            handle_output_links(event, idx, sequence, file)
            file.write("\n")
        file.write("\n")


@command(splitter=obj_name_splitter, description="Graph a bpd.")
def dump_bpd(args: argparse.Namespace) -> None:
    bpd = unrealsdk.find_object("BehaviorProviderDefinition", args.bpd)
    dump_bpd_sequence(
        bpd.BehaviorSequences[args.idx],
    )
    with outfile.open("a") as file:
        file.write(f"generate_bpd({bpd._path_name()!r})")


dump_bpd.add_argument("bpd")
dump_bpd.add_argument("idx", type=int, default=0)
