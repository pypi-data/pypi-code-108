"""
 - This module parsing and generating recording output and provide useful data options
 - compatible with jmeter version 5.3 output records files
 - compatible for mapproxy
"""
import csv
import os
import datetime
from mc_automation_tools import init_logger
from mc_automation_tools import common
import logging
logger = logging.getLogger('jmeter_records_parsers')

url = "/home/ronenk1/dev/apache-jmeter-5.3/tests/summary_wmts_openshift.csv"# todo - delete after debug
url_wms = "/home/ronenk1/dev/apache-jmeter-5.3/tests/wms-res.jtl" # todo - delete after debug
url_wmts_jtl = "/home/ronenk1/dev/apache-jmeter-5.3/tests/map_proxy_tests_jmeter/stress/wmts/27-04-21-07:02:27/wmts-res.jtl"

def generate_tiles_csv(orig_file_url, mode="jmeter_csv"):
    """
    This method get original csv records output file and return parced tiles params file/
    :param orig_file_url: directory to csv file
    :return: csv with z,x,y tiles list
    """

    urls_list = []
    if not os.path.exists(orig_file_url):
        raise FileNotFoundError("File not exists! try another directory path to provide")
    logger.info('Read and parse file %s', str(os.path.basename(orig_file_url)))

    with open(orig_file_url) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                logger.info(f'Column names are {", ".join(row)}')
                line_count += 1
            else:
                if mode=='jmeter_csv':
                    urls_list.append(row[0])
                    logger.info("reads line of : %s", row[0])
                    line_count += 1
                elif mode=='jtl':
                    urls_list.append(row[13])
                    logger.info("reads line of : %s", row[13])
                    line_count += 1
                else:
                    raise Exception('Unknown parsing mode, choose jtl or jmeter_csv')
        logger.info(f'Processed {line_count} lines.')

    return urls_list


def generate_wmts_csv(url_list):
    dict_list = []
    for url in url_list:
        args = url.split('/')[2:]
        if 'wmts' in args and len(args) >=7:
            try:
                # res_dict = {'base_url': args[0],
                #                   'protocol': args[1],
                #                   'layer': args[2],
                #                   'tile_matrix_set': args[3],
                #                   'tile_matrix': int(args[4]),
                #                   'tile_cols': int(args[5]),
                #                   'tile_rows': int(args[6].split('.')[0])}
                res_dict = {'tile_matrix': int(args[-3]),
                            'tile_cols': int(args[-2]),
                            'tile_rows': int(args[-1].split('.')[0])}
                dict_list.append(res_dict)
            except Exception as e:
                print(str(e))
                continue

    return dict_list


def generate_wms_csv(url_list):
    dict_list = []
    for url in url_list:
        substr = "SERVICE=WMS"
        if substr in url:
            url = url.split("service?")[1]
            arg_list = url.split("&")
            arg_dict = {arg.split("=")[0]:arg.split("=")[1] for arg in arg_list}
            dict_list.append(arg_dict)
    return dict_list




def write_dict_to_csv(dict_list, output_dir="/tmp",protocol="wms"):
    # file_url = common.combine_url(output_dir, datetime.datetime.now().strftime("%H_%M_%S"),'wmts_csv.csv')
    file_url = common.combine_url(output_dir, ".".join([protocol, 'csv']))
    if protocol=="wmts":
        with open(file_url, mode="w") as wmts_file:
            wmts_writer = csv.writer(wmts_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for request in dict_list:
                request_list = [request['tile_matrix'], request['tile_cols'], request['tile_rows']]
                wmts_writer.writerow(request_list)
    elif protocol=="wms":
        with open(file_url, mode="w") as wms_file:
            wmts_writer = csv.writer(wms_file, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for request in dict_list:
                # request_list = [request['LAYERS'],
                #                 request['FORMAT'],
                #                 request['SRS'],
                #                 request['EXCEPTIONS'],
                #                 request['TRANSPARENT'],
                #                 request['SERVICE'],
                #                 request['VERSION'],
                #                 request['REQUEST'],
                #                 request['STYLES'],
                #                 request['BBOX'],
                #                 request['WIDTH'],
                #                 request['HEIGHT']]
                request_list = [request['BBOX'],
                                request['WIDTH'],
                                request['HEIGHT']]
                wmts_writer.writerow(request_list)
    else:
        raise Exception('Unknown parsing mode, choose wms or wmts')


list_url = generate_tiles_csv(url_wmts_jtl, "jtl")


def generate_wmts_jtl(list_url):
    dict_list = []
    for url in list_url:
        if 'http://map-raster.apps.v0h0bdx6.eastus.aroapp.io/wmts/full_il/newGrids/' in url:
            tmp = url.split('.')[-2]
            tmp = tmp.split('/')[-3:]
            res_dict = {'tile_matrix': int(tmp[0]),
                        'tile_cols': int(tmp[1]),
                        'tile_rows': int(tmp[2])}
            dict_list.append(res_dict)

    return dict_list


result = generate_wmts_jtl(list_url)
# result = generate_wms_csv(list_url)
# result = generate_wmts_csv(list_url)
result = write_dict_to_csv(result, "/tmp", "wmts")
