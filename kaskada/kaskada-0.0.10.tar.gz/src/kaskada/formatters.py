"""
Copyright (C) 2022 Kaskada Inc. All rights reserved.

This package cannot be used, copied or distributed without the express
written permission of Kaskada Inc.

For licensing inquiries, please contact us at info@kaskada.com.
"""

from datetime import datetime
import inspect
import io
import re
import sys

def get_datetime(pb2_timestamp):
    return datetime.fromtimestamp(pb2_timestamp.seconds + pb2_timestamp.nanos/1e9)

def get_properties(obj):
    results = {}
    for propName in dir(obj):
        if re.search(r"^[a-z]", propName) is None:
            continue
        propVal = getattr(obj,propName)
        propType = type(propVal)
        if propType in (int, float, bool):
            results[propName] = propVal
        elif propType is str:
            if propVal != '':
                results[propName] = propVal
        elif propType.__name__ == "RepeatedCompositeContainer" and propType.__module__ == "google.protobuf.pyext._message":
            if len(propVal) > 0:
                results[propName] = [get_properties(subObj) for subObj in propVal]
        elif propType.__name__ == "Timestamp" and propType.__module__  == "google.protobuf.timestamp_pb2":
            results[propName] = get_datetime(propVal).isoformat()
        elif propType.__module__.startswith("pandas."):
            results[propName] = propVal
        else:
            results[propName] = get_properties(propVal)
    return results

# safely recursively gets an item from a dict, otherwise returns the default value
def get_item(obj, keys, default = ""):
    while (len(keys) > 0):
        key = keys.pop(0)
        if key in obj:
            obj = obj[key]
        else:
            return default
    return obj


def html_table_style():
    return """
    <style>
        table.kda_table {
            border: 1px solid grey !important;
            border-collapse: collapse !important;
            border-spacing: 0 !important;
            font-size: 14px !important;
            margin-bottom: 6px !important;
        }
        table.kda_table table {
            margin-bottom: 0 !important;
        }
        .kda_table td, .kda_table th {
            border: 1px solid grey !important;
            border-collapse: collapse !important;
            padding: 6px !important;
            text-align: left !important;
            vertical-align: top !imporant;
        }
        .kda_table tr {
            background-color: inherit !important;
        }
    </style>
    """

def html_open_table():
    return '<table class="kda_table">'

def html_close_table():
    return '</table>'

def html_obj_table_row(key, value):
    if value is None or value == '':
        return ''
    return f'<tr><td><b>{key}</b></td><td><pre>{value}</pre></td></tr>'

def html_table_row(key, value):
    return f'<tr><td><b>{key}</b></td><td>{value}</td></tr>'

def html_request_details(obj, props):
    if 'request_details' in props:
        nested_table = html_open_table() + html_obj_table_rows(getattr(obj, 'request_details'), props.pop('request_details')) + html_close_table()
        return html_open_table() + html_obj_table_row('request_details', nested_table) + html_close_table()
    return ''
    

def html_obj_table_rows(obj, props):
    obj_type = type(obj).__name__.lower()

    #try to pop off obj_id and obj_name first
    obj_id_key = f'{obj_type}_id'
    props.pop(obj_id_key) if obj_id_key in props else None
    obj_name_key = f'{obj_type}_name'
    obj_name = props.pop(obj_name_key) if obj_name_key in props else None

    rows = ""
    #build html table rows
    if obj_name is not None:
        rows += html_obj_table_row(obj_name_key, obj_name)
    for key in props:
        rows += html_obj_table_row(key, props[key])
    return rows

def html_obj_id_row(index, obj, props):
    obj_type = type(obj).__name__.lower()
    obj_name_key = f'{obj_type}_name'
    obj_name = get_item(props, [obj_name_key])
    
    return f'<tr><td><pre>{index}</pre></td><td><pre>{obj_name}</pre></td></tr>'

def html_obj(obj):
    props = get_properties(obj)

    # pull off standard items on request & response objects
    request_details = html_request_details(obj, props)

    html = html_table_style() + html_open_table()
    # if only the primary obj is left, nest it under its key
    if len(props) == 1 and type(props[list(props)[0]]) not in (int, float, bool, str):
        primary_obj_key = list(props)[0]
        nested_table = html_open_table() + html_obj_table_rows(getattr(obj, primary_obj_key), props[primary_obj_key]) + html_close_table()
        html += html_table_row(primary_obj_key, nested_table)
    else:
        html += html_obj_table_rows(obj, props)

    return html + html_close_table() + request_details

def html_list_resp_id_name(list_resp):
    html = html_table_style() + html_open_table()
    # skip id for now since not queryable
    # html += "<tr><th>index</th><th>id</th><th>name</th></tr>"
    html += "<tr><th>index</th><th>name</th></tr>"

    list_type = type(list_resp)
    # check to see if passed resp is just a proto list
    if list_type.__name__ == "RepeatedCompositeContainer" and list_type.__module__ == "google.protobuf.pyext._message":
        for i in range(len(list_resp)):
            html += html_obj_id_row(i, list_resp[i], get_properties(list_resp[i]))
        return html + html_close_table()
    
    # otherwise assume it is a proto list response object
    props = get_properties(list_resp)
    
    # pull off standard items on response objects
    request_details = html_request_details(list_resp, props)

    done = False
    # check if only nested list remains
    if len(props) == 1:
        list_key = list(props)[0]
        list_value = getattr(list_resp, list_key)
        list_props = props[list_key]
        list_type = type(list_value)

        if list_type.__name__ == "RepeatedCompositeContainer" and list_type.__module__ == "google.protobuf.pyext._message":
            for i in range(len(list_value)):
                html += html_obj_id_row(f'{list_key}.{i}', list_value[i], list_props[i])
            done = True

    if not done:
        html += html_obj_table_rows(list_resp, props)  

    return html + html_close_table() + request_details 
    
def html_query_response(obj):
    props = get_properties(obj)
    html = html_table_style() + html_open_table()
    html += html_obj_table_row('data_token_id', get_item(props, ['data_token_id']))
    html += html_obj_table_row('next_resume_token', get_item(props, ['next_resume_token']))
    html += html_obj_table_row('parquet.path', get_item(props, ['parquet', 'path']))
    html += html_obj_table_row('redis_bulk.path', get_item(props, ['redis_bulk', 'path']))     
    return html + html_close_table() + html_request_details(obj, props) 

def html_fenlmagic_query_result(obj):
    props = get_properties(obj)
    html = html_table_style() + html_open_table()

    # include the query
    html += html_obj_table_row('query', get_item(props, ['query']))
    
    # make an href for the results_url
    result_url = get_item(props, ['result_url'])
    result_url_without_query_string = result_url.split("?")[0]
    href = f'<a href="{result_url}"> {result_url_without_query_string}</a>'
    html += html_table_row('result_url', href)
    
    # get info about the dataframe to show instead of the dataframe
    df = get_item(props, ['dataframe'])
    buf = io.StringIO()
    df.info(verbose=False,buf=buf)
    info = buf.getvalue().replace("<class 'pandas.core.frame.DataFrame'>\n","")
    html += html_obj_table_row('dataframe', info)

    return html + html_close_table()

def try_init():
    try:
        # the following command will throw an exception in non-iPython environments
        html_formatter = get_ipython().display_formatter.formatters['text/html']

        # dynamically assign formatters to kaskada protobuf types
        mods = sys.modules.copy()
        for key in mods:
            if key.endswith("_grpc"):
                continue
            if key.startswith("kaskada."):
                for cls in inspect.getmembers(mods[key], inspect.isclass):
                    classname = f'{cls[1].__module__}.{cls[1].__name__}'
                    if classname == 'kaskada.api.v1alpha.compute_pb2.QueryResponse':
                        html_formatter.for_type(classname, html_query_response) # kda_table formatter for QueryResponse
                    elif 'List' in classname and 'Response' in classname:
                        html_formatter.for_type(classname, html_list_resp_id_name) # generic formatter for List responses
                    else:
                        html_formatter.for_type(classname, html_obj) # generic formatter for all other proto types
        
        # the following types don't normally exist when the library first loads
        html_formatter.for_type("kaskada.materialization.MaterializationView", html_obj)
        html_formatter.for_type("kaskada.materialization.RedisAIDestination", html_obj)
        html_formatter.for_type("fenlmagic.QueryResult", html_fenlmagic_query_result)

        # additional non-kaskada types we want to assign formatters to
        html_formatter.for_type("google.protobuf.pyext._message.RepeatedCompositeContainer", html_list_resp_id_name)

    except:
        pass
