"""
.. module:: procedure_rig
   :synopsis: helper module for procedures used with any rig

"""

import numpy as np

from . import kine, kine_or, ligaments as liga, fio, vtkh

import os
from mpl_toolkits.mplot3d import Axes3D
import matplotlib
from .pyver import __pyver
if __pyver == 3:
    matplotlib.use('Qt5Agg')
else:
    matplotlib.use('Qt4Agg')
import matplotlib.pyplot as plt


def performAnalysis(
        markers,
        params,
        resultsDir
        ):
    
    
    if not os.path.exists(resultsDir):
        os.mkdir(resultsDir)
    
    cr = 4
    cc = 2
    
    results = {}
    
    results['landmarks'] = {}
    
    linePaths = {}

    side = params['side']
    
    mkrsLoc = {m: np.array(params['mkrsLoc'][m]['pos']) for m in params['mkrsLoc']}
    
    mkrsSegs = {}
    for m in params['mkrsLoc']:
        if 'fixedTo' in params['mkrsLoc'][m]:
            mkrsSegs[m] = params['mkrsLoc'][m]['fixedTo']
            
    ALs = {m: np.array(params['mkrsLoc'][m]['pos']) for m in params['mkrsLoc']}

    mkrs = markers
    N = markers[list(markers.keys())[0]].shape[0]
    
    t = np.arange(N)
    
    globalPoints = {}
    
    for m in params['mkrsLoc']:
        if params['mkrsLoc'][m]['fixedTo'] == 'global':
            pos = np.array(params['mkrsLoc'][m]['pos'])
            globalPoints[m] = np.tile(pos[np.newaxis,:], (N, 1))
        
    results['landmarks'].update(globalPoints)
    
    args = {}
    args['mkrsLoc'] = mkrsLoc
    args['verbose'] = False

    RTs = {}

    allALs = {}
    
    defSegPoses = params['defSegPoses']
    
    segList = params['calcSegPoses']['selected']

    poses = {}
    
    axesLength = 100.
    axesPoints = {
        'O': np.array([0.,0.,0.]),
        'X': np.array([axesLength,0.,0.]),
        'Y': np.array([0.,axesLength,0.]),
        'Z': np.array([0.,0.,axesLength]),
    }

    axes = {}
    
    meshes = {}

    for segName in segList:

        defSegPose = [s for s in defSegPoses if s['name'] == segName][0]

        type = defSegPose['type']
        mkrList = defSegPose['markers'].split(',')
        funName = defSegPose['defFun']

        if type == 'markers_fitting':

            R, T, info = kine.rigidBodySVDFun(mkrs, mkrList, args)
            RT = kine.composeRotoTranslMatrix(R, T)
            RTs[segName] = RT
            pose = {}
            pose['matrix'] = RT
            pose['RMSE'] = info['RMSE']
            pose['err_max'] = info['eMax']
            pose['err_max_marker'] = info['eMaxMarker']
            poses[segName] = pose
            
            plt.subplot(cr,cc,1)
            plt.plot(t, pose['RMSE'], label=segName)
            plt.legend(loc='upper right', fontsize=7)
            plt.title('Markers fitting RMSE (mm)')
            plt.subplot(cr,cc,2)
            plt.plot(t, pose['err_max'], label=segName)
            plt.legend(loc='upper right', fontsize=7)
            plt.title('Markers fitting error max (mm)')

        elif type == 'define_from_markers':

            RTseg = RTs[mkrsSegs[mkrList[0]]]
            usedALs = {m: ALs[m] for m in mkrList}
            allALs.update(kine.changeMarkersReferenceFrame(usedALs, RTseg))
            R, T = kine_or.register[funName](allALs, s=side)
            RT = kine.composeRotoTranslMatrix(R, T)
            RTs[segName] = RT
            pose = {}
            pose['matrix'] = RT
            pose['RMSE'] = [0] * N
            pose['err_max'] = [0] * N
            pose['err_max_marker'] = [''] * N
            poses[segName] = pose
            
        if type == 'define_from_markers':
            axesPointsGlob = kine.changeMarkersReferenceFrame(axesPoints, RT)
            for a in ['X', 'Y', 'Z']:
                axesName = segName + '_' + a
                axes[axesName] = [[]] * N
                for i in range(N):
                    axes[axesName][i] = np.array([axesPointsGlob['O'][i,:], axesPointsGlob[a][i,:]])
        
        geometryFile = defSegPose['geometryFile']
        if geometryFile != '':
            meshes[segName] = fio.readSTL(geometryFile)
            
    results['poses'] = poses
        
    results['landmarks'].update({m: allALs[m] for m in allALs})
    
    linePaths.update(axes)
    
    defJoints = params['defJoints']
    
    jointsList = params['calcJoints']['selected']
    
    results['joint_angles'] = {}
    results['joint_transl'] = {}
    results['joint_outputs'] = {}

    for jointName in jointsList:

        defJoint = [j for j in defJoints if j['name'] == jointName][0]
        segName1 = defJoint['seg1']
        segName2 = defJoint['seg2']
        invertJointRotMatrix = defJoint['invertJointRotMatrix']
        defAngles = defJoint['R2AnglesFun']
        outputs = defJoint['outputs']

        RT1 = RTs[segName1]
        RT2 = RTs[segName2]

        Ra1, Oa1 = RT1[:,:3,:3], RT1[:,:3,3]
        Ra2, Oa2 = RT2[:,:3,:3], RT2[:,:3,3]

        if defAngles == 'ges':
            R2anglesFun = kine_or.gesOR
            funInput = 'segmentsR'
        else:
            R2anglesFun = defAngles
            funInput = 'jointRMatrix'
        if invertJointRotMatrix:
            Ra1, Ra2 = Ra2, Ra1
        angles = kine.getJointAngles(Ra1, Ra2, R2anglesFun=R2anglesFun, funInput=funInput, s=side)
        transl = kine.getJointTransl(Ra1, Ra2, Oa1, Oa2, T2translFun=kine_or.gesTranslOR)

        results['joint_angles'][jointName] = angles
        results['joint_transl'][jointName] = transl
        
        outputNames = outputs.split(',')
        angleName1 = '%s_%s' % (jointName, outputNames[0])
        angleName2 = '%s_%s' % (jointName, outputNames[1])
        angleName3 = '%s_%s' % (jointName, outputNames[2])
        translName1 = '%s_%s' % (jointName, outputNames[3])
        translName2 = '%s_%s' % (jointName, outputNames[4])
        translName3 = '%s_%s' % (jointName, outputNames[5])
        results['joint_outputs'][angleName1] = angles[:,0]
        results['joint_outputs'][angleName2] = angles[:,1]
        results['joint_outputs'][angleName3] = angles[:,2]
        results['joint_outputs'][translName1] = transl[:,0]
        results['joint_outputs'][translName2] = transl[:,1]
        results['joint_outputs'][translName3] = transl[:,2]
        
        plt.subplot(cr,cc,3)
        plt.plot(t, angles[:,0], label=angleName1)
        plt.plot(t, angles[:,1], label=angleName2)
        plt.plot(t, angles[:,2], label=angleName3)
        plt.legend(loc='upper right', fontsize=7)
        plt.title('Joint angles (deg)')
        plt.subplot(cr,cc,4)
        plt.plot(t, transl[:,0], label=translName1)
        plt.plot(t, transl[:,1], label=translName2)
        plt.plot(t, transl[:,2], label=translName3)
        plt.legend(loc='upper right', fontsize=7)
        plt.title('Joint translations (mm)') 
        
    splinesLoc = {s: np.array(params['splines'][s]['pos']) for s in params['splines']}

    splinesSegs = {s: params['splines'][s]['fixedTo'] for s in params['splines']}

    splinesLocParams = {}
    for s in params['splines']:
        splinesLocParams[s] = liga.createParamSpline(splinesLoc[s])
        
    ligaPaths = {}
    ligaLengths = {}
    ligaStrains = {}
    
    defLigas = params['defLigas']
    
    ligasList = params['calcLigas']['selected']
    
    outputSnapshots = params['outputSnapshots']

    for ligaName in ligasList:

        defLiga = [l for l in defLigas if l['name'] == ligaName][0]
        name = defLiga['name']
        ins1 = defLiga['ins1']
        method = defLiga['method']
        spline = defLiga['edge']
        ins2 = defLiga['ins2']

        segIns1 = mkrsSegs[ins1]
        segIns2 = mkrsSegs[ins2]
        segSpline = None
        if spline != '':
            segSpline = splinesSegs[spline]

        if segIns1 == 'global':
            RT1 = np.tile(np.eye(4)[np.newaxis,:,:], (N, 1, 1))
        else:
            RT1 = RTs[segIns1]
        if segIns2 == 'global':
            RT2 = np.tile(np.eye(4)[np.newaxis,:,:], (N, 1, 1))
        else:
            RT2 = RTs[segIns2]
            
        if segSpline is not None:
            RTe = RTs[segSpline]

        p1Loc = {ins1: mkrsLoc[ins1]}
        p1 = kine.changeMarkersReferenceFrame(p1Loc, RT1)[ins1]

        p2Loc = {ins2: mkrsLoc[ins2]}
        p2 = kine.changeMarkersReferenceFrame(p2Loc, RT2)[ins2]
        
        ligaPaths[name] = [[]] * N
        ligaLengths[name] = np.nan * np.zeros((N,))
        ligaStrains[name] = np.nan * np.zeros((N,))
        
        ligaSnapshots = [l for l in outputSnapshots if l['output'] == '%s_length' % name]
        ligaLengthRef = None
        if len(ligaSnapshots) > 0:
            ligaSnapshot = ligaSnapshots[0]
            ligaLengthRef = ligaSnapshot['value']
        
        meshNames = [segIns1, segIns2]
        frames = range(N)
        saveScene = False
        sceneOutputDir = None
        
        if 'args' in defLiga:
            extraArgs = defLiga['args']
            extraMeshNames = extraArgs['extraMeshes']
            meshNames.extend(extraMeshNames)
            if 'frames' in extraArgs:
                frames = extraArgs['frames'] 
            if 'algoArgs' in extraArgs:
                algoArgs = extraArgs['algoArgs']
            if 'saveScene' in extraArgs:
                saveScene = extraArgs['saveScene']
                sceneOutputDir = extraArgs['sceneOutputDir']

        meshNames = list(set(meshNames))
        if 'global' in meshNames:
             meshNames.remove('global')
        meshes_ = {m: meshes[m] for m in meshNames}
        
        for i in range(N):
            
            if i in frames:

                ligaPath = np.array((p1[i,:], p2[i,:]))
                
                meshesReposed = [vtkh.reposeVTKData(meshes_[m], RTs[m][i,...]) for m in meshNames]
        
                if method == 'shortest_via_edge':
        
                    splineParams = liga.reposeSpline(splinesLocParams[spline], RTe[i,...])
                    dummy, ligaPath = liga.ligamentPathBlankevoort1991(ligaPath, splineParams)
                    
                elif method == 'marai_2024':
                    
                    dummy, ligaPath = liga.ligamentPathMonari2021(ligaPath, meshesReposed[0], meshesReposed[1], **algoArgs)
                    
                elif method == 'monari_2021':
                    
                    for j in range(ligaPath.shape[0]):                                
                        ligaPath[j,:] = vtkh.externalizePointFromMeshes(ligaPath[j,:], meshesReposed, factor=0.5)
                    
                    ligaPath = liga.ligamentPathMonari2021(ligaPath, meshesReposed, **algoArgs)
                    
                if saveScene:
                    
                    print('saving scene for frame %d for ligament %s... ' % (i, ligaName))
                    
                    actors = []
                    actorNames = []
                    
                    for lp in ligaPath:
                        actors.append(vtkh.createVTKActor(vtkh.createSphereVTKData(lp, 1)))
                        actorNames.append('p')
                    
                    actors.extend([vtkh.createVTKActor(meshReposed) for meshReposed in meshesReposed])
                    actorNames.extend(meshNames)
                    
                    vtkLigaPath = vtkh.createLineVTKData(ligaPath)
                    actors.append(vtkh.createVTKActor(vtkLigaPath, color=[255,0,0]))
                    actorNames.append(ligaName)
                    
                    scene = vtkh.createScene(actors)
                    vtkh.exportScene(scene, sceneOutputDir + ('/scene_%05d' % i), ext='vtm', names=actorNames)
        
                ligaLength = np.linalg.norm(np.diff(ligaPath, axis=0), axis=1).sum()
                
                if ligaLengthRef is not None:
                    ligaStrain = 100. * (1.*ligaLength - ligaLengthRef) / ligaLengthRef
                else:
                    ligaStrain = np.nan
                    
            else:
                
                ligaPath = np.nan * np.ones((0,3))
                ligaLength = np.nan
                ligaStrain = np.nan

            ligaPaths[name][i] = ligaPath
            ligaLengths[name][i] = ligaLength
            ligaStrains[name][i] = ligaStrain
        
        ls = '-'
        ms = None
        hasNans = np.isnan(ligaLengths[name]).any()
        if hasNans:
            ls = '.'
            ms = 2.0
        plt.subplot(cr,cc,5)
        plt.plot(t, ligaLengths[name], ls, ms=ms, label=name)
        plt.legend(loc='upper right', fontsize=7)
        plt.title('Ligament lengths (mm)')
        plt.subplot(cr,cc,6)
        plt.plot(t, ligaStrains[name], ls, ms=ms, label=name)
        plt.legend(loc='upper right', fontsize=7)
        plt.title('Ligament strains (%)') 

    linePaths.update(ligaPaths)
    results['lengths'] = ligaLengths
    results['strains'] = ligaStrains
    
    defL2PProjs = params['defL2PProjs']
    
    L2PProjsList = params['calcL2PProjs']['selected']
    
    lineProjPaths = {}

    for L2PProjName in L2PProjsList:

        defL2PProj = [l for l in defL2PProjs if l['name'] == L2PProjName][0]
        name = defL2PProj['name']
        lineName = defL2PProj['line']
        planeName = defL2PProj['plane']
        segName, normName = planeName.split(';')
        
        RT = RTs[segName]
    
        RTi = kine.inv2(RT)
        
        lineProjPaths[name] = [[]] * N
        
        for i in range(N):

            linePath = np.array(linePaths[lineName][i])
    
            points = {}
            
            for r in range(linePath.shape[0]):
                points['p%d' % r] = linePath[r,:]

            pointsInRef = kine.changeMarkersReferenceFrame(points, RTi[i:i+1,...])
    
            if normName == 'nX':
                idx = 0
            elif normName == 'nY':
                idx = 1
            elif normName == 'nZ':
                idx = 2
    
            for p in pointsInRef:
                pointsInRef[p][0,idx] = 0
    
            pointsProj = kine.changeMarkersReferenceFrame(pointsInRef, RT[i:i+1,...])
            pointsProj = np.array([pointsProj[m][0,:] for m in pointsProj])
    
            lineProjPaths[name][i] = pointsProj
        
        
    linePaths.update(lineProjPaths)
    
    defInterlineAngles = params['defInterlineAngles']
    
    interlineAnglesList = params['calcInterlineAngles']['selected']
    
    angles = {}

    for interlineAngleName in interlineAnglesList:

        defInterlineAngle = [a for a in defInterlineAngles if a['name'] == interlineAngleName][0]
        name = defInterlineAngle['name']
        lineName1 = defInterlineAngle['line1']
        lineName2 = defInterlineAngle['line2']
        
        angles[name] = np.nan * np.zeros((N,))
        
        for i in range(N):

            linePath1 = np.array(linePaths[lineName1][i])
            linePath2 = np.array(linePaths[lineName2][i])
    
            vec1 = np.diff(linePath1, axis=0)[0,:]
            vec2 = np.diff(linePath2, axis=0)[0,:]
    
            vec1 /= np.linalg.norm(vec1)
            vec2 /= np.linalg.norm(vec2)
    
            angle = np.rad2deg(np.arccos(np.dot(vec1, vec2)))
            if angle > 90:
                angle = 180. - angle
    
            angles[name][i] = angle
            
        plt.subplot(cr,cc,7)
        plt.plot(t, angles[name], label=name)
        plt.legend(loc='upper right', fontsize=7)
        plt.title('Interline angles (deg)')

    results['interline_angles'] = angles

    results['paths'] = linePaths
    
    
    defScenes = params['defScenes']
    
    scenesList = params['useScenes']['selected']

    for sceneName in scenesList:

        defScene = [l for l in defScenes if l['name'] == sceneName][0]
        geomNames = defScene['geomItems']
        pointNames = defScene['pointItems']
        refName = defScene['ref']
        frames = defScene['frames']
        exporter = defScene['exporter']
        
        RT = RTs[refName]
        RTi = kine.inv2(RT)
        RTRef = RTi
        
        if geomNames == 'all_selected':
            meshNames = list(meshes.keys())
        RTsRef = {m: kine.dot3(RTRef, RTs[m]) for m in meshNames}
                
        if pointNames == 'all_selected':
            points = results['landmarks']
        pointsInRef = kine.changeMarkersReferenceFrame(points, RTRef)
        
        if frames == 'all':
            frames_ = list(range(N))
        elif frames == 'first_and_last':
            frames_ = [0, N-1]
        else:
            frames_ = frames[:]
         
        for i in range(N):
            
            if i in frames_:
                
                folderName = '%s_fr_%05d' % (sceneName, i)
                folderPath = os.path.join(resultsDir, folderName)
                
                if not os.path.exists(folderPath):
                    os.mkdir(folderPath)
                
                exportSTLs = False
                
                if exporter == 'XML3Matic':
                    
                    pointCloud = []
                    for m in pointsInRef:
                        item = {}
                        item['name'] = str(m)
                        item['type'] = 'point'
                        item['coords'] = pointsInRef[m][i,:]
                        pointCloud.append(item)
    
                    filePathXML = os.path.join(folderPath, 'mimics.xml')
                    fio.writeXML3Matic(filePathXML, pointCloud)
                    
                    exportSTLs = True
                    
                if exportSTLs:
                    
                    for m in meshNames:
                        meshInRef = vtkh.reposeVTKData(meshes[m], RTsRef[m][i,...])
                        filePathSTL = os.path.join(folderPath, '%s.stl' % m)
                        fio.writeSTL(filePathSTL, meshInRef)

    
    plt.tight_layout()
    
    manager = plt.get_current_fig_manager()
    manager.window.showMaximized()
    plt.savefig(os.path.join(resultsDir, 'summary.png'), format='png', orientation='landscape')
    
    plt.show()
    
    return results
