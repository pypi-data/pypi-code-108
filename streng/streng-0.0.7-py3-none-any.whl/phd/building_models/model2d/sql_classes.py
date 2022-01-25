from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, String, Date, MetaData, Float, ForeignKey
from sqlalchemy.orm import relationship

Base = declarative_base()


class BuildingIdentity(Base):
    __tablename__ = 'Building_Identities'
    id = Column(String, primary_key=True)
    NodesBuilding = Column(String)
    SectionsBuilding = Column(String)

    def __init__(self, id, NodesBuilding, SectionsBuilding):
        self.id = id
        self.NodesBuilding = NodesBuilding
        self.SectionsBuilding = SectionsBuilding


class NodesCase(Base):
    __tablename__ = 'nodes_cases'
    Id = Column(String, primary_key=True)

    def __init__(self, Id):
        self.Id = Id


class Node(Base):
    __tablename__ = 'nodes'
    Id = Column(Integer, primary_key=True)
    CaseId = Column(String, ForeignKey('nodes_cases.Id'))
    NodeID = Column(Integer)
    X = Column(Float)
    Y = Column(Float)
    Z = Column(Float)
    Storey = Column(Integer)
    Point_Etabs = Column(Integer)

    def __init__(self, Id, CaseId, NodeID, X, Y, Z, Storey, Point_Etabs):
        self.Id = Id
        self.CaseId = CaseId
        self.NodeID = NodeID
        self.X = X
        self.Y = Y
        self.Z = Z
        self.Storey = Storey
        self.Point_Etabs = Point_Etabs

    def __repr__(self):
        return f'{self.CaseId}: Node {self.NodeID} coordinates {self.X}, {self.Y} , {self.Z}'


class SectionsCase(Base):
    __tablename__ = 'sections_cases'
    Id = Column(String, primary_key=True)

    def __init__(self, Id):
        self.Id = Id


class Section(Base):
    __tablename__ = 'sections'
    Id = Column(Integer, primary_key=True)
    CaseId = Column(String, ForeignKey('sections_cases.Id'))
    ElementType = Column(String)
    Frame = Column(Integer)
    Storey = Column(Integer)
    Frame_Loc = Column(String)
    SectionName = Column(String)
    b = Column(Float)
    h = Column(Float)

    def __init__(self, Id, CaseId, ElementType, Frame, Storey, Frame_Loc, SectionName, b, h):
        self.Id = Id
        self.CaseId = CaseId
        self.ElementType = ElementType
        self.Frame = Frame
        self.Storey = Storey
        self.Frame_Loc = Frame_Loc
        self.SectionName = SectionName
        self.b = b
        self.h = h


class ElementsCase(Base):
    __tablename__ = 'elements_cases'
    Id = Column(String, primary_key=True)

    def __init__(self, Id):
        self.Id = Id


class Element(Base):
    __tablename__ = 'elements'
    Id = Column(Integer, primary_key=True)
    CaseId = Column(String, ForeignKey('elements_cases.Id'))
    ElementID = Column(Integer)
    NodeI = Column(Integer)
    NodeJ = Column(Integer)
    ElementType = Column(String)
    SectionName = Column(String)
    Storey = Column(Integer)
    Line_Etabs = Column(String)
    ReinforcementID = Column(String)

    def __init__(self, Id, CaseId, ElementID, NodeI, NodeJ, ElementType, SectionName, Storey, Line_Etabs, ReinforcementID):
        self.Id = Id
        self.CaseId = CaseId
        self.ElementID = ElementID
        self.NodeI = NodeI
        self.NodeJ = NodeJ
        self.ElementType = ElementType
        self.SectionName = SectionName
        self.Storey = Storey
        self.Line_Etabs = Line_Etabs
        self.ReinforcementID = ReinforcementID


class SlabsCase(Base):
    __tablename__ = 'slabs_cases'
    Id = Column(String, primary_key=True)

    def __init__(self, Id):
        self.Id = Id


class Slab(Base):
    __tablename__ = 'slabs'
    Id = Column(Integer, primary_key=True)
    CaseId = Column(String, ForeignKey('slabs_cases.Id'))
    SlabID = Column(Integer)
    SlabType = Column(String)
    Lmax = Column(Float)
    Lmin = Column(Float)

    def __init__(self, Id, CaseId, SlabID, SlabType, Lmax, Lmin):
        self.Id = Id
        self.CaseId = CaseId
        self.SlabID = SlabID
        self.SlabType = SlabType
        self.Lmax = Lmax
        self.Lmin = Lmin


class NodeSlabConnCase(Base):
    __tablename__ = 'node_slab_conns_cases'
    Id = Column(String, primary_key=True)

    def __init__(self, Id):
        self.Id = Id


class NodeSlabConn(Base):
    __tablename__ = 'node_slab_conns'
    Id = Column(Integer, primary_key=True)
    CaseId = Column(String, ForeignKey('node_slab_conns_cases.Id'))
    NodeID = Column(Integer)
    Frame_Trans_Loc = Column(String)
    SlabConΔ1 = Column(String)
    SlabConΔ2 = Column(String)

    def __init__(self, Id, CaseId, NodeID, Frame_Trans_Loc, SlabConΔ1, SlabConΔ2):
        self.Id = Id
        self.CaseId = CaseId
        self.NodeID = NodeID
        self.Frame_Trans_Loc = Frame_Trans_Loc
        self.SlabConΔ1 = SlabConΔ1
        self.SlabConΔ2 = SlabConΔ2


class BeamSlabConnCase(Base):
    __tablename__ = 'beam_slab_conns_cases'
    Id = Column(String, primary_key=True)

    def __init__(self, Id):
        self.Id = Id


class BeamSlabConn(Base):
    __tablename__ = 'beam_slab_conns'
    Id = Column(Integer, primary_key=True)
    CaseId = Column(String, ForeignKey('beam_slab_conns_cases.Id'))
    ElementID = Column(Integer)
    SectionName = Column(String)
    Storey = Column(Integer)
    Line_Etabs = Column(String)
    SlabConnectivity = Column(String)
    Frame_Loc = Column(String)

    def __init__(self, Id, CaseId, ElementID, SectionName, Storey, Line_Etabs, SlabConnectivity, Frame_Loc):
        self.Id = Id
        self.CaseId = CaseId
        self.ElementID = ElementID
        self.SectionName = SectionName
        self.Storey = Storey
        self.Line_Etabs = Line_Etabs
        self.SlabConnectivity = SlabConnectivity
        self.Frame_Loc = Frame_Loc


class MaterialsCase(Base):
    __tablename__ = 'materials_cases'
    Id = Column(String, primary_key=True)

    def __init__(self, Id):
        self.Id = Id


class Material(Base):
    __tablename__ = 'materials'
    Id = Column(Integer, primary_key=True)
    CaseId = Column(String, ForeignKey('materials_cases.Id'))
    materialID = Column(String)
    fc = Column(Float)
    E = Column(Float)
    U = Column(Float)
    A = Column(Float)
    γc = Column(Float)
    fy = Column(Float)
    fyw = Column(Float)

    def __init__(self, Id, CaseId, materialID, fc, E, U, A, γc, fy, fyw):
        self.Id = Id
        self.CaseId = CaseId
        self.materialID	= materialID
        self.fc = fc
        self.E = E
        self.U = U
        self.A = A
        self.γc = γc
        self.fy = fy
        self.fyw = fyw


class BeamReinforcementsCase(Base):
    __tablename__ = 'beam_reinforcements_cases'
    Id = Column(String, primary_key=True)

    def __init__(self, Id):
        self.Id = Id


class BeamReinforcement(Base):
    __tablename__ = 'beam_reinforcements'
    Id = Column(Integer, primary_key=True)
    CaseId = Column(String, ForeignKey('beam_reinforcements.Id'))
    ReinforcementID = Column(String)
    LongTopLeft = Column(String)
    LongBotLeft = Column(String)
    TransLeft = Column(String)
    LongTopRight = Column(String)
    LongBotRight = Column(String)
    TransRight = Column(String)

    def __init__(self, Id, CaseId, ReinforcementID, LongTopLeft, LongBotLeft, TransLeft, LongTopRight, LongBotRight, TransRight):
        self.Id = Id
        self.CaseId = CaseId
        self.ReinforcementID = ReinforcementID
        self.LongTopLeft = LongTopLeft
        self.LongBotLeft = LongBotLeft
        self.TransLeft = TransLeft
        self.LongTopRight = LongTopRight
        self.LongBotRight = LongBotRight
        self.TransRight = TransRight


class ColumnReinforcementsCase(Base):
    __tablename__ = 'column_reinforcements_cases'
    Id = Column(String, primary_key=True)

    def __init__(self, Id):
        self.Id = Id


class ColumnReinforcement(Base):
    __tablename__ = 'column_reinforcements'
    Id = Column(Integer, primary_key=True)
    CaseId = Column(String, ForeignKey('column_reinforcements_cases.Id'))
    ReinforcementID = Column(String)
    LongMain = Column(String)
    LongSide = Column(String)
    Trans = Column(String)
    SideHoopLegs = Column(Integer)

    def __init__(self, Id, CaseId, ReinforcementID, LongMain, LongSide, Trans, SideHoopLegs):
        self.Id = Id
        self.CaseId = CaseId
        self.ReinforcementID = ReinforcementID
        self.LongMain = LongMain
        self.LongSide = LongSide
        self.Trans = Trans
        self.SideHoopLegs = SideHoopLegs


class ModFactorsCase(Base):
    __tablename__ = 'mod_factors_cases'
    Id = Column(String, primary_key=True)

    def __init__(self, Id):
        self.Id = Id


class ModFactor(Base):
    __tablename__ = 'mod_factors'
    Id = Column(Integer, primary_key=True)
    CaseId = Column(String, ForeignKey('mod_factors_cases.Id'))
    ElementType = Column(String)
    Area = Column(Float)
    Moment = Column(Float)
    Shear = Column(Float)
    Torsional = Column(Float)

    def __init__(self, Id, CaseId, ElementType, Area, Moment, Shear, Torsional):
        self.Id = Id
        self.CaseId = CaseId
        self.ElementType = ElementType
        self.Area = Area
        self.Moment = Moment
        self.Shear = Shear
        self.Torsional = Torsional
