import pandas as pd
import warnings
import re

import humailib.utils as hu
import humailib.hasher as hh
from humailib.cloud_tools import GoogleCloudStorage, GoogleBigQuery

class GenerateCustomerID:
    
    def __init__(self):
        self.cid_offset = 0
        
        # personifier_to_cid:
        # {
        #  'Personifier' : str(customer_id), 
        #   ...
        # }
        self.personifier_to_cid = {}

        # Each person can have one or more different personifiers, that need
        # the same Customer_ID
        # person_to_personifiers=
        # {
        #  'Person' : [personifier0, personifier1, ...], 
        #   ...
        # }
        self.person_to_personifiers = {}
        
        # Each personifier could refer to one or more different persons, for example
        # if a person entered their first name slightly differently in two occasions.
        # personifiers_to_person=
        # {
        #  'Personifier' : [person0, person1, ...], 
        #   ...
        # }
        self.personifier_to_persons = {}
        
    def _walk_personifiers(self, personifier, people=[], personifiers=[]):
        
        for person in self.personifier_to_persons[personifier]:
            if person not in people:
                people.append(person)
                for m in self.person_to_personifiers[person]:
                    if m not in personifiers:
                        personifiers.append(m)
                        self._walk_personifiers(m, people=people, personifiers=personifiers)
                
        return people, personifiers
                
        
    def add(
        self, 
        df, 
        personifier_col='Email',
        cols_to_match=[],
        verbose=False
    ):   
        """
        Generate unique Customer IDs for people, based on personifier and
        person information from columns.
        
        Each personifier gets a unique Customer ID, initially. And then personifiers
        which are different but have matching person information are merged, and get 
        assigned the same Customer ID.
        
        """
        print("[GenerateCustomerID::add] transforming columns...")
        df = df[[personifier_col]+[c for c in cols_to_match if c is not personifier_col]].copy()
        
        df.loc[:,personifier_col] = df[personifier_col].str.strip().str.upper()
        
        def get_person(x, cols_to_match):
            person = [
                re.sub(r'[^\w]', '', x[c]) \
                  .replace('_','') \
                  .upper() for c in cols_to_match
            ]
            if person is None or len(person) == 0:
                return ''
            
            for p in person:
                if p == '':
                    return ''
                
            return '_'.join(person)
        
        # We assume that [cols_to_match] is the minimum information required to
        # uniquely identify and merge a person, so if any of this information is 
        # missing, mark it as an empty person, so it does not get merged.
        df.loc[:,'Person'] = df.apply(lambda x: get_person(x, cols_to_match), axis=1)
        
        for i,personifier in enumerate(df[personifier_col].unique()):
            self.personifier_to_cid[personifier] = self.personifier_to_cid.get(personifier, 'S'+str(i+self.cid_offset))
        
        personifier_in_common = {}
        
        print("[GenerateCustomerID::add] adding new people to table...")
        
        n_new_people = 0
        n_new_personifiers = 0
        ii = 0
        nn = len(df)
        for index, row in df.iterrows():

            if ii % 10000 == 0:
                print("  {:,}/{:,} rows ({:.2f}%)".format(
                    ii,
                    nn,
                    100.0*float(ii)/nn
                ))

            person = row['Person']
            
            # Don't attempt to merge empty persons
            if person != '': 
                personifier = row[personifier_col]

                if personifier not in self.personifier_to_persons:
                    n_new_personifiers = 1 + n_new_personifiers
                    self.personifier_to_persons[ personifier ] = [ person ]
                elif person not in self.personifier_to_persons[personifier]:
                    self.personifier_to_persons[ personifier ].append(person)

                if person not in self.person_to_personifiers:
                    n_new_people = 1 + n_new_people
                    self.person_to_personifiers[ person ] = [ personifier ]
                elif personifier not in self.person_to_personifiers[person]:
                    self.person_to_personifiers[ person ].append(personifier)
                
            ii = 1 + ii
                

        print("[GenerateCustomerID::add] merging ids...")
        n_personifiers = 0
        n_merged = 0
        nn = len(self.personifier_to_persons)
        for personifier in self.personifier_to_persons.keys():
            # Gather all people and personifiers that can be 'reached' by shared personifiers
            people, personifiers = self._walk_personifiers(personifier, people=[], personifiers=[])
            
            if n_personifiers % 5000 == 0:
                print("  {:,}/{:,} personifiers ({:.2f}%)".format(
                    n_personifiers,
                    nn,
                    100.0*float(n_personifiers)/nn
                ))
            
            #if 'MATERS' in personifier:
            #    print("------======------")
            #    print(personifier)
            #    print("walked people: {}".format(people))
            #    print("walked personifiers: {}".format(personifiers))
            #    for mm in personifiers:
            #        print("cid {}".format(self.personifier_to_cid[mm]))
        
            cid = self.personifier_to_cid[personifier]
            # Determine oldest Customer_ID
            for m in personifiers:
                contestant = self.personifier_to_cid.get(m,'')
                if contestant != '' and (int(contestant[1:]) < int(cid[1:])):
                    cid = contestant
            
            # Set all these people's personifiers to oldest Customer_ID
            for m in personifiers:
                if self.personifier_to_cid.get(m,'') != cid:
                    n_merged = 1 + n_merged
                    if verbose:# or 'MATERS' in personifier:
                        print("{} '{}' and '{}' belong to same person: {} (old cid='{}', new cid='{}')".format(
                            n_merged,
                            m,
                            personifier,
                            self.personifier_to_persons[m][0],
                            self.personifier_to_cid[m],
                            cid
                        ))                    
                    self.personifier_to_cid[m] = cid
                    
            n_personifiers = 1 + n_personifiers
            
        cids = [value for _,value in self.personifier_to_cid.items()]
        
        print("====================")
        print("[GenerateCustomerID::generate_from_transactions] New people: {:,}, new personifiers (='{}') {:,}".format(n_new_people, personifier_col, n_new_personifiers))
        print("[GenerateCustomerID::generate_from_transactions] Unique personifiers (='{}') with assigned Customer IDs: {:,}, unique Customer IDs {:,}".format(personifier_col, len(self.personifier_to_cid),len(set(cids))))
        print("[GenerateCustomerID::generate_from_transactions] Total personifiers (='{}') in merge-able person table: {:,}, of which merged (but weren't before): {:,}\n".format(personifier_col, n_personifiers, n_merged))
                
        return self.personifier_to_cid
    
    
    def get_ids(self, df, personifier_col='Email'):
    
        """
        """
        return df[personifier_col].apply(lambda x: self.personifier_to_cid.get(x.strip().upper(),''))
    
    
    def add_and_get_ids(
        self, 
        df, 
        personifier_col,
        cols_to_match,
        verbose=False
    ):
        
        """
        """
        self.add(df, personifier_col=personifier_col, cols_to_match=cols_to_match, verbose=verbose)
        return self.get_ids(df, personifier_col)
    
    
    def to_dataframe(self):
        
        """
        """
        if len(self.personifier_to_cid) == 0 or len(self.person_to_personifiers) == 0:
            return None
        
        data = []
        for personifier,cid in self.personifier_to_cid.items():
            if personifier in self.personifier_to_persons:
                for person in self.personifier_to_persons[personifier]:
                    data.append((cid, personifier, person))
            else:
                data.append((cid, personifier, ''))
                
        df = pd.DataFrame(data, columns=['Customer_ID','Personifier','Person'])
        hu.columns_as_str(df, columns=['Customer_ID','Personifier','Person'])

        df.drop_duplicates(inplace=True)
                    
        return df
    
    
    def upload_and_replace(self, dataset_table_name, gbq):
        
        """
        """
        if len(self.personifier_to_cid) == 0 or len(self.person_to_personifiers) == 0:
            return False
        
        if gbq is None:
            gbq = GoogleBigQuery()
            
        df = self.to_dataframe()

        hh.encrypt_columns(df, columns=['Personifier','Person'])
        gbq.upload_and_replace_table(df, dataset_table_name)
        
        return True
        
        
    def load(self, dataset_table_name, gbq, flush_cache=True):
        
        """
        """
        self.__init__()
        
        if gbq is None:
            gbq = GoogleBigQuery()
            
        df_customers = hu.load_table(
            gbq, 
            dataset_table_name, 
            table_type='customer_ids', 
            flush_cache=flush_cache
        )
        if df_customers is None:
            print("[GenerateCustomerID::load] Failed to load customers table '{}'".format(dataset_table_name))
            return False
        
        personifier_col = 'Personifier'
        if 'Email' in df_customers:
            ## Old table format.
            personifier_col = 'Email'
        
        hh.decrypt_columns(df_customers, columns=[personifier_col,'Person'])
        
        self.cid_offset = df_customers.Customer_ID.str[1:].astype(int).max() + 1
        self.personifier_to_cid = {
            personifier:cid for (cid,personifier) in zip(
                df_customers.Customer_ID.to_numpy(),
                df_customers[personifier_col].to_numpy()
            )
        }
        
        self.personifier_to_persons = {}
        self.person_to_personifiers = {}
        for index, row in df_customers.iterrows():

            person = row['Person']
            personifier = row[personifier_col]

            if person != '': 
                                    
                if personifier not in self.personifier_to_persons:
                    self.personifier_to_persons[ personifier ] = [ person ]
                elif person not in self.personifier_to_persons[personifier]:
                    self.personifier_to_persons[ personifier ].append(person)

                if person not in self.person_to_personifiers:
                    self.person_to_personifiers[ person ] = [ personifier ]
                elif personifier not in self.person_to_personifiers[person]:
                    self.person_to_personifiers[ person ].append(personifier)
            
        return True
        
        