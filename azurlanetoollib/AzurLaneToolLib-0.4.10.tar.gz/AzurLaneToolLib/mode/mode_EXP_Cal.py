#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
THIS FILE IS PART OF AZUR LANE TOOL BY MATT BELFAST BROWN
mode_EXP_Cal.py - The core mode of the Azur Lane Tool.

Author:Matt Belfast Brown 
Create Date:2021-07-10
Version Date:2022-01-21
Version:0.4.10
Mode Create Date:2020-09-25
Mode Date:2022-01-22
Mode Version:0.4.1

THIS PROGRAM IS FREE FOR EVERYONE,IS LICENSED UNDER GPL-3.0
YOU SHOULD HAVE RECEIVED A COPY OF GPL-3.0 LICENSE.

Copyright (C) 2021-2022 Matt Belfast Brown

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

'''
#define function
 y=kx+b and k=da and b=mn
 m=-100 n=1000
 a and n are in function fun_cexp_vrfu
'''

#define import list
    #Null

#define function
def fun_cexp_vrfu(flag_kstp,vari_leve):
    if flag_kstp=='Top Solution':
        if vari_leve==0:
            vari_vara=0
            vari_inva=0
        elif vari_leve>0 and vari_leve<=40:
            vari_vara=0.1
            vari_inva=0
        elif vari_leve>40 and vari_leve<=60:
            vari_vara=0.2
            vari_inva=40
        elif vari_leve>60 and vari_leve<=70:
            vari_vara=0.3
            vari_inva=100
        elif vari_leve>70 and vari_leve<=80:
            vari_vara=0.4
            vari_inva=170
        elif vari_leve>80 and vari_leve<=90:
            vari_vara=0.5
            vari_inva=250
        elif vari_leve>90 and vari_leve<=92:
            vari_vara=1
            vari_inva=700
        elif vari_leve>92 and vari_leve<=94:
            vari_vara=2
            vari_inva=1620
        elif vari_leve==95:
            vari_vara=4
            vari_inva=3500
        elif vari_leve>95 and vari_leve<=97:
            vari_vara=5
            vari_inva=4450
        elif vari_leve==98:
            vari_vara=20
            vari_inva=19000
        elif vari_leve==99:
            vari_vara=72
            vari_inva=69960
        elif vari_leve==100:
            vari_vara=-82
            vari_inva=-82500
        elif vari_leve>100 and vari_leve<=105:
            vari_vara=3
            vari_inva=2500
        elif vari_leve>105 and vari_leve<=110:
            vari_vara=6
            vari_inva=5650
        elif vari_leve>110 and vari_leve<=115:
            vari_vara=10
            vari_inva=10050
        elif vari_leve>115 and vari_leve<=120:
            vari_vara=15
            vari_inva=15800
        elif vari_leve>120 and vari_leve<125:
            vari_vara=21
            vari_inva=23000
        elif vari_leve==125:
            vari_vara=2696
            vari_inva=3340000
    elif flag_kstp=='Decisive Plan':
        if vari_leve==0:
            vari_vara=0
            vari_inva=0
        elif vari_leve>0 and vari_leve<=40:
            vari_vara=0.12
            vari_inva=0
        elif vari_leve>40 and vari_leve<=60:
            vari_vara=0.24
            vari_inva=48
        elif vari_leve>60 and vari_leve<=70:
            vari_vara=0.36
            vari_inva=120
        elif vari_leve>70 and vari_leve<=80:
            vari_vara=0.48
            vari_inva=204
        elif vari_leve>80 and vari_leve<90:
            vari_vara=0.6
            vari_inva=300
        elif vari_leve==90:
            vari_vara=0.65
            vari_inva=325
        elif vari_leve>90 and vari_leve<=92:
            vari_vara=1.3
            vari_inva=910
        elif vari_leve>92 and vari_leve<=94:
            vari_vara=2.6
            vari_inva=2106
        elif vari_leve==95:
            vari_vara=5.2
            vari_inva=4550
        elif vari_leve>95 and vari_leve<=97:
            vari_vara=6.5
            vari_inva=5785
        elif vari_leve==98:
            vari_vara=26
            vari_inva=24700
        elif vari_leve==99:
            vari_vara=93.6
            vari_inva=90948
        elif vari_leve==100:
            vari_vara=-111.6
            vari_inva=-112200
        elif vari_leve>100 and vari_leve<=105:
            vari_vara=3.6
            vari_inva=3000
        elif vari_leve>105 and vari_leve<=110:
            vari_vara=7.2
            vari_inva=6780
        elif vari_leve>110 and vari_leve<=115:
            vari_vara=12
            vari_inva=12060
        elif vari_leve>115 and vari_leve<=120:
            vari_vara=18
            vari_inva=18960
        elif vari_leve>120 and vari_leve<125:
            vari_vara=25.2
            vari_inva=27600
        elif vari_leve==125:
            vari_vara=2635.2
            vari_inva=3264000
    cons_slin=1000
    cons_inqu=-100
    para_ince=cons_inqu*vari_inva
    para_slop=cons_slin*vari_vara
    vari_erfv=int(para_slop*vari_leve+para_ince)
    return vari_erfv
    
def fun_crex_cele(flag_kstp,vari_lede,vari_levn,vari_eexp):
    vari_texp=0
    vari_teep=0
    for para_leve in range (vari_lede):
        vari_texp+=fun_cexp_vrfu(flag_kstp,para_leve)
    for para_leex in range (vari_levn):
        vari_teep+=fun_cexp_vrfu(flag_kstp,para_leex)
    vari_teep+=vari_eexp
    vari_rexp=vari_texp-vari_teep
    return vari_rexp,vari_teep #总需经验值 现有总经验值