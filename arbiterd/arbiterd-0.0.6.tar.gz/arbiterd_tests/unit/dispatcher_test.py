# -*- coding: utf-8 -*-
# Copyright 2021 - 2021, Sean Mooney and the arbiterd contributors
# SPDX-License-Identifier: Apache-2.0
from unittest import mock

import testtools
from arbiterd import dispatcher
from arbiterd.arbiters import cpu_state


class TestDispatcher(testtools.TestCase):

    def test_init(self):
        dispatch = dispatcher.Dispatcher()
        self.assertIsNotNone(dispatch.arbiters)
        self.assertIn(cpu_state.CPUStateArbiter.TYPE, dispatch.arbiters)
        self.assertIsInstance(
            dispatch.arbiters[cpu_state.CPUStateArbiter.TYPE],
            cpu_state.CPUStateArbiter
        )

    def test_arbitrate_and_revoke_base(self):
        dispatch = dispatcher.Dispatcher()
        arbiter_mock = mock.MagicMock()
        dispatch.arbiters['fake'] = arbiter_mock
        dispatch.arbitrate('fake', None)
        dispatch.revoke('fake', 42)
        arbiter_mock.arbitrate.assert_called_with(None)
        arbiter_mock.revoke.assert_called_with(42)
