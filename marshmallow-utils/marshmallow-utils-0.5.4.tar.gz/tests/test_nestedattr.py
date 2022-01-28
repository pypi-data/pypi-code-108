# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Marshmallow-Utils is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

from datetime import date

from marshmallow import Schema, fields

from marshmallow_utils.fields import nestedattr


class ArtistSchema(Schema):
    """Artist Schema."""
    name = fields.Str()


class AlbumSchema(Schema):
    """Album Schema."""

    artist = nestedattr.NestedAttribute(ArtistSchema())


class MyAlbum(dict):

    @property
    def artist(self):
        return {'name': self['artist']['name'].capitalize()}


def test_schema():
    album = MyAlbum(
        artist={'name': 'david'},  # this shouldn't be used in the schema dump
        title="Hunky Dory",
        release_date=date(1971, 12, 17)
    )

    schema = AlbumSchema()
    result = schema.dump(album)

    assert result['artist'] == {'name': 'David'}
