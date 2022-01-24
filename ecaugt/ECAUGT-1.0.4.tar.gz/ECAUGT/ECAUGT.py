# coding=UTF-8
import pandas as pd
import numpy as np
import tablestore
import os
import json
import re
import multiprocessing

__author__ = 'Yixin Chen & Haiyang Bian & Minsheng Hao'

# global variables 
df = pd.DataFrame()
client_global = None
_tablename = None

# [0621]load tree relationship file
cpath = os.path.realpath(__file__)
df_tree = pd.read_csv(cpath.split(os.path.basename(__file__))[0]+"uhafOBO_0621.csv")

####### Preprocessing functions #######

# priority value in the logical computation
def _priority(x):
    if x=='!':
        return 0
    elif x=='&&':
        return 1
    elif x =='||':
        return 2
    else:
        return 3


# standardize the condition string
def _standardize_seq(seq):
    # delete spaces in the string
    seq = seq.strip(" ")
    seq = re.sub('\s*!\s*','!',seq)
    seq = re.sub('\s*\(\s*','(',seq)
    seq = re.sub('\s*\)\s*',')',seq)
    seq = re.sub('\s*&&\s*','&&',seq)
    seq = re.sub('\s*\|\|\s*','||',seq)   
    seq = re.sub('\s*==\s*','==',seq)
    seq = re.sub('\s*<>\s*','<>',seq)
    seq = re.sub('\s*>\s*','>',seq)
    seq = re.sub('\s*<\s*','<',seq)
    seq = re.sub('\s*>=\s*','>=',seq)
    seq = re.sub('\s*<=\s*','<=',seq)
    return seq


# split the condition string with || && ! ( )
def _split_seq(forward_seq):
    forward_seq = np.array(re.split('(\(|\)|\&&|\|\||!)',forward_seq))
    forward_seq = forward_seq[forward_seq!='']
    updated_seq = []
    i = 0
    while i <len(forward_seq):
        if forward_seq[i]=='(':
            if i+2<len(forward_seq) and forward_seq[i+2] == ')':
                is_expression = False
                for symbol in ['==','>=','<=','<','>']:
                    is_expression = is_expression or (forward_seq[i+1].find(symbol)!=-1)
                if not is_expression:
                    if i + 3 <len(forward_seq):
                        updated_seq[-1] = (forward_seq[i-1]+forward_seq[i]+forward_seq[i+1]+forward_seq[i+2]+forward_seq[i+3]) 
                        i = i + 4
                        continue
                    else:
                        updated_seq[-1] = (forward_seq[i-1]+forward_seq[i]+forward_seq[i+1]+forward_seq[i+2]) 
                        i = i + 3
                        continue
                else:
                    updated_seq.append(forward_seq[i])
                    updated_seq.append(forward_seq[i+1])
                    updated_seq.append(forward_seq[i+2])
                    i = i + 3
                    continue
            else:
                updated_seq.append(forward_seq[i])
        else:
            updated_seq.append(forward_seq[i])
        i = i+1
    return updated_seq



# transform a forward logical expression into an afterward one
def _forward2afterward(forward_seq):
    afterward_seq = []
    stack = []    
    for word in forward_seq:
        if word == '(':
            stack.append(word)
        elif word == ')':
            while(len(stack)!=0 and stack[-1]!='('):
                afterward_seq.append(stack.pop())
            if len(stack)!= 0:
                stack.pop()
            elif stack_top=='(':
                print("Bracket mismatch!")
                break
        elif word in ['||','&&','!']:
            while(len(stack)!=0 and _priority(stack[-1])<=_priority(word)):
                afterward_seq.append(stack.pop())
            stack.append(word)
        else:
            afterward_seq.append(word)
    while(len(stack)!=0):
        afterward_seq.append(stack.pop()) 
    return afterward_seq


# transform an string into OTS BoolQuery to set searching condition in metadata
def _seq2boolquery(metadata_condition,include_children = True, exlude_Unclassified = False):
    if metadata_condition == "":
        metadata_condition = "organ<>a" # all cells
    
    if(exlude_Unclassified):
        metadata_condition = "(" + metadata_condition + ") && (cell_type <> Unclassified)"
        
    ## [0601] transform uHAF_name to hcad_name
    metadata_condition = metadata_condition.replace("uHAF_name","hcad_name")
    # standardize string
    forward_seq = _standardize_seq(metadata_condition)
    # divide string into logical computation units
    forward_seq = _split_seq(forward_seq)
    # transform it into an afterward logical expression
    afterward_seq = _forward2afterward(forward_seq)
    # transform the lofgical expression into OTS conditions
    stack = []
    for word in afterward_seq:
        if word not in ['||','&&','!']:
            if "==" in word:
                w_pair = word.split("==")
                # [0621]
                if w_pair[0] == "cell_type"  and include_children:
                    # find all childs in the table
                    stack_father = []
                    stack_child = []
                    stack_father.append("T cell")
                    while not len(stack_father)==0:
                        father = stack_father.pop()
                        stack_child.append(father)
                        childs = df_tree['child'][df_tree['father'] == father]
                        for c in childs:
                            stack_father.append(c)

                    all_childs = np.unique(stack_child)
                    child_queries = []
                    for c in all_childs:
                        child_queries.append(tablestore.TermQuery("cell_type",c))
                    stack.append(tablestore.BoolQuery(should_queries=child_queries,minimum_should_match=1))
                else:
                    stack.append(tablestore.TermQuery(w_pair[0], w_pair[1]))
            elif "<>" in word:
                w_pair = word.split("<>")
                stack.append(tablestore.BoolQuery(must_not_queries=[tablestore.TermQuery(w_pair[0], w_pair[1])]))
        elif word =='!':
            stack.append(tablestore.BoolQuery(must_not_queries=[stack.pop()]))
        elif word =="&&":
            stack.append(tablestore.BoolQuery(must_queries=[stack.pop(),stack.pop()]))
        else:
            stack.append(tablestore.BoolQuery(should_queries=[stack.pop(),stack.pop()],minimum_should_match=1))
    return stack.pop()


# transform an string into OTS BoolQuery to set searching condition in genes
def seq2filter(gene_condition):
    
    """transform a gene-condition string into a OTS column condition

    This function will analyze the logical expression string of the gene condition for cell searching and generate a combined column condition of OTS database.

    Parameters
    ----------
    gene_condition: str
        It is a structured string which is a combination of several logical expressions.

        Each logical expression should be in the following forms:
            gene_name1 == value1,                          here '==' means equal

            gene_name2 <> value2,                          here '<>' means unequal
            
            gene_name3 > value3,                          here '>' means larger than 
            
            gene_name4 < value4,                          here '<' means smaller than
            
            gene_name5 >= value5,                          here '>=' means not smaller than
            
            gene_name6 <= value6,                          here '<=' means not larger than

        Three symbols are used for logical operation between expressions:
            logical_expression1 && logical_expression2,     here '&&' means AND operation

            logical_expression1 || logical_expression2,     here '||' means OR operation

            ！ logical_expression1,                         here '!' means not NOT operation

        Brackets are allowed and the priorities of the logical operations are as common. The metadata condition string is also robust to the space character.

        Here are some examples of legal condition strings:
            '(CD3D > 2 && CD3E >= 0.1) || (PTPRC <= 3 && CD8A >= 0.01)'



    Returns
    -------
    tablestore.CompositeColumnCondition
        the column condition for tablestore to seach cells
    """
    
    
    # standardize string
    forward_seq = _standardize_seq(gene_condition)
    # divide string into logical computation units
    forward_seq = np.array(re.split('(\(|\)|\&&|\|\||!)',forward_seq))
    forward_seq = forward_seq[forward_seq!='']
    # transform it into an afterward logical expression
    afterward_seq = _forward2afterward(forward_seq)
    # transform the lofgical expression into OTS conditions
    stack = []
    for word in afterward_seq:
        if word not in ['||','&&','!']:
            if "==" in word:
                w_pair = word.split("==")
                stack.append(tablestore.SingleColumnCondition(w_pair[0], float(w_pair[1]),tablestore.ComparatorType.EQUAL,pass_if_missing=False))
            elif "<>" in word:
                w_pair = word.split("<>")
                stack.append(tablestore.SingleColumnCondition(w_pair[0], float(w_pair[1]),tablestore.ComparatorType.NOT_EQUAL,pass_if_missing=False))
            elif ">=" in word:
                w_pair = word.split(">=")
                stack.append(tablestore.SingleColumnCondition(w_pair[0], float(w_pair[1]),tablestore.ComparatorType.GREATER_EQUAL,pass_if_missing=False))
            elif "<=" in word:
                w_pair = word.split("<=")
                stack.append(tablestore.SingleColumnCondition(w_pair[0], float(w_pair[1]),tablestore.ComparatorType.LESS_EQUAL,pass_if_missing=False))
            elif ">" in word:
                w_pair = word.split(">")
                stack.append(tablestore.SingleColumnCondition(w_pair[0], float(w_pair[1]),tablestore.ComparatorType.GREATER_THAN,pass_if_missing=False))
            elif "<" in word:
                w_pair = word.split("<")
                stack.append(tablestore.SingleColumnCondition(w_pair[0], float(w_pair[1]),tablestore.ComparatorType.LESS_THAN,pass_if_missing=False))
        elif word =='!':
            f = tablestore.CompositeColumnCondition(tablestore.LogicalOperator.NOT)
            f.add_sub_condition(stack.pop())
            stack.append(f)
        elif word =="&&":
            f = tablestore.CompositeColumnCondition(tablestore.LogicalOperator.AND)
            f.add_sub_condition(stack.pop())
            f.add_sub_condition(stack.pop())
            stack.append(f)
        else:
            f = tablestore.CompositeColumnCondition(tablestore.LogicalOperator.OR)
            f.add_sub_condition(stack.pop())
            f.add_sub_condition(stack.pop())
            stack.append(f)
    return stack.pop()


def check_data(genenum_chk=True):
    """check if the loaded data satisfied the standardization in metadata and gene numbers

    This function checkes if the loaded data satisfied the following standards:

        1. If the column number of the matrix equals to 43896 (43878 genes and 18 metadata columns)

        2. If the name of the metadata columns is correct

        3. If donors' genders are presented in correct form ('Female', 'Male', 'NA')

        4. If the cids in the matrix are correct based on the user_id and current quota value

    Parameters
    ----------
    genenum_chk: bool
        genenum_chk is the parameter deciding if to do the check on the column number of the dataset. The default value is true and it can be set False when using on other species' datasets.
    

    Returns
    -------
    bool
        if the dataset pass the check
    """

    # check the gene number
    if genenum_chk and df.shape[1] != 43896:
        print("Gene number error.")
        return False
    
    # check if the metadata columns are completed
    ## 【0601】 add uHAF_name column
    ##if sum([x in df.columns for x in ['user_id', 'study_id', 'cell_id', 'organ', 'region', 'subregion','seq_tech', 'sample_status', 'donor_id', 'donor_gender', 'donor_age', 'original_name', 'cl_name', 'hcad_name', 'tissue_type', 'cell_type', 'marker_gene','cid']]) != 18:
    if sum([x in df.columns for x in ['user_id', 'study_id', 'cell_id', 'organ', 'region', 'subregion','seq_tech', 'sample_status', 'donor_id', 'donor_gender', 'donor_age', 'original_name', 'cl_name', 'hcad_name', 'uHAF_name', 'tissue_type', 'cell_type', 'marker_gene','cid']]) != 19:
        print("Metadata names error.")
        return False
    
    # check if the donor_gender column is standardized
    if set(np.unique(df['donor_gender'])).union({'Female', 'Male', 'NA'}) != {'Female', 'Male', 'NA'}:
        print("donor_gender error.")
        return False

    # check if the cids in the matrix are correct based on the user_id and current quota value
    quota = df['user_id'][0]
    if min(df['cid'])<quota*1000000 or max(df['cid'])>quota*1000000 + 999999:
        print("cid error.")
        return False
    
    print("Dataset pass the check.")
    return True


# transform a row(cell) in the matrix into a set of packages(Rows) to be uploaded to the OTS server
def _Cell2Row(sample):
    # build the attribute columns part
    attribute_columns = []
    for i in range(sample.shape[0]):
        if sample.index[i]!= "cid":
            if sample.index[i] == 'user_id':
                attribute_columns.append((sample.index[i],int(sample[i])))
            elif isinstance(sample[i],np.int64):
                attribute_columns.append((sample.index[i],float(sample[i])))
            else:
                attribute_columns.append((sample.index[i],sample[i]))
    
    # build the primary_key part 
    primary_key = [('cid',int(sample['cid']))]
    
    # the maxium number of attribute columns in each writing operation is 1024, so we split a row into blocks
    row_blocks = []
    for i in range(len(attribute_columns)//1024+1): # the maxium number of attribute columns in each writing operation is 1024
        if i==0:
            row_blocks.append(tablestore.Row(primary_key,attribute_columns[i*1024:min(i*1024+1024,len(attribute_columns))]))
        else:
            row_blocks.append(tablestore.Row(primary_key,{'PUT':attribute_columns[i*1024:min(i*1024+1024,len(attribute_columns))]}))
    return row_blocks



#######Operation funcntions communicating with the OTS server#######

def Setup_Client(endpoint, access_key_public, access_key_secret, instance_name, table_name):
    """Sets up an OTSClient connected to the OTS server
    
    This function builds an OTSClient variable based on the parameters and connects to the corresponding server. If successed, this function will print the discription of the selected table on the server.
    This function should be run as the first step of any usage of our package. And the Client is only need to be setup once.
    
    Parameters
    ----------
    endpoint: str
        The address of the OTS server on the public network
    access_key_public: str
        The public key of a user accessed to the server
    access_key_secret: str
        The cryptographic key of the given public key
    instance_name: str
        The name of the instance which the table belongs to
    table_name: str
        The name of the selected table

    Returns
    -------
    int 
        0 means success to connected to the server while -1 means failure.
        
    """
    global client_global
    global _tablename
    _tablename = table_name
    client_global =  tablestore.OTSClient(endpoint, access_key_public, access_key_secret, instance_name, logger_name = "table_store.log", retry_policy = tablestore.WriteRetryPolicy())
    try:
        describe_response = client_global.describe_table(_tablename)
        print("Connected to the server, find the table.")
        print (table_name)
        print ('TableName: %s' % describe_response.table_meta.table_name)
        print ('PrimaryKey: %s' % describe_response.table_meta.schema_of_primary_key)
        print ('Reserved read throughput: %s' % describe_response.reserved_throughput_details.capacity_unit.read)
        print ('Reserved write throughput: %s' % describe_response.reserved_throughput_details.capacity_unit.write)
        print ('Last increase throughput time: %s' % describe_response.reserved_throughput_details.last_increase_time)
        print ('Last decrease throughput time: %s' % describe_response.reserved_throughput_details.last_decrease_time)
        print ('table options\'s time to live: %s' % describe_response.table_options.time_to_live)
        print ('table options\'s max version: %s' % describe_response.table_options.max_version)
        print ('table options\'s max_time_deviation: %s' % describe_response.table_options.max_time_deviation)
        return 0
    except Exception as e:
        print(e)
        return -1


def _insert_row(row):
    """upload a cell to the table on the OTS server.
    
    This function uploads packaged information of a cell onto the OTS server. The packaged information should be a list of tablestore::Row variables. An exception will be risen with the corresponding upload error.
    
    This function should not be directly used by the users but will be called by the other functions.
    
    
    Parameters
    ----------
    row: list
        The packaged information in a list of tablestore::Row variables which contains all columns of informations of a cell. Because of the gene number, all columns cannot be store in one tablestore::Row structure. Hence we sparate the information of a cell into several groups and stored in several tablestore::Row variables.


    Returns
    -------
    0
        Success to upload the row to the OTS server
    -1
        Fail to upload the row to the OTS server and print the error message
    """
    condition = tablestore.Condition(tablestore.RowExistenceExpectation.IGNORE)
    for i in range(len(row)):
        try :
            if (i==0):
                consumed, return_row = client_global.put_row(_tablename, row[i], condition)
            else:
                consumed, return_row = client_global.update_row(_tablename, row[i], condition)
        except tablestore.OTSClientError as e:
            print (e.get_error_message())
            return -1
        except tablestore.OTSServiceError as e:
            print (e.get_error_message())
            return -1 
    return 0


def _para_upload(arg_bag):
    """the unit upload operation for the parallel upload process
    
    This function should not be directly used by the users but will be called by the insert_matrix_para function when users upload a group of cells parallelly.


    Parameters
    ----------
    arg_bag: list
        arg_bag is a list which contains only an int element. This element represents which row to get from the global data.frame. The got row will be transfromed by calling the _Cell2Row function and then uploaded to the server by calling the _insert_row function.


    Returns
    -------
    int
        the status of the upload operation, 0 means success and -1 means failure.
    """
    i = arg_bag
    row = _Cell2Row(df.iloc[i,:])
    insert_stat = _insert_row(row)
    return(insert_stat)


def insert_matrix_para(thread_num = multiprocessing.cpu_count() - 1):
    """upload the loaded dataframe to the server parallelly
    
        This function uploads the DataFrame stored in the gloable variable df to the server. We recommand running the check_data function before using this function to ensure the DataFrame is standardized and ready for upload.
        
        This function will print how many rows failed to be uploaded and return the upload results of each operation.

    Parameters
    ----------
    thread_num: int
        thread_num is number of threads used in the parallel upload process. The default value of this parameter is multiprocessing.cpu_count()-1 ,which means the function will use as many as accessible threads

    Returns
    -------
    int/list
        If all upload operations in the parallel upload process success, this function will return 0
        
        If any operation fails, this function will return the list of all upload status. In i-th element, 0 means success and -1 means failure in the i-th operation.
    """
    nrow = df.shape[0]
    arg_bag = [(i) for i in range(nrow)]
    with multiprocessing.Pool(thread_num) as pool:
        b = pool.map(_para_upload,arg_bag)
        pool.close()
        pool.join()
    if sum(b)!= 0:
        print(b.count(-1), "rows upload failed")
        return b
    else:
        print(nrow,"rows upload successfully")
        return 0


def build_index():
    """build the index on the metadata columns for cell searching
    
        This function builds index on all metadata columns in the table on the OTS server. The index contains 17 fields and each one represents a metadata column in the OTS table.The 17 fields are user_id, study_id, cell_id, organ, region, subregion, seq_tech, sample_status, donor_id, donor_gender, donor_age, original_name, cl_name, hcad_name, tissue_type, cell_type and marker_gene.
        
        The index is neccessary for any processes containing searching operation. Index is only need to be built once in a table and can update automatically when the table changes. Hence we will print a warning if the index exists.


    Returns
    -------
    None
        no return but print a warning when the index has been built
    """

    # check if the index exists in the table
    index_list = client_global.list_search_index(_tablename)
    if index_list and (_tablename, 'metadata')  in index_list:
        print("index already exist.")
    else:
        # create index
        field_sid = tablestore.FieldSchema('study_id',tablestore.FieldType.KEYWORD, is_array = False, index = True, enable_sort_and_agg = True, store = True)
        field_cid = tablestore.FieldSchema('cell_id',tablestore.FieldType.KEYWORD, is_array = False, index = True, enable_sort_and_agg = True, store = True)
        field_uid = tablestore.FieldSchema('user_id',tablestore.FieldType.LONG, is_array = False, index = True, enable_sort_and_agg = True, store = True)
        field_organ = tablestore.FieldSchema('organ',tablestore.FieldType.KEYWORD, is_array = False, index = True, enable_sort_and_agg = True, store = True)
        field_region = tablestore.FieldSchema('region',tablestore.FieldType.KEYWORD, is_array = False, index = True, enable_sort_and_agg = True, store = True)
        field_subr = tablestore.FieldSchema('subregion',tablestore.FieldType.KEYWORD, is_array = False, index = True, enable_sort_and_agg = True, store = True)
        field_st = tablestore.FieldSchema('seq_tech',tablestore.FieldType.KEYWORD, is_array = False, index = True, enable_sort_and_agg = True, store = True)
        field_ss = tablestore.FieldSchema('sample_status',tablestore.FieldType.KEYWORD, is_array = False, index = True, enable_sort_and_agg = True, store = True)
        field_did = tablestore.FieldSchema('donor_id',tablestore.FieldType.KEYWORD, is_array = False, index = True, enable_sort_and_agg = True, store = True)
        field_dg = tablestore.FieldSchema('donor_gender',tablestore.FieldType.KEYWORD, is_array = False, index = True, enable_sort_and_agg = True, store = True)
        field_da = tablestore.FieldSchema('donor_age',tablestore.FieldType.KEYWORD, is_array = False, index = True, enable_sort_and_agg = True, store = True)
        field_on = tablestore.FieldSchema('original_name',tablestore.FieldType.KEYWORD, is_array = False, index = True, enable_sort_and_agg = True, store = True)
        field_cn = tablestore.FieldSchema('cl_name',tablestore.FieldType.KEYWORD, is_array = False, index = True, enable_sort_and_agg = True, store = True)
        field_hn = tablestore.FieldSchema('hcad_name',tablestore.FieldType.KEYWORD, is_array = False, index = True, enable_sort_and_agg = True, store = True)
        field_tt = tablestore.FieldSchema('tissue_type',tablestore.FieldType.KEYWORD, is_array = False, index = True, enable_sort_and_agg = True, store = True)
        field_ct = tablestore.FieldSchema('cell_type',tablestore.FieldType.KEYWORD, is_array = False, index = True, enable_sort_and_agg = True, store = True)
        field_mg = tablestore.FieldSchema('marker_gene',tablestore.FieldType.KEYWORD, is_array = False, index = True, enable_sort_and_agg = True, store = True)
        fields = [field_tt,field_ct,field_mg,field_cid,field_uid, field_sid, field_organ, field_region, field_subr, field_st, field_ss, field_did,field_dg, field_da, field_on, field_cn, field_hn]
        index_meta = tablestore.SearchIndexMeta(fields)
        client_global.create_search_index(_tablename, "metadata", index_meta)


def query_cells(metadata_conditions="",include_children=False,exlude_Unclassified=False,print_message=True):
    """query cells and return the list of their primary keys
    
        This function is used to query cells satisfing the metadata conditions in the OTS table on the server. The conditions on the metadata should be a structured string which is a combination of several logical expressions. 
        
        Users should remember that this function only enable them to query cell based on the conditions on the metadata columns in the index while conditions on gene expression should be set in the get_columnsbycell function or get_columnsbycell_para function.
    
    
    Parameters
    ----------
    metadata_conditions: str
        It is a structured string which is a combination of several logical expressions.

        Each logical expression should be in the following forms:
            field_name1 == value1,                          here '==' means equal

            field_name2 <> value2,                          here '<>' means unequal

        Three symbols are used for logical operation between expressions:
            logical_expression1 && logical_expression2,     here '&&' means AND operation

            logical_expression1 || logical_expression2,     here '||' means OR operation

            ！ logical_expression1,                         here '!' means not NOT operation

        Brackets are allowed and the priorities of the logical operations are as common. The metadata condition string is also robust to the space character.

        Here are some examples of legal condition strings:
            '(user_id == 2 && organ == Heart) || (user_id == 3 && organ <> Brain)'

            'organ == Lung && !seq_tech == 10X  '

            'organ == Heart &&(cell_type == Fibrocyte || region <> atria)'
        
        The default value of this parameter is '', which will get all rows in the database.

    include_children: bool 
        include_children is the parameter deciding if subtypes should be included in the query with condition on cell type. For example, when we query "cell_type == T cell" and set include_children as True, 
        cells in the query result would contain T cell and the subtypes of T cells like CD4 T cell, CD8 T cell and so on; otherwise, only T cells would exist in the query result.
    
    Returns
    -------
    list
        The return is a list of the primary keys of quried cells. Each element is a list containing a tuple with the name of primary key and its value: [('cid',2021119)].
        
        Here is an example return with 2000 quried cells:

            [[('cid',2000001)],[('cid',2000002)],[('cid',2000003)],[('cid',2000004)],...,[('cid',2002000)]]

        The primary key list can be used for downstream data downloading or table updating.
    """
    query = _seq2boolquery(metadata_conditions,include_children,exlude_Unclassified)
    # get primary keys
    results = []
    next_token = None
    total_cells = 0
    # [0620] update for tablestore 5.2.1
    search_result = client_global.search(
        _tablename, "metadata", 
        tablestore.SearchQuery(query, next_token=next_token, limit=100, get_total_count=True), 
        tablestore.ColumnsToGet(return_type=tablestore.ColumnReturnType.NONE)
    )
    next_token = search_result.next_token
    results += search_result.rows
    total_cells += search_result.total_count

    while next_token:# if not finished
        # [0620] update for tablestore 5.2.1
        search_result = client_global.search(
        _tablename, "metadata", 
        tablestore.SearchQuery(query, next_token=next_token, limit=100, get_total_count=True), 
        tablestore.ColumnsToGet(return_type=tablestore.ColumnReturnType.NONE)  
        )
        next_token = search_result.next_token
        results += search_result.rows
        total_cells += search_result.total_count
    
    # build the list of the primary keys of the quried cells
    rows_to_get = [x[0] for x in results]

    # [1108] print the number of cells
    if print_message:
        print("%d cells found" %len(results))

    return rows_to_get


def _para_get_column(arg_bag):
    """the unit download operation for the parallel download process
    
    This function should not be directly used by the users but will be called by the get_columnsbycell_para function when users download selected columns of a group of cells parallelly from the server.
    
    
    Parameters
    ----------
    arg_bag: list
        arg_bag is a list with three elements

        The first element is a list containing a primary key tuple like [('cid',XXXXXXX)].

        The second element is a list of strings containing the names of the selected columns which can be either metadata columns or genes. The second element can be None that the function will only download the primary key.
        The third element is a tablestore::ColumnCondition.g

        Here is an example of arg_bag:
            [(cid,2000001),["PTPRC","cell_type","organ","user_id"],None]

    Returns
    -------
    list
        A list of values in the selected columns of the cell
    """
    primary_key, columns_to_get, col_filter = arg_bag
    consumed, return_row, next_token= client_global.get_row(_tablename, primary_key,columns_to_get,column_filter=col_filter)
    ### [0601] avoid errors from NA in the row
    if not return_row is None:
        return [(x[0],x[1]) for x in return_row.primary_key] + [(x[0],x[1]) for x in return_row.attribute_columns]
    else:
        return None
    #   return ([x[1] for x in return_row.primary_key] + [x[1] for x in return_row.attribute_columns])


def get_columnsbycell_para(rows_to_get=None,cols_to_get=None,col_filter=None,do_transfer = True, thread_num = multiprocessing.cpu_count()-1,exlude_Unclassified=False):
    """download the selected columns of the given cells from the OTS table on the server parallelly
    
        This function gets the cells in the given primary key list and downloads parts of columns or all columns. A further filtering on the gene expression levels can be conducted based on given column filters.
        Users can select the return data form as a pandas::DataFrame or a list without transformation.

    Parameters
    ----------
    rows_to_get: list
        rows_to_get is a list of primary keys of the cells to download. Each element in the list is a list containing a primary key tuple like [('cid',XXXXXXX)]. The default value of this parameter is None which means to get all rows in the database.

    cols_to_get: list
        cols_to_get is a list of strings containing the names of the selected columns which can be either metadata columns or genes.
        
        The default value of this parameter is None that means the function will download all columns.

    col_filter: tablestore::CompositeColumnCondition
        col_filter is a combined column condition in tablestore package. It can be generated by the seq2filter function which takes a structed string as input.
        
        Once a filter is set, the function will first filter the given cells then download the selected columns of the cells pass the filter. A massage will be print if no cells pass the given filter. The default value of this parameter is None that means no filtering will be conducted.

    do_transfer: bool
        If do_transfer is true, the output of this function will be transform into a pandas::DataFrame; vice versa.
        
        The default value of this parameter is True.

    thread_num: int
        Thread_num is number of threads used in the parallel upload process. The default value of this parameter is multiprocessing.cpu_count()-1 ,which means the function will use as many as accessible threads

    exlude_Unclassified: bool
        This parameter is only used when rows_to_get is None. It decides whether the cells with Unclassified cell_type will be included in the result.
    
    Returns
    -------
    pandas::DataFrame/list
        If do_transfer == True, the return will be a pandas::DataFrame where each row represents a cell.
        
        If do_transfer == False, the return will be a list. Each element is a list which represents a cell.
    """
    if rows_to_get == None:
        rows_to_get = query_cells(exlude_Unclassified=exlude_Unclassified)
    
    # [1108] replace the uHAF_name to hcad_name in the cols_to_get
    if not cols_to_get == None:
        cols_to_get = ["hcad_name" if i == "uHAF_name" else i for i in cols_to_get]
    
    arg_bag = [(rows_to_get[i],cols_to_get,col_filter) for i in range(len(rows_to_get))]
    try:
        with multiprocessing.Pool(thread_num) as pool:
            df_get = pool.map(_para_get_column,arg_bag)
            pool.close()
            pool.join()
    except:
        with multiprocessing.Pool(thread_num) as pool:
            df_get = pool.map(_para_get_column,arg_bag)
            pool.close()
            pool.join()

    while None in df_get:
        df_get.remove(None)
        
    if len(df_get)==0:
            print("no cell satisfy")
    else:
        if do_transfer:
            df_get = pd.DataFrame.from_dict([dict(df_get[i]) for i in range(len(df_get))]) 
            df_get = df_get.set_index(['cid'])

            # [1108] replace the hcad_name in the colnames with uHAF_name
            df_get.columns = ["uHAF_name" if i == "hcad_name" else i for i in df_get.columns ]

    return df_get


def get_columnsbycell(rows_to_get=None,cols_to_get=None,col_filter=None,do_transfer = True,exlude_Unclassified=False):
    """download the selected columns of the given cells from the OTS table on the server (nonparallelly)
    
        This function gets the cells in the given primary key list and downloads parts of columns or all columns. A further filtering on the gene expression levels can be conducted based on given column filters.
        
        Users can select the return data form as a pandas::DataFrame or a list without transformation.


    Parameters
    ----------
    rows_to_get: list
        rows_to_get is a list of primary keys of the cells to download. Each element in the list is a list containing a primary key tuple like [('cid',XXXXXXX)]. The default value of this parameter is None which means to get all rows in the database.

    cols_to_get: list
        cols_to_get is a list of strings containing the names of the selected columns which can be either metadata columns or genes

        The default value of this parameter is None that means the function will download all columns.

    col_filter: tablestore::CompositeColumnCondition
        col_filter is a combined column condition in tablestore package. It can be generated by the seq2filter function which takes a structed string as input.
        
        Once a filter is set, the function will first filter the given cells then download the selected columns of the cells pass the filter. A massage will be print if no cells pass the given filter. The default value of this parameter is None that means no filtering will be conducted.

    do_transfer: bool
        If do_transfer is true, the output of this function will be transform into a pandas::DataFrame; vice versa.
        
        The default value of this parameter is True.
    
    exlude_Unclassified: bool
        This parameter is only used when rows_to_get is None. It decides whether the cells with Unclassified cell_type will be included in the result.


    Returns
    -------
    pandas::DataFrame/list
        If do_transfer == True, the return will be a pandas::DataFrame where each row represents a cell.
        
        If do_transfer == False, the return will be a list. Each element is a list which represents a cell.
    """
    
    if rows_to_get == None:
        rows_to_get = query_cells(exlude_Unclassified)
        
    # [1108] replace the uHAF_name to hcad_name in the cols_to_get
    if not cols_to_get == None:
        cols_to_get = ["hcad_name" if i == "uHAF_name" else i for i in cols_to_get]

    request = tablestore.BatchGetRowRequest()
    df_get = []
    colnames = None
    for i in range(len(rows_to_get)//100+1):
        request.add(tablestore.TableInBatchGetRowItem(_tablename, rows_to_get[i*100:i*100+100],cols_to_get,col_filter,1))
        try:
            got_rows = client_global.batch_get_row(request).get_succeed_rows()
            for row in got_rows:
                if not row.row is None:
                    if colnames == None:
                        colnames = [x[0] for x in row.row.primary_key] + [x[0] for x in row.row.attribute_columns]
                        ## [0601] transform the hcad_name in the colnames into uHAF_name
                        if "hcad_name" in colnames:
                            colnames[colnames.index("hcad_name")] = "uHAF_name"

                    df_get.append([(x[0],x[1]) for x in row.row.primary_key] + [(x[0],x[1]) for x in row.row.attribute_columns])
        except tablestore.OTSClientError as e:
            print(e)
        except tablestore.OTSServiceError as e:
            print(e)
    if len(df_get)==0:
            print("no cell satisfy")
    else:
        if do_transfer:
            df_get = pd.DataFrame.from_dict([dict(df_get[i]) for i in range(len(df_get))])
            df_get.set_index(['cid'])

            # [1108] replace the hcad_name in the colnames with uHAF_name
            df_get.columns = ["uHAF_name" if i == "hcad_name" else i for i in df_get.columns ]

        return df_get


def get_column_set(rows_to_get=None, col_to_get=None, col_filter=None,exlude_Unclassified=False):
    """get all unique values in a selected column in the given cells
    
    This function calls the get_columnsbycell_para function to download the values of a selected column in the given cells and return a set of all unique values.
    
    Parameters
    ----------
    rows_to_get: list
        rows_to_get is a list of primary keys of the cells to download. Each element in the list is a list containing a primary key tuple like [('cid',XXXXXXX)]. The default value of this parameter is None which means to get all rows in the database.

    col_to_get: list
        col_to_get is a list whose length is 1. The element in this list is the name of the selected column. if the length of the list is not 1, a error will be risen.

    col_filter: tablestore::CompositeColumnCondition
        col_filter is a combined column condition in tablestore package. It can be generated by the seq2filter function which takes a structed string as input.
        
        Once a filter is set, the function will first filter the given cells then download the selected columns of the cells pass the filter. A massage will be print if no cells pass the given filter. The default value of this parameter is None that means no filtering will be conducted.

    exlude_Unclassified: bool
        This parameter is only used when rows_to_get is None. It decides whether the cells with Unclassified cell_type will be included in the result.

    Returns
    -------
    Set
        A set of all unique values in the selected column
    """
    if(len(col_to_get) == 1):

        # [1108] replace uHAF_name with hcad_name
        if col_to_get == ['uHAF_name']:
            col_to_get = ['hcad_name']

        if rows_to_get == None:
            rows_to_get = query_cells(exlude_Unclassified)
        
        rows = get_columnsbycell_para(rows_to_get, col_to_get,do_transfer = False)
        s = set()
        for row in rows:
            if len(row):
                s.add(row[1][1])
        return s
    else:
        print('ParameterLenthError: col_to_get must be a lenth 1 list.')
        return None


def get_all_rows(cols_to_get = []):
    """get values in the selected columns in all cells in the OTS table
    
    This function downloads all values of the selected columns in the whole OTS table
    
    Parameters
    ----------
    cols_to_get: list
        cols_to_get is a list of strings containing the names of the selected columns which can be either metadata columns or genes.
        
        The default value of this parameter is an empty list that means the function will only download the primary keys


    Returns
    -------
    list
        A list of tablestore::Row variables, each one represent a cell
    """
    query = tablestore.MatchAllQuery()
    all_rows = []
    next_token = None
    col_return_type = tablestore.ColumnReturnType.ALL
    if cols_to_get:
        col_return_type = tablestore.ColumnReturnType.SPECIFIED

    # [1108] replace the uHAF_name to hcad_name in the cols_to_get
    if not cols_to_get == None:
        cols_to_get = ["hcad_name" if i == "uHAF_name" else i for i in cols_to_get]

    while not all_rows or next_token:
        # [0620] update for tablestore 5.2.1
        search_result = client_global.search(_tablename, 'metadata',
            tablestore.SearchQuery(query, next_token=next_token, limit=100, get_total_count=True),
            columns_to_get=tablestore.ColumnsToGet(cols_to_get, col_return_type))
        next_token = search_result.next_token
        all_rows.extend(search_result.rows)

    print("%d cells found" %len(all_rows))

    return all_rows


def update_row(primary_key, update_data):
    """update a cell in the OTS table with the given columns' values
    
    This function first checks if the given cell is in the OTS table. If the cell is found, the given columns will be update by the given values; otherwise, a warning message will be risen.


    Parameters
    ----------
    primary_key: list
        primary_key is a list which contains a tuple like: [('cid',XXXXXXX)]

    update_data: list
        updtae_data is a list which contains several tuples. Each tuple contains the name of a column and the value to update.

        Here is an example of update_data:

            [("oragn","Heart"),("user_id",2),("cell_type","T cell")]


    Returns
    -------
    int
        the status of the update operation, 0 means success and -1 means failure.
    """
    try:
        consumed, return_row, next_token = client_global.get_row(_tablename, primary_key,columns_to_get=['cid'])
        if return_row == None:
            print("Error! This row doesn't exist in the table.")
            return -1
        else:
            # convert update data to blockes
            row = []
            for i in range(len(update_data)//1024+1): # the maxium number of attribute columns in each writing operation is 1024
                row.append(tablestore.Row(primary_key,{'PUT':update_data[i*1024:min(i*1024+1024,len(update_data))]}))

            # try to update data
            condition = tablestore.Condition(tablestore.RowExistenceExpectation.IGNORE)
            for i in range(len(row)):
                try :
                    consumed, return_row = client_global.update_row(_tablename, row[i], condition)
                    return 0
                except tablestore.OTSClientError as e:
                    print (e.get_error_message())
                    return -1
                except tablestore.OTSServiceError as e:
                    print (e.get_error_message())
                    return -1

    except tablestore.OTSClientError as e:
        print (e.get_error_message()) 
        return -1
    except tablestore.OTSServiceError as e:
        print (e.get_error_message())
        return -1


def _update_para(arg_bag):
    """the unit update operation for the parallel update process
    
    This function should not be directly used by the users but will be called by the update_batch function when users update some columns of a group of cells parallelly.


    Parameters
    ----------
    arg_bag: list
        arg_bag is a list which contains two elements. 

        The first element is a list which contains a tuple like: [('cid',XXXXXXX)]
        
        The second element is a list which contains several tuples where each tuple contains the name of a column and the value to update.


    Returns
    -------
    int
        the status of the upload operation, 0 means success and -1 means failure.
    """
    primary_key,update_data = arg_bag
    return update_row(primary_key,update_data)


def update_batch(rows_to_update, update_sets, thread_num = 5):
    """update cells in the OTS table with the given columns' values parallelly
    
        This function updates the cells in the given primary key list with the given column values.


    Parameters
    ----------
    rows_to_update: list
        rows_to_update is a list of primary keys of the cells to be updated. Each element in the list is a list containing a primary key tuple like [('cid',XXXXXXX)]

    update_sets: list
        update_sets is a list whose length is the same as the parameter rows_to_update. Each element in this list is a list which contains several tuples where each tuple contains the name of a column and the value to update: [(column_name1, value1),(column_name2, value2),...]

    thread_num: int
        Thread_num is number of threads used in the parallel update process. The default value of this parameter is 5.


    Returns
    -------
    int/list
        If all update operations in the parallel update process success, this function will return 0
        
        If any operation fails, this function will return the list of all update status. In i-th element, 0 means success and -1 means failure in the i-th operation.
    """
    
    
    arg_bag = [ (rows_to_update[i],update_sets[i]) for i in range(len(rows_to_update))]
    ## [0601] add try... except to avoid error
    try:
        with multiprocessing.Pool(thread_num) as pool:
            b = pool.map(_update_para,arg_bag)
            pool.close()
            pool.join()
    except:
        with multiprocessing.Pool(thread_num) as pool:
            b = pool.map(_update_para,arg_bag)
            pool.close()
            pool.join()
    if sum(b)!= 0:
        print(b.count(-1)," rows update failed")
        return b
    else:
        return 0
    
    
    
# [1108] add new interfaces with new names

def search_metadata(metadata_conditions="",include_children=False,exlude_Unclassified=False,print_message=True):
    """query cells and return the list of their primary keys
    
        This function is used to query cells satisfing the metadata conditions in the OTS table on the server. The conditions on the metadata should be a structured string which is a combination of several logical expressions. 
        
        Users should remember that this function only enable them to query cell based on the conditions on the metadata columns in the index while conditions on gene expression should be set in the get_columnsbycell function or get_columnsbycell_para function.
    
    
    Parameters
    ----------
    metadata_conditions: str
        It is a structured string which is a combination of several logical expressions.

        Each logical expression should be in the following forms:
            field_name1 == value1,                          here '==' means equal

            field_name2 <> value2,                          here '<>' means unequal

        Three symbols are used for logical operation between expressions:
            logical_expression1 && logical_expression2,     here '&&' means AND operation

            logical_expression1 || logical_expression2,     here '||' means OR operation

            ！ logical_expression1,                         here '!' means not NOT operation

        Brackets are allowed and the priorities of the logical operations are as common. The metadata condition string is also robust to the space character.

        Here are some examples of legal condition strings:
            '(user_id == 2 && organ == Heart) || (user_id == 3 && organ <> Brain)'

            'organ == Lung && !seq_tech == 10X  '

            'organ == Heart &&(cell_type == Fibrocyte || region <> atria)'
        
        The default value of this parameter is '', which will get all rows in the database.

    include_children: bool 
        include_children is the parameter deciding if subtypes should be included in the query with condition on cell type. For example, when we query "cell_type == T cell" and set include_children as True, 
        cells in the query result would contain T cell and the subtypes of T cells like CD4 T cell, CD8 T cell and so on; otherwise, only T cells would exist in the query result.
    
    Returns
    -------
    list
        The return is a list of the primary keys of quried cells. Each element is a list containing a tuple with the name of primary key and its value: [('cid',2021119)].
        
        Here is an example return with 2000 quried cells:

            [[('cid',2000001)],[('cid',2000002)],[('cid',2000003)],[('cid',2000004)],...,[('cid',2002000)]]

        The primary key list can be used for downstream data downloading or table updating.
    """
    return query_cells(metadata_conditions,include_children,exlude_Unclassified,print_message)


def set_gene_condition(gene_condition):
    """transform a gene-condition string into a OTS column condition

    This function will analyze the logical expression string of the gene condition for cell searching and generate a combined column condition of OTS database.

    Parameters
    ----------
    gene_condition: str
        It is a structured string which is a combination of several logical expressions.

        Each logical expression should be in the following forms:
            gene_name1 == value1,                          here '==' means equal

            gene_name2 <> value2,                          here '<>' means unequal
            
            gene_name3 > value3,                          here '>' means larger than 
            
            gene_name4 < value4,                          here '<' means smaller than
            
            gene_name5 >= value5,                          here '>=' means not smaller than
            
            gene_name6 <= value6,                          here '<=' means not larger than

        Three symbols are used for logical operation between expressions:
            logical_expression1 && logical_expression2,     here '&&' means AND operation

            logical_expression1 || logical_expression2,     here '||' means OR operation

            ！ logical_expression1,                         here '!' means not NOT operation

        Brackets are allowed and the priorities of the logical operations are as common. The metadata condition string is also robust to the space character.

        Here are some examples of legal condition strings:
            '(CD3D > 2 && CD3E >= 0.1) || (PTPRC <= 3 && CD8A >= 0.01)'



    Returns
    -------
    tablestore.CompositeColumnCondition
        the column condition for tablestore to seach cells
    """
    return seq2filter(gene_condition)