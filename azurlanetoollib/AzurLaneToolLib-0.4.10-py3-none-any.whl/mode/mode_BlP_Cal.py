#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
THIS FILE IS PART OF AZUR LANE TOOL BY MATT BELFAST BROWN
mode_BlP_Cal.py - The core mode of the Azur Lane Tool.

Author:Matt Belfast Brown 
Creat Date:2021-07-10
Version Date:2022-01-22
Version:0.4.10
Mode Create Date:2020-05-02
Mode Date:2022-01-22
Mode Version:1.0.3

THIS PROGRAM IS FREE FOR EVERYONE,IS LICENSED UNDER GPL-3.0
YOU SHOULD HAVE RECEIVED A COPY OF GPL-3.0 LICENSE.

Copyright (C) 2021-2022 Matt Belfast Brown

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

#define import list
    #Null

def fun_cnbp_rqub (vari_plle) :
    #最高方案类型
    if 1 <= vari_plle <= 4 or 6 <= vari_plle <= 9 or 11 <= vari_plle <= 14 :
        vari_bprb = 0.4 * vari_plle - 0.4* ( vari_plle % 5 ) + 2
    elif 16 <= vari_plle <= 19 or 21 <= vari_plle<= 24 or 26 <= vari_plle <= 29 :
        vari_bprb = vari_plle - ( vari_plle % 5) - 5
    elif vari_plle == 5:
        vari_bprb = 5 
    elif vari_plle % 5 ==0:
        vari_bprb =int ( -(vari_plle ** 3 ) / 375 + ( vari_plle ** 2 ) / 5 - 2.9333 * vari_plle +20 )
    return vari_bprb  #升一级所需基础蓝图数量

def fun_cnbp_rqup (flag_pltp,vari_plle):
    if flag_pltp =='Top Solution':
        #最高方案
        vari_bprq = fun_cnbp_rqub(vari_plle)
    elif flag_pltp == 'Decisive Plan' :
        #决战方案
        vari_bprq = int(fun_cnbp_rqub(vari_plle)*1.5)  #最高方案类的1.5倍，并向下取整
    return vari_bprq  #升一级所需蓝图数量

def fun_cnbp_rrcl(flag_pltp,vari_plde,vari_epbp):
    vari_tbpr=0
    vari_tebp=0
    for para_plle in range (vari_lede):
        vari_tbpr+=fun_cnbp_rqup(flag_pltp,para_leve)
    for para_plee in range (vari_levn):
        vari_tebp+=fun_cnbp_rqup(flag_pltp,para_leex)
    vari_tebp+=vari_epbp
    vari_prbp=vari_tbpr-vari_tebp
    return vari_prbp,vari_tebp  #科研图纸需求计算结果 已用的总蓝图数

def fun_cnbp_tyfi(flag_pltp,vari_tfdl,vari_tyfg,vari_crtf):
    vari_bpty=0
    if flag_pltp == 'Top Solution' :
        for i in range(x):
            vari_bpty+=list_fitt[i]
        vari_bpty+=int((vari_crtf/100)*list_fitt[x])
        vari_tbtf=165-vari_bpty
    elif flag_pltp == 'Decisive Plan' :
        for i in range(x):
            vari_bpty+=list_fitd[i]
        vari_bpty+=int((vari_crtf/100)*list_fitt[x])
        vari_tbtf=215-vari_bpty   
    return vari_tbtf,vari_bpty  #天运拟合总需蓝图数  天运拟合总用蓝图数
    
def fun_cnbp_rbpt(flag_pltp,flag_pftf,vari_plde,vari_epbp,vari_tfdl,vari_tyfg,vari_crtf):
    if flag_pftf == True:
        vari_tbtf,vari_bpty=fun_cnbp_tyfi(flag_pltp,vari_tfdl,vari_tyfg,vari_crtf)
    elif flag_pftf == False:
        vari_tbtf,vari_bpty=0,0
    vari_prbp,vari_tebp=fun_cnbp_rrcl(flag_pltp,vari_plde,vari_epbp)
    vari_prbt=vari_prbp+vari_tbtf
    vari_tbpt=vari_tebp+vari_bpty
    return [vari_prbt,vari_tbpt,vari_prbp,vari_tebp,vari_tbtf,vari_bpty]#[科研图纸需求含天运拟合,已用的总蓝图数含天运拟合,科研图纸需求计算结果,已用的总蓝图数,天运拟合总需蓝图数,天运拟合总用蓝图数]
    
#define list
list_fitt=[10,20,30,40,65]
list_fitd=[20,30,40,50,75]