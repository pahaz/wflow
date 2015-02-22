import threading

__author__ = 'pahaz'


class EventManager(object):
    """
    Base class for all events

    Plugin example:

        # simple_plugin/__init__.py

        import logging


        def woow_printer_listener(**kwargs):
            print("Woow simple-event EVENT!!")


        def load(command_manager, event_manager, env):
            event_manager.add_event_listener('simple-event', woow_printer_listener)
    
    """
    def __init__(self):
        """
        Create a new signal.
        """
        self._receivers = {}
        self._lock = threading.Lock()

    def add_event_listener(self, event_name, receiver):
        """
        Connect receiver to event.

        Arguments:

            event_name
                Trigged event name.

            receiver
                A function or an instance method which is to receive signals.
                Receivers must be hashable objects.

                Receivers must be able to accept keyword arguments.

        """
        import inspect
        if not callable(receiver):
            raise TypeError("Signal receivers must be callable.")

        # Check for **kwargs
        # Not all callables are inspectable with getargspec, so we'll
        # try a couple different ways but in the end fall back on assuming
        # it is -- we don't want to prevent registration of valid but weird
        # callables.
        try:
            argspec = inspect.getargspec(receiver)
        except TypeError:
            try:
                argspec = inspect.getargspec(receiver.__call__)
            except (TypeError, AttributeError):
                argspec = None
        if not argspec:
            raise TypeError("Unknown receiver argspec.")

        if argspec.keywords is None:
                raise TypeError("Event receivers must accept "
                                "keyword arguments (**kwargs).")

        with self._lock:
            event_receivers = self._receivers.get(event_name, [])
            event_receivers.append(receiver)
            self._receivers[event_name] = event_receivers

    def rm_event_listener(self, event_name, receiver):
        """
        Disconnect receiver from event.

        If weak references are used, disconnect need not be called. The receiver
        will be remove from dispatch automatically.

        Arguments:

            event_name
                Trigged event name.

            receiver
                The registered receiver to disconnect. May be none if
                dispatch_uid is specified.

        """
        with self._lock:
            event_receivers = self._receivers.get(event_name)
            if not event_receivers:
                raise ValueError('Unknown event name')

            try:
                event_receivers.remove(receiver)
            except ValueError:
                raise ValueError('Unknown event receiver')

    def has_event_listener(self, event_name, receiver):
        return receiver in self._receivers.get(event_name, [])

    def trigger_event(self, event_name, **kwargs):
        """
        Trigger event from all connected receivers.

        Arguments:

            event_name
                Trigged event name.

        Returns a list of tuple pairs [(receiver, response), ... ].
        """
        responses = []

        event_receivers = self._receivers.get(event_name)
        if not event_receivers:
            return responses

        for receiver in event_receivers:
            rez = receiver(**kwargs)
            responses.append((receiver, rez))
        return responses

    def listen(self, *event_names):
        """
        A decorator for connecting receivers to events.

            @listen("super-important-event")
            def signal_receiver(**kwargs):
                ...

            @listen("super-important-event", "super-event-2")
            def signals_receiver(**kwargs):
                ...

        """
        def _decorator(func):
            for event_name in event_names:
                self.add_event_listener(event_name, func)
            return func
        return _decorator
