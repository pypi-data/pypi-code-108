from dataclasses import dataclass, field
from openseespy import opensees
from streng.phd.building_models.model2d_older.model_input import Model2d

@dataclass
class OpenSeesModel2d(Model2d):
    # etabs_filename: str = ''

    # procedure to read
    def ElasticBeamColumn(self, eleTag, iNode, jNode, sectType, E, transfTag, M, massType):
        found = 0
        prop = WSection[sectType]

        A = prop[0]
        I = prop[1]
        opensees.element('elasticBeamColumn', eleTag, iNode, jNode, A, E, I, transfTag, '-mass', M, massType)

    def start(self):

        opensees.wipe()
        opensees.model('Basic', '-ndm', 2)

        #    units kN, m

        E = 29000000.0
        massX = 0.49
        M = 0.
        coordTransf = "Linear"  # Linear, PDelta, Corotational
        massType = "-lMass"  # -lMass, -cMass

        self.write_nodes()


    def write_nodes(self):
        ds = self.input_data['joint_coordinates']
        for i, row in ds.iterrows():
            _nodeID = int(row['NodeID'])
            _X = row['X']
            _Y = row['Z']
            opensees.node(_nodeID, _X, _Y)


mymodel = OpenSeesModel2d(input_excel_filename=r'D:\phd_closure\ch3\designs\eak_frames\9st_016\9eak016.xlsm')
mymodel.start()

