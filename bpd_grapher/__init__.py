from __future__ import annotations

import argparse
import math
import site
import struct
from pathlib import Path
from typing import TYPE_CHECKING

import unrealsdk
from command_extensions.builtins import obj_name_splitter
from mods_base import build_mod, command
from unrealsdk.unreal import UObject, WrappedStruct

site.addsitedir(str(Path(__file__).parent.absolute() / "dist"))

import graphviz  # noqa: E402

if TYPE_CHECKING:
    from bl2.GearboxFramework import BehaviorProviderDefinition

EBehaviorVariableLinkType = ["Unknown", "Context", "Input", "Output", "MAX"]
BLANK_NAME = '" "'
EBehaviorVariableType = [
    "None",
    "Bool",
    "Int",
    "Float",
    "Vector",
    "Object",
    "AllPlayers",
    "Attribute",
    "InstanceData",
    "NamedVariable",
    "NamedKismetVariable",
    "DirectionVector",
    "AttachmentLocation",
    "UnaryMath",
    "BinaryMath",
    "Flag",
    "MAX",
]

REMOTE_EVENT_CLASSES = [
    "Behavior_CustomEvent",
    "Behavior_SkillCustomEvent",
    "Behavior_FireCustomSkillEvent",
    "Behavior_RemoteEvent",
    "Behavior_RemoteCustomEvent",
    "Behavior_MissionCustomEvent",
]


class BpdError(Exception):  # noqa: D101
    pass


def simple_round(n: float) -> float | int:
    if n == 0:
        return 0
    sgn = -1 if n < 0 else 1
    scale = int(-math.floor(math.log10(abs(n))))
    if scale <= 0:
        scale = 1
    factor = 10**scale
    return sgn * math.floor(abs(n) * factor) / factor


def try_get_pathname(obj: UObject | None) -> str:
    if obj is None:
        return ""
    return obj._path_name()


def parse_arrayindexandlength(number: int) -> tuple[int, int]:
    """Return an array index and length tuple for the given number."""
    # Could just use >> and & for this, but since we have to be more
    # careful with LinkIdAndLinkedBehavior anyway, since that one's
    # weirder, we may as well just use struct here, as well.
    number = int(number)
    byteval = struct.pack(">i", number)
    return struct.unpack(">HH", byteval)


def parse_linkidandlinkedbehavior(number: int) -> tuple[int, int]:
    """Return a link ID index and behavior tuple for the given number."""
    number = int(number)
    byteval = struct.pack(">i", number)
    (linkid, _, behavior) = struct.unpack(">bbH", byteval)
    return (linkid, behavior)


def additional_behaviour_data(behaviour: UObject) -> str:  # noqa: C901, PLR0911, PLR0912
    if behaviour.Class.Name == "Behavior_ActivateSkill" and behaviour.SkillToActivate:
        return f"\n{try_get_pathname(behaviour.SkillToActivate)}"

    if behaviour.Class.Name == "Behavior_DeactivateSkill" and behaviour.SkillToDeactivate:
        return f"\nskill {try_get_pathname(behaviour.SkillToDeactivate)}"

    if behaviour.Class.Name == "Behavior_Delay":
        return f"\ndelay {behaviour.Delay}"

    if behaviour.Class.Name == "Behavior_ChangeInstanceDataSwitch":
        return f"\n{behaviour.SwitchName} > {behaviour.NewValue}"

    if behaviour.Class.Name == "Behavior_CustomEvent":
        return f"\n{behaviour.CustomEventName}"

    if behaviour.Class.Name == "Behavior_SkillCustomEvent":
        return f"\n{try_get_pathname(behaviour.SkillDef)} {behaviour.EventName}"

    if behaviour.Class.Name == "Behavior_FireCustomSkillEvent":
        return f"\n{try_get_pathname(behaviour.Skill)} {behaviour.EventName}"

    if behaviour.Class.Name == "Behavior_RemoteEvent":
        return f"\n{behaviour.EventName}"

    if behaviour.Class.Name == "Behavior_RemoteCustomEvent":
        components = [
            comp
            for comp in behaviour.ProviderDefinitionPathName.PathComponentNames
            if comp != "None"
        ]
        return f"\n{'.'.join(components)} {behaviour.CustomEventName}"

    if behaviour.Class.Name == "Behavior_MissionCustomEvent":
        return f"\n{try_get_pathname(behaviour.RelatedMission)} {behaviour.EventName}"

    if behaviour.Class.Name == "Behavior_PostAkEvent":
        return f"\n{try_get_pathname(behaviour.Event)}"

    if behaviour.Class.Name == "Behavior_Metronome":
        a = f"\ni={round(behaviour.TickInterval, 3)}"
        b = f" d={round(behaviour.Duration, 3)}" if behaviour.bUseDuration else ""
        c = f" c={behaviour.MaxTickCount}" if behaviour.bUseTickCount else ""
        return a + b + c

    if behaviour.Class.Name == "Behavior_ModifyTimer":
        behavior_timer_function = [
            "None",
            "Start",
            "Pause",
            "Toggle",
            "Resume",
            "Stop",
            "MAX",
        ]
        return f"\nTimer_{behaviour.TimerId} {behavior_timer_function[behaviour.Operation]}"

    if behaviour.Class.Name == "Behavior_CallFunction":
        return f"\n{behaviour.FunctionName}"

    return ""


def additional_behaviour_link_data(from_behavior: UObject, id: int) -> str:  # noqa: PLR0911, A002
    if from_behavior.Class.Name == "Behavior_CompareObject":
        return "==" if id == 0 else "!="
    if from_behavior.Class.Name == "Behavior_CompareValues":
        if id == 0:
            return "<="
        if id == 1:
            return ">"
        if id == 2:
            return "=="
        if id == 3:
            return "<"
        if id == 4:
            return ">="
    return ""


def get_behaviour_name(behaviour: UObject, idx: int, sidx: int) -> str:
    name = f"[{sidx}][{idx}] {behaviour.Name}"
    name += additional_behaviour_data(behaviour)
    return name


def get_variable_data(
    behavior_sequence: BehaviorProviderDefinition.BehaviorSequenceData,
    linked_variables: int,
) -> str:
    data = ""
    idx, length = parse_arrayindexandlength(linked_variables)
    for var in list(range(idx, idx + length)):
        try:
            link_data = behavior_sequence.ConsolidatedVariableLinkData[var]
        except IndexError:
            msg = f"Index {var} is out of range for ConsolidatedVariableLinkData"
            raise BpdError(msg)
        data += f"\n{EBehaviorVariableLinkType[link_data.VariableLinkType]}: "
        idx, length = parse_arrayindexandlength(link_data.LinkedVariables.ArrayIndexAndLength)
        for v in list(range(idx, idx + length)):
            try:
                v_index = behavior_sequence.ConsolidatedLinkedVariables[v]
            except IndexError:
                msg = f"Index {v} is out of range for ConsolidatedLinkedVariables"
                raise BpdError(msg)
            try:
                d = behavior_sequence.VariableData[v_index]
            except IndexError:
                msg = f"Index {v_index} is out of range for VariableData"
                raise BpdError(msg)
            data += str(
                f"[{behavior_sequence.ConsolidatedLinkedVariables[v]}]{d.Name}"
                f"({EBehaviorVariableType[d.Type]}) "
            )
        data += f"via [{var}]{link_data.PropertyName} ({link_data.ConnectionIndex})"
    return data


def get_event_name(
    behavior_sequence: BehaviorProviderDefinition.BehaviorSequenceData,
    event_data: BehaviorProviderDefinition.BehaviorEventData,
    b_idx: int,
    e_idx: int,
) -> str:
    return (
        f"[{b_idx}] {behavior_sequence.BehaviorSequenceName} "
        f"[{e_idx}] {event_data.UserData.EventName}"
    )


def generate_graph(behavior_provider_definition: BehaviorProviderDefinition) -> graphviz.Digraph:  # noqa: PLR0912, C901
    dot = graphviz.Digraph()
    dot.edge_attr.update(arrowhead="vee")
    dot.body.append(
        f"""    labelloc="t";
		label="{behavior_provider_definition._path_name()}";\n""",
    )
    for behavior_sequence_idx, behavior_sequence in enumerate(
        behavior_provider_definition.BehaviorSequences
    ):
        for event_data_idx, event_data in enumerate(behavior_sequence.EventData2):
            event_info = get_event_name(
                behavior_sequence,
                event_data,
                behavior_sequence_idx,
                event_data_idx,
            )
            try:
                event_info += get_variable_data(
                    behavior_sequence,
                    event_data.OutputVariables.ArrayIndexAndLength,
                )
            except BpdError as e:
                unrealsdk.logging.error(f"Error for event:\n{event_data}")
                unrealsdk.logging.error(e)
                return None
            dot.node(
                get_event_name(
                    behavior_sequence,
                    event_data,
                    behavior_sequence_idx,
                    event_data_idx,
                ),
                event_info,
                shape="box",
                style="filled",
                fillcolor="chartreuse2",
                group="event",
            )
        for behavior_data_idx, behavior_data in enumerate(behavior_sequence.BehaviorData2):
            if behavior_data.Behavior is None:
                continue
            full_name = behavior_provider_definition.PathName(behavior_data.Behavior)
            full_name = full_name.replace(try_get_pathname(behavior_data.Behavior.Outer), "")[1:]

            behavior_info = get_behaviour_name(
                behavior_data.Behavior,
                behavior_data_idx,
                behavior_sequence_idx,
            )
            behavior_info += get_variable_data(
                behavior_sequence,
                behavior_data.LinkedVariables.ArrayIndexAndLength,
            )
            if behavior_data.Behavior.Class.Name in REMOTE_EVENT_CLASSES:
                dot.node(
                    get_behaviour_name(
                        behavior_data.Behavior,
                        behavior_data_idx,
                        behavior_sequence_idx,
                    ),
                    behavior_info,
                    shape="cds",
                    style="filled",
                    fillcolor="gold1",
                    margin="0.15",
                )
            else:
                dot.node(
                    get_behaviour_name(
                        behavior_data.Behavior,
                        behavior_data_idx,
                        behavior_sequence_idx,
                    ),
                    behavior_info,
                    shape="box",
                    style="rounded",
                )
        for event_data_idx, event_data in enumerate(behavior_sequence.EventData2):
            idx, length = parse_arrayindexandlength(event_data.OutputLinks.ArrayIndexAndLength)
            for i, link in enumerate(list(range(idx, idx + length))):
                link_id, idx = parse_linkidandlinkedbehavior(
                    behavior_sequence.ConsolidatedOutputLinkData[link].LinkIdAndLinkedBehavior,
                )
                rounded_delay = simple_round(
                    behavior_sequence.ConsolidatedOutputLinkData[link].ActivateDelay,
                )
                delay = (
                    ""
                    if behavior_sequence.ConsolidatedOutputLinkData[link].ActivateDelay == 0.0
                    else f" d={rounded_delay}"
                )
                dot.edge(
                    get_event_name(
                        behavior_sequence,
                        event_data,
                        behavior_sequence_idx,
                        event_data_idx,
                    ),
                    get_behaviour_name(
                        behavior_sequence.BehaviorData2[idx].Behavior,
                        idx,
                        behavior_sequence_idx,
                    ),
                    label=f"[{i}] ({link_id},{idx}){delay}",
                )
        for behavior_data_idx, behavior_data in enumerate(behavior_sequence.BehaviorData2):
            if behavior_data.Behavior is None:
                continue
            idx, length = parse_arrayindexandlength(behavior_data.OutputLinks.ArrayIndexAndLength)
            for i, link in enumerate(list(range(idx, idx + length))):
                link_id, idx = parse_linkidandlinkedbehavior(
                    behavior_sequence.ConsolidatedOutputLinkData[link].LinkIdAndLinkedBehavior,
                )
                rounded_delay = simple_round(
                    behavior_sequence.ConsolidatedOutputLinkData[link].ActivateDelay,
                )
                delay = (
                    ""
                    if behavior_sequence.ConsolidatedOutputLinkData[link].ActivateDelay == 0.0
                    else f" d={rounded_delay}"
                )
                if behavior_sequence.BehaviorData2[idx].Behavior is None:
                    continue
                dot.edge(
                    get_behaviour_name(
                        behavior_data.Behavior,
                        behavior_data_idx,
                        behavior_sequence_idx,
                    ),
                    get_behaviour_name(
                        behavior_sequence.BehaviorData2[idx].Behavior,
                        idx,
                        behavior_sequence_idx,
                    ),
                    label=(
                        f"[{i}] ({link_id},{idx}){delay} "
                        f"{additional_behaviour_link_data(behavior_data.Behavior,link_id)}"
                    ),
                )
    return dot


@command(splitter=obj_name_splitter, description="Graph a bpd.")
def graph_bpd(args: argparse.Namespace) -> None:
    dot = generate_graph(unrealsdk.find_object("BehaviorProviderDefinition", args.bpd))
    if dot:
        dot.render(filename="bpd", directory=Path(__file__).parent, view=True)


graph_bpd.add_argument("bpd")

build_mod()
