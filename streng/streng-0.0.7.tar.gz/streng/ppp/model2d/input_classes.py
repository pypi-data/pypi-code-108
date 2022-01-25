import math
from .sql_base import Base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, String, Integer, Float, ForeignKey


# from sqlalchemy.ext.declarative import declared_attr


class Building(Base):
    __tablename__ = 'building'
    id = Column(String(30), primary_key=True)
    geometry_id = Column(String(30), ForeignKey('geometry.id'))
    structural_system = Column(String(20))
    storeys = Column(Integer)
    code = Column(String(10))

    geometry = relationship("Geometry", back_populates="building")  # For many-to-one. See sqlalchemy docs
    frame_sections = relationship("FrameSection", backref="building")  # One-to-many


class Geometry(Base):
    __tablename__ = 'geometry'
    id = Column(String(30), primary_key=True)
    slab_pattern = Column(String(10))

    # One-to-many relationships
    nodes = relationship("Node", back_populates="geometry")
    frame_elements = relationship("FrameElement", back_populates="geometry")
    slabs = relationship("Slab", back_populates="geometry")
    beam_slab_conns = relationship("BeamSlabConn", back_populates="geometry")

    # For many-to-one. See sqlalchemy docs
    building = relationship("Building", back_populates="geometry",
                            uselist=False)

    @property
    def number_of_storeys(self):
        return self.building.storeys

    @property
    def number_of_nodes(self):
        return len(list(self.nodes))

    @property
    def number_of_frame_elements(self):
        return len(list(self.frame_elements))

    @property
    def nodes_x_levels(self):
        xs = [n.X for n in self.nodes]
        return {(k + 1): v for k, v in enumerate(sorted(set(xs)))}

    @property
    def nodes_y_levels(self):
        ys = [n.Y for n in self.nodes]
        return {k: v for k, v in enumerate(sorted(set(ys)))}

    def __repr__(self):
        return f'Geometry: id={self.id} slab_pattern={self.slab_pattern} ' + \
               f'number_of_nodes={self.number_of_nodes} number_of_frame_elements={self.number_of_frame_elements}'

    @property
    def nodes_to_tcl(self):
        str_lines = []
        _str = '# ---------------------------------------------------------------------------------------------------\n'
        _str += '# N O D E S\n'
        _str += '# ---------------------------------------------------------------------------------------------------\n'
        _str += '#        nodeID            X            Y\n'
        for n in self.nodes:
            _str += f'node {n.id:10} {n.X:12.3f} {n.Y:12.3f}\n'
        return _str + '\n'

        str_lines.append('')
        str_lines.append(
            '# --------------------------------------------------------------------------------------------------------------')
        sstr_lines.append('# N O D E S')
        str_lines.append(
            '# --------------------------------------------------------------------------------------------------------------')
        sstr_lines.append('')
        str_lines.append('# node $NodeTag $XCoord $Ycoord')
        str_lines.append('')

        for n in self.nodes:
            str_lines.append(f'node{n.id:7}{n.X:13.3f}{n.Y:13.3f}')

        return '\n'.join(str_lines)


class Node(Base):
    __tablename__ = 'node'
    geometry_id = Column(String(30), ForeignKey('geometry.id'), primary_key=True)
    id = Column(Integer, primary_key=True)
    X = Column(Float)
    Y = Column(Float)
    storey = Column(Integer)
    x_level = Column(Integer)

    # relationships
    geometry = relationship("Geometry", back_populates='nodes')

    def __repr__(self):
        return f'Node: geometry_id={self.geometry_id} id={self.id} X={self.X} Y={self.Y}'


class Slab(Base):
    __tablename__ = 'slab'
    pattern = Column(String(10), ForeignKey('geometry.slab_pattern'), primary_key=True)
    id = Column(String(10), primary_key=True)
    slab_type = Column(String(2))
    Lmax = Column(Float)
    Lmin = Column(Float)

    # relationships
    geometry = relationship("Geometry", back_populates='slabs')

    def __repr__(self):
        return f'Slab: pattern={self.pattern} id={self.id} slab_type={self.slab_type} Lmax={self.Lmax} Lmin={self.Lmin}'


class FrameElement(Base):
    __tablename__ = 'frame_element'
    geometry_id = Column(String(30), ForeignKey('geometry.id'), primary_key=True, nullable=False)
    id = Column(Integer, primary_key=True, nullable=False)
    node_i = Column(Integer, nullable=False)
    node_j = Column(Integer, nullable=False)
    section_id = Column(String(30), nullable=False)
    # columns filled using code
    storey = Column(Integer)

    # relationships
    geometry = relationship("Geometry", back_populates='frame_elements')

    def __repr__(self):
        return f'FrameElement: geometry_id={self.geometry_id} id={self.id} ' + \
               f'node_i={self.node_i} node_j={self.node_j} section_id={self.section_id}'


class BeamSlabConn(Base):
    __tablename__ = 'beam_slab_conn'
    geometry_id = Column(String(30), ForeignKey('geometry.id'), primary_key=True)
    element_id = Column(Integer, ForeignKey('frame_element.id'), primary_key=True)
    slab_connectivity = Column(String(20))

    # relationships
    geometry = relationship("Geometry", back_populates='beam_slab_conns')

    frame_element = relationship('FrameElement', uselist=False)



class FrameSection(Base):
    __tablename__ = 'frame_section'
    building_id = Column(String(30), ForeignKey('building.id'), primary_key=True)
    id = Column(String(30), primary_key=True)
    b = Column(Float)
    h = Column(Float)
    hf = Column(Float)
    beff = Column(Float)

    structural_type = Column(String(15))
