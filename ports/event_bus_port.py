from typing import Protocol, Any

class IEventBus(Protocol):
    """
    Interface untuk Event Bus dalam arsitektur heksagonal.
    """
    def subscribe(self, event_type: str, callback) -> None:
        ...

    def unsubscribe(self, event_type: str, callback) -> None:
        ...

    def publish(self, event: Any) -> None:
        ...
