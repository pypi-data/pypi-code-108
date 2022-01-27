#!/usr/bin/env python
# Copyright 2020-2022 The PyFLOSIC Developers. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Author: Sebastian Schwalbe <theonov13@gmail.com>
#
from pyflosic2.systems.uflosic_systems import H as UH, He as UHe, H2 as UH2, CH4 as UCH4, Ne_ontop as UNe_ontop, \
    Ne_inverted as UNe_inverted, Ar as UAr, H2O as UH2O, COH2 as UCOH2
from pyflosic2.systems.rflosic_systems import He as RHe, H2 as RH2, CH4 as RCH4, Ne_ontop as RNe_ontop, Ar as RAr, \
    H2O as RH2O, COH2 as RCOH2


def H(p):
    if p.mode == 'unrestricted':
        return UH()
    if p.mode == 'restricted':
        print('Restricted mode for open-shell system currently not supported.')


def He(p):
    if p.mode == 'unrestricted':
        return UHe()
    if p.mode == 'restricted':
        return RHe()


def H2(p):
    if p.mode == 'unrestricted':
        return UH2()
    if p.mode == 'restricted':
        return RH2()


def CH4(p):
    if p.mode == 'unrestricted':
        return UCH4()
    if p.mode == 'restricted':
        return RCH4()


def Ne_ontop(p):
    if p.mode == 'unrestricted':
        return UNe_ontop()
    if p.mode == 'restricted':
        return RNe_ontop()


def Ne_inverted(p):
    if p.mode == 'unrestricted':
        return UNe_inverted()
    if p.mode == 'restricted':
        print('Restricted mode for open-shell system currently not supported.')


def Ar(p):
    if p.mode == 'unrestricted':
        return UAr()
    if p.mode == 'restricted':
        return RAr()


def H2O(p):
    if p.mode == 'unrestricted':
        return UH2O()
    if p.mode == 'restricted':
        return RH2O()


def COH2(p):
    if p.mode == 'unrestricted':
        return UCOH2()
    if p.mode == 'restricted':
        return RCOH2()
