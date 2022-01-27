import matplotlib.pyplot as plt
import sys,os
sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))
import PyEFVLib
import numpy as np

def navierStokes(problemData):
	propertyData 	 = problemData.propertyData
	timeStep 		 = problemData.timeStep
	grid 			 = problemData.grid
	numberOfVertices = grid.numberOfVertices
	dimension 		 = grid.dimension

	csvSaver = PyEFVLib.CsvSaver(grid, problemData.outputFilePath, problemData.libraryPath)
	meshioSaver = PyEFVLib.MeshioSaver(grid, problemData.outputFilePath, problemData.libraryPath, extension="xdmf")

	vField    = np.repeat(0.0, dimension*numberOfVertices)
	prevVField    = np.repeat(0.0, dimension*numberOfVertices)
	oldVField = np.concatenate((problemData.initialValues["v_x"], problemData.initialValues["v_y"], problemData.initialValues["v_z"])) if dimension==3 else np.concatenate((problemData.initialValues["v_x"], problemData.initialValues["v_y"]))

	pField    = np.repeat(0.0, numberOfVertices)
	prevPField    = np.repeat(0.0, numberOfVertices)
	oldPField = problemData.initialValues["p"].copy()

	def assembleMatrix():
		matrix 		= np.zeros(((1+dimension)*numberOfVertices, (1+dimension)*numberOfVertices))
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
							matrix[backwardsHandle+(coord)*numberOfVertices][vertex.handle+(coord)*numberOfVertices] += shapeFunctions[local] * area[coord]
							matrix[forwardHandle+(coord)*numberOfVertices][vertex.handle+(coord)*numberOfVertices] += -shapeFunctions[local] * area[coord]


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
							matrix[backwardsHandle+(dimension)*numberOfVertices][vertex.handle+(dimension)*numberOfVertices] += shapeFunctions[local] * area[coord] 
							matrix[forwardHandle+(dimension)*numberOfVertices][vertex.handle+(dimension)*numberOfVertices] += -shapeFunctions[local] * area[coord]

				# ∇·(ρVV) - Fluxo de massa no VC
				prevVElementField = np.array([[prevVField[vertex.handle + coord * numberOfVertices] for vertex in element.vertices] for coord in range(dimension)])
				for face in element.innerFaces:
					area = face.area.getCoordinates()[:dimension]
					shapeFunctions = face.getShapeFunctions()

					matrixCoefficients = rho * np.dot( np.dot(prevVElementField, shapeFunctions), area ) * shapeFunctions

					backwardsHandle, forwardHandle = face.getNeighborVerticesHandles()
					for local, vertex in enumerate(element.vertices):
						for coord in range(dimension):
							matrix[backwardsHandle+(coord)*numberOfVertices][vertex.handle+(coord)*numberOfVertices] += matrixCoefficients[local]
							matrix[forwardHandle+(coord)*numberOfVertices][vertex.handle+(coord)*numberOfVertices] += -matrixCoefficients[local]

				# ∇·(μ∇V) - Termo viscoso
				for face in element.innerFaces:
					area = face.area.getCoordinates()[:dimension]
					matrixCoefficients = (-1) * mu * np.matmul( area.T, face.globalDerivatives )
					backwardsHandle, forwardHandle = face.getNeighborVerticesHandles()
					for local, vertex in enumerate(element.vertices):
						for coord in range(dimension):
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
		plt.spy(matrix)
		plt.show()
		inverseMatrix = np.linalg.inv(matrix)
		return inverseMatrix

	def assembleIndependent():
		independent = np.zeros((1+dimension)*numberOfVertices)

		for region in grid.regions:
			mu         = propertyData.get(region.handle, "mu")
			rho       = propertyData.get(region.handle, "rho")
			g = np.array([0.0, propertyData.get(region.handle, "g"), 0.0])[:dimension]

			for element in region.elements:
				# ρg
				for vertex in element.vertices:
					for coord in range(dimension):
						independent[vertex.handle+coord*numberOfVertices] += vertex.getSubElementVolume(element) * rho * g[coord]

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
	iteration = 0
	currentTime = 0.0
	converged = False
	global residuals

	while not converged:
		iteration = 0
		independent = assembleIndependent()

		while iteration < 2:
			inverseMatrix = assembleMatrix()

			results = np.matmul(inverseMatrix, independent)
			vField = results[(0)*numberOfVertices:(0+dimension)*numberOfVertices]
			pField = results[(dimension)*numberOfVertices:(dimension+1)*numberOfVertices]

			difference = max( max(abs(pField - oldPField)), max(abs(vField - oldVField)) )
			residuals.append(difference)

			prevPField = pField.copy()
			prevVField = vField.copy()
			
			iteration += 1

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

		print("{:>9}	{:>14.2e}	{:>14.2e}	{:>14.2e}".format(iteration, currentTime, timeStep, difference))
		converged = ( difference <= tolerance ) or ( currentTime >= problemData.finalTime ) or ( iteration >= problemData.maxNumberOfIterations )

		if iteration >= problemData.maxNumberOfIterations:
			break

	csvSaver.finalize()
	meshioSaver.finalize()

def main():
	problemData = PyEFVLib.ProblemData(
		meshFilePath = "placa_plana.msh",
		outputFilePath = "{RESULTS}/navierStokes",
		numericalSettings = PyEFVLib.NumericalSettings( timeStep = 1000, tolerance = 1, maxNumberOfIterations = 50 ),
		propertyData = PyEFVLib.PropertyData({
			'Body':
			{
				'mu': 1e-3,
				'rho': 1000.0,
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
	residuals = []
	import matplotlib.pyplot as plt
	navierStokes( problemData )
	plt.plot(residuals)
	plt.title("Residuals x Iteration")
	plt.show()


if __name__ == '__main__':
	main()
