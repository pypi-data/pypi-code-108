import re
import datetime

DATE_RANGE_FILTER = 'date'
TEXT_FILTER = 'text'
NUMBER_RANGE_FILTER = 'number'
FILTER_TYPES = [DATE_RANGE_FILTER, TEXT_FILTER, NUMBER_RANGE_FILTER]

# Check for date in format YYYY-XX-XX
DATE_CHECK = re.compile(r'^\d\d\d\d[-/]\d\d[-/]\d\d$')


def date_format_checker(date):
    if not DATE_CHECK.match(date):
        return False

    year = int(date[:4])
    month = int(date[5:7])
    day = int(date[8:10])
    # Check for date in format YYYY-MM-DD
    # TODO: allow for YYYY-M-D dates without 0 padding
    try:
        d = datetime.datetime(year,month,day)
        return True
    except ValueError:
        return False
    

class JobConfig:
    def __init__(self, pipeline_id, job_name):
        self.pipeline_id = pipeline_id
        self.filters = {}
        self.__allow_push_to_db = False
        self.__job_name = job_name

    def add_filter(self, field, filter_type, value, negate=False):
        if filter_type not in FILTER_TYPES:
            raise ValueError('"filter_type" should be one of ' + str(FILTER_TYPES))
        if filter_type == TEXT_FILTER:
            if not isinstance(value, str):
                raise ValueError('Value must be a string when using a text filter.')
            filter_params = {'filter_type': filter_type, 'value': value, 'not': negate}

        elif filter_type in [DATE_RANGE_FILTER, NUMBER_RANGE_FILTER]:
            if not isinstance(value, list) or len(value) != 2:
                raise ValueError('Value must be a list of length 2 [start, end] when using a date or number range filter.')
            if filter_type == NUMBER_RANGE_FILTER:
                if not all([isinstance(v, int) or isinstance(v, float) for v in value]):
                    raise ValueError('Each entry of the filter value must be numeric when using a number range filter.')
            elif filter_type == DATE_RANGE_FILTER:
                if not all([date_format_checker(v) for v in value]):
                    raise ValueError('Please specify a start and an end date in "YYYY-MM-DD" format.')
            
            filter_params = {'filter_type': filter_type, 'start': value[0], 'end': value[1], 'not': negate}

        self.filters[field] = filter_params
        
    def get_push_permissions(self):
        return self.__allow_push_to_db

    def enable_push_to_db(self, warn=True):
        if warn:
            print('WARNING: this will enable pushing of pipeline output to connected databases.')
        self.__allow_push_to_db = True
    
    def disable_push_to_db(self):
        self.__allow_push_to_db = False

    def clear_filters(self):
        self.filters = {}

    def to_json(self):
        return {
            'job_name': self.__job_name,
            'pipelineID': self.pipeline_id,
            'allowPushToDB': self.__allow_push_to_db,
            'filters': self.filters
        }
