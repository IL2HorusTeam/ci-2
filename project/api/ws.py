# coding: utf-8

from flask_sockets import Sockets as FlaskSockets


class Sockets(FlaskSockets):

    def __init__(self, *args, **kwargs):
        super(Sockets, self).__init__(*args, **kwargs)

        self.blueprints = {}
        self._blueprint_order = []

    def register_blueprint(self, blueprint, **options):
        """
        Registers a blueprint on the application.
        """
        first_registration = False

        if blueprint.name in self.blueprints:
            assert self.blueprints[blueprint.name] is blueprint, \
                'A blueprint\'s name collision occurred between %r and ' \
                '%r.  Both share the same name "%s".  Blueprints that ' \
                'are created on the fly need unique names.' % \
                (blueprint, self.blueprints[blueprint.name], blueprint.name)

        else:
            self.blueprints[blueprint.name] = blueprint
            self._blueprint_order.append(blueprint)
            first_registration = True

        blueprint.register(self, options, first_registration)
