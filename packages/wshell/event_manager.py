from __future__ import unicode_literals, print_function, generators, division
import logging
import threading

from wutil.env_stack import EnvStack

__author__ = 'pahaz'


class EventManager(object):
    """
    Base class for all events

    Plugin example:

        # simple_plugin/__init__.py

        import logging


        def printer_listener(env):
            print("Woow simple-event EVENT!!")


        def load(command_manager, event_manager, env):
            event_manager.add_event_listener('print-event', printer_listener)
    
    """
    log = logging.getLogger(__name__)

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
            raise TypeError("event listener must be callable")

        # Check receiver signature.
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

        if argspec is None:
            raise TypeError("No receiver specification")

        args = argspec.args
        if len(args) > 3:
            raise TypeError("Invalid receiver specification. "
                            "More then two positional args. "
                            "`callable(manager, env)` required")

        has_wrong_args = args not in (['manager', 'env'],
                                      ['self', 'manager', 'env'],
                                      ['cls', 'manager', 'env'])
        has_kwargs = argspec.keywords is not None
        has_args = argspec.varargs is not None
        has_defaults = argspec.defaults is not None

        if has_args or has_kwargs or has_defaults or has_wrong_args:
            raise TypeError("Invalid receiver specification. "
                            "`callable(manager, env)`, "
                            "`callable(self, manager, env)` or "
                            "`callable(cls, manager, env)` required")

        self.log.info('add listener {0} for event {1}'
                      .format(receiver, event_name))

        with self._lock:
            event_receivers = self._receivers.get(event_name, [])
            event_receivers.append(receiver)
            self._receivers[event_name] = event_receivers

    def remove_event_listener(self, event_name, receiver):
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
        self.log.info('remove listener {0} for event {1}'
                      .format(receiver, event_name))

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

    def trigger_event(self, event_name, env_stack, env_extra_layer=None):
        """
        Trigger event from all connected receivers.

        Arguments:

            event_name
                Trigged event name.

        Returns a list of tuple triples [(receiver, result, error), ... ].
        """
        if not isinstance(env_stack, EnvStack):
            raise TypeError('Invalid env type. EnvStack instance required')

        self.log.info('trigger {0} event extra={1}'
                      .format(event_name, env_extra_layer))

        responses = []
        event_receivers = self._receivers.get(event_name)
        if not event_receivers:
            self.log.debug('no receivers for event {0}'.format(event_name))
            return responses

        if env_extra_layer:
            try:
                env_stack.push(env_extra_layer)
            except TypeError as e:
                self.log.debug('push env_extra_layer error')
                raise TypeError('Invalid env extra layer. ' + str(e))

        for receiver in event_receivers:
            try:
                rez = receiver(self, env_stack)
            except Exception as e:
                error_msg = 'receiver {0} error: {1} ({2})' \
                    .format(receiver, e, type(e).__name__)
                self.log.error(error_msg)
                self.log.debug(error_msg, exc_info=True)
                err, rez = e, None
            else:
                self.log.info('receiver {0} return: {1}'.format(receiver, rez))
                err, rez = None, rez

            responses.append((receiver, rez, err))

        if env_extra_layer:
            env_stack.pop()

        return responses

    def listen(self, *event_names):
        """
        A decorator for connecting receivers to events.

            @listen("super-important-event")
            def signal_receiver(env):
                ...

            @listen("super-important-event", "super-event-2")
            def signals_receiver(env):
                ...

        """

        def _decorator(func):
            for event_name in event_names:
                self.add_event_listener(event_name, func)
            return func

        return _decorator
