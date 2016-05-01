# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import abc
import six

from flask import Blueprint
from slugify import slugify
from unipath import Path


class AbstractBlueprint(six.with_metaclass(abc.ABCMeta, Blueprint)):

    def add_view_url_rule(self, rule, view_cls, **kwargs):
        name = "{0}/{1}".format(self.name, rule)
        name = slugify(name, separator='_')
        name = self.generate_blueprint_name(name)
        name = str(name)
        view_func = view_cls.as_view(name)

        kwargs.setdefault('view_func', view_func)
        self.add_url_rule(rule, **kwargs)

    @property
    def collection_name(self):
        return Path(self.name)

    def child(self, name, import_name, *args, **kwargs):
        name = self.collection_name.child(name)
        name = self.generate_blueprint_name(name)
        return Blueprint(name, import_name, *args, **kwargs)

    def generate_blueprint_name(self, initial):
        value = initial
        i = 1

        while value in self.registry:
            value = "{0}{1}".format(initial, i)
            i += 1

        return value

    @abc.abstractproperty
    def registry(self):
        """
        Registry of blueprints.
        """


class RESTBlueprint(AbstractBlueprint):

    @property
    def registry(self):
        from project.app import app
        return app.blueprints


class WSBlueprint(AbstractBlueprint):

    @property
    def registry(self):
        from project.app import sockets
        return sockets.blueprints
