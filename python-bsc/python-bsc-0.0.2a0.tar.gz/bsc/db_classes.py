# coding: utf-8
from sqlalchemy import CHAR, Column, Float, ForeignKey, ForeignKeyConstraint, Index, Integer, String, Time,text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.expression import null
from sqlalchemy.sql.sqltypes import TIMESTAMP, Boolean
import flask_login
from flask_login import UserMixin
from db_init_file import db
from sqlalchemy.schema import UniqueConstraint

Base = declarative_base()
metadata = Base.metadata


class EntityType(db.Model):
    __tablename__ = 'entity_type'

    entity_type_id = Column(CHAR(50), primary_key=True)
    entity_type_description = Column(CHAR(100), nullable=False)


class MeasureType(db.Model):
    __tablename__ = 'measure_type'

    measure_type_id = Column(CHAR(50), primary_key=True)
    measure_type_description = Column(CHAR(100), nullable=False)


class Mentor(db.Model):
    __tablename__ = 'mentor'

    mentor_id = Column(CHAR(100), primary_key=True)
    name = Column(CHAR(100), nullable=False)
    surname = Column(CHAR(100), nullable=False)


class Perspective(db.Model):
    __tablename__ = 'perspective'

    perspective_id = Column(CHAR(50), primary_key=True)
    perspective_description = Column(CHAR(100), nullable=False)


class SensorStore(db.Model):
    __tablename__ = 'sensor_store'

    sensor_store_catalog_id = Column(Integer, primary_key=True, nullable=False)
    sensor_store_id = Column(CHAR(100), primary_key=True, nullable=False)
    sensor_description = Column(CHAR(100), nullable=False)
    sensor_active_indicator = Column(CHAR(50), nullable=False)


class Farm(db.Model):
    __tablename__ = 'farm'

    farm_id = Column(CHAR(100), primary_key=True)
    farm_type = Column(CHAR(100), nullable=False)
    longitude = Column(CHAR(100), nullable=False)
    lattitude = Column(CHAR(100), nullable=False)
    size = Column(Integer, nullable=False)
    entity_type_id = Column(ForeignKey('entity_type.entity_type_id'), nullable=False, index=True)

    entity_type = relationship('EntityType')


class MeasureStore(db.Model):
    __tablename__ = 'measure_store'

    measure_store_catalog_id = Column(Integer, primary_key=True, nullable=False)
    measure_store_id = Column(CHAR(100), primary_key=True, nullable=False)
    measure_description = Column(CHAR(100), nullable=False)
    measure_type_id = Column(ForeignKey('measure_type.measure_type_id'), nullable=False, index=True)

    measure_type = relationship('MeasureType')


class ObjectiveStore(db.Model):
    __tablename__ = 'objective_store'

    objective_id = Column(CHAR(100), primary_key=True)
    objective_description = Column(CHAR(100), nullable=False)
    perspective_id = Column(ForeignKey('perspective.perspective_id'), nullable=False, index=True)

    perspective = relationship('Perspective')


class Customer(db.Model):
    __tablename__ = 'customer'

    customer_id = Column(CHAR(100), primary_key=True)
    farm_id = Column(ForeignKey('farm.farm_id'), nullable=False, index=True)
    customer_name = Column(CHAR(100), nullable=False)

    farm = relationship('Farm')

class CustomerTransaction(db.Model):
    __tablename__ = 'customer_transactions'

    transaction_id = Column(Integer, primary_key=True)
    product_id = Column(ForeignKey('product_store.product_id'), nullable=False, index=True)
    customer_id = Column(ForeignKey('customer.customer_id'), nullable=False, index=True)
    farm_id = Column(ForeignKey('farm.farm_id'), nullable=False, index=True)

    customer = relationship('Customer')
    farm = relationship('Farm')
    product = relationship('ProductStore')

class ProductStore(db.Model):
    __tablename__ = 'product_store'
    product_id = Column(CHAR(100), primary_key=True)
    product_description = Column(CHAR(100), nullable=False)


class FarmProduct(db.Model):
    __tablename__ = 'farm_product'

    farm_product_catalog_id = Column(Integer, primary_key=True)
    product_id = Column(ForeignKey('product_store.product_id'), nullable=False, index=True)
    farm_id = Column(ForeignKey('farm.farm_id'), nullable=False, index=True)
    create_time = Column(Time(True), server_default=text("now()"), nullable=False)

    farm = relationship('Farm')
    product = relationship('ProductStore')
    

    
class Employee(db.Model):
    __tablename__ = 'employee'

    employee_id = Column(CHAR(100), primary_key=True)
    name = Column(CHAR(100), nullable=False)
    surname = Column(CHAR(100), nullable=False)
    farm_id = Column(ForeignKey('farm.farm_id'), nullable=False, index=True)

    farm = relationship('Farm')


class FarmMeasure(db.Model):
    __tablename__ = 'farm_measure'
    __table_args__ = (
        ForeignKeyConstraint(['measure_store_catalog_id', 'measure_store_id'], ['measure_store.measure_store_catalog_id', 'measure_store.measure_store_id']),
        Index('fkidx_89', 'measure_store_catalog_id', 'measure_store_id')
    )

    farm_measure_catalog_id = Column(Integer, primary_key=True)
    measure_store_catalog_id = Column(Integer, nullable=False)
    measure_store_id = Column(CHAR(100), nullable=False)
    farm_id = Column(ForeignKey('farm.farm_id'), nullable=False, index=True)

    farm = relationship('Farm')
    measure_store_catalog = relationship('MeasureStore')


class FarmObjective(db.Model):
    __tablename__ = 'farm_objective'

    farm_objective_catalog_id = Column(Integer, primary_key=True)
    objective_id = Column(ForeignKey('objective_store.objective_id'), nullable=False, index=True)
    farm_id = Column(ForeignKey('farm.farm_id'), nullable=False, index=True)

    farm = relationship('Farm')
    objective = relationship('ObjectiveStore')


class FarmSensor(db.Model):
    __tablename__ = 'farm_sensor'
    __table_args__ = (
        ForeignKeyConstraint(['sensor_store_catalog_id', 'sensor_store_id'], ['sensor_store.sensor_store_catalog_id', 'sensor_store.sensor_store_id']),
        Index('fkidx_54', 'sensor_store_catalog_id', 'sensor_store_id')
    )

    sensor_store_id = Column(CHAR(100), primary_key=True, nullable=False)
    create_time = Column(Time(True), server_default=text("now()"), nullable=False)
    farm_id = Column(ForeignKey('farm.farm_id'), primary_key=True, nullable=False, index=True)
    sensor_store_catalog_id = Column(Integer, primary_key=True, nullable=False)
    sensor_value_lower_bound = Column(Float,nullable=False )
    sensor_value_upper_bound = Column(Float,nullable=True )
    sensor_value_ideal = Column(Float,nullable=True)
    farm = relationship('Farm')
    sensor_store_catalog = relationship('SensorStore')


class SensorForecast(FarmSensor):
    __tablename__ = 'sensor_forecast'
    __table_args__ = (
        ForeignKeyConstraint(['sensor_store_id', 'farm_id', 'sensor_store_catalog_id'], ['farm_sensor.sensor_store_id', 'farm_sensor.farm_id', 'farm_sensor.sensor_store_catalog_id']),
        Index('fkidx_70', 'sensor_store_id', 'farm_id', 'sensor_store_catalog_id')
    )

    sensor_store_catalog_id = Column(Integer, primary_key=True, nullable=False)
    farm_id = Column(CHAR(100), primary_key=True, nullable=False)
    sensor_store_id = Column(CHAR(100), primary_key=True, nullable=False)
    forecast_value = Column(String(50), nullable=False)
    forecast_value_upper = Column(Float, nullable=False)
    forecast_value_lower = Column(Float, nullable=False)
    forecast_date = Column(Float, nullable=False)


class Finance(db.Model):
    __tablename__ = 'finance'

    tran_id = Column(Integer, primary_key=True)
    farm_id = Column(ForeignKey('farm.farm_id'), nullable=False, index=True)
    income = Column(Float, nullable=True)
    expense = Column(Float, nullable=True)
    returns = Column(Float, nullable=True)
    expected_revenue = Column(Float, nullable=False)
    date = Column(Time(True), server_default=text("now()"), nullable=False)

    farm = relationship('Farm')


class MeasureSensor(db.Model):
    __tablename__ = 'measure_sensor'
    __table_args__ = (
        ForeignKeyConstraint(['measure_store_catalog_id', 'measure_store_id'], ['measure_store.measure_store_catalog_id', 'measure_store.measure_store_id']),
        ForeignKeyConstraint(['sensor_store_catalog_id', 'sensor_store_id'], ['sensor_store.sensor_store_catalog_id', 'sensor_store.sensor_store_id']),
        Index('fkidx_78', 'measure_store_catalog_id', 'measure_store_id'),
        Index('fkidx_82', 'sensor_store_catalog_id', 'sensor_store_id')
    )

    measure_sensor_relationship_id = Column(Integer, primary_key=True)
    measure_store_catalog_id = Column(Integer, nullable=False)
    measure_store_id = Column(CHAR(100), nullable=False)
    sensor_store_catalog_id = Column(Integer, nullable=False)
    sensor_store_id = Column(CHAR(100), nullable=False)

    measure_store_catalog = relationship('MeasureStore')
    sensor_store_catalog = relationship('SensorStore')


class MentorComment(db.Model):
    __tablename__ = 'mentor_comment'

    comment_id = Column(Integer, primary_key=True)
    comment = Column(CHAR(100), nullable=False)
    farm_id = Column(ForeignKey('farm.farm_id'), nullable=False, index=True)
    mentor_id = Column(ForeignKey('mentor.mentor_id'), nullable=False, index=True)

    farm = relationship('Farm')
    mentor = relationship('Mentor')


class ObjectiveMeasure(db.Model):
    __tablename__ = 'objective_measure'
    __table_args__ = (
        ForeignKeyConstraint(['measure_store_catalog_id', 'measure_store_id'], ['measure_store.measure_store_catalog_id', 'measure_store.measure_store_id']),
        Index('fkidx_128', 'measure_store_catalog_id', 'measure_store_id')
    )

    objective_measure_relationship_id = Column(Integer, primary_key=True, nullable=False)
    objective_id = Column(ForeignKey('objective_store.objective_id'), nullable=False, index=True)
    measure_store_catalog_id = Column(Integer, nullable=False)
    measure_store_id = Column(CHAR(100), nullable=False)

    measure_store_catalog = relationship('MeasureStore')
    objective = relationship('ObjectiveStore')


class ObjectiveSensor(db.Model):
    __tablename__ = 'objective_sensor'
    __table_args__ = (
        ForeignKeyConstraint(['sensor_store_catalog_id', 'sensor_store_id'], ['sensor_store.sensor_store_catalog_id', 'sensor_store.sensor_store_id']),
        Index('fkidx_115', 'sensor_store_catalog_id', 'sensor_store_id')
    )

    objective_sensor_catalog_id = Column(Integer, primary_key=True)
    sensor_store_catalog_id = Column(Integer, nullable=False)
    sensor_store_id = Column(CHAR(100), nullable=False)
    objective_id = Column(ForeignKey('objective_store.objective_id'), nullable=False, index=True)

    objective = relationship('ObjectiveStore')
    sensor_store_catalog = relationship('SensorStore')


class EmployeeStatus(db.Model):
    __tablename__ = 'employee_status'

    employee_id = Column(ForeignKey('employee.employee_id'), primary_key=True, nullable=False, index=True)
    farm_id = Column(ForeignKey('farm.farm_id'), primary_key=True, nullable=False, index=True)
    date = Column(Time(True), primary_key=True, server_default=text("now()") ,nullable=False)
    employee_satisfaction = Column('employee satisfaction', Integer, nullable=False)
    complaint = Column(CHAR(180))
    comment = Column(CHAR(180), nullable=False)

    employee = relationship('Employee')
    farm = relationship('Farm')

class SensorDatum(db.Model):
    __tablename__ = 'sensor_data'
    __table_args__ = (
        ForeignKeyConstraint(['sensor_store_id', 'farm_id', 'sensor_store_catalog_id'], ['farm_sensor.sensor_store_id', 'farm_sensor.farm_id', 'farm_sensor.sensor_store_catalog_id']),
        Index('fkidx_202', 'sensor_store_id', 'farm_id', 'sensor_store_catalog_id')
    )

    sensor_store_id = Column(CHAR(100), primary_key=True, nullable=False)
    farm_id = Column(CHAR(100), primary_key=True, nullable=True)
    sensor_store_catalog_id = Column(Integer, primary_key=True, nullable=False)
    row_id = Column(Float, primary_key=True, nullable=False)
    sensor_value = Column(Float, nullable=False)
    create_time = Column(TIMESTAMP(True), nullable=False)

    sensor_store = relationship('FarmSensor')


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.String(160), primary_key=True, nullable=False)
    name = db.Column(db.String(160), nullable=False)
    email = db.Column(db.String(240), nullable=False)
    profile_pic = db.Column(db.String(160), nullable=False)


class ResourceType(db.Model):
    __tablename__ = 'resource_type'

    resource_type_id = Column(CHAR(100), primary_key=True, nullable=False)
    resource_type = Column(CHAR(100), primary_key=True, nullable=False)
    source = Column(CHAR(100), primary_key=True, nullable=False)

class ResourceStore(db.Model):
    __tablename__ = 'resource_store'
    __table_args__ = (
        ForeignKeyConstraint(['resource_type_id', 'resource_type', 'source'], ['resource_type.resource_type_id', 'resource_type.resource_type', 'resource_type.source']),
        Index('fkidx_268', 'resource_type_id', 'resource_type', 'source')
    )

    resource_store_catalog_id = Column(Integer, primary_key=True, nullable=False)
    resource_store_id = Column(CHAR(100), primary_key=True, nullable=False)
    resource_description = Column(CHAR(100), nullable=False)
    farm_id = Column(ForeignKey('farm.farm_id'), index=True, nullable=True)
    resource_type_id = Column(CHAR(100), nullable=False)
    resource_type = Column(CHAR(100), nullable=False)
    source = Column(CHAR(100), nullable=False)
    capacity = Column(Float, nullable=False)
    can_split = Column(Boolean, nullable=False)

    farm = relationship('Farm')
    resource_type1 = relationship('ResourceType')

class FarmResource(db.Model):
    __tablename__ = 'farm_resource'
    __table_args__ = (
        ForeignKeyConstraint(['resource_store_catalog_id', 'resource_store_id'], ['resource_store.resource_store_catalog_id', 'resource_store.resource_store_id']),
        Index('fkidx_289', 'resource_store_catalog_id', 'resource_store_id')
    )

    farm_resource_relationship_id = Column(Integer, primary_key=True)
    resource_store_catalog_id = Column(Integer, nullable=False)
    resource_store_id = Column(CHAR(100), nullable=False)
    farm_id = Column(ForeignKey('farm.farm_id'), nullable=False, index=True)

    farm = relationship('Farm')
    resource_store_catalog = relationship('ResourceStore')

class SensorResource(db.Model):
    __tablename__ = 'sensor_resource'
    __table_args__ = (
        ForeignKeyConstraint(['resource_store_catalog_id', 'resource_store_id'], ['resource_store.resource_store_catalog_id', 'resource_store.resource_store_id']),
        ForeignKeyConstraint(['sensor_store_catalog_id', 'sensor_store_id'], ['sensor_store.sensor_store_catalog_id', 'sensor_store.sensor_store_id']),
        Index('fkidx_280', 'resource_store_catalog_id', 'resource_store_id'),
        Index('fkidx_299', 'sensor_store_catalog_id', 'sensor_store_id')
    )

    resource_store_catalog_id = Column(Integer, nullable=False)
    resource_store_id = Column(CHAR(100), nullable=False)
    sensor_store_catalog_id = Column(Integer, nullable=False)
    sensor_store_id = Column(CHAR(100), nullable=False)
    sensor_resource_relationship_id = Column(Integer, primary_key=True)

    resource_store_catalog = relationship('ResourceStore')
    sensor_store_catalog = relationship('SensorStore')

class ResourceDatum(db.Model):
    __tablename__ = 'resource_data'
    __table_args__ = (
        ForeignKeyConstraint(['sensor_store_id', 'farm_id', 'sensor_store_catalog_id', 'row_id_1'], ['sensor_data.sensor_store_id', 'sensor_data.farm_id', 'sensor_data.sensor_store_catalog_id', 'sensor_data.row_id']),
        Index('fkidx_308', 'sensor_store_id', 'farm_id', 'sensor_store_catalog_id', 'row_id_1')
    )

    sensor_store_id = Column(CHAR(100), nullable=False)
    farm_id = Column(CHAR(100), nullable=True)
    sensor_store_catalog_id = Column(Integer, nullable=False)
    row_id_1 = Column(Float, nullable=False)
    farm_resource_relationship_id = Column(ForeignKey('farm_resource.farm_resource_relationship_id'), nullable=False, index=True)
    row_id = Column(Integer, primary_key=True)

    farm_resource_relationship = relationship('FarmResource')
    sensor_store = relationship('SensorDatum')    


class State(db.Model):
    __tablename__ = 'state'

    ID = Column(CHAR(20), nullable=False, primary_key=True)
    Name = Column(CHAR(20), nullable=False)


class Stakeholder(db.Model):
    __tablename__ = 'stakeholder'
    __table_args__ = (
        ForeignKeyConstraint(['resource_store_catalog_id', 'resource_store_id'], ['resource_store.resource_store_catalog_id', 'resource_store.resource_store_id']),
        Index('fk_324', 'resource_store_catalog_id', 'resource_store_id')
    )

    stakeholder_id = Column(Integer, primary_key=True)
    stakeholder_name = Column(CHAR(100), nullable=False)
    resource_store_catalog_id = Column(Integer)
    farm_id = Column(ForeignKey('farm.farm_id'), index=True)
    resource_store_id = Column(CHAR(100))
    stakeholder_type = Column(CHAR(100), nullable=False)

    farm = relationship('Farm')
    resource_store_catalog = relationship('ResourceStore')