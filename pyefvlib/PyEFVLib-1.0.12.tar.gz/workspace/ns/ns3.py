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
	oldVField = np.concatenate((problemData.initialValues["v_x"], problemData.initialValues["v_y"], problemData.initialValues["v_z"])) if dimension==3 else np.concatenate((problemData.initialValues["v_x"], problemData.initialValues["v_y"]))
	prevVField    = oldVField.copy() # Pois a matriz calcula os fluxos a partir de prevVField

	pField    = np.repeat(0.0, numberOfVertices)
	oldPField = problemData.initialValues["p"].copy()
	prevPField    = oldPField.copy()

	"""
		[ v_x ]
		[ v_y ]
		[ v_z ]
		[  p  ]
	"""

	def assembleMatrix():
		matrix 		= np.zeros(((1+dimension)*numberOfVertices, (1+dimension)*numberOfVertices))
		for region in grid.regions:
			mu         = propertyData.get(region.handle, "mu")
			rho       = propertyData.get(region.handle, "rho")
			g = np.array([0.0, propertyData.get(region.handle, "g"), 0.0])[:dimension]

			for element in region.elements:
				# ∇·V      - Conservação da Massa
				for innerFace in element.innerFaces:
					area = innerFace.area.getCoordinates()[:dimension]
					shapeFunctions = innerFace.getShapeFunctions()

					backwardsHandle, forwardHandle = innerFace.getNeighborVerticesHandles()
					for coord in range(dimension):
						for local, vertex in enumerate(element.vertices):
							# estava coord nos dois
							matrix[backwardsHandle+(dimension)*numberOfVertices][vertex.handle+(coord)*numberOfVertices] += shapeFunctions[local] * area[coord]
							matrix[forwardHandle+(dimension)*numberOfVertices][vertex.handle+(coord)*numberOfVertices] -= shapeFunctions[local] * area[coord]


				# ∂/∂t(ρV) - Termo transiente / Acumulação
				for vertex in element.vertices:
					for coord in range(dimension):
						matrix[vertex.handle+(coord)*numberOfVertices][vertex.handle+(coord)*numberOfVertices] += vertex.getSubElementVolume(element) * rho * (1/timeStep) 

				# ∇·P    - Termo da pressão
				for face in element.innerFaces:
					area = face.area.getCoordinates()[:dimension]
					shapeFunctions = face.getShapeFunctions()

					backwardsHandle, forwardHandle = face.getNeighborVerticesHandles()
					for coord in range(dimension):
						for local, vertex in enumerate(element.vertices):
							# estava dimension nos dois
							matrix[backwardsHandle+(coord)*numberOfVertices][vertex.handle+(dimension)*numberOfVertices] += shapeFunctions[local] * area[coord]
							matrix[forwardHandle+(coord)*numberOfVertices][vertex.handle+(dimension)*numberOfVertices] -= shapeFunctions[local] * area[coord]

				# ∇·(ρVV) - Fluxo de massa no VC
				# Começa tudo zero na primeira iteração pois V=0
				prevVElementField = np.array([[prevVField[vertex.handle + coord * numberOfVertices] for vertex in element.vertices] for coord in range(dimension)])
				for face in element.innerFaces:
					area = face.area.getCoordinates()[:dimension]
					shapeFunctions = face.getShapeFunctions()

					matrixCoefficients = rho * np.dot( np.dot(prevVElementField, shapeFunctions), area ) * shapeFunctions

					backwardsHandle, forwardHandle = face.getNeighborVerticesHandles()
					for local, vertex in enumerate(element.vertices):
						for coord in range(dimension):
							matrix[backwardsHandle+(coord)*numberOfVertices][vertex.handle+(coord)*numberOfVertices] += matrixCoefficients[local]
							matrix[forwardHandle+(coord)*numberOfVertices][vertex.handle+(coord)*numberOfVertices] -= matrixCoefficients[local]

				# ∇·(μ∇V) - Termo viscoso
				for face in element.innerFaces:
					area = face.area.getCoordinates()[:dimension]
					matrixCoefficients = (-1) * mu * np.matmul( area.T, face.globalDerivatives )
					backwardsHandle, forwardHandle = face.getNeighborVerticesHandles()
					for local, vertex in enumerate(element.vertices):
						for coord in range(dimension):
							matrix[backwardsHandle+coord*(numberOfVertices)][vertex.handle+coord*(numberOfVertices)] += matrixCoefficients[local]
							matrix[forwardHandle+coord*(numberOfVertices)][vertex.handle+coord*(numberOfVertices)] -= matrixCoefficients[local]

		# plt.spy(matrix)
		# plt.show()
		# exit()

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
			g = np.array([0.0, propertyData.get(region.handle, "g"), 0.0])[:dimension]

			for element in region.elements:
				# # ρg
				# for vertex in element.vertices:
				# 	for coord in range(dimension):
				# 		independent[vertex.handle+coord*numberOfVertices] += vertex.getSubElementVolume(element) * rho * g[coord]

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

	iteration = 0
	while not converged:

		independent = assembleIndependent()
		for i in range(10):
			matrix = assembleMatrix()

			results = np.linalg.solve(matrix, independent)
			vField = results[:dimension*numberOfVertices]
			pField = results[dimension*numberOfVertices:(dimension+1)*numberOfVertices]

			difference = max( max(abs(pField - oldPField)), max(abs(vField - oldVField)) )
			residuals.append(difference)

			prevPField = pField.copy()
			prevVField = vField.copy()
			
			iteration += 1

		pDifference = max(abs(pField - oldPField))
		uDifference = max(abs(vField[:numberOfVertices] - oldVField[:numberOfVertices]))
		vDifference = max(abs(vField[numberOfVertices:2*numberOfVertices] - oldVField[numberOfVertices:2*numberOfVertices]))

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

		print("{:>14.2e}	{:>14.2e}	{:>14.2e}	{:>14.2e}	{:>14.2e}	{:>14.2e}".format(pDifference, uDifference, vDifference, np.mean(vField[:numberOfVertices]), np.mean(pField), np.mean(vField[numberOfVertices:2*numberOfVertices])))
		converged = ( difference <= tolerance ) or ( currentTime >= problemData.finalTime ) or ( iteration >= problemData.maxNumberOfIterations )

		if iteration >= problemData.maxNumberOfIterations:
			break

	csvSaver.finalize()
	meshioSaver.finalize()

	U,V,P = np.split(results, 3)
	prevVField = np.array([*U,*V])
	prevPField = P.copy()

	fig, axs = plt.subplots(2,2)
	axs[0,0].scatter(*zip(*[(U[vtx.handle], vtx.y) for vtx in grid.vertices if vtx.x==1.5]),color='k')
	axs[0,0].set(title="u [m/s] at x=1.5", ylabel="y [m]")
	axs[0,1].scatter(*zip(*[(U[vtx.handle], vtx.y) for vtx in grid.vertices if vtx.x==0.0]),color='k')
	axs[0,1].set(title="u [m/s] at x=0", ylabel="y [m]")
	axs[1,1].scatter(*zip(*[(U[vtx.handle], vtx.y) for vtx in grid.vertices if vtx.x==3.0]),color='k')
	axs[1,1].set(title="u [m/s] at x=3", ylabel="y [m]")
	plt.show()

	fig, axs = plt.subplots(2,2)
	axs[0,0].scatter(*zip(*[(P[vtx.handle]/1e3, vtx.y) for vtx in grid.vertices if vtx.x==1.5]),color='k')
	axs[0,0].set(title="p [kPa] at x=1.5", ylabel="y [m]")
	axs[0,1].scatter(*zip(*[(P[vtx.handle]/1e3, vtx.y) for vtx in grid.vertices if vtx.x==0.0]),color='k')
	axs[0,1].set(title="p [kPa] at x=0", ylabel="y [m]")
	axs[1,1].scatter(*zip(*[(P[vtx.handle]/1e3, vtx.y) for vtx in grid.vertices if vtx.x==3.0]),color='k')
	axs[1,1].set(title="p [kPa] at x=3", ylabel="y [m]")
	axs[1,0].scatter(*zip(*[(vtx.x, P[vtx.handle]/1e3) for vtx in grid.vertices if vtx.y==0.5]),color='k')
	axs[1,0].set(xlabel="x [m]", title="p [kPa] at y=0.5")
	plt.show()


	# ∇p = (∯p dA)/ΔΩ
	elementPressures = np.array([[P[v.handle] for v in e.vertices] for e in grid.elements])
	pressureGradients = np.array([np.sum([np.dot(innerFace.getShapeFunctions(),elementPressures[innerFace.element.handle])*innerFace.area.getCoordinates() for innerFace in vtx.getInnerFaces()], axis=0)/vtx.volume for vtx in grid.vertices])
	fig, axs = plt.subplots(2,2)
	axs[0,0].scatter(*zip(*[(pressureGradients[vtx.handle][0]/1e3, vtx.y) for vtx in grid.vertices if vtx.x==1.5]),color='k')
	axs[0,0].set(title=r"$\partial p / \partial x$ [kPa/m] at x=1.5", ylabel="y [m]")
	axs[0,1].scatter(*zip(*[(pressureGradients[vtx.handle][1]/1e3, vtx.y) for vtx in grid.vertices if vtx.x==1.5]),color='k')
	axs[0,1].set(title=r"$\partial p / \partial y$ [kPa/m] at x=1.5", ylabel="y [m]")
	axs[1,0].scatter(*zip(*[(vtx.x, pressureGradients[vtx.handle][0]/1e3) for vtx in grid.vertices if vtx.y==0.5]),color='k')
	axs[1,0].set(title=r"$\partial p / \partial x$ [kPa/m] at y=0.5", xlabel="x [m]")
	axs[1,1].scatter(*zip(*[(vtx.x, pressureGradients[vtx.handle][1]/1e3) for vtx in grid.vertices if vtx.y==0.5]),color='k')
	axs[1,1].set(title=r"$\partial p / \partial y$ [kPa/m] at y=0.5", xlabel="x [m]")
	# fig.tight_layout(pad=3.0)
	plt.subplots_adjust(left=0.09, bottom=0.08, right=0.936, top=0.94, wspace=0.2, hspace=0.436)
	plt.show()


def main():
	p2=1000
	p1=2000
	L=3
	H=1
	mu=1
	print("{:>14}	{:>14}	{:>14}	{:>14}	{:>14}	{:>14}".format("pDifference", "uDifference", "vDifference", "uMean", "pMean", "vMean"))
	problemData = PyEFVLib.ProblemData(
		meshFilePath = "placa_plana.msh",
		outputFilePath = "{RESULTS}/navierStokes",
		numericalSettings = PyEFVLib.NumericalSettings( timeStep = 1, tolerance = 1e-6, maxNumberOfIterations = 30 ),
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
                'InitialValue': 27.78,
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
	residuals = []
	import matplotlib.pyplot as plt
	navierStokes( problemData )
	plt.semilogy(residuals)
	plt.title("Residuals x Iteration")
	plt.show()


if __name__ == '__main__':
	main()
