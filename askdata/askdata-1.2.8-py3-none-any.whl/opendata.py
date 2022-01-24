import pandas as pd
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import logging
import requests

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 200)
pd.set_option('display.max_rows', 10)


def search_data(sentence, language="en", show_header=False, dataset_score_dict=None, boost_columns=False,
                boost_name_score=False, use_domains=True, store_df=True):
    if language != "en" and language != "it":
        print("Please use 'en' for english or 'it' for italian.")
        dict_response = {}
        return dict_response

    if sentence != "":
        headers = {
            "Content-Type": "application/json"
        }

        data = {
            "nl": sentence,
            "lang": language,
            "dataset_score_dict": dataset_score_dict,
            "store_df": store_df,
            "use_domains": use_domains,
            "boost_columns": boost_columns,
            "boost_name_score": boost_name_score
        }

        s = requests.Session()
        s.keep_alive = False
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))

        url = "https://api-dev.askdata.com/opendata/spacy"

        r = s.post(url=url, headers=headers, json=data)
        r.raise_for_status()

        try:
            dict_response = r.json()

            if show_header and store_df:
                # Print header
                i = 1
                j = 0
                for el in dict_response['dataset_rank']["first_place"]["dataset_list"]:
                    score = dict_response['dataset_rank']["first_place"]["scoring"]
                    name = el['dataset']
                    df = pd.DataFrame().from_dict(dict_response['df_list'][j])
                    print("#------------------------------------------------------------------#")
                    print("Dataset " + name + " ranked as #" + str(i) + " with score: " + str(score) + ".")
                    print()
                    print(df.head())
                    print("#------------------------------------------------------------------#")
                    print()
                    j += 1
                # i += 1

            return dict_response
        except Exception as e:
            logging.error(str(e))
    else:
        print("Input sentence is empty!")
        dict_response = {}
        return dict_response


def extract_specific_result(response, request, show=True):
    possible_request = ["first_place", "second_place", "third_place", "top_places", "all_datasets", "header", "joins",
                        "top1_df"]
    explained_possible_request = ["'first_place' - to obtain info of rank#1 datasets",
                                  "'second_place' - to obtain info of rank#2 datasets",
                                  "'third_place' - to obtain info of rank#3 datasets",
                                  "'top_places' - to obtain info of top ranked#1-3 datasets",
                                  "'all_datasets' - to obtain info of all ranked datasets",
                                  "'header' - to print rank#1 datasets headers",
                                  "'joins' - to obtain the possible joins between all ranked datasets",
                                  "'top1_df' - to obtain the top-1 dataset as a DataFrame"]

    if request in possible_request:

        # Print first three places
        if "first_place" in request or "second_place" in request or "third_place" in request:

            if request == "first_place":
                dataset_infos = response["dataset_rank"]['first_place']
                i = 1
            elif request == "second_place":
                dataset_infos = response["dataset_rank"]['second_place']
                i = 2
            else:
                dataset_infos = response["dataset_rank"]['third_place']
                i = 3

            if show:
                print("#----------------------------------------------------------------------------------------#")
                print("Rank#" + str(i) + " datasets")
                print()
                # Print first place datasets name
                for el in dataset_infos["dataset_list"]:
                    print("#-----------------------------#")
                    print("Dataset info:")
                    print()
                    print("Dataset name: " + el['dataset'])  # name
                    print()
                    print("Detected columns: " + str(el['important_columns']))  # detected columns
                    print()
                    print("All columns: " + str(el["columns"]))  # all columns
                    print()
                    # Print place scoring
                    print("Score: " + str(dataset_infos["scoring"]))
                    print("#-----------------------------#")
                    print()
                print("#----------------------------------------------------------------------------------------#")

            return dataset_infos

        # Print all top places
        elif request == "top_places":
            if show:
                for i in range(1, 4):

                    print("#----------------------------------------------------------------------------------------#")
                    print("Rank#" + str(i) + " datasets: ")
                    print()

                    if i == 1:
                        dataset_infos = response["dataset_rank"]["first_place"]
                    elif i == 2:
                        dataset_infos = response["dataset_rank"]["second_place"]
                    else:
                        dataset_infos = response["dataset_rank"]["third_place"]

                    # Print first place datasets name
                    for el in dataset_infos["dataset_list"]:
                        print("#-----------------------------#")
                        print("Dataset info:")
                        print()
                        print("Dataset name: " + el['dataset'])  # name
                        print()
                        print("Detected columns: " + str(el['important_columns']))  # detected columns
                        print()
                        print("All columns: " + str(el["columns"]))  # all columns
                        print()
                        # Print place scoring
                        print("Score: " + str(dataset_infos["scoring"]))
                        print("#-----------------------------#")
                        print()
                print("#----------------------------------------------------------------------------------------#")
            return response["dataset_rank"]

        elif request == "header":
            try:
                i = 1
                j = 0
                for el in response['dataset_rank']["first_place"]["dataset_list"]:
                    score = response['dataset_rank']["first_place"]["scoring"]
                    name = el['dataset']
                    df = pd.DataFrame().from_dict(response['df_list'][j])
                    if show:
                        print("#----------------------------------------------------------------------------------------#")
                        print("Dataset " + name + " ranked as #" + str(i) + " with score: " + str(score) + ".")
                        print()
                        print(df.head())
                        print("#----------------------------------------------------------------------------------------#")
                        print()
                    j += 1
                    return df.head()
            except:
                print("There is no DataFrame in the input structure. Use 'store_df' when you get the structure.")
                return None

        elif request == "all_datasets":

            # Print first, second third and other datasets places names
            all_datasets = response["dataset_list"]

            if show:
                print("#----------------------------------------------------------------------------------------#")
                print()
                print("List of all main datasets detected:")
                print()

                for el in all_datasets:
                    print(el['dataset'])  # name

                print("#----------------------------------------------------------------------------------------#")
                print()

            return all_datasets

        elif request == "joins":
            # Print the possible joins between datasets detected
            joins = response["join_dict"]

            if show:
                print("#----------------------------------------------------------------------------------------#")
                print()
                print("List of all joins between datasets detected:")
                print()
                for column, datasets in joins.items():
                    print("Column: " + column)
                    print("Datasets: " + str(datasets))
                    print()
                print("#----------------------------------------------------------------------------------------#")
                print()
            return joins

        elif request == "top1_df":
            try:
                df = pd.DataFrame().from_dict(response['df_list'][0])
                return df
            except:
                print("There is no DataFrame in the input structure. Use 'store_df' when you get the structure.")
                return pd.DataFrame()
    else:
        print("Please use a request from the following:")
        for el in explained_possible_request:
            print(el)
        return None
