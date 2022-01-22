from lark import Lark, Transformer, v_args
from lark.tree import Tree
from lark.lexer import Token
import copy
import itertools

# Grammer for Recursive parser (C type Condition Syntax)

LA_Grammer = """
        ?start: molecule                            -> getstatement

        !molecule: "(" molecule+ ")"                -> getmolecule
                 |  atom* LOGIC*

        ?atom: NAME RELATION VALUE                  -> getatom
             | "(" NAME RELATION VALUE ")"          -> getatom

        NAME: CNAME
        RELATION: ">"|"<"|">="|"<="|"=="|"!="
        LOGIC: "&&"|"||"
        VALUE: SIGNED_NUMBER

        %import common.CNAME
        %import common.SIGNED_NUMBER
        %import common.WS_INLINE
        %ignore WS_INLINE 

    """

# class : LA_Parser
# The class will be used as transformer for the LA_Grammer
@v_args(inline=True)    
class LA_Parser(Transformer):

    # constructor : __init__
    def __init__(self):
        self.__ID = [64, 96];
        self.__LeafDict = {};

    # method : __getUniqueVar (Internal function)
    # returns a unique key between Aa and Zz. ( 26 x 26 ) unique keys possible
    # Returns : 
    #   Str [ anything between Aa and Zz] 
    def __getUniqueVar(self):

        if(96 < self.__ID[1] < 122):
            self.__ID[1] = self.__ID[1]+1
        else:
            self.__ID[0] = self.__ID[0]+1;
            self.__ID[1] = 97
        RetStr = chr(self.__ID[0])+chr(self.__ID[1]);
        return RetStr;

    # method : getatom (Parser function)
    # adds the atom with elements name, relation, value to LeafDict and returns a unique key for that entry.
    # Parameters : 
    #   arg1 - name [CNAME]
    #   arg2 - relation [">"|"<"|">="|"<="|"=="|"!="]
    #   arg3 - value [SIGNED_NUMBER]
    # Returns : 
    #   Str [ unique key for relational reduction ]
    def getatom(self, name, relation, value):

        dict_val = tuple([name.value, relation.value, value.value])
        if(dict_val in self.__LeafDict.values()):
            dict_key = list(self.__LeafDict.keys())[list(self.__LeafDict.values()).index(dict_val)]
        else:
            dict_key = self.__getUniqueVar();
            self.__LeafDict[dict_key] = tuple([name.value, relation.value, value.value])
        return dict_key;

    # method : __OR_Op (Internal function)
    # returns the Logical OR of two args.
    # Parameters : 
    #   arg1 - type of List/str
    #   arg2 - type of List/str
    # Returns : 
    #   list [ Logical OR Expansion of the args ]
    def __OR_Op(self, arg1, arg2):

        if( isinstance(arg1, list) and isinstance(arg2, list) ):
            Retval = arg1+arg2;
        elif( isinstance(arg1, list) and isinstance(arg2, str) ):
            Retval = arg1+[[arg2]];
        elif( isinstance(arg1, str) and isinstance(arg2, list) ):
            Retval = [[arg1]]+arg2;
        else:
            Retval = [[arg1],[arg2]];

        return Retval

    # method : __AND_Op (Internal function)
    # returns the Logical AND of two args.
    # Parameters : 
    #   arg1 - type of List/str
    #   arg2 - type of List/str
    # Returns : 
    #   list [ Logical AND Expansion of the args ]
    def __AND_Op(self, arg1, arg2):

        if( isinstance(arg1, list) and isinstance(arg2, list) ):
            CalcVal = [ list(itertools.chain.from_iterable(val)) for val in list( itertools.product(arg1, arg2 ) ) ] # issue persists : to be modified 
        elif( isinstance(arg1, list) and isinstance(arg2, str) ):
            CalcVal = [ list(itertools.chain.from_iterable(val)) for val in list( itertools.product(arg1, [[arg2]] ) ) ] # issue persists : to be modified
        elif( isinstance(arg1, str) and isinstance(arg2, list) ):
            CalcVal = [ list(itertools.chain.from_iterable(val)) for val in list( itertools.product([[arg1]], arg2 ) ) ] # issue persists : to be modified
        else:
            CalcVal = [[arg1,arg2]];

        CalcVal = [ sorted(list(set(val))) for val in CalcVal ]
        RetVal = [];
        for val in CalcVal:
            if(val not in RetVal):
                RetVal.append(val);

        return RetVal

    # method : getmolecule (Parser function)
    # get list of tree/token and is responsible for recursive logical reduction based on the logical operators.
    # Parameters : 
    #   *args - list of tree/tokens 
    # Returns : 
    #   Tree of type molecule 
    def getmolecule(self, *args,**kwargs):

        Conditions = [];
        Operators = [];
        
        # finding indices of tree type molecule
        molecule_indices = [i for i in range(len(args)) if isinstance(args[i], Tree) and args[i].data == "molecule"]
        
        # Extracting Conditions And Operators from the list
        for i in range(len(args)):
            if(i in molecule_indices):
                for j in range(len(args[i].children)):
                    if(isinstance(args[i].children[j], Token)):
                        Operators.append(args[i].children[j].value)
                    else:
                        Conditions.append(args[i].children[j])

        # Syntactical Checking of Braces
        Operator = list(set(Operators));
        if(len(Operator) == 1):

            # logical reduction for OR
            if(Operator[0] == '||'):
                RetVal = Conditions[0];
                for cond in Conditions[1:]:
                    RetVal = self.__OR_Op(RetVal, cond);
            # logical reduction for AND
            if(Operator[0] == '&&'):
                RetVal = Conditions[0];
                for cond in Conditions[1:]:
                    RetVal = self.__AND_Op(RetVal, cond);
        else:
            assert 0, " Only One operator to be present within a single () "

        return Tree('molecule', [RetVal]);

    # method : getstatement (Parser function)
    # get a tree of type molecule for returnable abstraction of Solved List and Solved Dict.
    # Parameters : 
    #   molecule - Tree of type molecule 
    # Returns : 
    #   Tuple (Solved_List, Solved_Dict)
    def getstatement(self, molecule):

        Solved_List = [[molecule.children[0]]] if isinstance(molecule.children[0], str) else molecule.children[0];
        Solved_Dict = self.__LeafDict;
        return [ tuple(val) for val in Solved_List ], Solved_Dict;

# 
# (see LogExAnCodeFlow.png) for the code flow
#
# Visit @Palani-SN(github profile) or send messages to
# psn396@gmail.com.
#