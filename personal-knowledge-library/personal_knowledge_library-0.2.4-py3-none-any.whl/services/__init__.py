# -*- coding: utf-8 -*-
# Copyright © 2021 Wacom. All rights reserved.

USER_AGENT_STR: str = "Personal Knowledge Library/0.2.4 " \
                      "(+https://github.com/Wacom-Developer/personal-knowledge-library)"

__all__ = ['base', 'graph', 'ontology', 'USER_AGENT_STR']

from knowledge.services import base
from knowledge.services import graph
from knowledge.services import ontology
