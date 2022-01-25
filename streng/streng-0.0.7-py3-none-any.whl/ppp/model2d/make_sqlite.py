import os
import math
import contextlib
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy import and_, or_
from sqlalchemy.orm import relationship, backref, sessionmaker
from streng.ppp.model2d.sql_base import Base
from streng.ppp.model2d.input_classes import Building, Geometry, Node, FrameElement, Slab, BeamSlabConn
from streng.common.math.simple import digits_in_int

def do_it(filename, excel_file, echo=False):
    df = {}
    tablenames = ['node',
                  'geometry',
                  'frame_element',
                  'slab',
                  'beam_slab_conn',
                  'building',
                  'frame_section']
    for tablename in tablenames:
        df[tablename] = pd.read_excel(excel_file, tablename,
                                      engine='openpyxl')

    with contextlib.suppress(FileNotFoundError):
        os.remove(filename)

    engine = create_engine(r"sqlite:///" + filename, echo=echo)
    Base.metadata.create_all(engine, checkfirst=True)
    Session = sessionmaker(bind=engine)
    session = Session()

    for tablename in tablenames:
        df[tablename].to_sql(tablename, engine, index=False, if_exists="append")

    create_infilled_moment_frames(session=session)

    query = session.query(Building.id).distinct()
    building_names = [r[0] for r in list(query)]

    query = session.query(Geometry.id).distinct()
    geometry_names = [r[0] for r in list(query)]

    node_extra_columns(session=session, geometry_names=geometry_names)
    frame_element_extra_columns(session=session, geometry_names=geometry_names)

    session.close()
    engine.dispose()


def node_extra_columns(session, geometry_names):

    for gname in geometry_names:
        query = session.query(Geometry).filter_by(id=gname).first()

        nodes_y_levels = query.nodes_y_levels
        nodes_x_levels = query.nodes_x_levels

        for y_level, y in nodes_y_levels.items():
            for row in query.nodes:
                if math.isclose(row.Y, y):
                    row.storey = y_level

        for x_level, x in nodes_x_levels.items():
            for row in query.nodes:
                if math.isclose(row.X, x):
                    row.x_level = x_level

    session.commit()


def frame_element_extra_columns(session, geometry_names):

    for gname in geometry_names:
        query = session.query(Geometry).filter_by(id=gname).first()

        # Read frame_element storey from node_j of each element (need it for columns/walls)
        for frame_element in query.frame_elements:
            nodej_id = frame_element.node_j
            query_node_j = session.query(Node).filter(and_(Node.geometry_id == gname, Node.id == nodej_id)).first()
            frame_element.storey = query_node_j.storey

            if frame_element.storey != digits_in_int(frame_element.id)[0]:
                print('check elements and nodes numbering')

    session.commit()


def create_infilled_moment_frames(session):

    # add geometries
    gquery = session.query(Geometry).filter(Geometry.id.contains('moment')).all()
    for g in gquery:
        gnew = Geometry(id=g.id + '_inf', slab_pattern=g.slab_pattern)
        session.add(gnew)

    # add nodes
    nquery = session.query(Node).filter(Node.geometry_id.contains('moment')).all()
    # first copy identical nodes with bare frame
    for n in nquery:
        nnew = Node(geometry_id=n.geometry_id + '_inf', id=n.id, X=n.X, Y=n.Y)
        session.add(nnew)
    # next add new nodes
    for n in nquery:
        nnew = Node(geometry_id=n.geometry_id + '_inf', id=n.id+100, X=n.X+20., Y=n.Y)
        session.add(nnew)

    session.commit()
