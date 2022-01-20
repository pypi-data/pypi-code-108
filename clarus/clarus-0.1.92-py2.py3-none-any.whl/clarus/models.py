from collections import Mapping, defaultdict, OrderedDict
from six import StringIO, iteritems

import clarus.api
import clarus.resource_util
import logging
import csv
import json

logger = logging.getLogger(__name__)

class ApiRequest(dict):
    def __init__(self, event):
        super(ApiRequest, self).__init__(event)
        
    def is_gui(self):
        if (self.get('__invocationsrc') == 'gui'):
            return True
        else:
            return False
        
    def is_api(self):
        return not(self.is_gui())
    
    def get_output_type(self):
        return self.get('__output')
    
    def read_selected_files(self, filetype=None):
        selected = self.get('__datafileselection')
        if (selected is not None):
            # __datafileselection is a dict of string keys (file type) to list of file names
            # we require a list of file names with matching file type
            # So start with a list comprehension that iterates through the map 
            # (this gives us a list of lists which we'll flatten in the final step):
            #      [vlist for k, vlist in iteritems(selected)]
            # Next add the condition on file type
            #      [vlist for k, vlist in iteritems(selected) if fileType is None or fileType == k ]
            # Finally flatten the list of lists:
            #      [v for k, vlist in iteritems(selected) if filetype is None or filetype == k for v in vlist]
            # ... except what we really want is a set of file names so change to a set comprehension {}
            filenames = {v for k, vlist in iteritems(selected) if filetype is None or filetype == k for v in vlist}
            return clarus.resource_util.read(filenames)
        else:
            return []
        
class ApiResponse(Mapping):
    httpresponse = None
    context = None
    _stats = None
    __str = None
    __parsed = None
    
    def __init__(self, httpresponse):
        self.httpresponse = httpresponse
    
    def set_context(self, context):
        self.context = context
        
    def __getitem__(self, name):
        return self._parsed().__getitem__(name)

    def __iter__(self):
        return self._parsed().__iter__()
    
    def __len__(self):
        return self._parsed().__len__()
    
    def __str__(self):
        #if (self.__str is None):
        #    try:
        #        self.__str = self.to_string();
        #    except Exception as e:
        #        self.__str = self.httpresponse.text;
        #        logger.debug('Exception in __str__: %s' % (e))
        return str(self._parsed());
    
    def _parsed(self):
        if (self.__parsed is None):
            self._parse()
        return self.__parsed
    
    def _parse(self):
        content_type = self.httpresponse.headers.get('Content-Type')
        
        if (content_type is not None):
            ct = content_type.lower()
            
            if ('text/csv' in ct):
                self._parse_csv()
            elif ('text/tsv' in ct):
                self._parse_tsv()
            elif ('application/json' in ct):
                self._parse_json()
            else:
                self._parse_unknown()
        else:
            self._parse_unknown()
    
    def _parse_csv(self):
        self.__parsed = ParsedCsvResult(self.httpresponse.text, ',', self.is_grid())
    
    def _parse_tsv(self):
        self.__parsed = ParsedCsvResult(self.httpresponse.text, '\t', self.is_grid())
        
    def _parse_json(self):
        self.__parsed = ParsedJsonResult(self.httpresponse.text)
    
    def _parse_unknown(self):
        self.__parsed = self.httpresponse.text
        
    @property
    def text(self):
        return self.httpresponse.text
    
    @property
    def results(self):
        return self._parsed().results
        
    @property
    def stats(self):
        if (self._stats is None):
            self._stats = clarus.api.getStats(self.httpresponse)
        return self._stats
    
    @property
    def total(self):
        if ("GridTotal" in self.stats):
            return float(self.stats.get("GridTotal"))
        return None
    
    @property
    def warnings(self):
        return clarus.api.getWarnings(self.httpresponse)
    
    @property
    def request_time(self):
        return clarus.api.getRequestTime(self.httpresponse)
    
    def pivot(self, rowAxis='Currency', colAxis='SubType', ccy='USD', view='Latest', output=None):
        httpresp = clarus.api.pivot(self.httpresponse, rowAxis, colAxis, ccy, view, output)
        if (httpresp.status_code!=200):
            raise ApiError(httpresp)
        else:
            return ApiResponse(httpresp);
        
    def transpose(self):
        httpresp = clarus.api.pivot(self.httpresponse, rowAxis='Transpose', colAxis='Transpose')
        if (httpresp.status_code!=200):
            raise ApiError(httpresp)
        else:
            return ApiResponse(httpresp);
        
    def filter(self, filter, output=None):
        httpresp = clarus.api.filter(self.httpresponse, filter, output)
        if (httpresp.status_code!=200):
            raise ApiError(httpresp)
        else:
            return ApiResponse(httpresp);
        
    def drilldown(self, row='Total', col='Total', view='Default', reportCcy=None, output=None):
        httpresp = clarus.api.drilldown(self.httpresponse, row, col, view, reportCcy, output)
        if (httpresp.status_code!=200):
            raise ApiError(httpresp)
        else:
            return ApiResponse(httpresp);
        
    def to_string(self):
        return clarus.api.toString(self.httpresponse);
    
    def is_grid(self):
        g = self.stats.get("IsGrid")
        return g == "Yes"
    
    def get_value(self, row, col):
        return self._parsed().get_value(row, col, self.is_grid())
    
    def get_float_value(self, row, col):
        return float(self.get_value(row, col))
    
    def get_row_headers(self):
        return self._parsed().get_row_headers(self.is_grid())
    
    def get_col_headers(self):
        return self._parsed().get_col_headers(self.is_grid())
    
    def get_result_title(self):
        return self._parsed().get_result_title(self.is_grid())
    
    def get_value_grid(self):
        return self._parsed().get_value_grid()
    
class ParsedJsonResult(dict):
    def __init__(self, jsontext):
        super(ParsedJsonResult, self).__init__(json.loads(jsontext))
    
    def __str__(self):
        return json.dumps(self, sort_keys=True, indent=2)
    
    @property
    def results(self):
        return self.get('results')
    
    def get_value(self, r, c, isGrid):
        if (not isGrid):
            raise AttributeError('This operation is only supported on grid-like results')
        
        if (r not in self.results):
            raise ValueError('No row {} found'.format(r))
        
        row = self.results.get(r)
        
        if (c not in row):
             raise ValueError('No column {} found'.format(c))
         
        return row.get(c)
        
    def get_row_headers(self, isGrid):
        if (not isGrid):
            raise AttributeError('This operation is only supported on grid-like results')
        
        return list(self.results.keys())
    
    def get_col_headers(self, isGrid):
        if (not isGrid):
            raise AttributeError('This operation is only supported on grid-like results')
        
        first_r = next(iter(self.results)) #first row header
        first_row = self.results.get(first_r)
        
        return list(first_row.keys())
    
    def get_result_title(self, isGrid):
        raise AttributeError('This operation is not supported on json results')
    
    def get_value_grid(self):
        raise AttributeError('This operation is not supported on json results')
    
class ParsedCsvResult(Mapping):
    valuegrid = None
    
    def __init__(self, csvtext, delimiter = ',', hasrowheaders = True):
        reader = csv.reader(StringIO(csvtext), delimiter=delimiter)
        colheaders = None
        gridtitle = None
        
        for r, row in enumerate(reader):
            if (r == 0):
                colheaders = row
                if (hasrowheaders):
                    #first column header is not a "real" column header so strip it out
                    self.valuegrid = ValueGrid(hasrowheaders, colheaders[1:])
                    self.valuegrid.title = colheaders[0]
                else:
                    self.valuegrid = ValueGrid(hasrowheaders, colheaders)
            else:
                if (len(row) > len(colheaders)):
                    raise ValueError('Malformed csv at line {}: actual column count {} exceeds expected count {}'.format(r, len(row), len(colheaders)))
                
                rowheader = None
                
                for c, col in enumerate(row):
                    if (hasrowheaders):
                        if (c == 0):
                            rowheader = col
                            continue
                        else:
                            colheader = colheaders[c]
                            self.valuegrid.set_value(rowheader, colheader, col)
                    else:
                        colheader = colheaders[c]
                        self.valuegrid.set_value(r-1, colheader, col)
        
    def __getitem__(self, name):
        return self.valuegrid.__getitem__(name)

    def __iter__(self):
        return self.valuegrid.__iter__()
    
    def __len__(self):
        return self.valuegrid.__len__()
    
    def __str__(self):
        return self.valuegrid.__str__()
    
    @property
    def results(self):
        return self.valuegrid.valdict
    
    def get_value(self, r, c, isGrid=None):
        return self.valuegrid.get_value(r,c)
    
    def get_col_headers(self, isGrid=None):
        return self.valuegrid.col_headers
        
    def get_row_headers(self, isGrid=None):
        return self.valuegrid.row_headers
    
    def get_result_title(self, isGrid=None):
        return self.valuegrid.title
    
    def get_value_grid(self):
        return self.valuegrid
    
class ApiError(Exception):
    httpresponse = None
    
    def __init__(self, httpresponse):
        super(ApiError, self).__init__('{} [code {}]'.format(httpresponse.text, httpresponse.status_code))
        
        self.httpresponse = httpresponse
        
class ValueGrid(Mapping):
    hasrowheaders = None #if true first column is treated as row headers
    colheaders = None
    valdict = None #dictionary of header -> list of values
    widthdict = None #dictionary of header -> max column width
    maxrow = 0
    _title = None
    
    def __init__(self, hasrowheaders = True, colheaders = []):
        self.hasrowheaders = hasrowheaders
        if (hasrowheaders):
            self.colheaders = ['']+colheaders
        else:
            self.colheaders = colheaders
        self.valdict = OrderedDict() #dictionary of header -> list of values
        self.widthdict = defaultdict(int) #dictionary of header -> max column width
        
        for header in self.colheaders:
            self.valdict[header] = []
            self.widthdict[header] = len(header)
    
    
    @property
    def title(self):
        return self._title
    
    @title.setter
    def title(self, t):
        self._title = t
        self.upd_width_dict('', t)
        
    def __getitem__(self, name):
        return self.valdict.__getitem__(name)

    def __iter__(self):
        return self.valdict.__iter__()
    
    def __len__(self):
        return self.valdict.__len__()
    
    def __str__(self):
        def pad(c, header, text):
            if text is None:
                text = ''
            if (c == 0):
                width = self.widthdict[header] + 1
                return '{x: <{fill}}'.format(x=text, fill=width)
            else:
                width = self.widthdict[header] + 4
                return '{x: >{fill}}'.format(x=text, fill=width)
        
        pp = StringIO()
        #write first line
        for c, header in enumerate(self.colheaders):
            if (self.hasrowheaders and c == 0 and self.title is not None):
                padded = pad(c, header, self.title)
            else:
                padded = pad(c, header, header)    
            
            pp.write(padded)
        pp.write('\n')
        
        for r in range(0, self.maxrow):
            for c, header in enumerate(self.colheaders):
                col = self.valdict[header][r]
                padded = pad(c, header, col)
                pp.write(padded)
            pp.write('\n')
            
        return pp.getvalue() 
        
    def get_value(self, r, c):
        #locate the column
        if (c not in self.valdict):
            if (isinstance(c,int)):
                if (self.hasrowheaders):
                    col = self.valdict.get(self.colheaders[c+1])
                else:
                    col = self.valdict.get(self.colheaders[c])
        else:
            col = self.valdict.get(c)
        
        #locate the index into the column 
        if (self.hasrowheaders):
            first_col = self.valdict.get(self.colheaders[0])
            
            if (r not in first_col):
                if (isinstance(r,int)):
                    row_idx = r
                else:
                    raise ValueError('No row {} found'.format(r))
            else:
                row_idx  = first_col.index(r)
        else:
            row_idx = r
            
        return col[row_idx]
    
    def upd_width_dict(self, c, v):
        if (c not in self.widthdict):
            self.widthdict[c] = len(str(v))
        else:
            self.widthdict[c] = max(self.widthdict[c], len(str(v)))
    
    def set_value(self, r, c, v):
        #locate the column
        if (c not in self.valdict):
            if (isinstance(c,int)):
                if (self.hasrowheaders):
                    col = self.valdict.get(self.colheaders[c+1])
                else:
                    col = self.valdict.get(self.colheaders[c])
            else:
                col = []
                self.valdict[c] = col
                self.colheaders.append(c)
                self.upd_width_dict(c, c)
        else:
            col = self.valdict.get(c)
        
        #locate the index into the column
        if (self.hasrowheaders):
            #if (len(self.colheaders) == 0):
            #    self.colheaders.append('')
            #    self.valdict[''] = []
            #    self.upd_width_dict(c, '')
                
            first_col = self.valdict.get(self.colheaders[0])
            
            if (r not in first_col):
                if (isinstance(r,int)):
                    row_idx = r
                    
                    while (len(first_col) <= row_idx):
                        first_col.append(None)
                        
                    first_col[row_idx] = r
                    self.upd_width_dict(self.colheaders[0], r)
                    #len
                else:
                    #raise ValueError('No row {} found'.format(r))
                    first_col.append(r)
                    self.upd_width_dict(self.colheaders[0], r)
                    
                    row_idx = len(first_col)-1
            else:
                row_idx  = first_col.index(r)
        else:
            if (not isinstance(r,int)):
                raise ValueError('Row must be an integer, found {}'.format(r))
            row_idx = r
            
        while (len(col) <= row_idx):
            col.append(None)
            
        col[row_idx] = v
        self.upd_width_dict(c, v)
        self.maxrow = max(self.maxrow, row_idx+1)
        
    @property
    def col_headers(self):
        if (self.hasrowheaders):
            return self.colheaders[1:]
        else:
            return self.colheaders
    
    @property    
    def row_headers(self):
        if (not self.hasrowheaders):
            raise AttributeError('Row headers not available')
        
        first_c = self.colheaders[0] #first column header
        first_col = self.valdict.get(first_c)
        
        return first_col