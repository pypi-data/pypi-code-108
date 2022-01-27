import sys,os
sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))
import PyEFVLib
import numpy as np
from scipy.sparse.linalg import spsolve, gmres,dsolve
from scipy.sparse import csc_matrix
import matplotlib.pyplot as plt
import pandas as pd 


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
                            matrix[backwardsHandle+(dimension)*numberOfVertices][vertex.handle+(coord)*numberOfVertices] += shapeFunctions[local] * area[coord]
                            matrix[forwardHandle+(dimension)*numberOfVertices][vertex.handle+(coord)*numberOfVertices] += -shapeFunctions[local] * area[coord]


                # ∂/∂t(ρV) - Termo transiente / Acumulação
                for vertex in element.vertices:
                    for coord in range(dimension):
                        matrix[vertex.handle+(coord)*numberOfVertices][vertex.handle+(coord)*numberOfVertices] += vertex.getSubElementVolume(element) * rho * (1/timeStep) 

                # -∇·P    - Termo da pressão
                for face in element.innerFaces:
                    area = face.area.getCoordinates()[:dimension]
                    shapeFunctions = face.getShapeFunctions()

                    backwardsHandle, forwardHandle = face.getNeighborVerticesHandles()
                    for coord in range(dimension):
                        for local, vertex in enumerate(element.vertices):
                            matrix[backwardsHandle+(coord)*numberOfVertices][vertex.handle+(dimension)*numberOfVertices] +=  shapeFunctions[local] * area[coord]
                            matrix[forwardHandle+(coord)*numberOfVertices][vertex.handle+(dimension)*numberOfVertices] += -shapeFunctions[local] * area[coord]

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
                    print(shapeFunctions)
                    m_ponto = rho * np.dot( np.dot(prevVElementField, shapeFunctions), area )
                    matrixCoefficients = m_ponto * shapeFunctions
                    # print(matrixCoefficients)

                    backwardsHandle, forwardHandle = face.getNeighborVerticesHandles()
                    for local, vertex in enumerate(element.vertices):
                        for coord in range(dimension):
                            # matrixCoefficients[local]
                            # print(vertex.handle,'vertice', coord,'coord', matrixCoefficients[local], backwardsHandle,forwardHandle )
                            matrix[backwardsHandle+(coord)*numberOfVertices][vertex.handle+(coord)*numberOfVertices] += matrixCoefficients[local]
                            matrix[forwardHandle+(coord)*numberOfVertices][vertex.handle+(coord)*numberOfVertices] += -matrixCoefficients[local]

                # ∇·(μ∇V) - Termo viscoso
                for face in element.innerFaces:
                    area = face.area.getCoordinates()[:dimension]
                    matrixCoefficients = (-1) * mu * np.matmul( area.T, face.globalDerivatives )
                    backwardsHandle, forwardHandle = face.getNeighborVerticesHandles()
                    for local, vertex in enumerate(element.vertices):
                        for coord in range(dimension):
                            # matrixCoefficients[local]
                            # print(vertex.handle,'vertice', coord,'coord', matrixCoefficients[local], backwardsHandle,forwardHandle )
                            matrix[backwardsHandle+(coord)*numberOfVertices][vertex.handle+(coord)*numberOfVertices] += matrixCoefficients[local]
                            matrix[forwardHandle+(coord)*numberOfVertices][vertex.handle+(coord)*numberOfVertices] += -matrixCoefficients[local]

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
                        independent[vertex.handle+(coord)*numberOfVertices] += vertex.getSubElementVolume(element) * rho * (1/timeStep) * oldVField[vertex.handle+(coord)*numberOfVertices]

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
            matrix[15+(dimension)*numberOfVertices] = np.zeros((1+dimension)*numberOfVertices)
            matrix[15+(dimension)*numberOfVertices][15+(dimension)*numberOfVertices] = 1.0
            matrix[12] = np.zeros((1+dimension)*numberOfVertices)
            matrix[12][12] = 1.0
            matrix[15] = np.zeros((1+dimension)*numberOfVertices)
            matrix[15][15] = 1.0
            independent[12] = 1
            independent[15] = 1
            # independent[15+(dimension)*numberOfVertices] = 1
            plt.spy(matrix)           
            plt.show()
            # A_sparse = csc_matrix(matrix)
            # B_sparse = csc_matrix(independent)
            # results = spsolve(A_sparse, independent)
            # results = np.linalg.inv(matrix).dot(independent)
            # print(np.linalg.det(matrix))
            matriz_a.append(matrix)
            results = np.linalg.solve(matrix,independent)
            # print((np.array(matriz_a)).shape)
            # pd.DataFrame(np.array(matriz_a)[0]).to_csv("C:/Users/Public/PyEFVLIB/PyEFVLib/results/navier_stokes/matriz_3_3.xlsx")
            # results, exitCode = gmres(matrix,independent)
            # teste_1 = matrix.dot(results)
            # print(exitCode)
            # teste.append(teste_1)
            vField = results[(0)*numberOfVertices:(0+dimension)*numberOfVertices]
            pField = results[(dimension)*numberOfVertices:(dimension+1)*numberOfVertices]

            difference = max( max(abs(pField - oldPField)), max(abs(vField - oldVField)) )
            # difference = max(vField-oldVField)
            residuals.append(difference)
            velocidades.append(vField)
            pressoes.append(pField)
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

def main():
    problemData = PyEFVLib.ProblemData(
        meshFilePath = "C:\\Users/Public/PyEFVLIB/PyEFVLib/PyEFVLib/meshes/msh/2D/3x3.msh",
        outputFilePath = "{RESULTS}/navier_stokes",
        numericalSettings = PyEFVLib.NumericalSettings( timeStep = 1, tolerance = 1e-6, maxNumberOfIterations = 1 ),
        propertyData = PyEFVLib.PropertyData({
            'Body':
            {
                'mu': 1e-2,
                'rho': 1.0,
                'g': 0.0,
            },
        }),
        boundaryConditions = PyEFVLib.BoundaryConditions({
            'v_x': {
                'InitialValue': 0.0,
                'West': { 'condition' : PyEFVLib.Dirichlet, 'type' : PyEFVLib.Constant, 'value' : 0.0 },
                'East': { 'condition' : PyEFVLib.Dirichlet, 'type' : PyEFVLib.Constant, 'value' : 0.0 },
                'South': { 'condition' : PyEFVLib.Dirichlet, 'type' : PyEFVLib.Constant, 'value' : 0.0 },
                'North': { 'condition' : PyEFVLib.Dirichlet, 'type' : PyEFVLib.Constant, 'value' : 1.0 },
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
                'West': { 'condition' : PyEFVLib.Neumann, 'type' : PyEFVLib.Constant, 'value' : 0.0 },
                'East': { 'condition' : PyEFVLib.Neumann, 'type' : PyEFVLib.Constant, 'value' : 0.0 },
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
    teste=[]
    matriz_a=[]
    pressoes=[]
    residuals = []
    velocidades = []
    termo_b=[]
    import matplotlib.pyplot as plt
    navierStokes( problemData )
    # plt.plot(residuals)
    # plt.title("Residuals x Iteration")
    # plt.yticks('log')
    # plt.show()

    


if __name__ == '__main__':
    main()
