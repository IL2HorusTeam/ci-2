# coding: utf-8

import ujson as json

from geventwebsocket.exceptions import WebSocketError

from project.app import app

from .response.ws import WSError


class WebSocketView(object):

    decorators = []

    def __call__(self, ws):
        self.ws = ws
        while True:
            message = self.receive_message()
            if message is None:
                break
            else:
                self.on_message(message)

    dispatch_request = __call__

    def receive_message(self):
        try:
            message = self.ws.receive()
        except WebSocketError:
            message = None

        if message is not None:
            try:
                data = json.loads(message)
            except ValueError as e:
                app.logger.exception(
                    "Failed to read message '{:}':".format(message))
                self.ws.send(WSError(detail=e))
            else:
                return data

    def on_message(self, message):
        pass

    @classmethod
    def as_view(cls, name, *class_args, **class_kwargs):
        """
        Converts the class into an actual view function that can be used with
        the routing system. The arguments passed to :meth:`as_view` are
        forwarded to the constructor of the class.
        """
        def view(*args, **kwargs):
            self = view.view_class(*class_args, **class_kwargs)
            return self.dispatch_request(*args, **kwargs)

        if cls.decorators:
            view.__name__ = name
            view.__module__ = cls.__module__
            for decorator in cls.decorators:
                view = decorator(view)

        # We attach the view class to the view function for two reasons:
        # first of all it allows us to easily figure out what class-based
        # view this thing came from, secondly it's also used for instantiating
        # the view class so you can actually replace it with something else
        # for testing purposes and debugging.
        view.view_class = cls
        view.__name__ = name
        view.__doc__ = cls.__doc__
        view.__module__ = cls.__module__
        return view
