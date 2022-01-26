"""
views_runs
==========

This package collects views related tools and utilities used when planning,
training and storing views "runs" of predictions.

classes:
    ViewsRun:
        Class that encapsulates StepshiftedModels and DataPartitioner objects
        to provide a nice API for training and producing predictions.
    Storage:
        A class that exposes the viewser model_storage storage driver, used to
        save and load trained model objects.
    StepshiftedModels:
        Model class from the stepshift package that lets you train stepshifted
        models.
    DataPartitioner:
        Utility class for subsetting data in time, that lets you define
        tranining and testing periods, as well as do operations to ensure no
        overlap exists between these periods.
    ModelMetadata:
        Class used to specify metadata for trained model objects.

modules:
    utilities: Various utility functions ported from views 2
    stats: Resampling functions
    run: Defines the ViewsRun class
    storage: Defines the Storage class
    validation: Functions used internally to validate data

Each class and module mentioned here has more documentation. Use the help()
function.

"""

from .run import ViewsRun
from .storage import Storage
from .vendoring import *

from stepshift.views import StepshiftedModels
from views_partitioning.data_partitioner import DataPartitioner
from views_schema.models import ModelMetadata
