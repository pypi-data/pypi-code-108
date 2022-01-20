import argparse
from catswalk.scraping.webdriver import CWWebDriver
from catswalk.scraping.types.type_webdriver import *
from captool.order import *
import json
import csv
import os

def main():
    parser = argparse.ArgumentParser(description='cp tool')
    parser.add_argument('order', help='order')
    parser.add_argument('conf', help='conf')
    parser.add_argument('dataset', help='dataset')
    parser.add_argument('-d', '--debug', action='store_true')
    args = parser.parse_args()
    print(args)

    conf_tool_common = f"{args.conf}/common/browser.json"
    conf_tool_specific = f"{args.conf}/order/{args.order}/browser.json"
    conf_url = f"{args.dataset}/input/{args.order}.csv"
    conf_order = f"{args.conf}/order/{args.order}/command.od"
    conf_lark = f"{args.conf}/common/grammar.lark"
    print(f"conf_tool_common: {conf_tool_common}, conf_tool_specific: {conf_tool_specific},conf_url: {conf_url},conf_order: {conf_order},conf_lark: {conf_lark}")
    
    # common setting
    with open(conf_tool_common, "r") as f:
        j = json.load(f)
        binary_location = j["binary_location"]
        executable_path = j["executable_path"]
        execution_env = EXECUTION_ENV.str_to_enum(j["execution_env"])
        output_path = j["output_path"]
        debug = j["debug"]
        if debug:
            print("debug mode")

    # order specific setting
    with open(conf_tool_specific, "r") as f:
        j = json.load(f)
        device = DEVICE.str_to_enum(j["device"])

    # url_path_list
    with open(conf_url, "r") as f:
        reader = csv.reader(f)
        input_list =  [row for row in reader]
    print(input_list)

    if args.debug:
        request = None
        path_list = [execute(request=request, order_name=args.order, grammar_path=conf_lark, order_path=conf_order, url=i[0],output_path=output_path, filename=i[1]) for i in input_list]
    else:
        request = CWWebDriver(binary_location=binary_location, executable_path=executable_path, execution_env=execution_env,  device=device, debug=debug)
        #request = None
        path_list = [execute(request=request, order_name=args.order, grammar_path=conf_lark, order_path=conf_order, url=i[0],output_path=output_path, filename=i[1]) for i in input_list]
        request.close()
        print(path_list)

    #request.close
    # tool setting

if __name__ == "__main__":
    main()