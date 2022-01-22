from .Grammer.SyntaxParser import LA_Grammer, LA_Parser
from lark import Lark, Transformer, v_args
import pandas as pd
import numpy as np
import itertools
import json
import ast

# class : LogAn
# The class is the solver of any logical expression for analysing its results
class LogAn():

    # constructor : __init__
    # gets the Input logical condition to be used and the Output(True/False) that is expected. 
    # Parameters : 
    #   arg1 - Condition (Logical condition to be solved)
    #   arg2 - Output (True/False) [optional]
    def __init__(self, Condition):

        # Initialisation of Lark Parser
        LA_Template = Lark(LA_Grammer, parser='lalr', transformer=LA_Parser())
        Logan_Parser = LA_Template.parse

        # Reduction of the Condition using LogAn Parser
        Stripped_Condition = ''.join(Condition.split('\n'))
        Cond_List, Map_Dict = Logan_Parser(Stripped_Condition)

        # Initialising Empty Dataframe
        df = pd.DataFrame();
        df['Condition'] = np.nan;
        df['True'] = np.nan;
        df['False'] = np.nan;

        # Filling the dataframe with each OR conditions and the corresponding ranges for expected Boolean results 
        for idx in range(len(Cond_List)):
            for out in [True, False]:
                Cond, Res = self.__getConditionAndResult(Cond_List[idx], Map_Dict, out);
                df.loc[idx, 'Condition'] = Cond;
                df.loc[idx, f'{out}'] = str(Res);

        self.__ElaborateResults = df;

        Results = {'True': {}, 'False': {}};
        for idx, row in df.iterrows():
            for res in ['True', 'False']:
                Result_Dict = ast.literal_eval(row[res])
                for key, val in Result_Dict.items():

                    Expanded_Range = []
                    for tup in val:
                        Expanded_Range += [*range(tup[0],tup[1])];

                    if(key not in Results[res].keys()):
                        Results[res][key] = set(Expanded_Range)
                    else:
                        if(res == 'True'):
                            Results[res][key] |= set(Expanded_Range)
                        else:
                            Results[res][key] &= set(Expanded_Range)

            self.__Results = {'True': {}, 'False': {}};
            for res in ['True', 'False']:
                for key, val in Results[res].items():
                    self.__Results[res][key] = sorted(list(Results[res][key]));

    # method : getConditionAndResult (Internal Function)
    # gets logical condition with only AND operator between and the corresponding mapdict for access to relational conditions. 
    # Parameters : 
    #   arg1 - Cond_List (logical condition with only AND operator in between )
    #   arg2 - Map_Dict (mapdict for access to relational conditions)
    # returns :
    #   Cond_String - condition which only have AND operator in between
    #   Output_Dict - Dict with all the choosen range results for each of the Cond_String dependencies
    def __getConditionAndResult(self, Cond_List, Map_Dict, Result):

        Dependency_List = [];
        Dependency_Dict = {};
        # Dependency and ranges finalization
        for val in Cond_List:
            atom = Map_Dict[val];
            Dependency_List.append(atom);
            if(atom[0] in Dependency_Dict.keys()):
                Dependency_Dict[atom[0]] += [*range(int(atom[2])-5, int(atom[2])+6)];
            else:
                Dependency_Dict[atom[0]] = [*range(int(atom[2])-5, int(atom[2])+6)];

        Cond_String = " and ".join([ " ".join(list(elem)) for elem in Dependency_List])

        # Narrowing down the possibility of values based on Output expected
        Output_Dict = {};
        for dep, ranges in Dependency_Dict.items():
            Input_Condition = " and ".join([ " ".join(list(elem)) for elem in Dependency_List if elem[0] == dep]);
            Input_Range = sorted(list(set(Dependency_Dict[dep])));
            Output_Dict[dep] = self.__NarrowDownRanges(dep, Input_Condition, Input_Range, Result);

        return Cond_String, Output_Dict;

    # method : __GetRanges (Internal Function)
    # gets a continuous.discrete list and returns list of tuples defining ranges. 
    # Parameters : 
    #   arg1 - Inplist 
    # returns :
    #   list of tuples with each of them defining a range
    def __GetRanges(self, Inplist):

        for a, b in itertools.groupby(enumerate(Inplist), lambda pair: pair[1] - pair[0]):
            
            b = list(b)
            yield b[0][1], b[-1][1]+1

    # method : __NarrowDownRanges (Internal Function)
    # gets a continuous.discrete list and returns list of tuples defining ranges. 
    # Parameters : 
    #   arg1 - Variable [dependency variable name]
    #   arg2 - Condition [condition as string]
    #   arg3 - Value [list of possibilities]
    #   arg4 - Output [True/False]
    # returns :
    #   list of tuples with each of them defining a range
    def __NarrowDownRanges(self, Variable, Condition, Value, Output):

        Res_List = [];
        for val in Value:
            vars()[f'{Variable}'] = val;  
            if(eval(Condition) == Output):
                Res_List.append(val);

        Ret_List = list(self.__GetRanges(Res_List));
        return Ret_List;

    # method : solution
    # returns :
    #   Results [ Dictionary with final results ]
    def solution(self, format = 'DICT'):

        if(format == 'JSON'):
            return json.dumps(self.__Results, sort_keys=True, indent=4);
        else:
            return self.__Results;
        

    # method : elaborate_solution
    # returns :
    #   self.__DF [ Dataframe with conditions seperated as row based on OR operator and their corresponding results ]
    def elaborate_solution(self, format = 'DATAFRAME'):

        if(format == 'MARKDOWN'):
            return self.__ElaborateResults.to_markdown();
        else:
            return self.__ElaborateResults;

# 
# (see LogExAnCodeFlow.png) for the code flow
#
# Visit @Palani-SN(github profile) or send messages to
# psn396@gmail.com.
#