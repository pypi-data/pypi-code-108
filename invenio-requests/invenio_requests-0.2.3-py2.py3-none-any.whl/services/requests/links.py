# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 TU Wien.
#
# Invenio-Requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Utility for rendering URI template links."""

from invenio_records_resources.services.base.links import Link, LinksTemplate


class RequestLinksTemplate(LinksTemplate):
    """Templates for generating links for a request object."""

    def __init__(self, links, action_link, context=None):
        """Constructor."""
        super().__init__(links, context=context)
        self._action_link = action_link

    def expand(self, req, identity=None):
        """Expand all the link templates."""
        links = {}

        # expand links for all available actions on the request
        links["actions"] = {}
        link = self._action_link
        for action in req.type.available_actions:
            ctx = self.context.copy()
            ctx["action"] = action
            ctx["identity"] = identity
            if link.should_render(req, ctx):
                links["actions"][action] = link.expand(req, ctx)

        # expand the other configured links
        for key, link in self._links.items():
            if link.should_render(req, self.context):
                links[key] = link.expand(req, self.context)

        return links


class RequestLink(Link):
    """Shortcut for writing request links."""

    @staticmethod
    def vars(record, vars):
        """Variables for the URI template."""
        # TODO this uses the UUID of the record, should we maybe use the number/ext-id?
        vars.update({"id": record.id})
