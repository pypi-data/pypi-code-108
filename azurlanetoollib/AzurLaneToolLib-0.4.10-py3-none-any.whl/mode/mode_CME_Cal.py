#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
THIS FILE IS Mode OF AZUR LANE TOOL BY MATT BELFAST BROWN
mode_CME_Cal.py - The core mode of the Azur Lane Tool.

Author:Matt Belfast Brown 
Create Date:2021-07-10
Version Date:2022-01-21
Version:0.4.10
Mode Create Date:2019-08-10
Mode Date:2022-01-22
Mode Version:0.3.1

THIS PROGRAM IS FREE FOR EVERYONE,IS LICENSED UNDER GPL-3.0
YOU SHOULD HAVE RECEIVED A COPY OF GPL-3.0 LICENSE.

Copyright (C) 2021-2022 Matt Belfast Brown

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A ModeICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

#define import list
    #Null


#define function
def fun_evdb_cmul(vari_cmlv):
    if vari_cmlv==1:
        vari_cler=1
    elif 2<=vari_cmlv<=50:
        vari_cler=(vari_cmlv+1)//3
    elif 51<=vari_cmlv<=70:
        vari_cler=(vari_cmlv+1)//2
    elif 71<=vari_cmlv<=90:
        vari_cler=vari_cmlv+1
    elif 91<=vari_cmlv<=110:
        vari_cler=(vari_cmlv+1)*2
    elif 111<=vari_cmlv<=120:
        vari_cler=(vari_cmlv+1)*3
    elif 121<=vari_cmlv<=130:
        vari_cler=3*vari_cmlv
    elif 131<=vari_cmlv<=150:
        vari_cler=4*vari_cmlv
    elif 151<=vari_cmlv<=170:
        vari_cler=5*vari_cmlv
    elif 171<=vari_cmlv<=190:
        vari_cler=6*vari_cmlv
    elif 191<=vari_cmlv<200:
        vari_cler=7*vari_cmlv
    else:
        vari_cler=0
    vari_cler=int(vari_cler)
    return vari_cler
    
def fun_berf_cmug(vari_cmlv):
    para_cmex=40
    vari_cmex=0
    for para_cmlv in range(1,vari_cmlv+1):
        para_cmle=fun_evdb_cmul(para_cmlv)
        para_cmex=para_cmex+10*para_cmle
        vari_cmex=vari_cmex+para_cmex
    return vari_cmex