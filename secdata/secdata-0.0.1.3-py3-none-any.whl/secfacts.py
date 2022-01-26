# -*- coding: utf-8 -*-
"""
Created on Tue Jan 26 21:23:25 2022

A Class able to fetch:
    
    1. All available CIKs (Central Index Keys) for each company
       reporting to the SEC (Securities Exchange Commission)
    
    2. All facts reported to the SEC for a number of different CIKs
       in a tidy DataFrame format

@author: Konstantinos Voulgaropoulos
@contact: voulkon93@gmail.com

"""

#Load necessary libraries
import requests
import json
import pandas as pd
import os

        
class SecDownloader:
    
    """
    A Class present throughout the whole session\n
    Stores user's credentials and communicates with SEC's api on demand
    
    Parameters
    ----------
    user_email : str
        Your email. SEC needs it to identify who is querying the data
    
    """
    
    
    def __init__(self, user_email):
        
        #Headers will be needed throughout the whole session, in case we need repetitive downloads
        self.headers = {'User-Agent': user_email}
        
    
    def fetch_facts(self, ciks):
        
        """
        Returns all Sec facts tidy in a Pandas DataFrame
        
        Parameters
        ----------
        ciks : list
            integers, the Central Index Keys of wanted companies
        
        Returns
        -------
        Pandas DataFrame of All facts for All Companies asked for
        
        Examples
        --------
        
        >>> SecFacts(user_email = my_email).fetch_facts([320193, 789019]).head(1)
        
                  end          val  ... Underlying_Principles  start
        0  2009-06-27  895816758.0  ...                   dei    NaN
        
        """
        
        def handle_response(url, headers):
            """
            
            Requests the link from the SEC's api. 
            
            In case of error, it prints it out
            
            """
            
            #Request the url's content
            response = requests.get(url, headers=headers)
            
            #If things turn out bad
            if not response.ok:
                #Inform user about it 
                #(an Error Class is actually needed here)
                
                print("Unsuccessful API call")
                print("Status Code" ,response.status_code)
            
            #If things go well 
            else:
                #Read it as json
                response_content = json.loads(response.text)
        
                return response_content


        def facts_to_df(response_content, extract_which = "us-gaap"):
                
                """
                Receives a dictionary, part of the json response, and returns a dataframe of all facts included in it
                
                Parameters
                ----------
                response_content : dict
                
                    A dictionary containing 2 lists:
                        
                        1. dei - Document and Entity Information
                        
                            such as the Shareholding regime of a company 
                            
                            e.g. number of Shares Outstanding of Entity Common Stock
                            
                        2. us-gaap or ifrs-full or whichever accounting principles each company follows
                            
                            containing the figures each company came up with for each reporting period
                            
                            e.g. Income (Loss) from Continuing Operations before Income Taxes, Domestic 
                            
                                                            or 
                                                            
                                 Amount of income (expense) related to nonoperating activities, classified as other.
                            
                Returns
                -------
                A DataFrame containing all these information
                
                """
                #Isolate wanted sub-dictionary
                wanted_part_of_response = response_content["facts"][extract_which]
                
                all_facts_dfs = []
                
                #for each fact
                for k, key in enumerate(wanted_part_of_response.keys()):
                    
                    #Assign the sub-dictionary to a variable for easy reference
                    temp_dictionary = wanted_part_of_response[key]
                    
                    description_of_fact = temp_dictionary["description"]
                    
                    label_of_fact = temp_dictionary["label"]
                    
                    unit_of_measurement = list(temp_dictionary["units"])[0]
                    
                    dict_of_each_distinct_fact = temp_dictionary["units"]
                    
                    #Iterate to gather each distinct value reported
                    for s, sub_dict in enumerate(list(dict_of_each_distinct_fact.values())[0]):
                        
                        specific_fact_df = pd.DataFrame(sub_dict, index= [0])
                        
                        if s == 0:
                            
                            facts_df = specific_fact_df
                        
                        else:
                            facts_df = facts_df.append(specific_fact_df)
                        
                        
                    facts_df["Description"] = description_of_fact
                    facts_df["Label"] = label_of_fact    
                    facts_df["Unit_of_Measurement"] = unit_of_measurement  
                    
                    all_facts_dfs.append(facts_df)
                    
                    
                all_facts_df = pd.concat(all_facts_dfs)
                
                all_facts_df["cik"] = response_content["cik"]
                all_facts_df["Entity"] = response_content["entityName"]
                
                all_facts_df["Underlying_Principles"] =  extract_which
                
                return all_facts_df
        
        #Convert to string and pad left with 0's until it reaches length of 10
        ciks = [str(cik).zfill(10) for cik in ciks]
        
        #Create respective url for each cik
        urls = ["https://data.sec.gov/api/xbrl/companyfacts/CIK{}.json".format(c) for c in ciks]
        
        #Soon-to-be-DataFrame
        final_list = []
        #For each url we came up with
        for u, url in enumerate(urls):
            
            #Attempt to get the url's content 
            #(some error handling needed here)
            response_content = handle_response(url, self.headers)
            
            #Which keys are included each time. It could be us-gaap, ifrs-full, etc.
            specific_keys_of_response_content = response_content["facts"].keys()
            
            # #For each key finally included
            # for sk,specific_key in enumerate(specific_keys_of_response_content):
                
            #     #Fetch temporarily a dataframe
            #     specific_cik_df_ = facts_to_df(response_content, extract_which = specific_key)
                
            #     if sk == 0:
                    
            #         specific_cik_df = specific_cik_df_
                
            #     else:
                    
            #         specific_cik_df = specific_cik_df.append(specific_cik_df_)
            
            specific_cik_df  = pd.concat([facts_to_df(response_content, extract_which = specific_key)  for sk,specific_key in enumerate(specific_keys_of_response_content) ])
            
            #Include in the soon-to-be DataFrame list
            final_list.append(specific_cik_df)
        
               #List converted to DataFrame
        return pd.concat(final_list)


    def fetch_Sec_companies_info(self, file_if_info_already_downloaded = "companiesinfo.csv"):
        
        """
        Checks whether a downloaded table of company info already exists in the current working directory
        If not, it downloads it
        
        Company info included CIK, ticker and name for each company reporting to the SEC
        
        e.g. 320193,AAPL,Apple Inc. 
        
        """
        
        def sec_companies_info(self):
            
            """
            
            Downloads information for companies reporting to the SEC
            
            """
            
            #Where the company info resides
            companies_info_url = "https://www.sec.gov/files/company_tickers.json"
            #Request info
            response = requests.get(companies_info_url, headers = self.headers)
            #Convert to json
            json_response = response.json()
            
                   #Convert to DataFrame
            return pd.concat([pd.DataFrame(json_response[key], index = [0]) for key in json_response])
        
        #Best guess - how a file downloaded from previous session could have been named
        #file_if_info_already_downloaded = './companiesinfo.csv' 
        
        #If it already exists
        if os.path.isfile(file_if_info_already_downloaded):
            #Load it
            self.sec_companies_info = pd.read_csv(file_if_info_already_downloaded)
        
        #Otherwise, if not existing
        else:
            #Call the downloader
            self.sec_companies_info = sec_companies_info(self)

        

