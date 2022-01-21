#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Verify motor voltage and current mode-related commands execute
successfully.
"""


import pytest

from stepseries import commands, exceptions, responses
from stepseries.step800 import STEP800


@pytest.mark.skip_800_disconnected
@pytest.mark.reset_800_device
class TestVoltageCurrentMessages:
    def test_set_voltage_mode(self, device: STEP800, motor_id: int) -> None:
        # Not a valid command on the STEP800, the API will raise an
        # error
        with pytest.raises(exceptions.InvalidCommandError):
            device.set(commands.SetVoltageMode(motor_id))

    def test_kval(self, device: STEP800, motor_id: int, presets) -> None:
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

    def test_bemf_param(self, device: STEP800, motor_id: int, presets) -> None:
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

    def test_set_current_mode(self, device: STEP800, motor_id: int) -> None:
        # Not a valid command on the STEP800, the API will raise an
        # error
        with pytest.raises(exceptions.InvalidCommandError):
            device.set(commands.SetCurrentMode(motor_id))

    def test_tval(self, device: STEP800, motor_id: int) -> None:
        # Not a valid command on the STEP800, the API will raise an
        # error
        with pytest.raises(exceptions.InvalidCommandError):
            device.set(commands.SetTval(motor_id, 0, 0, 0, 0))

        with pytest.raises(exceptions.InvalidCommandError):
            device.get(commands.GetTval(motor_id))

        with pytest.raises(exceptions.InvalidCommandError):
            device.get(commands.GetTval_mA(motor_id))

    def test_decay_mode_param(self, device: STEP800, motor_id: int) -> None:
        # Not a valid command on the STEP800, the API will raise an
        # error
        with pytest.raises(exceptions.InvalidCommandError):
            device.set(commands.SetDecayModeParam(motor_id, 0, 0, 0))

        with pytest.raises(exceptions.InvalidCommandError):
            device.get(commands.GetDecayModeParam(motor_id))
