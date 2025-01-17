from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

import unrealsdk
from unrealsdk.hooks import Type
from unrealsdk.unreal import BoundFunction, UObject, WeakPointer, WrappedStruct

from mods_base import Library, bind_all_hooks, build_mod, get_pc, hook

__all__: tuple[str, ...] = ("UnrealTimer",)


@dataclass
class UnrealTimer:
    """A Timer object that takes advantage of the unreal timers system.

    Can be used as either its own object or as a decorator for the on_tick function.
    Timers only run while in game and not paused, so opening the menu in singleplayer
    will stop the timer. Timers will also automatically resume if left running on save quit
    or on map transition.
    The timer completely restarts on map transition, long timers may fail due to this.

    Args:
        on_tick: The callback that is triggered when the timer is up.

    """

    on_finish: Callable[[], None] = field(init=True)
    _timer_actor: WeakPointer | None = field(init=False, default_factory=WeakPointer)
    duration: float = field(init=False, default=0)
    loop: bool = field(init=False, default=False)

    def __post_init__(self) -> None:  # noqa: D105
        bind_all_hooks(self, f"{id(self)}:{id(self.on_finish)}")

    @hook("Engine.Actor:Timer")
    def _timer_finish(
        self,
        obj: UObject,
        _2: WrappedStruct,
        _3: Any,
        _4: BoundFunction,
    ) -> None:
        if obj != self._timer_actor():
            return
        timer_data = self._get_timer_data()
        if timer_data is None:
            return
        if not timer_data.bLoop:
            self.stop()
        self.on_finish()

    @hook("WillowGame.WillowGameInfo:PostCommitMapChange", Type.POST)
    def _post_commit_map_change(
        self,
        _1: UObject,
        _2: WrappedStruct,
        _3: Any,
        _4: BoundFunction,
    ) -> None:
        if self.duration == 0 and self.loop is False:
            return
        self.start(self.duration, self.loop)

    def _get_timer_actor(self) -> UObject:
        actor: UObject | None = self._timer_actor()
        if actor is None:
            new_actor: UObject = get_pc().WorldInfo.Spawn(unrealsdk.find_class("WillowWeapon"))
            actor = new_actor
            self._timer_actor = WeakPointer(actor)
        return actor

    def _get_timer_data(self) -> WrappedStruct | None:
        timer_actor = self._timer_actor()
        if self._timer_actor() is None:
            return None
        for timer in timer_actor.Timers:
            if timer.FuncName == "Timer":
                return timer
        return None

    def _enable_hooks(self) -> None:
        self._timer_finish.enable()
        self._post_commit_map_change.enable()

    def _disable_hooks(self) -> None:
        self._timer_finish.disable()
        self._post_commit_map_change.disable()

    def start(self, duration: float, loop: bool) -> None:
        """Start the timer.

        Args:
            duration: The duration of the timer.
            loop: If true the timer will restart automatically with the same values.
            start_time: The starting time for the timer, used to make the first tick of
                        the timer a different legnth, the value is limited to length.

        """
        timer_actor = self._get_timer_actor()
        if self._get_timer_data() is not None:
            msg = "Cannot start a timer that is running."
            raise RuntimeError(msg)
        # FuncName="Timer" is done so that Engine.Actor:Timer is called on finish.
        timer_data = unrealsdk.make_struct(
            "TimerData",
            FuncName="Timer",
            bLoop=loop,
            Rate=duration,
            TimerTimeDilation=1,
            TimerObj=timer_actor,
        )
        timer_actor.Timers = [timer_data]
        self._enable_hooks()
        self.duration = duration
        self.loop = loop

    def stop(self) -> None:
        """Stop the timer. Must do this when finished with a timer so it can be removed properly."""
        self._disable_hooks()
        self.duration = 0
        self.loop = False
        timer_actor = self._timer_actor()
        if timer_actor is None or self._get_timer_data() is None:
            msg = "Cannot stop a timer that is not running."
            raise RuntimeError(msg)
        timer_actor.Timers = []

    def pause(self) -> None:
        """Pause the timer, does not interrupt the count."""
        timer_data = self._get_timer_data()
        if timer_data is None:
            msg = "Cannot pause a timer that is not running."
            raise RuntimeError(msg)
        timer_data.bPaused = True

    def resume(self) -> None:
        """Resume the timer."""
        timer_data = self._get_timer_data()
        if timer_data is None:
            msg = "Cannot resume a timer that is not running."
            raise RuntimeError(msg)
            return
        timer_data.bPaused = False

    def update(self, duration: float, loop: bool) -> None:
        """Update the timer while it is running.

        Args:
            duration: the new duration for the timer.
            loop: If true the timer will restart automatically with the same values.

        """
        timer_data = self._get_timer_data()
        if timer_data is None:
            return
        timer_data.Rate = duration
        timer_data.bLoop = loop
        self.duration = duration
        self.loop = loop

    def is_running(self) -> bool:
        """Check if the timer has been started."""
        return self._get_timer_data() is not None

    def is_paused(self) -> bool:
        """Check if the timer is paused."""
        timer_data = self._get_timer_data()
        if timer_data is None:
            msg = "Timer is not running, cannot check if it is paused."
            raise RuntimeError(msg)
        return timer_data.bPaused


build_mod(cls=Library)
