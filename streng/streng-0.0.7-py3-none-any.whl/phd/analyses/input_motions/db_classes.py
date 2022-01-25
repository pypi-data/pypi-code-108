"""
.. uml::

    @startmindmap
    * db_classes
    ** Accellerogram
    ** RecordDescription
    @endmindmap
"""

import io
import zlib
import numpy as np

# from sqlalchemy import create_engine
# from sqlalchemy import orm
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, String, Date, MetaData, Float, ForeignKey, BLOB

Base = declarative_base()


class Accellerogram(Base):
    """
    .. uml::

        class Accellerogram {
        .. tablename ..
        accellerograms
        .. attributes - columns ..
        + accellerogram_id (String):
        + record_id (String):
        + dt (Float):
        + accellerations_compressed (BLOB):
        .. properties ..
        + accelerations()
        .. staticmethods ..
        + compress_accellerations(accelerations)
        }

    """
    __tablename__ = 'accellerogram'

    accellerogram_id = Column(String, primary_key=True)
    record_id = Column(String)
    dt = Column(Float)
    accellerations_compressed = Column(BLOB)

    def __init__(self, accellerogram_id, record_id, dt, accellerations_compressed):
        self.accellerogram_id = accellerogram_id
        self.record_id = record_id
        self.dt = dt
        self.accellerations_compressed = accellerations_compressed

    @property
    def accellerations(self):
        """

        Returns:
            numpy array: decompresses accelleration values
        """
        return np.load(io.BytesIO(zlib.decompress(self.accellerations_compressed)))

    @staticmethod
    def compress_accellerations(accellerations):
        """
            gets a numpy array with all accelleration values and returns it compressed to store in the sqlite database

        Args:
            accellerations (numpy array): accellerogram values

        Returns:
            a zlib compressed object

        """
        f = io.BytesIO()
        np.save(f, accellerations)
        comp = zlib.compress(f.getvalue())
        return comp

    def __repr__(self):
        return f'{self.symbol}: hey'


class RecordDescription(Base):
    """
    .. uml::

        class RecordDescription {
        .. attributes - columns ..
        + record_id: String
        + date: Date
        + latitude: Float
        + longitude: Float
        + magnitude: Float
        + epicentral_distance: Float
        + ground_ec8: String
        }

    """
    __tablename__ = 'records_descriptions'

    record_id = Column(String, primary_key=True)
    date = Column(Date)
    latitude = Column(Float)
    longitude = Column(Float)
    magnitude = Column(Float)
    epicentral_distance = Column(Float)
    ground_ec8 = Column(String)


