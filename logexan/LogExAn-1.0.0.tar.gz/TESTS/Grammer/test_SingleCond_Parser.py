from LogExAn.Grammer.SyntaxParser import LA_Grammer, LA_Parser
from lark import Lark, Transformer, v_args
import pytest
import json

from conftest import DEBUG

CondList = [ 

         " Var_new_9 == 12 ",
         " ( Var_new_9 == 12 ) "

           ];

CondsvsFiles = [ tuple([CondList[i], f'Parser_SingleCondition{i+1}.json']) for i in range(len(CondList))]

Logan_Parser = None;
Cond_Map = None;
Ref_File = None;

@pytest.fixture(autouse = True, scope="function")
def fix_function():

    global Logan_Parser;
    global Cond_Map;
    global Ref_File;

    LA_Template = Lark(LA_Grammer, parser='lalr', transformer=LA_Parser())
    Logan_Parser = LA_Template.parse
    
    yield
    
    Act_String = json.dumps(Cond_Map, sort_keys=True, indent=4);

    if(DEBUG):
        OutputFile = open(f'res_files/{Ref_File}', "w");
        OutputFile.write(Act_String)
        OutputFile.close();

    file = open(f'ref_files/{Ref_File}', 'r');
    Ref_String = file.read();
    print(Act_String)

    assert(Ref_String == Act_String)

##########################################################################################################
## Single condition based tests for Parser 
##########################################################################################################

@pytest.mark.parametrize("Condition, Filename", CondsvsFiles)
def test_SingleCondition(Condition, Filename):

    global Logan_Parser;
    global Cond_Map;
    global Ref_File;

    Cond = Condition;
    print(Cond)
    Cond_Map = Logan_Parser(Cond)
    Ref_File = Filename;
