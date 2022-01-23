#!/usr/bin/env python3

import vtk
#from vtk.util import numpy_support
from vtk import vtkStructuredPointsReader
from numpy import random
#from EMAN2 import *
import numpy as np

class VtkPointCloud:

    def __init__(self, listOfPoints, model="", thresholdModel=0.01, listOfPoints2=[], listSubsetGoodPoints=[], great_circle_V=[], great_circle_VNext=[]):
        zMin=50.0
        zMax=80.0
        maxNumPoints=1e6;
        self.model = model
        self.thresholdModel = thresholdModel
        self.maxNumPoints = maxNumPoints
        self.radius = 1
        self.center = 0
        self.centerX = 0
        self.centerY = 0
        self.centerZ = 0
        self.vtkControlPolyData = vtk.vtkPolyData()
        self.vtkPolyData = vtk.vtkPolyData()
        self.linesPolyData = vtk.vtkPolyData()        
        self.Go(listOfPoints, listOfPoints2, listSubsetGoodPoints, great_circle_V, great_circle_VNext)
        
#    def volumeReader(self, model):
#        print 'volume reader'
#        volume = EMNumPy.em2numpy(EMData(model))
#        imageData = vtk.vtkImageData()
#        print volume.shape[1]
#        imageData.SetDimensions(volume.shape[0],volume.shape[1],volume.shape[2])
#        imageData.AllocateScalars(vtk.VTK_DOUBLE, 1)
#        for z in range(0,volume.shape[2]):
#            for y in range(0,volume.shape[1]):
#                for x in range(0,volume.shape[0]):
#                    imageData.SetScalarComponentFromDouble(x, y, z, 0, volume[x][y][z])



    def modelVolumeActor(self):
#        reader = vtk.vtkMetaImageReader()
#        reader.SetFileName( "/Users/mauro/tmpSharedFolder/simulations/tube/allPadded.mhd" ) #self.model)
#        mapExtractor = vtk.vtkMarchingCubes()
#        mapExtractor.SetInputConnection(reader.GetOutputPort())
#        print ( str(reader.GetWidth() ))
#        print ( str(reader.GetHeight() ))


#        print ( str(reader.GetWidth() ))
#        print ( str(reader.GetHeight() ))

        #reader = vtk.vtkDataSet()
        reader2 = vtkStructuredPointsReader()
        #reader2.SetFileName("/Users/mauro/tmpSharedFolder/simulations/tube/allPadded.vtk")
        reader2.SetFileName(self.model)
        reader2.ReadAllVectorsOn()
        reader2.ReadAllScalarsOn()
        reader2.Update()
        data2 = reader2.GetOutput()
        dim = data2.GetDimensions()
        maxDim=max(dim)
        self.radius= maxDim/2.0
        self.center= 130 #self.radius
        self.centerX= 128
        self.centerY= 140
        self.centerZ= 132
        print (max(dim))
        print (self.radius)
        #reader = vtk.vtkGenericDataObjectReader()
        #reader.SetFileName( "/Users/mauro/tmpSharedFolder/simulations/tube/allPadded.vtk" )
        #print ( str( reader.GetCellDimension  () ))
        #GetLength ()GetCenter ()GetHeader ()
        #imageData=vtk.vtkImageData()
        #imageData.SetInputConnection(reader.GetOutputPort())
        
        mapExtractor = vtk.vtkMarchingCubes()
        mapExtractor.SetInputConnection(reader2.GetOutputPort())
        mapExtractor.SetValue(0, 0.01)
        
        #print ( str(mapExtractor.GetValues() ))
        actor = vtk.vtkActor()
        mapper=vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(mapExtractor.GetOutputPort())
        mapper.ScalarVisibilityOff(); #to allow color
        #mapper.SetCenter(0.0, 0.0, 0.0)
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(0.3,0.3,0.3);
        actor.GetProperty().SetOpacity(1.0)
        return actor


    def axisActor(self):
        cylinderSource=vtk.vtkCylinderSource();
        cylinderSource.SetCenter(0, 0, 0);
        cylinderSource.SetRadius(0.01*self.radius);
        cylinderSource.SetHeight(2.3*self.radius);
        cylinderSource.SetResolution(100);
        actor = vtk.vtkActor()
        mapper=vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(cylinderSource.GetOutputPort());
        actor.SetMapper(mapper)
        actor.RotateX(90);
        #actor.GetProperty().SetOpacity(0.1)
        return actor



    def sphereActor(self):    
         # Create a sphere
        sphereSource = vtk.vtkSphereSource()
        sphereSource.SetCenter(self.centerX, self.centerY, self.centerZ)
        sphereSource.SetRadius(self.radius)
        #sphereSource.SetCenter(0.0, 0.0, 0.0)
        #if len(str(self.model)) < 2:
        sphereSource.SetRadius(0.9*self.radius)

        # Make the surface smooth.
        sphereSource.SetPhiResolution(300)
        sphereSource.SetThetaResolution(300)
        mapperSphere = vtk.vtkPolyDataMapper()
        mapperSphere.SetInputConnection(sphereSource.GetOutputPort())
        colors = vtk.vtkNamedColors()
        actorSphere = vtk.vtkActor()
        actorSphere.SetMapper(mapperSphere)
        actorSphere.GetProperty().SetColor(colors.GetColor3d("Cornsilk"))
        if len(str(self.model))>1:
          actorSphere.GetProperty().SetOpacity(0.2);
        else:
          actorSphere.GetProperty().SetOpacity(1.0);
        return actorSphere



    def actorDiameterCircle(self, Phi, Theta):
        disk=vtk.vtkDiskSource()
        disk.SetInnerRadius (1.0*self.radius)
        disk.SetOuterRadius (1.05*self.radius)
        disk.SetRadialResolution (100)
        disk. SetCircumferentialResolution(100)
        mapperSphere = vtk.vtkPolyDataMapper()
        mapperSphere.SetInputConnection(disk.GetOutputPort())
        colors = vtk.vtkNamedColors()
        vtkActor = vtk.vtkActor()
        vtkActor.SetMapper(mapperSphere)
        vtkActor.GetProperty().SetColor(colors.GetColor3d("AliceBlue"))
        vtkActor.RotateX ( Phi )
        vtkActor.RotateY ( Theta)
        return vtkActor

    def actorSegmentsError(self, listOfPoints, listOfPoints2):
        vtkPoints = vtk.vtkPoints()
        vtkCells = vtk.vtkCellArray()
        vtkColour = vtk.vtkDoubleArray()
        vtkColour.SetName('vtkColour')
        vtkPolyData = vtk.vtkPolyData()
        vtkPolyData.SetPoints(vtkPoints)
        #vtkPolyData.SetVerts(vtkCells)
        vtkPolyData.SetLines(vtkCells) #for the line
        vtkPolyData.GetPointData().SetScalars(vtkColour)
        vtkPolyData.GetPointData().SetActiveScalars('vtkColour')
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(vtkPolyData)
        mapper.SetColorModeToDefault()
        mapper.SetScalarRange(0, 1)
        #mapper.SetScalarVisibility(2)
        print ("ecchimi")
        for k in range(0, len(listOfPoints2)):
            pointId = vtkPoints.InsertNextPoint(listOfPoints[k])
            pointNextId = vtkPoints.InsertNextPoint(listOfPoints2[k])
            #vtkColour.InsertNextValue(0.5)
            #vtkColour.InsertNextValue(0.5)
            vtkColour.InsertNextValue( 0.1 )
            vtkColour.InsertNextValue( 0.1)
            vtkCells.InsertNextCell(2)
            vtkCells.InsertCellPoint(pointId)
            vtkCells.InsertCellPoint(pointNextId)

        vtkActor = vtk.vtkActor()
        vtkActor.GetProperty().SetPointSize(1)
        vtkActor.SetMapper(mapper)
        return vtkActor


    def actorSegments(self, listOfPoints, great_circle_V, great_circle_VNext):
        vtkPoints = vtk.vtkPoints()
        vtkCells = vtk.vtkCellArray()
        vtkColour = vtk.vtkDoubleArray()
        vtkColour.SetName('vtkColour')
        vtkPolyData = vtk.vtkPolyData()
        vtkPolyData.SetPoints(vtkPoints)
        #vtkPolyData.SetVerts(vtkCells)
        vtkPolyData.SetLines(vtkCells) #for the line
        vtkPolyData.GetPointData().SetScalars(vtkColour)
        vtkPolyData.GetPointData().SetActiveScalars('vtkColour')
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(vtkPolyData)
        mapper.SetColorModeToDefault()
        mapper.SetScalarRange(0, 1)
        #mapper.SetScalarVisibility(2)

        for k in range(0, len(great_circle_V)):
          pointIdx=int(float(great_circle_V[k]))
          pointNextIdx=int(float(great_circle_VNext[k]))
          if pointIdx>=0 and pointIdx<len(listOfPoints) and  pointNextIdx>=0 and pointNextIdx<len(listOfPoints):
            print (str(pointIdx), " -> ", str(pointNextIdx) )
            #print str(k)+': '+str(pointIdx)+' ->  '+str(pointNextIdx)
            pointId = vtkPoints.InsertNextPoint(listOfPoints[pointIdx])
            pointNextId = vtkPoints.InsertNextPoint(listOfPoints[pointNextIdx])
            vtkColour.InsertNextValue(0.1)
            vtkColour.InsertNextValue(0.1)
            vtkCells.InsertNextCell(2)
            vtkCells.InsertCellPoint(pointId)
            vtkCells.InsertCellPoint(pointNextId)


        vtkActor = vtk.vtkActor()
        vtkActor.GetProperty().SetPointSize(1)
        vtkActor.SetMapper(mapper)
        return vtkActor






        
    def actorPoints(self, listOfPoints, listSubsetGoodPoints):
        vtkPoints = vtk.vtkPoints()
        vtkCells = vtk.vtkCellArray()
        vtkColour = vtk.vtkDoubleArray()
        vtkColour.SetName('vtkColour')
        vtkPolyData = vtk.vtkPolyData()
        vtkPolyData.SetPoints(vtkPoints)
        vtkPolyData.SetVerts(vtkCells)
        vtkPolyData.GetPointData().SetScalars(vtkColour)
        vtkPolyData.GetPointData().SetActiveScalars('vtkColour')
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(vtkPolyData)
        mapper.SetColorModeToDefault()
        mapper.SetScalarRange(0, 3)
        #mapper.SetScalarVisibility(2)
#        stepDistance=float(10.0/len(listOfPoints))
        stepDistance=float(30.0/len(listOfPoints))
        for k in range(0, len(listOfPoints)):
            #for each point check how many other points are same.
            previousPoints = 0
#ok            for ddd in range(0, k):
#ok             if (listOfPoints[k][0]==listOfPoints[ddd][0] and listOfPoints[k][1]==listOfPoints[ddd][1] and listOfPoints[k][2]==listOfPoints[ddd][2] ):
#ok````````````               previousPoints = previousPoints + 1
#            for ddd in range(0, k):
#             if (listOfPoints[k][0]==listOfPoints[ddd][0] and listOfPoints[k][1]==listOfPoints[ddd][1] and listOfPoints[k][2]==listOfPoints[ddd][2] ):
#                previousPoints = previousPoints + 1

            #print (previousPoints)
            DistanceFactor=float(self.radius)+float(previousPoints)*stepDistance
            tmpPointNewCoordinates=[DistanceFactor*listOfPoints[k][0]+float(self.centerX),DistanceFactor*listOfPoints[k][1]+float(self.centerY),DistanceFactor*listOfPoints[k][2]+float(self.centerZ) ]

            #print tmpPointNewCoordinates
            #pointId = vtkPoints.InsertNextPoint(listOfPoints[k])
            pointId = vtkPoints.InsertNextPoint(tmpPointNewCoordinates)
            #vtkColour.InsertNextValue(1)
            vtkCells.InsertNextCell(1)
            vtkCells.InsertCellPoint(pointId)
            if not listSubsetGoodPoints==[]:
             if float(listSubsetGoodPoints[k]) > 0:
              vtkColour.InsertNextValue(0)
             else:
              vtkColour.InsertNextValue(2)
            else:
             vtkColour.InsertNextValue(0)
        vtkCells.Modified()
        vtkPoints.Modified()
        vtkColour.Modified()
        vtkActor = vtk.vtkActor()
        vtkActor.GetProperty().SetPointSize(3)
        vtkActor.SetMapper(mapper)
        return vtkActor

    def Go(self, listOfPoints, listOfPoints2, listSubsetGoodPoints, great_circle_V, great_circle_VNext):

        #for the diameter plot
        Phi=50
        Theta=30



        #Create a renderer, render window, and interactor
        #renderer =vtkRenderer();
        #renderer.SetActiveCamera(camera);
        
        # Renderer
        self.renderer = vtk.vtkRenderer()


        if len(str(self.model))>1:
          self.renderer.AddActor(self.modelVolumeActor())
        else:
          self.renderer.AddActor(self.axisActor())

        self.renderer.AddActor(self.sphereActor())
        if len (listOfPoints2)==len(listOfPoints):
            print ("we have the list of errors")
            self.renderer.AddActor(self.actorPoints(listOfPoints2, listSubsetGoodPoints))
            self.renderer.AddActor( self.actorSegmentsError(listOfPoints, listOfPoints2) )
        else:
            print ("we do not have the list of errors")
        
        self.renderer.AddActor(self.actorPoints(listOfPoints, listSubsetGoodPoints))
        #ok self.renderer.AddActor(self.actorPoints(listOfPoints, listSubsetGoodPoints))
        #ok self.renderer.AddActor(self.actorSegments(listOfPoints, great_circle_V, great_circle_VNext))
        #self.renderer.AddActor(self.actorDiameterCircle(Phi, Theta))
        
        self.renderer.SetBackground(0.42,0.42,0.42)
        camera =vtk.vtkCamera ();
        #camera.SetPosition(-self.center, -self.center, -self.center);
        self.renderer.SetActiveCamera(camera);
        self.renderer.ResetCamera()
        camera.SetFocalPoint(self.centerX, self.centerY, self.centerZ);
        
        

        # Render Window
        renderWindow = vtk.vtkRenderWindow()
        renderWindow.AddRenderer(self.renderer)

        # Interactor
        renderWindowInteractor = vtk.vtkRenderWindowInteractor()
        renderWindowInteractor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
        renderWindowInteractor.SetRenderWindow(renderWindow)

        # Begin Interaction
        renderWindow.Render()
        renderWindowInteractor.Start()
        
