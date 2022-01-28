# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Marshmallow-Utils is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Persistent identifier Schema with automatic scheme detection.

Integrates idutils library to detect the scheme.
"""

import idutils
from marshmallow import Schema, ValidationError, post_load, pre_load, \
    validates_schema

from ..fields import SanitizedUnicode


class IdentifierSchema(Schema):
    """Identifier with automatic scheme detection."""

    identifier = SanitizedUnicode()
    scheme = SanitizedUnicode()

    error_messages = {
        "invalid_identifier": "Invalid {scheme} identifier.",
        "invalid_scheme": "Invalid scheme.",
        "required": "Missing data for required field.",
    }

    def __init__(self, allowed_schemes, identifier_required=True, **kwargs):
        """Constructor.

        :param allowed_schemes: a dictionary of allowed schemes. Each key must
            contain a validator function and a scheme label.
        :param identifier_required: True when the identifier value is required.
        """
        self.identifier_required = identifier_required
        self.allowed_schemes = allowed_schemes
        super().__init__(**kwargs)

    def _intersect_with_order(self, detected_schemes):
        """Returns the first detected scheme that is allowed."""
        allowed_schemes = set(self.allowed_schemes.keys())
        for detected in detected_schemes:
            if detected in allowed_schemes:
                return detected

        return None

    @pre_load(pass_many=False)
    def load_scheme(self, data, **kwargs):
        """Loads the scheme of the identifier."""
        # If no identifier provided, proceed to validation
        identifier = data.get("identifier")
        if not identifier:
            return data

        # If identifier and scheme is provided, proceed to validation.
        scheme = data.get("scheme")
        if scheme:
            return data

        # If identifier but no scheme is provided, try to detect scheme
        detected_schemes = idutils.detect_identifier_schemes(identifier)

        # Select a valid scheme from the detected ones.
        detected_scheme = self._intersect_with_order(detected_schemes)
        if detected_scheme:
            data["scheme"] = detected_scheme
        return data

    @validates_schema
    def validate_identifier(self, data, **kwargs):
        """Validate the identifier format and scheme."""
        identifier = data.get("identifier")
        scheme = data.get("scheme")

        # Bail if identifier is not required and identifier/scheme is not
        # provided
        if not self.identifier_required and not identifier and not scheme:
            return

        errors = dict()

        # Validate scheme
        if not scheme:
            errors['scheme'] = self.error_messages["required"]
        elif scheme not in self.allowed_schemes:
            errors['scheme'] = self.error_messages["invalid_scheme"]

        # Validate identifier
        if not identifier:
            errors['identifier'] = self.error_messages["required"]
        elif scheme and scheme in self.allowed_schemes:
            validator = self.allowed_schemes[scheme]["validator"]
            if not validator(identifier):
                message = self.error_messages["invalid_identifier"]
                scheme_label = self.allowed_schemes[scheme].get(
                    "label", scheme
                )
                errors['identifier'] = message.format(scheme=scheme_label)

        if errors:
            raise ValidationError(errors)

    @post_load
    def normalize_identifier(self, data, **kwargs):
        """Normalizes the identifier based on the scheme."""
        identifier = data.get("identifier")

        # It can be empty if not required
        if identifier:
            # at this point, `scheme` is set or validation failed earlier
            scheme = data["scheme"]
            # will return the same value if not able to normalize by idutils
            data["identifier"] = idutils.normalize_pid(identifier, scheme)

        return data
