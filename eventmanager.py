'''事件管理器'''
from typing import Dict, Iterator, List, Set
from agemanager import WeightedEvent
from event import Event


class EventManager:
    '''事件管理器,用于管理发生的事件'''
    @staticmethod
    def load(config):
        EventManager._events: Dict[int, Event] = {
            int(k): Event(config[k]) for k in config}
        for k in EventManager._events:
            for b in EventManager._events[k].branch:
                b.evt = EventManager._events[b.id]

    def __init__(self, base, rnd):
        self._base = base
        self.triggered: Set[int] = set()
        self._rnd = rnd

    def _rand_event(self, events: List[WeightedEvent]) -> int:
        events_checked = [ev for ev in events if EventManager._events[ev.evt].check_condition(
            self._base.property)]
        total = sum(e.weight for e in events_checked)
        rnd = self._rnd.random() * total
        for ev in events_checked:
            rnd -= ev.weight
            if rnd <= 0:
                return ev.evt
        return events[0].evt

    def _run_event(self, event: Event) -> Iterator[str]:
        self.triggered.add(event.id)
        return event.run_event(self._base.property, self._run_event)

    def run_events(self, events: List[WeightedEvent]) -> Iterator[str]:
        ev = self._rand_event(events)
        return self._run_event(EventManager._events[ev])
