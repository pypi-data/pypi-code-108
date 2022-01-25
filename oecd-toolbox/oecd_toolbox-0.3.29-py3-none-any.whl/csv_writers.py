import csv
import ujson as json
import warnings
from pathlib import Path
from typing import Callable, List, Optional, Tuple, Iterator
from dbnomics_data_model.observations import Frequency, detect_period_format_strict, period_format_strict_regex_list
from .converters import SimpleConverter
from dbnomics_fetcher_toolbox.resources import Resource 
from slugify import slugify


class FileResource(Resource):
    """ A resource-type consisting of a single downloadable file, identified by a URL
    and a target path where it should be deposited.
    """
    targetDataset: Path
    sourceFolder: Path
    fileToProcess: str
    

    def delete(self):
        """ Deletes the local representation of a dataset including its containing folder. """
        for f in self.targetDataset.glob('*.*'):
            f.unlink()
        self.targetDataset.rmdir

class DataCaptureConverter(SimpleConverter):
    ''' A converter to create DataCapture ready files from DbNomics jsonl files for an entire project.'''
    def prepare_resources(self) -> Iterator[Resource]:
        #print('Create an iterator of resources - can be a similar function outside of a subclass')
        
        for f in self.source_dir.rglob('series.jsonl'):
            dirPath = f.parents[0]
            fileName = f.name
            relDirPath = dirPath.relative_to(self.source_dir)
            did = slugify(str(relDirPath))
            yield FileResource(id=did, sourceFolder = dirPath, targetDataset = self.target_dir / relDirPath, fileToProcess = fileName)
            

    def process_single_resource(self, res: Resource):
        if not res.targetDataset.exists():
            res.targetDataset.mkdir(parents=True)
        series_jsonl_to_DataCapturecsv(res.sourceFolder / res.fileToProcess, Path(res.targetDataset / res.fileToProcess).with_suffix('.csv'))


def dataset_json_to_csv(source_dir : Path):
    """Convert dataset.json into a csv file"""
    warnings.warn("Dataset.json to csv conversion is deprecated. Use the json file directly to access structural information.", warnings.DeprecationWarning)    


#----------------------series_jsonl conversions----------------------
def series_jsonl_to_csv_base(source_file: Path, target_file: Path, fieldnames: List, obslist_fn: Callable[[List], None]):
    """ Convert series.jsonl into a csv file. 
    Base function.
    Needs to be called by a function that provides the fields and methods to convert to.
    """

    json_file = []
    for line in open(source_file, 'r', encoding="UTF-8"):
        json_file.append(json.loads(line))
    
    def create_csv_file(tf: Path, fn: list):
        with open(tf, 'w', encoding="UTF-8", newline='') as csvfile:
            writer = csv.DictWriter(f=csvfile, fieldnames=fn, extrasaction='ignore')
            writer.writeheader()
            for data in obslist_fn(json_file):
                writer.writerow(data)
    
    create_csv_file(target_file, fieldnames)


def series_jsonl_to_csv(source_file: Path):
    """ Simple generic csv flavour of the convertor. """

    def create_observations_list(json_file: List) -> List:
        L=[]
        for series in json_file:
            for obs in series['observations'][1:]:
                dim_dict=dict()
                dim_dict['code'] = series['code']
                dim_dict['PERIOD'] =  obs[0]
                dim_dict['VALUE'] = obs[1]

                L.append(dim_dict)
        return L 

    series_jsonl_to_csv_base(source_file=source_file, target_file='series.csv', fieldnames=['code' ,'PERIOD','VALUE'], obslist_fn=create_observations_list)       


DC_eligible_frequencies = [Frequency.ANNUAL, Frequency.QUARTERLY, Frequency.MONTHLY, Frequency.BI_ANNUAL]
DC_eligible_frequency_codes = [f.to_dimension_code() for f in DC_eligible_frequencies]


def series_jsonl_to_DataCapturecsv(source_file: Path, target_file: Path):
    """ DataCapture csv flavour of the convertor. """

    def create_DCobservations_list(json_file: List) -> List:
        L=[]
        for series in json_file:
            if series['dimensions']['FREQ'] in DC_eligible_frequency_codes:
                for obs in series['observations'][1:]:
                    dim_dict=dict()
                    dim_dict['code'] = series['code']
                    dim_dict['year'], dim_dict['freq'], dim_dict['period'] = get_DC_compatible_date(obs[0])
                    dim_dict['value'] = obs[1]

                    L.append(dim_dict)
        return L 

    series_jsonl_to_csv_base(source_file=source_file, target_file=target_file, fieldnames=['code', 'year', 'freq', 'period', 'value'], obslist_fn=create_DCobservations_list)


  

def get_DC_compatible_date(period: str) -> Optional[Tuple[int, str, int]]:
    """Return a tuple of (year, frequency_code, period_withinyear) or `None` if unable to detect.

    # Working examples:
    >>> get_DC_compatible_date("2014")
    2014, A, 1 
    >>> get_DC_compatible_date("2014-S1")
    2014, Q, 2
    >>> get_DC_compatible_date("2014-Q1")
    2014, Q, 1 
    >>> get_DC_compatible_date("2014-01")
    2014, M, 1

    # Invalid formats:
    >>> detect_period_format_strict("ABCDE")
    >>> detect_period_format_strict("2014Z01")
    """
    freq = detect_period_format_strict(period)
    if freq in DC_eligible_frequencies:
        for period_format, regex in period_format_strict_regex_list: 
            if freq == period_format:
                m = regex.match(period)
                if freq == Frequency.ANNUAL:
                    return int(m.group(1)), freq.to_dimension_code(), 1
                elif freq == Frequency.BI_ANNUAL:
                    return int(m.group(1)), "Q", int(m.group(2)) * 2
                else:
                    return int(m.group(1)), freq.to_dimension_code(), int(m.group(2))
    return None






