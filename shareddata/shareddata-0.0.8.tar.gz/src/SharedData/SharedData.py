
from SharedData.SharedDataFeeder import SharedDataFeeder
from SharedData.Metadata import Metadata

class SharedData:

    def __init__(self, database,s3read=False,s3write=False):                            
        self.database = database
        self.s3read = s3read
        self.s3write = s3write
        
        # DATA DICTIONARY
        # SharedDataTimeSeries: data[feeder][period][tag] (date x symbols)
        # SharedDataFrame: data[feeder][period][date] (symbols x tags)
        self.data = {} 

        # Symbols collections metadata
        self.metadata = {}
        
        # DATASET
        md = Metadata('DATASET/DATASET_' + database,\
            s3read=self.s3read,s3write=self.s3write)
        self.dataset = md.static

    def __setitem__(self, feeder, value):
        self.data[feeder] = value
                
    def __getitem__(self, feeder):        
        if not feeder in self.data.keys():
            self.data[feeder] = SharedDataFeeder(self, feeder)
        return self.data[feeder]

    def getMetadata(self, collection):
        if not collection in self.metadata.keys():              
            self.metadata[collection] = Metadata(collection,\
                s3read=self.s3read,s3write=self.s3write)
        return self.metadata[collection]

    def getSymbols(self, collection):        
        return self.getMetadata(collection).static.index.values
    
    