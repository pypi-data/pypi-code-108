import sys,os
sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))
import PyEFVLib
import numpy as np
from scipy.sparse.linalg import spsolve, gmres,dsolve
from scipy.sparse import csc_matrix
import matplotlib.pyplot as plt

def navierStokes(problemData):
    propertyData      = problemData.propertyData
    timeStep          = problemData.timeStep
    grid              = problemData.grid
    numberOfVertices = grid.numberOfVertices
    dimension          = grid.dimension

    csvSaver = PyEFVLib.CsvSaver(grid, problemData.outputFilePath, problemData.libraryPath)
    meshioSaver = PyEFVLib.MeshioSaver(grid, problemData.outputFilePath, problemData.libraryPath, extension="xdmf")

    vField    = np.repeat(0.0, dimension*numberOfVertices)
    prevVField    = np.repeat(0.0, dimension*numberOfVertices)
    oldVField = np.concatenate((problemData.initialValues["v_x"], problemData.initialValues["v_y"], problemData.initialValues["v_z"])) if dimension==3 else np.concatenate((problemData.initialValues["v_x"], problemData.initialValues["v_y"]))

    pField    = np.repeat(0.0, numberOfVertices)
    prevPField    = np.repeat(0.0, numberOfVertices)
    oldPField = problemData.initialValues["p"].copy()
    

        


    def assembleMatrix():
        matrix         = np.zeros(((1+dimension)*numberOfVertices, (1+dimension)*numberOfVertices))
        for region in grid.regions:
            mu         = propertyData.get(region.handle, "mu")
            rho       = propertyData.get(region.handle, "rho")
            g = np.array([0.0, propertyData.get(region.handle, "g"), 0.0])[:dimension]

            for element in region.elements:
                # ∇·V      - Conservação da Massa
                for face in element.innerFaces:
                    area = face.area.getCoordinates()[:dimension]
                    shapeFunctions = face.getShapeFunctions()

                    backwardsHandle, forwardHandle = face.getNeighborVerticesHandles()
                    for coord in range(dimension):
                        for local, vertex in enumerate(element.vertices):
                            # if coord ==0 and vertex.handle == 5:
                            #     print(vertex.handle,'vertice', area[coord]*shapeFunctions[local],'valor',backwardsHandle,'back',forwardHandle,'for',coord)
                            matrix[backwardsHandle+(dimension)*numberOfVertices][vertex.handle] += shapeFunctions[local] * area[0]
                            matrix[forwardHandle+(dimension)*numberOfVertices][vertex.handle] -= shapeFunctions[local] * area[0]


                # ∂/∂t(ρV) - Termo transiente / Acumulação
                for vertex in element.vertices:
                    for coord in range(dimension):
                        # vertex.getSubElementVolume(element) * rho * (1/timeStep)
                        # print(vertex.handle,'vertice', coord, 'coord',vertex.getSubElementVolume(element) * rho * (1/timeStep) ,'volume')
                        matrix[vertex.handle][vertex.handle] += vertex.getSubElementVolume(element) * rho * (1/timeStep) 

                # -∇·P    - Termo da pressão
                for face in element.innerFaces:
                    area = face.area.getCoordinates()[:dimension]
                    shapeFunctions = face.getShapeFunctions()

                    backwardsHandle, forwardHandle = face.getNeighborVerticesHandles()
                    for coord in range(dimension):
                        for local, vertex in enumerate(element.vertices):
                            # if coord == 0 and vertex.handle == 10:
                            #     print(vertex.handle,'vertex',local,'local',backwardsHandle,'back',forwardHandle,'forward',shapeFunctions[local],area[coord],coord)
                            matrix[backwardsHandle][vertex.handle+(dimension)*numberOfVertices] +=  shapeFunctions[local] * area[0]
                            matrix[forwardHandle][vertex.handle+(dimension)*numberOfVertices] += -shapeFunctions[local] * area[0]

                # ∇·(ρVV) - Fluxo de massa no VC
                prevVElementField = np.array([[prevVField[vertex.handle + coord * numberOfVertices] for vertex in element.vertices] for coord in range(dimension)])
                # aux1=[]
                # for coord in range(dimension):
                #     aux2=[]      
                #     for vertex in element.vertices:
                #         aux2.append(prevVField[vertex.handle + coord * numberOfVertices])
                #     aux1.append(aux2)
                for face in element.innerFaces:
                    area = face.area.getCoordinates()[:dimension]
                    shapeFunctions = face.getShapeFunctions()
                    # print(shapeFunctions)
                    m_ponto = rho * np.dot( np.dot(prevVElementField, shapeFunctions), area )
                    matrixCoefficients = m_ponto * shapeFunctions
                    # print(matrixCoefficients)

                    backwardsHandle, forwardHandle = face.getNeighborVerticesHandles()
                    for local, vertex in enumerate(element.vertices):
                        for coord in range(dimension):
                            # matrixCoefficients[local]
                            # print(vertex.handle,'vertice', coord,'coord', matrixCoefficients[local], backwardsHandle,forwardHandle )
                            matrix[backwardsHandle][vertex.handle] += matrixCoefficients[local]
                            matrix[forwardHandle][vertex.handle] += -matrixCoefficients[local]

                # ∇·(μ∇V) - Termo viscoso
                for face in element.innerFaces:
                    area = face.area.getCoordinates()[:dimension]
                    matrixCoefficients = (-1) * mu * np.matmul( area.T, face.globalDerivatives )
                    backwardsHandle, forwardHandle = face.getNeighborVerticesHandles()
                    for local, vertex in enumerate(element.vertices):
                        for coord in range(dimension):
                            # matrixCoefficients[local]
                            # print(vertex.handle,'vertice', coord,'coord', matrixCoefficients[local], backwardsHandle,forwardHandle )
                            matrix[backwardsHandle+coord*(numberOfVertices)][vertex.handle+coord*(numberOfVertices)] += matrixCoefficients[local]
                            matrix[forwardHandle+coord*(numberOfVertices)][vertex.handle+coord*(numberOfVertices)] -= matrixCoefficients[local]

        # Dirichlet Boundary Conditions
        for bCondition in problemData.dirichletBoundaries["v_x"]:
            for vertex in bCondition.boundary.vertices:
                matrix[vertex.handle+(0)*numberOfVertices] = np.zeros((1+dimension)*numberOfVertices)
                matrix[vertex.handle+(0)*numberOfVertices][vertex.handle+(0)*numberOfVertices] = 1.0

        for bCondition in problemData.dirichletBoundaries["v_y"]:
            for vertex in bCondition.boundary.vertices:
                matrix[vertex.handle+(1)*numberOfVertices] = np.zeros((1+dimension)*numberOfVertices)
                matrix[vertex.handle+(1)*numberOfVertices][vertex.handle+(1)*numberOfVertices] = 1.0

        if dimension == 3:
            for bCondition in problemData.dirichletBoundaries["v_z"]:
                for vertex in bCondition.boundary.vertices:
                    matrix[vertex.handle+(2)*numberOfVertices] = np.zeros((1+dimension)*numberOfVertices)
                    matrix[vertex.handle+(2)*numberOfVertices][vertex.handle+(2)*numberOfVertices] = 1.0

        for bCondition in problemData.dirichletBoundaries["p"]:
            for vertex in bCondition.boundary.vertices:
                matrix[vertex.handle+(dimension)*numberOfVertices] = np.zeros((1+dimension)*numberOfVertices)
                matrix[vertex.handle+(dimension)*numberOfVertices][vertex.handle+(dimension)*numberOfVertices] = 1.0

        # Inverse Matrix
        # inverseMatrix = np.linalg.inv(matrix)
        return matrix

    def assembleIndependent():
        independent = np.zeros((1+dimension)*numberOfVertices)

        for region in grid.regions:
            mu         = propertyData.get(region.handle, "mu")
            rho       = propertyData.get(region.handle, "rho")
            # g = np.array([0.0, propertyData.get(region.handle, "g"), 0.0])[:dimension]

            for element in region.elements:
                # ρg
                # for vertex in element.vertices:
                #     for coord in range(dimension):
                #         independent[vertex.handle+coord*numberOfVertices] += vertex.getSubElementVolume(element) * rho * g[coord]

                # ∂/∂t(ρV)
                for vertex in element.vertices:
                    for coord in range(dimension):
                        independent[vertex.handle] += vertex.getSubElementVolume(element) * rho * (1/timeStep) * oldVField[vertex.handle]

        # Neumann Boundary Condition
        for bCondition in problemData.neumannBoundaries["v_x"]:
            for facet in bCondition.boundary.facets:
                for outerFace in facet.outerFaces:
                    independent[outerFace.vertex.handle+(0)*numberOfVertices] += bCondition.getValue(outerFace.handle) * np.linalg.norm(outerFace.area.getCoordinates())

        for bCondition in problemData.neumannBoundaries["v_y"]:
            for facet in bCondition.boundary.facets:
                for outerFace in facet.outerFaces:
                    independent[outerFace.vertex.handle+(1)*numberOfVertices] += bCondition.getValue(outerFace.handle) * np.linalg.norm(outerFace.area.getCoordinates())

        if dimension == 3:
            for bCondition in problemData.neumannBoundaries["v_z"]:
                for facet in bCondition.boundary.facets:
                    for outerFace in facet.outerFaces:
                        independent[outerFace.vertex.handle+(2)*numberOfVertices] += bCondition.getValue(outerFace.handle) * np.linalg.norm(outerFace.area.getCoordinates())

        for bCondition in problemData.neumannBoundaries["p"]:
            for facet in bCondition.boundary.facets:
                for outerFace in facet.outerFaces:
                    independent[outerFace.vertex.handle+(dimension)*numberOfVertices] += bCondition.getValue(outerFace.handle) * np.linalg.norm(outerFace.area.getCoordinates())

        # Dirichlet Boundary Condition
        for bCondition in problemData.dirichletBoundaries["v_x"]:
            for vertex in bCondition.boundary.vertices:
                independent[vertex.handle+(0)*numberOfVertices] = bCondition.getValue(vertex.handle)

        for bCondition in problemData.dirichletBoundaries["v_y"]:
            for vertex in bCondition.boundary.vertices:
                independent[vertex.handle+(1)*numberOfVertices] = bCondition.getValue(vertex.handle)

        if dimension == 3:
            for bCondition in problemData.dirichletBoundaries["v_z"]:
                for vertex in bCondition.boundary.vertices:
                    independent[vertex.handle+(2)*numberOfVertices] = bCondition.getValue(vertex.handle)

        for bCondition in problemData.dirichletBoundaries["p"]:
            for vertex in bCondition.boundary.vertices:
                independent[vertex.handle+(dimension)*numberOfVertices] = bCondition.getValue(vertex.handle)

        return independent

    tolerance = problemData.tolerance
    difference = 2*tolerance
    iteration_time = 0
    currentTime = 0.0
    converged = False

    while not converged:
        iteration_nonlinearity = 0
        independent = assembleIndependent()

        while iteration_nonlinearity < 1:
            matrix = assembleMatrix()
            for i in range (numberOfVertices,2*numberOfVertices):
                matrix[i] = np.zeros((1+dimension)*numberOfVertices)
                matrix[i][i]=1
                independent[i]=0
            plt.spy(matrix)           
            plt.show()
            matriz_a.append(matrix)
            termo_b.append(independent)
            A_sparse = csc_matrix(matrix)
            # B_sparse = csc_matrix(independent)
            results = spsolve(matrix, independent)
            # results = np.linalg.inv(matrix).dot(independent)
            print(np.linalg.det(matrix))
            # matriz_a.append(matrix)
            # results = np.linalg.solve(matrix,independent)
            # results, exitCode = gmres(matrix,independent)
            # teste_1 = matrix.dot(results)
            # print(exitCode)
            # teste.append(teste_1)
            vField = results[(0)*numberOfVertices:(0+dimension)*numberOfVertices]
            uField = results[(0)*numberOfVertices:(1)*numberOfVertices]
            pField = results[(dimension)*numberOfVertices:(dimension+1)*numberOfVertices]


            difference = max( max(abs(pField - oldPField)), max(abs(vField - oldVField)) )
            # difference = max(vField-oldVField)
            residuals.append(difference)
            velocidades.append(vField)

            matriz_a.append(matrix)
            termo_b.append(independent)

            prevPField = pField.copy()
            prevVField = vField.copy()
            
            iteration_nonlinearity += 1
            iteration_time += 1
        # plt.spy(matrix)
        # plt.show()
     

        oldPField = pField.copy()
        oldVField = vField.copy()



        currentTime += timeStep

        csvSaver.save("v_x", vField[0*numberOfVertices:1*numberOfVertices], currentTime)
        csvSaver.save("v_y", vField[1*numberOfVertices:2*numberOfVertices], currentTime)
        if dimension == 3:
            csvSaver.save("v_z", vField[2*numberOfVertices:3*numberOfVertices], currentTime)
        csvSaver.save("p", pField, currentTime)

        meshioSaver.save("v_x", vField[0*numberOfVertices:1*numberOfVertices], currentTime)
        meshioSaver.save("v_y", vField[1*numberOfVertices:2*numberOfVertices], currentTime)
        if dimension == 3:
            meshioSaver.save("v_z", vField[2*numberOfVertices:3*numberOfVertices], currentTime)
        meshioSaver.save("p", pField, currentTime)

        print("{:>9}    {:>14.2e}    {:>14.2e}    {:>14.2e}".format(iteration_time, currentTime, timeStep, difference))
        converged = ( difference <= tolerance ) or ( currentTime >= problemData.finalTime ) or ( iteration_time >= problemData.maxNumberOfIterations )

        if iteration_time >= problemData.maxNumberOfIterations:
            break

    csvSaver.finalize()
    meshioSaver.finalize()
    velocidades_u.append(uField)
    for i in range (351,378):
        perfil_ux.append(uField[i])
    for i in range (13,716,27):
        perfil_uy.append(vField[i])
    for i in range (0,703,27):
        parabolic.append(vField[i])
    for i in range (351,378):
        perfil_p.append(pField[i])
    # for i in range (16,32):
    #     perfil_u.append(vField[i])
    pressoes.append(pField)
    plt.spy(matrix)           
    plt.show()


def main():
    p2=1000
    p1=2000
    L=3
    H=1
    mu=1
    
    
    problemData = PyEFVLib.ProblemData(
        meshFilePath = "C:\\Users/Public/PyEFVLIB/PyEFVLib/PyEFVLib/meshes/msh/2D/placa_plana.msh",
        outputFilePath = "{RESULTS}/navier_stokes",
        numericalSettings = PyEFVLib.NumericalSettings( timeStep = 1, tolerance = 1e-6, maxNumberOfIterations = 20 ),
        propertyData = PyEFVLib.PropertyData({
            'Body':
            {
                'mu': 1.0,
                'rho': 1.0,
                'g': 0.0,
            },
        }),
        boundaryConditions = PyEFVLib.BoundaryConditions({
            'v_x': {
                'InitialValue': 0.0,
                'West': { 'condition' : PyEFVLib.Dirichlet, 'type' : PyEFVLib.Variable, 'value' : f"{(p2-p1)/L}*y*(y-{H})/{2*mu}" },
                'East': { 'condition' : PyEFVLib.Dirichlet, 'type' : PyEFVLib.Variable, 'value' : f"{(p2-p1)/L}*y*(y-{H})/{2*mu}" },
                'South': { 'condition' : PyEFVLib.Dirichlet, 'type' : PyEFVLib.Constant, 'value' : 0.0 },
                'North': { 'condition' : PyEFVLib.Dirichlet, 'type' : PyEFVLib.Constant, 'value' : 0.0 },
            },
            'v_y': {
                'InitialValue': 0.0,
                'West': { 'condition' : PyEFVLib.Dirichlet, 'type' : PyEFVLib.Constant, 'value' : 0.0 },
                'East': { 'condition' : PyEFVLib.Dirichlet, 'type' : PyEFVLib.Constant, 'value' : 0.0 },
                'South': { 'condition' : PyEFVLib.Dirichlet, 'type' : PyEFVLib.Constant, 'value' : 0.0 },
                'North': { 'condition' : PyEFVLib.Dirichlet, 'type' : PyEFVLib.Constant, 'value' : 0.0 },
            },
            'p': {
                'InitialValue': 0.0,
                'West': { 'condition' : PyEFVLib.Dirichlet, 'type' : PyEFVLib.Constant, 'value' : p1 },
                'East': { 'condition' : PyEFVLib.Dirichlet, 'type' : PyEFVLib.Constant, 'value' : p2 },
                'South': { 'condition' : PyEFVLib.Neumann, 'type' : PyEFVLib.Constant, 'value' : 0.0 },
                'North': { 'condition' : PyEFVLib.Neumann, 'type' : PyEFVLib.Constant, 'value' : 0.0 },
            },
        }),
    )
    global residuals
    global velocidades
    global pressoes
    global matriz_a
    global termo_b
    global teste
    global resultados
    global perfil_u
    global perfil_uy
    global velocidades_u
    global perfil_ux
    global parabolic
    global perfil_p
    perfil_p=[]
    parabolic=[]
    perfil_ux=[]
    velocidades_u=[]
    perfil_uy=[]
    coordenada_x=np.linspace(0,3,27)
    coordenada_y=np.linspace(0,1,27)
    perfil_u=[]
    resultados = []
    teste=[]
    matriz_a=[]
    pressoes=[]
    residuals = []
    velocidades = []
    termo_b=[]
    import matplotlib.pyplot as plt
    navierStokes( problemData )

    plt.plot(perfil_uy,coordenada_y)
    plt.show()
    plt.plot(coordenada_x,perfil_ux)
    plt.show()
    plt.plot(coordenada_x,perfil_p)
    plt.show()
    
    
    

    


if __name__ == '__main__':
    main()
