from LogExAn.LogicalAnalyser import LogAn
import pytest
import ast
import json
from conftest import DEBUG

CondList = [ 

         "( Var_new_1 > 5 && Var_new_2 > 5 )",
         "( Var_new_1 > 5 && Var_new_2 < 5 )",
         "( Var_new_1 > 5 && Var_new_2 >= 5 )",
         "( Var_new_1 > 5 && Var_new_2 <= 5 )",
         "( Var_new_1 > 5 && Var_new_2 == 5 )",
         "( Var_new_1 > 5 && Var_new_2 != 5 )",

         "( Var_new_1 < 5 && Var_new_2 > 5 )",
         "( Var_new_1 < 5 && Var_new_2 < 5 )",
         "( Var_new_1 < 5 && Var_new_2 >= 5 )",
         "( Var_new_1 < 5 && Var_new_2 <= 5 )",
         "( Var_new_1 < 5 && Var_new_2 == 5 )",
         "( Var_new_1 < 5 && Var_new_2 != 5 )",

         "( Var_new_1 >= 5 && Var_new_2 > 5 )",
         "( Var_new_1 >= 5 && Var_new_2 < 5 )",
         "( Var_new_1 >= 5 && Var_new_2 >= 5 )",
         "( Var_new_1 >= 5 && Var_new_2 <= 5 )",
         "( Var_new_1 >= 5 && Var_new_2 == 5 )",
         "( Var_new_1 >= 5 && Var_new_2 != 5 )",

         "( Var_new_1 <= 5 && Var_new_2 > 5 )",
         "( Var_new_1 <= 5 && Var_new_2 < 5 )",
         "( Var_new_1 <= 5 && Var_new_2 >= 5 )",
         "( Var_new_1 <= 5 && Var_new_2 <= 5 )",
         "( Var_new_1 <= 5 && Var_new_2 == 5 )",
         "( Var_new_1 <= 5 && Var_new_2 != 5 )",

         "( Var_new_1 == 5 && Var_new_2 > 5 )",
         "( Var_new_1 == 5 && Var_new_2 < 5 )",
         "( Var_new_1 == 5 && Var_new_2 >= 5 )",
         "( Var_new_1 == 5 && Var_new_2 <= 5 )",
         "( Var_new_1 == 5 && Var_new_2 == 5 )",
         "( Var_new_1 == 5 && Var_new_2 != 5 )",

         "( Var_new_1 != 5 && Var_new_2 > 5 )",
         "( Var_new_1 != 5 && Var_new_2 < 5 )",
         "( Var_new_1 != 5 && Var_new_2 >= 5 )",
         "( Var_new_1 != 5 && Var_new_2 <= 5 )",
         "( Var_new_1 != 5 && Var_new_2 == 5 )",
         "( Var_new_1 != 5 && Var_new_2 != 5 )",

         "( Var_new_1 > 5 || Var_new_2 > 5 )",
         "( Var_new_1 > 5 || Var_new_2 < 5 )",
         "( Var_new_1 > 5 || Var_new_2 >= 5 )",
         "( Var_new_1 > 5 || Var_new_2 <= 5 )",
         "( Var_new_1 > 5 || Var_new_2 == 5 )",
         "( Var_new_1 > 5 || Var_new_2 != 5 )",

         "( Var_new_1 < 5 || Var_new_2 > 5 )",
         "( Var_new_1 < 5 || Var_new_2 < 5 )",
         "( Var_new_1 < 5 || Var_new_2 >= 5 )",
         "( Var_new_1 < 5 || Var_new_2 <= 5 )",
         "( Var_new_1 < 5 || Var_new_2 == 5 )",
         "( Var_new_1 < 5 || Var_new_2 != 5 )",

         "( Var_new_1 >= 5 || Var_new_2 > 5 )",
         "( Var_new_1 >= 5 || Var_new_2 < 5 )",
         "( Var_new_1 >= 5 || Var_new_2 >= 5 )",
         "( Var_new_1 >= 5 || Var_new_2 <= 5 )",
         "( Var_new_1 >= 5 || Var_new_2 == 5 )",
         "( Var_new_1 >= 5 || Var_new_2 != 5 )",

         "( Var_new_1 <= 5 || Var_new_2 > 5 )",
         "( Var_new_1 <= 5 || Var_new_2 < 5 )",
         "( Var_new_1 <= 5 || Var_new_2 >= 5 )",
         "( Var_new_1 <= 5 || Var_new_2 <= 5 )",
         "( Var_new_1 <= 5 || Var_new_2 == 5 )",
         "( Var_new_1 <= 5 || Var_new_2 != 5 )",

         "( Var_new_1 == 5 || Var_new_2 > 5 )",
         "( Var_new_1 == 5 || Var_new_2 < 5 )",
         "( Var_new_1 == 5 || Var_new_2 >= 5 )",
         "( Var_new_1 == 5 || Var_new_2 <= 5 )",
         "( Var_new_1 == 5 || Var_new_2 == 5 )",
         "( Var_new_1 == 5 || Var_new_2 != 5 )",

         "( Var_new_1 != 5 || Var_new_2 > 5 )",
         "( Var_new_1 != 5 || Var_new_2 < 5 )",
         "( Var_new_1 != 5 || Var_new_2 >= 5 )",
         "( Var_new_1 != 5 || Var_new_2 <= 5 )",
         "( Var_new_1 != 5 || Var_new_2 == 5 )",
         "( Var_new_1 != 5 || Var_new_2 != 5 )"
           ];

CondsvsFiles = [ tuple([CondList[i], f'Solver_DualCondition{i+1}']) for i in range(len(CondList))]

Cond_In = None;
LA = None;
Ref_File = None;

@pytest.fixture(autouse = True, scope="function")
def fix_function():

    global Cond_In;
    global LA;
    global Ref_File;
    
    yield
    
    Act_String = f""" 
{Cond_In}

{LA.solution('JSON')}

{LA.elaborate_solution('MARKDOWN')}""";

    if(DEBUG):
        OutputFile = open(f'res_files/{Ref_File}', "w");
        OutputFile.write(Act_String)
        OutputFile.close();
        
    file = open(f'ref_files/{Ref_File}', 'r');
    Ref_String = file.read();
    print(Act_String)

    assert(Ref_String == Act_String)

##########################################################################################################
## Dual condition based tests for Solver 
##########################################################################################################

@pytest.mark.parametrize("Condition, Filename", CondsvsFiles)
def test_DualCondition(Condition, Filename):

    global Cond_In;
    global LA;
    global Ref_File;

    Cond_In = Condition;
    print(Cond_In)

    LA = LogAn(Cond_In);

    Ref_File = f'{Filename}.log';
