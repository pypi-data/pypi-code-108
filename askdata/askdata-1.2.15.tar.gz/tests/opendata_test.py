from askdata import opendata


if __name__ == "__main__":
    nl = "wine consumption by countries"
    response = opendata.search_data(sentence=nl)
    extraction = opendata.extract_specific_result(response=response, request="top1_df", show=True)
    print(extraction)
