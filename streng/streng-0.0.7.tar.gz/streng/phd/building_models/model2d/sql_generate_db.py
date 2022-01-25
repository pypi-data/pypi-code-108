from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import orm
from sqlalchemy import Table, Column, Integer, String, Date, MetaData, Float, ForeignKey
from sqlalchemy import func

import pandas as pd

from .sql_classes import Base
from .sql_classes import Node, NodesCase, \
                Section, SectionsCase, \
                Element, ElementsCase, \
                Slab, SlabsCase, \
                NodeSlabConn, NodeSlabConnCase, \
                BeamSlabConn, BeamSlabConnCase, \
                Material, MaterialsCase, \
                BeamReinforcement, BeamReinforcementsCase, \
                ColumnReinforcement, ColumnReinforcementsCase, \
                ModFactor, ModFactorsCase, \
                BuildingIdentity


def create_db(excel_filename, db_filename):
    engine = create_engine(f'sqlite:///{db_filename}', echo=True)

    myBase = Base
    myBase.metadata.create_all(engine)

    Session = orm.sessionmaker(bind=engine)
    session = Session()

    # Load Excel file
    input_data = dict()
    xls = pd.ExcelFile(excel_filename)
    for sheet_name in xls.sheet_names:
        input_data[sheet_name] = pd.read_excel(excel_filename, sheet_name=sheet_name)

    # Create nodes_cases table
    nodes_cases_list = input_data['nodes'].CaseId.unique().tolist()
    for nc in nodes_cases_list:
        nodes_case = NodesCase(Id=nc)
        session.add(nodes_case)
    session.commit()

    # Create sections_cases table
    sections_cases_list = input_data['sections'].CaseId.unique().tolist()
    for sc in sections_cases_list:
        sections_case = SectionsCase(Id=sc)
        session.add(sections_case)
    session.commit()

    # Create elements_cases table
    elements_cases_list = input_data['elements'].CaseId.unique().tolist()
    for ec in elements_cases_list:
        elements_case = ElementsCase(Id=ec)
        session.add(elements_case)
    session.commit()

    # Create slabs_cases table
    slabs_cases_list = input_data['slabs'].CaseId.unique().tolist()
    for sc in slabs_cases_list:
        slabs_case = SlabsCase(Id=sc)
        session.add(slabs_case)
    session.commit()

    # Create node_slab_conns_cases table
    node_slab_conns_cases_list = input_data['node_slab_conns'].CaseId.unique().tolist()
    for nsc in node_slab_conns_cases_list:
        node_slab_conns_case = NodeSlabConnCase(Id=nsc)
        session.add(node_slab_conns_case)
    session.commit()

    # Create beam_slab_conns_cases table
    beam_slab_conns_cases_list = input_data['beam_slab_conns'].CaseId.unique().tolist()
    for bsc in beam_slab_conns_cases_list:
        beam_slab_conns_case = BeamSlabConnCase(Id=bsc)
        session.add(beam_slab_conns_case)
    session.commit()

    # Create materials_cases table
    materials_cases_list = input_data['materials'].CaseId.unique().tolist()
    for mc in materials_cases_list:
        materials_case = MaterialsCase(Id=mc)
        session.add(materials_case)
    session.commit()

    # Create beam_reinforcements_cases table
    beam_reinforcements_cases_list = input_data['beam_reinforcements'].CaseId.unique().tolist()
    for brc in beam_reinforcements_cases_list:
        beam_reinforcements_case = BeamReinforcementsCase(Id=brc)
        session.add(beam_reinforcements_case)
    session.commit()

    # Create column_reinforcements_cases table
    column_reinforcements_cases_list = input_data['column_reinforcements'].CaseId.unique().tolist()
    for crc in column_reinforcements_cases_list:
        column_reinforcements_case = ColumnReinforcementsCase(Id=crc)
        session.add(column_reinforcements_case)
    session.commit()

    # Create mod_factors_cases table
    mod_factors_cases_list = input_data['mod_factors'].CaseId.unique().tolist()
    for mfc in column_reinforcements_cases_list:
        mod_factors_case = ModFactorsCase(Id=mfc)
        session.add(mod_factors_case)
    session.commit()

    # Get data from excel file sheets
    con = engine.connect()
    for sheet_name in xls.sheet_names:
        input_data[sheet_name].to_sql(sheet_name, con, index=False, if_exists="append")
    # con.commit()
    con.close()

    session.close()


# create_db(excel_filename=r'D:\phd_closure\files\ch3\designs\all_building_models_sqlite_v1.xlsm',
#           db_filename='test_building_models.db')

