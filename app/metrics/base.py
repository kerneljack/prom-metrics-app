from abc import ABC, abstractmethod
from contextlib import contextmanager
from functools import wraps
from typing import Callable, Iterator, TypeVar

F = TypeVar("F", bound=Callable)


class MetricsBackend(ABC):
    """Abstract base class defining the metrics interface."""

    @abstractmethod
    def inc_requests(self) -> None:
        """Increment total HTTP request counter."""
        pass

    @abstractmethod
    def inc_successful(self) -> None:
        """Increment successful HTTP request counter."""
        pass

    @abstractmethod
    def inc_4xx(self) -> None:
        """Increment 4xx error counter."""
        pass

    @abstractmethod
    def inc_5xx(self) -> None:
        """Increment 5xx error counter."""
        pass

    @abstractmethod
    @contextmanager
    def time_request(self) -> Iterator[None]:
        """Context manager to time request duration."""
        pass

    def time_request_decorator(self) -> Callable[[F], F]:
        """Decorator to time request duration."""
        def decorator(func: F) -> F:
            @wraps(func)
            def wrapper(*args, **kwargs):
                with self.time_request():
                    return func(*args, **kwargs)
            return wrapper  # type: ignore
        return decorator

    @abstractmethod
    def get_metrics_summary(self) -> dict:
        """Return current metric values for display."""
        pass
