# -*- coding: utf-8 -*-

import numpy as np
from . import kine

from mpl_toolkits.mplot3d import Axes3D
import matplotlib
from .pyver import __pyver
if __pyver == 3:
    matplotlib.use('Qt5Agg')
else:
    matplotlib.use('Qt4Agg')
import matplotlib.pyplot as plt
from . import mplh
import json


def adjustDictForML(d):
    dML = {}
    for k in d:
        kML = k.replace(' ', '_')
        dML[kML] = d[k]
    return dML


def duplicateMarkersFromRigidClusters(
        markersSource,
        markersTarget,
        dataDef,
        verbose
    ):
    
    rigidBodySVDFunVerbose = verbose
    
    # prepare results store
    res = {}
    res['newMarkers'] = {}
    
    # scan cluster definitions for rigid clusters and store them
    clustersMarkersLoc = {}
    for clusterDef in dataDef['clusters']:
        clusterName = clusterDef['name']
        if clusterDef['is_rigid']:
            clustersMarkersLoc[clusterName] = {m['name']: np.array(m['loc']) for m in clusterDef['markers']}

    # create marker by marker
    for markerDef in dataDef["markers"]:
        
        if 'name' in markerDef:
            markerNameSource = markerDef['name']
            markerNameTarget = markerDef['name']
        else:
            markerNameSource = markerDef['name_source']
            markerNameTarget = markerDef['name_target']
        clusterDef = markerDef["cluster"]
        markersLoc = None
        markersLocNames = None
        useRigidCluster = None
        
        if isinstance(clusterDef, dict):
            clusterName = None
            allFromSameCluster = True
            namesMap = {}
            for marker in clusterDef["markers"]:
                if 'from' in marker.keys():
                    if clusterName is None:
                        clusterName = marker['from']
                else:
                    allFromSameCluster = False
                    break
                modelName = marker['as']
                realName = marker['name']
                namesMap[modelName] = realName
            if not allFromSameCluster:
                raise Exception('not all markers from same cluster')
            markersLoc = clustersMarkersLoc[clusterName]
            markersLoc2 = {}
            for m in markersLoc:
                realName = namesMap[m]
                markersLoc2[realName] = markersLoc[m]
            markersLoc = markersLoc2
            useRigidCluster = True
        else:
            clusterDefName = clusterDef
            l = list(filter(lambda clusterDef: clusterDef['name'] == clusterDefName, dataDef['clusters']))
            if len(l) == 1:
                clusterDef = l[0]
                markersLocNames = [marker['name'] for marker in clusterDef['markers']]
                useRigidCluster = False
            else:
                raise Exception('no single cluster definition called %s' % clusterDefName)
                
        # Plot spine in 3D
#        fig = plt.figure()
#        ax = fig.gca(projection='3d')
#        ax.scatter(markersSource['CL1'][0,0], markersSource['CL1'][0,1], markersSource['CL1'][0,2], 'r')
#        ax.scatter(markersSource['CL2'][0,0], markersSource['CL2'][0,1], markersSource['CL2'][0,2], 'g')
#        ax.scatter(markersSource['CL3'][0,0], markersSource['CL3'][0,1], markersSource['CL3'][0,2], 'b')
#        ax.scatter(markersSource['CL_TRUE'][0,0], markersSource['CL_TRUE'][0,1], markersSource['CL3'][0,2], c='y')
#        ax.scatter(markersSource['T12'][0,0], markersSource['T12'][0,1], markersSource['T12'][0,2], c='c')
#        ax.scatter(markersSource['L2'][0,0], markersSource['L2'][0,1], markersSource['L2'][0,2], c='k')
#        ax.scatter(markersSource['L4'][0,0], markersSource['L4'][0,1], markersSource['L4'][0,2], c='k')
#        mplh.set_axes_equal(ax)
#        plt.xlabel('x')
#        plt.ylabel('y')
#        plt.show()
#        input()

        # SVD for markers source
        print('=====================')
        if useRigidCluster:
            args = {}
            args['mkrsLoc'] = markersLoc
            args['verbose'] = rigidBodySVDFunVerbose
            args['useOriginFromTrilat'] = False
            mkrList = list(markersLoc.keys())
            R1, T1, infoSVD1 = kine.rigidBodySVDFun2(markersSource, mkrList, args)
        else:
            R1, T1 = kine.markersClusterFun(markersSource, markersLocNames)
        RT1 = kine.composeRotoTranslMatrix(R1, T1)
        print('=====================')
        
        # Express cluster base and real marker in cluster reference frame
        RT1i = kine.inv2(RT1)
        targetMarkers = {}
        targetMarkers[markerNameTarget] = markersSource[markerNameSource]
        targetMarkersLoc = kine.changeMarkersReferenceFrame(targetMarkers, RT1i)
        if not useRigidCluster:
            mkrs = {m: markersSource[m] for m in markersLocNames}
            markersLoc = kine.changeMarkersReferenceFrame(mkrs, RT1i)
            markersLoc = {m: markersLoc[m][0] for m in markersLoc.keys()}
        
        # SVD for markers target
        args = {}
        args['mkrsLoc'] = markersLoc
        args['verbose'] = rigidBodySVDFunVerbose
        args['useOriginFromTrilat'] = False
        mkrList = list(set(markersLoc.keys()) & set(markersTarget.keys()))
        R2, T2, infoSVD2 = kine.rigidBodySVDFun2(markersTarget, mkrList, args)
        RT2 = kine.composeRotoTranslMatrix(R2, T2)
        print('=====================')
        
        # create new marker
        newMarker = kine.changeMarkersReferenceFrame(targetMarkersLoc, RT2)[markerNameTarget]
        res['newMarkers'][markerNameTarget] = newMarker
        
    return res


def updateParams(params):
    lastVersion = 4
    if 'version' not in params:
        if 'defSegPoses' not in params:
            ver = 0
        elif ('defSegPoses' in params) and ('defL2PProjs' not in params):
            ver = 1
    else:
        ver = params['version']
    params2 = json.loads(json.dumps(params))
    for v in range(ver, lastVersion, 1):
        
        if v == 1:
            
            params2['defL2PProjs'] = [
                {
                    "name": "my_proj",
                    "line": "my_line",
                    "plane": "my_plane;nZ"
                }
            ]
            params2['calcL2PProjs'] = {
                "list": [
                    "my_proj"
                ],
                "selected": []
            }
            params2['defInterlineAngles'] = [
                {
                    "name": "my_il_angle",
                    "line1": "my_line_1",
                    "line2": "my_line_2"
                }
            ]
            params2['calcInterlineAngles'] = {
                "list": [
                    "my_il_angle"
                ],
                "selected": []
            }
            
        elif v == 2:
            
            graphItems = json.loads(json.dumps(params['UI']['points']))
            for itemName in list(graphItems.keys()):
                item = graphItems[itemName]
                item['color'] = '#%s' % item['color'][1:]
                item['opacity'] = 100.
                item['visible'] = True
            params2['graphItems'] = graphItems
            del params2['UI']
            params2['streamOut'] = [
                {
                    'name': 'flexion_angle',
                    'from': 'knee_extension_angle',
                    'sign': '-'
                }
            ]
            
        elif v == 3:
            
            params2['defScenes'] = [
                {
                     "name": "my_scene",
                     "geomItems": "all_selected",
                     "pointItems": "all_selected",
                     "ref": "my_ref",
                     "frames": "first_and_last",
                     "exporter": "XML3Matic"
                }
            ]
            params2['useScenes'] = {
                "list": [
                    "my_scene"
                ],
                "selected": []
            }
            
    params2['version'] = lastVersion
    return params2
