#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Verify motor voltage and current mode-related commands execute
successfully.
"""


import pytest

from stepseries import commands, responses
from stepseries.step400 import STEP400


@pytest.mark.skip_400_disconnected
@pytest.mark.reset_400_device
class TestVoltageCurrentMessages:
    def test_set_voltage_mode(self, device: STEP400, motor_id: int) -> None:
        # Send the set command
        device.set(commands.SetVoltageMode(motor_id))

    def test_kval(self, device: STEP400, motor_id: int, presets) -> None:
        # Send the set command
        device.set(
            commands.SetKval(
                motor_id,
                presets.kval_hold,
                presets.kval_run,
                presets.kval_acc,
                presets.kval_dec,
            )
        )

        # Verify the set command
        response: responses.Kval = device.get(commands.GetKval(motor_id))
        assert isinstance(response, responses.Kval)
        assert response.holdKVAL == presets.kval_hold
        assert response.runKVAL == presets.kval_run
        assert response.accKVAL == presets.kval_acc
        assert response.setDecKVAL == presets.kval_dec

    def test_bemf_param(self, device: STEP400, motor_id: int, presets) -> None:
        # Verify the motor is in a HiZ state
        device.set(commands.HardHiZ(motor_id))

        response: responses.HiZ = device.get(commands.GetHiZ(motor_id))
        assert response.state

        # Send the BEMF set command
        device.set(
            commands.SetBemfParam(
                motor_id,
                presets.bemf_int_speed,
                presets.bemf_st_slp,
                presets.bemf_fn_slp_acc,
                presets.bemf_fn_slp_dec,
            )
        )

        # Verify the set command was successful
        response: responses.BemfParam = device.get(commands.GetBemfParam(motor_id))
        assert isinstance(response, responses.BemfParam)
        assert response.INT_SPEED == presets.bemf_int_speed
        assert response.ST_SLP == presets.bemf_st_slp
        assert response.FN_SLP_ACC == presets.bemf_fn_slp_acc
        assert response.FN_SLP_DEC == presets.bemf_fn_slp_dec

    def test_set_current_mode(self, device: STEP400, motor_id: int) -> None:
        # Send the set command
        device.set(commands.SetCurrentMode(motor_id))

    def test_tval(self, device: STEP400, motor_id: int, presets) -> None:
        # Send the set command
        device.set(
            commands.SetTval(
                motor_id,
                presets.tval_hold,
                presets.tval_run,
                presets.tval_acc,
                presets.tval_dec,
            )
        )

        # Verify the set command
        response: responses.Tval = device.get(commands.GetTval(motor_id))
        assert isinstance(response, responses.Tval)
        assert response.holdTVAL == presets.tval_hold
        assert response.runTVAL == presets.tval_run
        assert response.accTVAL == presets.tval_acc
        assert response.decTVAL == presets.tval_dec

    def test_decay_mode_param(self, device: STEP400, motor_id: int, presets) -> None:
        # Send the set command
        device.set(
            commands.SetDecayModeParam(
                motor_id,
                presets.dmp_fast,
                presets.dmp_onmin,
                presets.dmp_offmin,
            )
        )

        # Verify the set command
        response: responses.DecayModeParam = device.get(
            commands.GetDecayModeParam(motor_id)
        )
        assert isinstance(response, responses.DecayModeParam)
        assert response.T_FAST == presets.dmp_fast
        assert response.TON_MIN == presets.dmp_onmin
        assert response.TOFF_MIN == presets.dmp_offmin
