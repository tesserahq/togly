"""Utilities for subscribing to NATS events using FastStream.

Ported from orcha's app/messaging/nats_subscriber.py (~/sites/linden-family/orcha) -
same shape, reused rather than reinvented. NatsEventPublisher
(tessera_sdk.infra.events.nats_router), already used by Togly for outbound
publishing, is publish-only in the currently pinned SDK version and has no
subscriber counterpart, so this is new code in Togly itself rather than an SDK
import. See docs/prds/0002-contact-custom-fields-and-events.md, "Custom Events".
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Mapping

from faststream import FastStream
from faststream.nats import NatsBroker

from app.config import Settings, get_settings

MessageHandler = Callable[..., Awaitable[None]]


class NatsEventSubscriber:
    """Convenience wrapper around FastStream's NATS broker."""

    def __init__(
        self,
        broker: NatsBroker | None = None,
        *,
        app: FastStream | None = None,
        settings: Settings | None = None,
    ) -> None:
        """Initialize the subscriber with the configured broker and app.

        Args:
            broker: Optional broker instance to reuse (useful for testing).
            app: Optional FastStream app instance to reuse (useful for testing).
            settings: Optional settings instance. When omitted the global
                application settings are loaded.
        """
        self.settings = settings or get_settings()
        self.broker = broker or NatsBroker(self.settings.nats_url)
        self.app = app or FastStream(self.broker)
        self._registered_subjects: set[str] = set()

    def subscribe(
        self,
        subject: str,
        handler: MessageHandler,
        *,
        queue: str | None = None,
    ) -> None:
        """Register a handler for a subject."""
        queue_name = queue or self.settings.nats_queue or None
        subscriber = self.broker.subscriber(subject, queue=queue_name)
        subscriber(handler)
        self._registered_subjects.add(subject)

    def subscribe_bulk(
        self,
        handlers: Mapping[str, MessageHandler],
        *,
        queue: str | None = None,
    ) -> None:
        """Register a mapping of subject names to handler callables."""
        for subject, handler in handlers.items():
            self.subscribe(subject, handler, queue=queue)

    def run(self, **kwargs) -> None:
        """Start the FastStream application to process subscriptions."""
        if not self.settings.nats_enabled:
            raise RuntimeError("NATS subscriptions are disabled in configuration.")
        self.app.run(**kwargs)

    @property
    def registered_subjects(self) -> set[str]:
        """Return the set of subjects currently registered."""
        return set(self._registered_subjects)
