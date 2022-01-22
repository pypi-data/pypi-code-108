import argparse
import os
import utils
import settings
import pandas as pd
import psycopg2
import yaml
log = utils.get_logger()

import sys
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import create_engine
import logging.config

log = logging.getLogger(__name__)


def connection_string(engine, host, port, username, password, database):
    return '{engine}{username}:{password}@{host}:{port}/{database}'.format(
        engine=engine,
        username=username,
        password=password,
        host=host,
        port=port,
        database=database)


class DbSession(object):
    __instance = None

    def __new__(cls, *args, **kwargs):
        if DbSession.__instance is None:
            DbSession.__instance = object.__new__(cls)
            try:
                cls.engine = create_engine(connection_string(
                    engine=kwargs['engine'],
                    host=kwargs['host'],
                    port=kwargs['port'],
                    username=kwargs['username'],
                    password=kwargs['password'],
                    database=kwargs['database']
                ), echo=settings.DEBUG)
                log.debug('activating session')
                cls.session = sessionmaker(bind=cls.engine, autocommit=False, autoflush=True)()
            except KeyError as e:
                print('DbSession available')
        return DbSession.__instance

    def __init__(self, **kwargs):
        """
        :param username: a database username
        :param password: database password
        :param host: ip of host
        :param port: port of db
        :param database: a database name
        """
        pass


def write(con, df, table_name, if_exists='append'):
    try:
        df.to_sql(table_name, con=con, if_exists=if_exists)
    except (Exception, psycopg2.Error) as error:
        print("Could not write to table", error)

    return None


def populate_measure_type(con=None):
    df = pd.DataFrame({'measure_type_id': ['increase', 'decrease', 'neutral'], #1,2,3
                       'measure_type_description': ['increase in measure is good', 'decrease in measure is good', 'agnostic at the moment']}).set_index('measure_type_id')

    write(con=con, df=df, table_name='measure_type')
    log.info("--- Created measure types in measure type table ---")


def populate_perspectives(con=None):
    df = pd.DataFrame({'perspective_id': ('FINANCIAL', 
                                       'CUSTOMER',
                                       'INTERNAL_BUSINESS_PROCESSES',
                                       'EMPLOYEE_LEARNING_AND_GROWTH'),
                        'perspective_description': ('relating to the financial perspective', 'relating to the customer perspective', 
                        'relating to the internal and business processes perspective', 'relating to the development and growth of employees')
                        }).set_index('perspective_id')
    write(con=con, df=df, table_name='perspective')
    log.info("--- Created perspectives in perspective table ---")


def populate_entity_type(con=None):
    df = pd.DataFrame({'entity_type_id': ('grain_crops',
                                       'micro_green_crops',
                                       'green_crops',
                                       'small_livestock',
                                       'livestock',
                                       'resource_location'),
                       'entity_type_description': ('grain crop based farming',
                                                   'micro greens based farming',
                                                   'greens based farming (spinach etc.)',
                                                   'small livestock such as chickens',
                                                   'livestock such as goats or cows',
                                                   'Either physical or digital (location, bank account)')
                       }).set_index('entity_type_id')

    write(con=con, df=df, table_name='entity_type')
    log.info("--- Created entity types in entity_type table ---")

def populate_sensor_store(con=None):

    df = pd.DataFrame({'sensor_store_catalog_id': (1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18, 19,20,21,22,23,24,25,26),
                       'sensor_store_id': ('soil moisture','ambient temperature','water level',
                                            'weight (kg)','weight (mg)', 'humidity', 'soil temperature',
                                            'light intensity', 'water quality', 'soil NPK levels',
                                           'electricty usage (kwh)', 'power remaining','water rate usage (l/min)',
                                            'operating profit','Overhead cost', 'No of customers on database', 'No of loyal/returning customers',
                                            'Delivery rate', 'Return rate', 'financial books/till', 'No of employees', 'Product variation',
                                            'Mentor visit log','Customer tracker','Employee satisfaction tracker', 'New selling method tracker'),

                       'sensor_description': ('to measure soil moisture', 'air temperature', 'water level in a tank',
                                              'weight of something in kg', 'weight of something in mg', 'air humidity',
                                              'temperature of the soil', 'energy of the sunlight at point', 'dirt in water',
                                              'NPK ratio of soil', 'electricity usage', 'amount of electricity remaining',
                                              'rate of water usage in litres per min', 'The operating profit as indicated by the accounting books', 'The overhead cost as indicated by the books',
                                              'The number of customers on the database', 'The number of customers that are returning/loyal', 'The rate of delivery of products to customers',
                                               'The rate of return on products', 'Ledger or document of transactions and monetary assets', 'The number of people employed at the farm','The number of different products on sale',
                                               'The number of mentor visits required', 'Customer tracker','Employee satisfaction tracker','New selling method tracker'),
                       'sensor_active_indicator': (1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1)
                       }).set_index('sensor_store_catalog_id')
    write(con=con, df=df, table_name='sensor_store')
    log.info("--- Created base sensors sensor store ---")

def populate_objective_store(con=None):
    
    df = pd.DataFrame( {'objective_id': (
    'Gain acitivity earning',
    'Increase operational cash margin',
    'Improve production efficiency',
    'Increase total income', 
    'Improve profitability of investments',
    'Meet shareholder expectations',
    'Achieve profitable & sustainable growth',
    'Increase of the activities of the agricultural company',
     'Decrease of financial costs/ Reduce indirect expenditure',
     'Reduce operational costs',
     'Increase asset utilisation',
     'To develop demand', 
'Set up high level of customer satisfaction',
'To set up competitive prices',
'Better health status',
'Increase customer base',
'Customer loyalty',
'Image of the agricultural farm',
'Quality of produce',
'Meet customer demand',
'Improve product delivery',
'Increase customer network',
'Increase level of productivity ',
'Increase product quality',
'Improve milk yield',
'Improve utilisation of feed',
'Higher yield of forage ',
'Improved utilisation of milk quota',
'Less stoarge loss of forage',
'Improve utilisation of buildings',
'Improve utilisation of machinery',
'Reduce the use of labour',
'Development of strategic segments',
'Development of innovative processes',
'Observance of environmental laws',
'Soil processing and fertilising',
'Quality of plant cultivation',
'On time and in full products',
'Customer communication',
'Develop new selling methods',
'Create interdependency between the firm and the community',
'Increase product offering',
'Improve managerial/partner and technical competences',
'Provide employee motivation',
'Hiring of more skilled herd manager',
'Use of better information systems',
'Development of managerial competences',
'Develop safety protocols to protect staff',
'Implement practises that employ and retain best staff',
'Create organisation with strong and constructive culture',
'Parner/employee satisfaction'),

    'objective_description': ('Gain earnings on activities',
    'Gain earnings on activities',
     'Improve operational efficiencies and reduce wastes',
      'Increase total income',
    'Increase profitability of investments',
    'Satisfy the shareholder expecations','Achieve profitable & sustainable growth', 
    'Increase the number of activities of the farm', 
    'Decrease of financial costs/ Reduce indirect expenditure',
    'Reduce operational costs',
    'Increase asset utilisation',
    'To develop demand', 
'Set up high level of customer satisfaction',
'To set up competitive prices',
'Better health status',
'Increase customer base',
'Customer loyalty',
'Image of the agricultural farm',
'Quality of produce',
'Meet customer demand',
'Improve product delivery',
'Increase customer network',
'Increase level of productivity ',
'Increase product quality',
'Improve milk yield',
'Improve utilisation of feed',
'Higher yield of forage ',
'Improved utilisation of milk quota',
'Less stoarge loss of forage',
'Improve utilisation of buildings',
'Improve utilisation of machinery',
'Reduce the use of labour',
'Development of strategic segments',
'Development of innovative processes',
'Observance of environmental laws',
'Soil processing and fertilising',
'Quality of plant cultivation',
'On time and in full products',
'Customer communication',
'Develop new selling methods',
'Create interdependency between the firm and the community',
'Increase product offering',
'Improve managerial/partner and technical competences',
'Provide employee motivation',
'Hiring of more skilled herd manager',
'Use of better information systems',
'Development of managerial competences',
'Develop safety protocols to protect staff',
'Implement practises that employ and retain best staff',
'Create organisation with strong and constructive culture',
'Parner/employee satisfaction'),

    'perspective_id': ('FINANCIAL','FINANCIAL', 'FINANCIAL', 'FINANCIAL', 'FINANCIAL', 'FINANCIAL', 'FINANCIAL', 'FINANCIAL', 'FINANCIAL', 'FINANCIAL', 'FINANCIAL',
     'CUSTOMER', 'CUSTOMER', 'CUSTOMER', 'CUSTOMER', 'CUSTOMER', 'CUSTOMER', 'CUSTOMER', 'CUSTOMER', 'CUSTOMER', 'CUSTOMER', 'CUSTOMER',
     'INTERNAL_BUSINESS_PROCESSES','INTERNAL_BUSINESS_PROCESSES','INTERNAL_BUSINESS_PROCESSES','INTERNAL_BUSINESS_PROCESSES','INTERNAL_BUSINESS_PROCESSES','INTERNAL_BUSINESS_PROCESSES','INTERNAL_BUSINESS_PROCESSES','INTERNAL_BUSINESS_PROCESSES'
     ,'INTERNAL_BUSINESS_PROCESSES','INTERNAL_BUSINESS_PROCESSES','INTERNAL_BUSINESS_PROCESSES','INTERNAL_BUSINESS_PROCESSES','INTERNAL_BUSINESS_PROCESSES','INTERNAL_BUSINESS_PROCESSES','INTERNAL_BUSINESS_PROCESSES','INTERNAL_BUSINESS_PROCESSES'
     ,'INTERNAL_BUSINESS_PROCESSES','INTERNAL_BUSINESS_PROCESSES','INTERNAL_BUSINESS_PROCESSES','INTERNAL_BUSINESS_PROCESSES',
     'EMPLOYEE_LEARNING_AND_GROWTH','EMPLOYEE_LEARNING_AND_GROWTH','EMPLOYEE_LEARNING_AND_GROWTH','EMPLOYEE_LEARNING_AND_GROWTH','EMPLOYEE_LEARNING_AND_GROWTH','EMPLOYEE_LEARNING_AND_GROWTH','EMPLOYEE_LEARNING_AND_GROWTH','EMPLOYEE_LEARNING_AND_GROWTH'
     ,'EMPLOYEE_LEARNING_AND_GROWTH') }




    ).set_index('objective_id')
    write(con=con, df=df, table_name='objective_store')
    log.info("--- Created base objective store ---")


def populate_measure_store(con=None):

    df = pd.DataFrame({'measure_store_catalog_id': (
        1,2,3,4,5,
        6,7,8,9,10,
        11,12,13,14,15,
        16,17,18,19,20,
        21,22,23,24,25,
        26,27,28,29,30,
        31,32,33,34,35,
        36,37,38,39,40,
        41,42,43,44,45,
        46,47,48,49,50,
        51,52,53,54,55,
        56,57,58,59,60,
        61,62,63,64,65,
        66,67,68,69,70,
        71,72,73,74,75),

    'measure_store_id': (
        'Financial returns','Cash margin', 'Customer satisfaction', 'Percentage of product that hits target market', 'Number of active customers on database',
    'Volume/Weight of product sold', 'Cash received', 'Income statement', 'Cost drivers', 'Gross margin per unit of product sold', 
    'Revenue per employee','Overhead cost per product sold',  'Return on investment (ROI)', 'Invesment portfolio', 'Return on Assets (ROA)', 
    'Operating profit margin (OPM)', 'Economic value add (EVA)', 'Cost of capital (COC)', 'Increase turnover','Variation of operating profit', 
    'Variation of financial expenses','Indirect costs','Demand', 'Selling price','Selling price relative to competitors',
    'Customer loyalty', 'Product replacement rate', 'Number of required mentor visits', 'Percentage of new customers','Turnover from new customers',
    'Customer lost', 'Turnover by customer loyalty','Total rejected products to total revenue','Customer complaints to total customers', 'Demand satisfaction rate',
    'Delivery time','On time delivery','Number of sales proposals per month', 'Productivity','Perceived quality',
    'Crop/resource yield','Hygiene and sanitary standards','Animal condition score','Feed units per animal', 'Yeild of forage',
     'Crop rotation', 'Storage loss', 'Building utilisation','Equipment utilisation','Labour requirements', 
     'Strategic segment development','Number of varieties of products on the market','Number of new cultivation techniques per year', 'Seedling success rate','Environmental complaints',
     'Production success rate','Demand planning accuracy','Proportion of products defective','Customer offerings','Customer care calls',
     'Number of new selling methods per year','Sales from new selling methods','Number of community conflicts', 'Employee capacity','Improvement proposals',
     'Complaint resolution', 'Employee satisfaction','Education opportunities', 'Administration costs','Information availability',
     'The length of courses','Employee weekends off', 'Staff development','Health and safety breaches', 'Resource consumption'),


    'measure_description': (
        'The financial return on an activity', 'The margin of cash', 'How satisfied are the customers', 'The percentage of the target market reached','Number of active customers', 
    'A quantifiable measurement of a product sold', 'The amount of cash received', 'Evaluation of the income statement', 'Value of the cost drivers',  'The profit margin per unit of of product',
     'The revenue earned divided by the number of employees', 'The cost to produce one unit of product', 'The return on various investements', 'The diversity of the investment portfolio', 'The return divided by the value of all the assets', 
     'Profit on sales after paying for variable costs of production','The value of the product minus the input costs', 'The cost of acquiring capital (investments etc.)', 'Increase the amount of money turned over','Diversify the avenues of operating profit',
     'The variety of financial expenses','The value of indirect costs','The volume/quantity of customer demand', 'The price at which products are sold', 'The price at which products are sold relative to competitors',
     'The number of return customers as a percentage of total customers', 'The number of times customers request product exchanges as a percentage of total sales', 'The number of times a mentor is required to visit a farm','Percentage or number of new customers', 'Turnover/sales to new customers',
     'The number/percentage of customers who do not return','The value of the turnover by loyal/return customers','The value of the rejected products compared to total products sold','The number of complaints divided by the number of customers','Unfulfilled demand to total demand',
     'The average delivery time of products', 'Proportion of deliveries delivered on time','Number of new sales avenues', 'The overall productivity (Time spent per product produced)', 'The perceived quality by the customers',
     'Increase the yield on the products per resource (Increase crop yield per plot)','The number of hygiene and sanitary standards and processes', 'A score out of 10 on animal wellbeing and health','Amount of feed units per animal','The yield per unit of forage used',
     'Crop rotation', 'Losses due to inadequate storage', 'The utilisation of the buildings (Time spent in use/total time)', 'The amount of time equipment is used/total time','The amount of manual labour required',
     'Number of products with strategic value', 'Number of different products on the market','The number of new culitvation techniques tried per year','The number of seedlings succeeded/total planted', 'Number of environmental related complaints',
    'Successful crop production per square meter', 'The accuracy of the demand planning', 'The proportion of products that are defective', 'The number of offers made to customers per year', 'Calls to customer care per year',
     'Total number of new selling methods/avenues per year','Proportion of sales from new selling methods', 'The number of community complaints/incidents', 'The management capacity of new employees', 'The number of improvement proposals identified',
     'Number of complaints resolved/total complaints', 'The level of employee satisfaction out of 10', 'The number of education opportunities for employees','The costs of administration and bookkeeping', 'The number of different information streams',
     'The time spent/length of education courses','Number of rest/off days', 'Time spent on staff development', 'Number of health and safety related breaches', 'Rate of resource consumption'),


    'measure_type_id': (
        'increase','increase','increase','increase','increase',
        'increase','increase','increase','increase','increase',
        'increase','decrease','increase','increase','increase',
        'increase','increase','decrease','increase','increase',
        'decrease','decrease','increase','neutral','decrease',
        'increase','decrease','decrease','increase','increase',
        'decrease','increase','decrease','decrease','decrease',
        'decrease','increase','increase','decrease','increase',
        'increase','increase','increase','decrease','increase',
        'increase','decrease','increase','increase','decrease',
        'increase','increase','increase','increase','decrease',
        'increase','increase','decrease','increase','decrease',
        'increase','increase','decrease','increase','increase',
        'increase','increase','increase','decrease','increase',
        'neutral','increase','increase','decrease','decrease')


}

    ).set_index('measure_store_catalog_id')
    write(con=con, df=df, table_name='measure_store')
    log.info("--- Created base measure store ---")


def populate_measure_sensor(con=None):
    df = pd.DataFrame (
    { 'measure_sensor_relationship_id': (
        1,2,3,4,5,
        6,7,8,9,10,
        11,12,13,14,15,
        16,17,18,19,20,
        21,22,23,24,25,
        26,27,28,29,30,
        31,32,33,34,35,
        36,37,38,39,40,
        41,42,43,44,45,
        46,47,48,49,50,
        51,52,53,54,55,
        56,57,58,59,60,
        61,62,63,64,65,
        66,67,68,69,70,
        71,72,73,74,75,
        76,77,78,79,80,
        81,82,83,84,85,
        86,87,88,89,90,
        91,92,93,94,95,
        96,97,98,99,100
        ,101,102,103,104,
        105,106,107,108,
        109,110,111,112,
        113,114,115,116,
        117,118,119,120,
        121,122,123,124,
        125,126,127,128,
        129,130,131,132,
        133,134,135,136,
        137,138,139,140,
        141,142,143,144,
        145,146,147,148,
        149,150,151,152,
        153,154,155,156,
        157,158,159),
    'measure_store_catalog_id': (1,1,1,1,2,2,2,3,3,3,4,4,5,5,6,6,7,7,7,8,8,8,8,9,9,9,9,9,10,10,10,11,11,11,11,12,13,13,15,15,15,16,16,16,17,17,17,18,18,18,20,20,20,21,21,21,22,22,22,23,23,23,23,24,24,25,25,26,26,26,27,27,27,27,28,29,30,30,30,31,31,31,32,32,32,32,33,33,34,34,34,35,39,39,39,40,41,41,41,41,41,41,41,41,41,41,41,41,45,45,45,45,45,45,45,45,45,45,45,47,48,48,50,50,50,52,54,54,54,54,54,54,54,54,54,54,54,54,54,55,58,60,61,63,67,69,75,75,75,75,75,75,75,75,75,75,75,75,75),
    'measure_store_id': ('Financial returns','Financial returns','Financial returns','Financial returns','Cash margin',
    'Cash margin','Cash margin','Customer satisfaction','Customer satisfaction',
    'Customer satisfaction','Percentage of product that hits target market','Percentage of product that hits target market','Number of active customers on database','Number of active customers on database',
    'Volume/Weight of product sold','Volume/Weight of product sold','Cash received','Cash received','Cash received',
    'Income statement','Income statement','Income statement','Income statement',
    'Cost drivers','Cost drivers','Cost drivers','Cost drivers','Cost drivers',
    'Gross margin per unit of product sold','Gross margin per unit of product sold','Gross margin per unit of product sold','Revenue per employee','Revenue per employee',
    'Revenue per employee','Revenue per employee','Overhead cost per product sold','Return on investment (ROI)','Return on investment (ROI)',
    'Return on Assets (ROA)','Return on Assets (ROA)','Return on Assets (ROA)','Operating profit margin (OPM)','Operating profit margin (OPM)',
    'Operating profit margin (OPM)','Economic value add (EVA)','Economic value add (EVA)','Economic value add (EVA)','Cost of capital (COC)',
    'Cost of capital (COC)','Cost of capital (COC)','Variation of operating profit','Variation of operating profit','Variation of operating profit','Variation of financial expenses',
    'Variation of financial expenses','Variation of financial expenses','Indirect costs','Indirect costs','Indirect costs',
    'Demand','Demand','Demand','Demand','Selling price','Selling price',
    'Selling price relative to competitors','Selling price relative to competitors','Customer loyalty','Customer loyalty','Customer loyalty',
    'Product replacement rate','Product replacement rate','Product replacement rate','Product replacement rate','Number of required mentor visits',
    'Percentage of new customers','Turnover from new customers','Turnover from new customers','Turnover from new customers','Customer lost',
    'Customer lost','Customer lost','Turnover by customer loyalty','Turnover by customer loyalty','Turnover by customer loyalty',
    'Turnover by customer loyalty','Total rejected products to total revenue','Total rejected products to total revenue','Customer complaints to total customers',
    'Customer complaints to total customers','Customer complaints to total customers','Demand satisfaction rate','Productivity','Productivity',
    'Productivity','Perceived quality','Crop/resource yield','Crop/resource yield','Crop/resource yield',
    'Crop/resource yield','Crop/resource yield','Crop/resource yield','Crop/resource yield','Crop/resource yield',
    'Crop/resource yield','Crop/resource yield','Crop/resource yield','Crop/resource yield',
    'Yeild of forage','Yeild of forage','Yeild of forage','Yeild of forage','Yeild of forage',
    'Yeild of forage','Yeild of forage','Yeild of forage','Yeild of forage',
    'Yeild of forage','Yeild of forage','Storage loss','Building utilisation',
    'Building utilisation','Labour requirements','Labour requirements','Labour requirements',
    'Number of varieties of products on the market','Seedling success rate','Seedling success rate','Seedling success rate',
    'Seedling success rate','Seedling success rate','Seedling success rate','Seedling success rate',
    'Seedling success rate','Seedling success rate','Seedling success rate','Seedling success rate',
    'Seedling success rate','Seedling success rate','Environmental complaints','Proportion of products defective',
    'Customer care calls','Number of new selling methods per year','Number of community conflicts','Employee satisfaction','Administration costs',
    'Resource consumption','Resource consumption','Resource consumption','Resource consumption','Resource consumption',
    'Resource consumption','Resource consumption','Resource consumption','Resource consumption','Resource consumption',
    'Resource consumption','Resource consumption','Resource consumption'),
    'sensor_store_catalog_id': (
        14,15,20,22,14,
        15,20,16,17,19,
        16,17,16,17,4,
        5,14,15,20,14,
        15,17,20,10,11,
        13,14,15,4,14,
        15,14,15,20,21,
        15,15,20,14,15,
        20,14,15,20,14,
        15,20,14,15,20,
        14,20,22,14,15,
        20,14,15,20,14,
        16,17,20,14,20,
        14,20,16,17,19,
        15,18,19,20,23,
        24,14,20,24,16,
        17,24,14,16,17,
        24,19,20,16,17,
        24,24,14,15,21,
        24,1,2,3,4,5,6,
        7,8,9,10,11,13,
        1,2,3,4,5,6,7,
        8,9,10,11,15,
        14,15,15,21,23,
        22,1,2,3,4,5,
        6,7,8,9,10,11,
        13,22,24,19,24,
        26,24,25,15,1,2,
        3,4,5,6,7,8,9,
        10,11,12,13),
    'sensor_store_id':( 'operating profit', 'Overhead cost', 'financial books/till', 'Product variation', 'operating profit', 'Overhead cost', 'financial books/till', 'No of customers on database', 'No of loyal/returning customers', 'Return rate', 'No of customers on database', 'No of loyal/returning customers', 'No of customers on database', 'No of loyal/returning customers', 'weight (kg)', 'weight (mg)', 'operating profit', 'Overhead cost', 'financial books/till', 'operating profit', 'Overhead cost', 'No of loyal/returning customers', 'financial books/till', 'soil NPK levels', 'electricty usage (kwh)', 'water rate usage (l/min)', 'operating profit', 'Overhead cost', 'weight (kg)', 'operating profit', 'Overhead cost', 'operating profit', 'Overhead cost', 'financial books/till', 'No of employees', 'Overhead cost', 'Overhead cost', 'financial books/till', 'operating profit', 'Overhead cost', 'financial books/till', 'operating profit', 'Overhead cost', 'financial books/till', 'operating profit', 'Overhead cost', 'financial books/till', 'operating profit', 'Overhead cost', 'financial books/till', 'operating profit', 'financial books/till', 'Product variation', 'operating profit', 'Overhead cost', 'financial books/till', 'operating profit', 'Overhead cost', 'financial books/till', 'operating profit', 'No of customers on database', 'No of loyal/returning customers', 'financial books/till', 'operating profit', 'financial books/till', 'operating profit', 'financial books/till', 'No of customers on database', 'No of loyal/returning customers', 'Return rate', 'Overhead cost', 'Delivery rate', 'Return rate', 'financial books/till', 'Mentor visit log', 'Customer tracker', 'operating profit', 'financial books/till', 'Customer tracker', 'No of customers on database', 'No of loyal/returning customers', 'Customer tracker', 'operating profit', 'No of customers on database', 'No of loyal/returning customers', 'Customer tracker', 'Return rate', 'financial books/till', 'No of customers on database', 'No of loyal/returning customers', 'Customer tracker', 'Customer tracker', 'operating profit', 'Overhead cost', 'No of employees', 'Customer tracker', 'soil moisture', 'ambient temperature', 'water level', 'weight (kg)', 'weight (mg)', 'humidity', 'soil temperature', 'light intensity', 'water quality', 'soil NPK levels', 'electricty usage (kwh)', 'water rate usage (l/min)', 'soil moisture', 'ambient temperature', 'water level', 'weight (kg)', 'weight (mg)', 'humidity', 'soil temperature', 'light intensity', 'water quality', 'soil NPK levels', 'electricty usage (kwh)', 'Overhead cost', 'operating profit', 'Overhead cost', 'Overhead cost', 'No of employees', 'Mentor visit log', 'Product variation', 'soil moisture', 'ambient temperature', 'water level', 'weight (kg)', 'weight (mg)', 'humidity', 'soil temperature', 'light intensity', 'water quality', 'soil NPK levels', 'electricty usage (kwh)', 'water rate usage (l/min)', 'Product variation', 'Customer tracker', 'Return rate', 'Customer tracker', 'New selling method tracker', 'Customer tracker', 'Employee satisfaction tracker', 'Overhead cost', 'soil moisture', 'ambient temperature', 'water level', 'weight (kg)', 'weight (mg)', 'humidity', 'soil temperature', 'light intensity', 'water quality', 'soil NPK levels', 'electricty usage (kwh)', 'power remaining', 'water rate usage (l/min)')
    }
    ).set_index('measure_sensor_relationship_id')
    write(con=con, df=df, table_name='measure_sensor')
    log.info("--- Created base measure-sensor relationship ---")

def populate_objective_measure(con=None):


   df=pd.DataFrame({ 'objective_measure_relationship_id': (1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,
      21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,
      41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,
      61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,
      81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,
      101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,
      121,122,123,124,125,126,127,128,129,130,131,132,133,134,135,136,137,138,139,140,
      141,142,143,144,145,146,147,148,149,150,151,152,153,154,155,156,157,158,159,160,
      161,162,163,164,165,166,167,168,169,170,171,172,173,174,175,176,177,178,179,180,
      181,182,183,184,185,186,187,188,189,190,191,192,193,194,195,196,197,198,199,200,
      201,202,203,204,205,206,207,208,209,210,211,212,213,214,215,216,217,218,219,220,
      221,222,223,224,225,226,227,228,229,230,231,232,233,234,235,236,237,238,239,240,
      241,242,243,244,245,246,247,248,249,250,251,252,253,254,255,256,257,258,259,260,
      261,262,263,264,265,266,267,268,269,270,271,272,273,274,275,276,277,278,279,280,
      281,282,283,284,285,286,287,288,289,290,291,292,293,294,295,296,297,298,299,300,
      301,302,303,304,305,306,307,308,309,310,311,312,313,314,315,316,317,318,319,320,
      321,322,323,324,325,326,327,328,329,330,331,332,333,334,335,336,337,338,339,340,
      341,342,343,344,345,346,347,348,349,350,351,352,353,354,355,356,357,358,359,360,
      361,362,363,364,365,366,367,368,369,370,371,372,373,374,375,376,377,378,379,380,
      381,382,383,384,385,386,387,388,389,390,391,392,393,394,395,396,397,398,399,400,
      401,402,403,404,405,406,407,408,409,410,411,412,413,414,415,416,417,418,419,420,
      421,422,423,424,425,426,427,428,429,430,431,432,433,434,435,436,437,438,439,440,
      441,442,443,444,445,446,447,448,449,450,451,452,453,454,455,456,457,458,459,
      460,461,462,463,464,465),
      
      'objective_id': ( 
 'Gain acitivity earning', 'Gain acitivity earning', 'Gain acitivity earning', 'Gain acitivity earning', 'Gain acitivity earning', 'Gain acitivity earning', 'Gain acitivity earning', 'Increase operational cash margin', 'Increase operational cash margin',
  'Increase operational cash margin', 'Increase operational cash margin', 'Increase operational cash margin', 
 'Increase operational cash margin', 'Increase operational cash margin', 
 'Increase operational cash margin', 'Increase operational cash margin', 'Increase operational cash margin', 'Increase operational cash margin', 'Increase operational cash margin', 'Increase operational cash margin', 'Increase operational cash margin',
  'Increase operational cash margin', 'Increase operational cash margin', 'Increase operational cash margin', 'Increase operational cash margin', 'Increase operational cash margin', 'Increase operational cash margin', 'Increase operational cash margin', 
  'Increase operational cash margin', 'Increase operational cash margin', 'Increase operational cash margin', 'Increase operational cash margin', 'Increase operational cash margin', 'Increase operational cash margin', 'Increase operational cash margin', 
  'Increase operational cash margin', 'Increase operational cash margin', 'Increase operational cash margin', 'Increase operational cash margin', 'Increase operational cash margin', 'Increase operational cash margin', 'Increase operational cash margin', 
  'Increase operational cash margin', 'Increase operational cash margin', 'Increase operational cash margin', 'Improve production efficiency', 'Improve production efficiency', 'Improve production efficiency', 'Improve production efficiency', 'Improve production efficiency', 
  'Improve production efficiency', 'Improve production efficiency', 'Improve production efficiency', 'Improve production efficiency', 'Improve production efficiency', 'Improve production efficiency', 'Improve production efficiency', 'Improve production efficiency',
   'Improve production efficiency', 'Improve production efficiency', 'Improve production efficiency', 'Improve production efficiency', 'Improve production efficiency', 'Improve production efficiency', 'Improve production efficiency', 'Improve production efficiency', 
   'Improve production efficiency', 'Improve production efficiency', 'Improve production efficiency', 'Increase total income', 'Increase total income', 'Increase total income', 'Increase total income', 'Increase total income', 'Increase total income', 'Increase total income',
    'Increase total income', 'Increase total income', 'Increase total income', 'Increase total income', 'Increase total income', 'Increase total income', 'Increase total income', 'Increase total income', 'Increase total income', 'Increase total income', 'Increase total income', 
    'Increase total income', 'Increase total income', 'Increase total income', 'Increase total income', 'Increase total income', 'Increase total income', 'Increase total income', 'Increase total income', 'Increase total income', 'Increase total income', 
    'Increase total income', 'Increase total income', 'Increase total income', 'Increase total income', 'Increase total income', 'Increase total income', 'Increase total income', 'Increase total income', 'Increase total income', 'Increase total income',
     'Increase total income', 'Increase total income', 'Increase total income', 'Achieve profitable & sustainable growth', 'Achieve profitable & sustainable growth', 'Achieve profitable & sustainable growth', 'Achieve profitable & sustainable growth',
      'Achieve profitable & sustainable growth', 'Achieve profitable & sustainable growth', 'Achieve profitable & sustainable growth', 'Achieve profitable & sustainable growth', 'Achieve profitable & sustainable growth', 'Achieve profitable & sustainable growth', 
      'Achieve profitable & sustainable growth', 'Achieve profitable & sustainable growth', 'Achieve profitable & sustainable growth', 'Achieve profitable & sustainable growth', 'Achieve profitable & sustainable growth', 'Achieve profitable & sustainable growth',
       'Achieve profitable & sustainable growth', 'Achieve profitable & sustainable growth', 'Achieve profitable & sustainable growth', 'Achieve profitable & sustainable growth', 'Achieve profitable & sustainable growth', 'Achieve profitable & sustainable growth',
        'Achieve profitable & sustainable growth', 'Achieve profitable & sustainable growth', 'Achieve profitable & sustainable growth', 'Achieve profitable & sustainable growth', 'Achieve profitable & sustainable growth', 'Achieve profitable & sustainable growth', 
        'Achieve profitable & sustainable growth', 'Achieve profitable & sustainable growth', 'Achieve profitable & sustainable growth', 'Achieve profitable & sustainable growth', 'Achieve profitable & sustainable growth', 'Achieve profitable & sustainable growth', 
        'Achieve profitable & sustainable growth', 'Achieve profitable & sustainable growth', 'Achieve profitable & sustainable growth', 'Achieve profitable & sustainable growth', 'Achieve profitable & sustainable growth', 'Achieve profitable & sustainable growth', 
        'Achieve profitable & sustainable growth', 'Achieve profitable & sustainable growth', 'Achieve profitable & sustainable growth', 'Achieve profitable & sustainable growth', 'Achieve profitable & sustainable growth', 'Achieve profitable & sustainable growth', 
        'Achieve profitable & sustainable growth', 'Achieve profitable & sustainable growth', 'Achieve profitable & sustainable growth', 'Achieve profitable & sustainable growth', 'Achieve profitable & sustainable growth', 'Achieve profitable & sustainable growth',
         'Achieve profitable & sustainable growth', 'Achieve profitable & sustainable growth', 'Achieve profitable & sustainable growth', 'Achieve profitable & sustainable growth', 'Achieve profitable & sustainable growth', 'Achieve profitable & sustainable growth',
          'Achieve profitable & sustainable growth', 'Achieve profitable & sustainable growth', 'Achieve profitable & sustainable growth', 'Achieve profitable & sustainable growth', 'Achieve profitable & sustainable growth', 'Achieve profitable & sustainable growth', 
          'Achieve profitable & sustainable growth', 'Achieve profitable & sustainable growth', 'Achieve profitable & sustainable growth', 'Achieve profitable & sustainable growth', 'Achieve profitable & sustainable growth', 'Achieve profitable & sustainable growth',
           'Achieve profitable & sustainable growth', 'Achieve profitable & sustainable growth', 'Decrease of financial costs/ Reduce indirect expenditure', 'Decrease of financial costs/ Reduce indirect expenditure', 'Reduce operational costs', 'Reduce operational costs',
            'Reduce operational costs', 'Reduce operational costs', 'Reduce operational costs', 'Reduce operational costs', 'Reduce operational costs', 'Reduce operational costs', 'Reduce operational costs', 'Reduce operational costs', 'Reduce operational costs',
             'Reduce operational costs', 'Reduce operational costs', 'Reduce operational costs', 'Set up high level of customer satisfaction', 'Set up high level of customer satisfaction', 'Set up high level of customer satisfaction', 'Set up high level of customer satisfaction',
              'Set up high level of customer satisfaction', 'Set up high level of customer satisfaction', 'Set up high level of customer satisfaction', 'Set up high level of customer satisfaction', 'Set up high level of customer satisfaction', 'Set up high level of customer satisfaction',
               'Set up high level of customer satisfaction', 'Set up high level of customer satisfaction', 'Set up high level of customer satisfaction', 'Set up high level of customer satisfaction', 'Set up high level of customer satisfaction', 
               'Set up high level of customer satisfaction', 'To set up competitive prices', 'To set up competitive prices', 'To set up competitive prices', 'To set up competitive prices', 'To set up competitive prices', 'To set up competitive prices',
                'To set up competitive prices', 'To set up competitive prices', 'To set up competitive prices', 'To set up competitive prices', 'To set up competitive prices', 'To set up competitive prices', 'To set up competitive prices', 'To set up competitive prices',
                 'To set up competitive prices', 'To set up competitive prices', 'To set up competitive prices', 'To set up competitive prices', 'To set up competitive prices', 'To set up competitive prices', 'To set up competitive prices', 'To set up competitive prices', 
                 'To set up competitive prices', 'To set up competitive prices', 'To set up competitive prices', 'To set up competitive prices', 'To set up competitive prices', 'To set up competitive prices', 'To set up competitive prices', 'To set up competitive prices', 'Increase customer base',
                  'Increase customer base', 'Increase customer base', 'Increase customer base', 'Increase customer base', 'Increase customer base', 'Increase customer base', 'Increase customer base', 'Increase customer base', 'Increase customer base', 'Customer loyalty', 'Customer loyalty', 
                  'Customer loyalty', 'Customer loyalty', 'Customer loyalty', 'Customer loyalty', 'Image of the agricultural farm', 'Image of the agricultural farm', 'Image of the agricultural farm', 'Image of the agricultural farm', 'Image of the agricultural farm', 'Image of the agricultural farm',
                   'Image of the agricultural farm', 'Image of the agricultural farm', 'Image of the agricultural farm', 'Image of the agricultural farm', 'Quality of produce', 'Quality of produce', 'Meet customer demand', 'Meet customer demand', 'Meet customer demand', 'Meet customer demand',
                    'Meet customer demand', 'Meet customer demand', 'Meet customer demand', 'Meet customer demand', 'Meet customer demand', 'Improve product delivery', 'Improve product delivery', 'Increase customer network', 'Increase customer network', 'Increase customer network', 
                    'Increase customer network', 'Increase customer network', 'Increase customer network', 'Increase level of productivity ', 'Increase level of productivity ', 'Increase level of productivity ', 'Increase level of productivity ', 'Increase level of productivity ',
                     'Increase level of productivity ', 'Increase level of productivity ', 'Increase level of productivity ', 'Increase level of productivity ', 'Increase level of productivity ', 'Increase level of productivity ', 'Increase level of productivity ', 
                     'Increase level of productivity ', 'Increase level of productivity ', 'Increase level of productivity ', 'Increase level of productivity ', 'Increase level of productivity ', 'Increase level of productivity ', 'Increase product quality', 'Increase product quality',
                      'Increase product quality', 'Increase product quality', 'Increase product quality', 'Increase product quality', 'Improve utilisation of feed', 'Higher yield of forage ', 'Higher yield of forage ', 'Less stoarge loss of forage', 'Improve utilisation of buildings', 'Improve utilisation of machinery', 
                      'Improve utilisation of machinery', 'Improve utilisation of machinery', 'Improve utilisation of machinery', 'Improve utilisation of machinery', 'Improve utilisation of machinery', 'Improve utilisation of machinery', 'Improve utilisation of machinery',
                       'Improve utilisation of machinery', 'Improve utilisation of machinery', 'Reduce the use of labour', 'Reduce the use of labour', 'Reduce the use of labour', 'Reduce the use of labour', 'Reduce the use of labour', 'Reduce the use of labour',
                        'Reduce the use of labour', 'Reduce the use of labour', 'Reduce the use of labour', 'Reduce the use of labour', 'Reduce the use of labour', 'Reduce the use of labour', 'Reduce the use of labour', 'Reduce the use of labour', 'Reduce the use of labour', 'Development of strategic segments', 
                        'Development of strategic segments', 'Development of strategic segments', 'Development of strategic segments', 'Development of innovative processes', 'Development of innovative processes', 'Development of innovative processes', 'Development of innovative processes', 
                        'Development of innovative processes', 'Development of innovative processes', 'Development of innovative processes', 'Development of innovative processes', 'Development of innovative processes', 'Observance of environmental laws', 'Observance of environmental laws', 
                        'Observance of environmental laws', 'Observance of environmental laws', 'Soil processing and fertilising', 'Soil processing and fertilising', 'Soil processing and fertilising', 'Soil processing and fertilising', 'Soil processing and fertilising', 
                        'Soil processing and fertilising', 'Soil processing and fertilising', 'Soil processing and fertilising', 'Soil processing and fertilising', 'Soil processing and fertilising', 'Soil processing and fertilising', 'Soil processing and fertilising', 
                        'Soil processing and fertilising', 'Soil processing and fertilising', 'Quality of plant cultivation', 'Quality of plant cultivation', 'Quality of plant cultivation', 'Quality of plant cultivation', 'Quality of plant cultivation', 'Quality of plant cultivation',
                         'Quality of plant cultivation', 'Quality of plant cultivation', 'Quality of plant cultivation', 'Quality of plant cultivation', 'Quality of plant cultivation', 'Quality of plant cultivation', 'On time and in full products', 'On time and in full products', 
                         'On time and in full products', 'On time and in full products', 'On time and in full products', 'On time and in full products', 'On time and in full products', 'On time and in full products', 'On time and in full products', 'Customer communication', 'Customer communication', 
                         'Customer communication', 'Develop new selling methods', 'Develop new selling methods', 'Develop new selling methods', 'Create interdependency between the firm and the community', 'Create interdependency between the firm and the community', 'Create interdependency between the firm and the community',
                          'Create interdependency between the firm and the community', 'Create interdependency between the firm and the community', 'Create interdependency between the firm and the community', 'Create interdependency between the firm and the community', 'Create interdependency between the firm and the community',
                           'Create interdependency between the firm and the community', 'Create interdependency between the firm and the community', 'Create interdependency between the firm and the community', 'Create interdependency between the firm and the community', 
                           'Create interdependency between the firm and the community', 'Increase product offering', 'Increase product offering', 'Increase product offering', 'Increase product offering', 'Increase product offering', 'Increase product offering', 'Increase product offering', 
                           'Increase product offering', 'Increase product offering', 'Improve managerial/partner and technical competences', 'Improve managerial/partner and technical competences', 'Improve managerial/partner and technical competences', 
                           'Improve managerial/partner and technical competences', 'Provide employee motivation', 'Provide employee motivation', 'Provide employee motivation', 'Provide employee motivation', 'Provide employee motivation', 'Use of better information systems', 'Development of managerial competences',
                            'Development of managerial competences', 'Development of managerial competences', 'Develop safety protocols to protect staff', 'Develop safety protocols to protect staff', 'Develop safety protocols to protect staff', 'Develop safety protocols to protect staff', 'Implement practises that employ and retain best staff',
                             'Implement practises that employ and retain best staff', 'Implement practises that employ and retain best staff', 'Implement practises that employ and retain best staff', 'Create organisation with strong and constructive culture', 'Create organisation with strong and constructive culture', 'Create organisation with strong and constructive culture',
                              'Create organisation with strong and constructive culture', 'Create organisation with strong and constructive culture', 'Parner/employee satisfaction', 'Parner/employee satisfaction', 'Parner/employee satisfaction', 'Parner/employee satisfaction', 'Parner/employee satisfaction', 'Parner/employee satisfaction', 
                              'Parner/employee satisfaction', 'Parner/employee satisfaction', 'Parner/employee satisfaction', 'Parner/employee satisfaction', 'Parner/employee satisfaction', 'Parner/employee satisfaction', 'Parner/employee satisfaction', 'Parner/employee satisfaction', 'Parner/employee satisfaction',
                               'Parner/employee satisfaction'
      ),

      'measure_store_catalog_id': (1,2,8,19,20,21,29,1,2,6,7,8,9,10,11,12,13,15,16,17,18,19,22,23,24,27,33,39,41,44,45,46,47,48,49,50,51,53,54,57,58,61,65,69,75,20,22,27,7,29,40,41,42,43,44,45,46,47,48,49,50,54,57,58,61,65,68,70,75,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,19,22,24,25,26,27,29,39,41,44,45,46,47,48,49,50,51,54,56,57,58,64,69,70,75,1,2,3,4,5,6,7,9,10,11,12,13,14,15,16,17,18,20,21,22,23,24,25,26,27,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,10,12,12,22,41,42,43,45,46,47,48,49,50,51,53,69,25,27,33,34,35,36,37,42,52,55,58,59,60,63,66,70,4,6,7,12,17,18,20,21,22,24,25,27,39,41,43,44,45,46,47,48,49,50,51,53,54,56,57,58,65,69,24,25,31,51,52,58,59,60,63,66,3,5,26,31,32,34,3,26,28,34,40,42,55,60,66,74,3,40,23,35,36,37,40,41,42,57,58,36,37,24,25,59,60,63,66,1,2,3,4,6,11,27,39,41,44,45,46,49,50,54,56,58,75,3,6,26,40,41,46,44,44,45,47,48,1,6,9,13,15,18,19,22,39,49,11,22,39,41,42,44,45,46,49,50,53,65,67,68,73,51,61,65,68,51,53,61,65,68,70,71,73,75,55,63,66,70,6,17,19,22,39,40,41,43,45,46,50,54,56,75,3,4,6,26,27,32,33,34,40,52,53,54,23,35,36,37,39,41,56,57,58,60,66,70,61,62,70,26,29,31,32,33,34,35,55,59,60,63,66,67,38,41,45,46,51,52,53,61,62,70,71,72,73,67,68,70,72,73,70,70,71,73,70,71,73,74,70,71,73,74,70,71,72,73,74,1,2,5,6,7,8,11,13,14,15,16,17,70,72,73,74),
            
            'measure_store_id': (  'Financial returns', 'Cash margin', 'Income statement', 'Increase turnover', 'Variation of operating profit', 'Variation of financial expenses', 'Percentage of new customers', 'Financial returns', 'Cash margin', 'Volume/Weight of product sold', 'Cash received', 'Income statement', 
            'Cost drivers', 'Gross margin per unit of product sold', 'Revenue per employee', 'Overhead cost per product sold', 'Return on investment (ROI)', 'Return on Assets (ROA)', 'Operating profit margin (OPM)', 'Economic value add (EVA)', 'Cost of capital (COC)', 'Increase turnover', 'Indirect costs', 'Demand', 
            'Selling price', 'Product replacement rate', 'Total rejected products to total revenue', 'Productivity', 'Crop/resource yield', 'Feed units per animal', 'Yeild of forage', 'Crop rotation', 'Storage loss', 'Building utilisation', 'Equipment utilisation', 'Labour requirements', 'Strategic segment development', 
            'Number of new cultivation techniques per year', 'Seedling success rate', 'Demand planning accuracy', 'Proportion of products defective', 'Number of new selling methods per year', 'Improvement proposals', 'Administration costs', 'Resource consumption', 'Variation of operating profit', 'Indirect costs', 'Product replacement rate',
             'Cash received', 'Percentage of new customers', 'Perceived quality', 'Crop/resource yield', 'Hygiene and sanitary standards', 'Animal condition score', 'Feed units per animal', 'Yeild of forage', 'Crop rotation', 'Storage loss', 'Building utilisation', 'Equipment utilisation', 'Labour requirements', 'Seedling success rate', 
             'Demand planning accuracy', 'Proportion of products defective', 'Number of new selling methods per year', 'Improvement proposals', 'Education opportunities', 'Information availability', 'Resource consumption', 'Financial returns', 'Cash margin', 'Customer satisfaction', 'Percentage of product that hits target market', 
             'Number of active customers on database', 'Volume/Weight of product sold', 'Cash received', 'Income statement', 'Cost drivers', 'Gross margin per unit of product sold', 'Revenue per employee', 'Overhead cost per product sold', 'Return on investment (ROI)', 'Invesment portfolio', 'Return on Assets (ROA)', 'Operating profit margin (OPM)', 
             'Increase turnover', 'Indirect costs', 'Selling price', 'Selling price relative to competitors', 'Customer loyalty', 'Product replacement rate', 'Percentage of new customers', 'Productivity', 'Crop/resource yield', 'Feed units per animal', 'Yeild of forage', 'Crop rotation', 'Storage loss', 'Building utilisation', 'Equipment utilisation',
              'Labour requirements', 'Strategic segment development', 'Seedling success rate', 'Production success rate', 'Demand planning accuracy', 'Proportion of products defective', 'Employee capacity', 'Administration costs', 'Information availability', 'Resource consumption', 'Financial returns', 'Cash margin', 'Customer satisfaction', 
              'Percentage of product that hits target market', 'Number of active customers on database', 'Volume/Weight of product sold', 'Cash received', 'Cost drivers', 'Gross margin per unit of product sold', 'Revenue per employee', 'Overhead cost per product sold', 'Return on investment (ROI)', 'Invesment portfolio', 'Return on Assets (ROA)',
               'Operating profit margin (OPM)', 'Economic value add (EVA)', 'Cost of capital (COC)', 'Variation of operating profit', 'Variation of financial expenses', 'Indirect costs', 'Demand', 'Selling price', 'Selling price relative to competitors', 'Customer loyalty', 'Product replacement rate', 'Percentage of new customers', 
               'Turnover from new customers', 'Customer lost', 'Turnover by customer loyalty', 'Total rejected products to total revenue', 'Customer complaints to total customers', 'Demand satisfaction rate', 'Delivery time', 'On time delivery', 'Number of sales proposals per month', 'Productivity', 'Perceived quality', 'Crop/resource yield',
                'Hygiene and sanitary standards', 'Animal condition score', 'Feed units per animal', 'Yeild of forage', 'Crop rotation', 'Storage loss', 'Building utilisation', 'Equipment utilisation', 'Labour requirements', 'Strategic segment development', 'Number of varieties of products on the market', 'Number of new cultivation techniques per year',
                 'Seedling success rate', 'Environmental complaints', 'Production success rate', 'Demand planning accuracy', 'Proportion of products defective', 'Customer offerings', 'Customer care calls', 'Number of new selling methods per year', 'Sales from new selling methods', 'Number of community conflicts', 'Employee capacity', 'Improvement proposals', 
                 'Complaint resolution', 'Employee satisfaction', 'Education opportunities', 'Administration costs', 'Information availability', 'The length of courses', 'Employee weekends off', 'Staff development', 'Health and safety breaches', 'Resource consumption', 'Gross margin per unit of product sold', 'Overhead cost per product sold', 'Overhead cost per product sold', 
                 'Indirect costs', 'Crop/resource yield', 'Hygiene and sanitary standards', 'Animal condition score', 'Yeild of forage', 'Crop rotation', 'Storage loss', 'Building utilisation', 'Equipment utilisation', 'Labour requirements', 'Strategic segment development', 'Number of new cultivation techniques per year', 'Administration costs', 
                 'Selling price relative to competitors', 'Product replacement rate', 'Total rejected products to total revenue', 'Customer complaints to total customers', 'Demand satisfaction rate', 'Delivery time', 'On time delivery', 'Hygiene and sanitary standards', 'Number of varieties of products on the market', 'Environmental complaints',
                  'Proportion of products defective', 'Customer offerings', 'Customer care calls', 'Number of community conflicts', 'Complaint resolution', 'Information availability', 'Percentage of product that hits target market', 'Volume/Weight of product sold', 'Cash received', 'Overhead cost per product sold', 'Economic value add (EVA)', 
                  'Cost of capital (COC)', 'Variation of operating profit', 'Variation of financial expenses', 'Indirect costs', 'Selling price', 'Selling price relative to competitors', 'Product replacement rate', 'Productivity', 'Crop/resource yield', 'Animal condition score', 'Feed units per animal', 'Yeild of forage', 'Crop rotation', 'Storage loss',
                   'Building utilisation', 'Equipment utilisation', 'Labour requirements', 'Strategic segment development', 'Number of new cultivation techniques per year', 'Seedling success rate', 'Production success rate', 'Demand planning accuracy', 'Proportion of products defective', 'Improvement proposals', 'Administration costs', 'Selling price', 
                   'Selling price relative to competitors', 'Customer lost', 'Strategic segment development', 'Number of varieties of products on the market', 'Proportion of products defective', 'Customer offerings', 'Customer care calls', 'Number of community conflicts', 'Complaint resolution', 'Customer satisfaction', 'Number of active customers on database',
                    'Customer loyalty', 'Customer lost', 'Turnover by customer loyalty', 'Customer complaints to total customers', 'Customer satisfaction', 'Customer loyalty', 'Number of required mentor visits', 'Customer complaints to total customers', 'Perceived quality', 'Hygiene and sanitary standards', 'Environmental complaints', 
                    'Customer care calls', 'Complaint resolution', 'Health and safety breaches', 'Customer satisfaction', 'Perceived quality', 'Demand', 'Demand satisfaction rate', 'Delivery time', 'On time delivery', 'Perceived quality', 'Crop/resource yield', 'Hygiene and sanitary standards', 'Demand planning accuracy',
                     'Proportion of products defective', 'Delivery time', 'On time delivery', 'Selling price', 'Selling price relative to competitors', 'Customer offerings', 'Customer care calls', 'Number of community conflicts', 'Complaint resolution', 'Financial returns', 'Cash margin', 'Customer satisfaction', 'Percentage of product that hits target market',
                      'Volume/Weight of product sold', 'Revenue per employee', 'Product replacement rate', 'Productivity', 'Crop/resource yield', 'Feed units per animal', 'Yeild of forage', 'Crop rotation', 'Equipment utilisation', 'Labour requirements', 'Seedling success rate', 'Production success rate', 'Proportion of products defective', 'Resource consumption', 
                      'Customer satisfaction', 'Volume/Weight of product sold', 'Customer loyalty', 'Perceived quality', 'Crop/resource yield', 'Crop rotation', 'Feed units per animal', 'Feed units per animal', 'Yeild of forage', 'Storage loss', 'Building utilisation', 'Financial returns', 'Volume/Weight of product sold', 'Cost drivers', 'Return on investment (ROI)',
                       'Return on Assets (ROA)', 'Cost of capital (COC)', 'Increase turnover', 'Indirect costs', 'Productivity', 'Equipment utilisation', 'Revenue per employee', 'Indirect costs', 'Productivity', 'Crop/resource yield', 'Hygiene and sanitary standards', 'Feed units per animal', 'Yeild of forage', 'Crop rotation', 'Equipment utilisation', 
                       'Labour requirements', 'Number of new cultivation techniques per year', 'Improvement proposals', 'Employee satisfaction', 'Education opportunities', 'Staff development', 'Strategic segment development', 'Number of new selling methods per year', 'Improvement proposals', 'Education opportunities', 'Strategic segment development',
                        'Number of new cultivation techniques per year', 'Number of new selling methods per year', 'Improvement proposals', 'Education opportunities', 'Information availability', 'The length of courses', 'Staff development', 'Resource consumption', 'Environmental complaints', 'Number of community conflicts', 'Complaint resolution',
                         'Information availability', 'Volume/Weight of product sold', 'Economic value add (EVA)', 'Increase turnover', 'Indirect costs', 'Productivity', 'Perceived quality', 'Crop/resource yield', 'Animal condition score', 'Yeild of forage', 'Crop rotation', 'Labour requirements', 'Seedling success rate', 'Production success rate', 
                         'Resource consumption', 'Customer satisfaction', 'Percentage of product that hits target market', 'Volume/Weight of product sold', 'Customer loyalty', 'Product replacement rate', 'Turnover by customer loyalty', 'Total rejected products to total revenue', 'Customer complaints to total customers', 'Perceived quality',
                          'Number of varieties of products on the market', 'Number of new cultivation techniques per year', 'Seedling success rate', 'Demand', 'Demand satisfaction rate', 'Delivery time', 'On time delivery', 'Productivity', 'Crop/resource yield', 'Production success rate', 'Demand planning accuracy', 'Proportion of products defective', 
                          'Customer care calls', 'Complaint resolution', 'Information availability', 'Number of new selling methods per year', 'Sales from new selling methods', 'Information availability', 'Customer loyalty', 'Percentage of new customers', 'Customer lost', 'Turnover by customer loyalty', 'Total rejected products to total revenue', 
                          'Customer complaints to total customers', 'Demand satisfaction rate', 'Environmental complaints', 'Customer offerings', 'Customer care calls', 'Number of community conflicts', 'Complaint resolution', 'Employee satisfaction', 'Number of sales proposals per month', 'Crop/resource yield', 'Yeild of forage', 'Crop rotation', 
                          'Strategic segment development', 'Number of varieties of products on the market', 'Number of new cultivation techniques per year', 'Number of new selling methods per year', 'Sales from new selling methods', 'Information availability', 'The length of courses', 'Employee weekends off', 'Staff development', 'Employee satisfaction',
                           'Education opportunities', 'Information availability', 'Employee weekends off', 'Staff development', 'Information availability', 'Information availability', 'The length of courses', 'Staff development', 'Information availability', 'The length of courses', 'Staff development', 'Health and safety breaches', 'Information availability', 
                           'The length of courses', 'Staff development', 'Health and safety breaches', 'Information availability', 'The length of courses', 'Employee weekends off', 'Staff development', 'Health and safety breaches', 'Financial returns', 'Cash margin', 'Number of active customers on database', 'Volume/Weight of product sold', 'Cash received', 
                           'Income statement', 'Revenue per employee', 'Return on investment (ROI)', 'Invesment portfolio', 'Return on Assets (ROA)', 'Operating profit margin (OPM)', 'Economic value add (EVA)', 'Information availability', 'Employee weekends off', 'Staff development', 'Health and safety breaches')  
 



    }).set_index('objective_measure_relationship_id')
   write(con=con, df=df, table_name='objective_measure')
   log.info("--- Created base objective-measure relationship ---")




def populate_product_store(con=None):

    df = pd.DataFrame({
        "product_id": ("cabbage", "kale", "beans", "spinach", "pumpkin", "strawberry" , "rosemary", "chives") ,
        "product_description": ("plain cabbage", "southern kale", "broad beans","spinach", "pumpkin", "strawberry",
        "rosemary", "chives")




    }).set_index('product_id')
    write(con=con, df=df, table_name='product_store')
    log.info("--- Created base product store table ---")


def populate_resource_type(con=None):

    df = pd.DataFrame(
        { "resource_type_id": ('water','water','finance','plant_nutrients',
                                'animal_feed','animal_feed','seed',
                                'fertilizer','soil','mentor',
                                'finance'),
        "resource_type": ('water_tank', 'borehole','cash' ,'plant_food',
                            'seeds', 'hay_and_grass', 'crop_seeds',
                            'soil_fertilizer', 'top_soil', 'mentor', 'bank_account' ),
        "source": ('municipal', 'borehole','government', 'store',
        'store','store', 'store', 'store','store','government', 'donor' )

        }


    ).set_index('resource_type_id')
    write(con=con, df=df, table_name='resource_type')
    log.info("--- Created base resource type table ---")

def run(con=None):
    try:
        populate_measure_type(con=con)
        populate_perspectives(con=con)
        populate_entity_type(con=con)
        populate_sensor_store(con=con)
        populate_objective_store(con=con)
        populate_measure_store(con=con)
        populate_measure_sensor(con=con)
        populate_objective_measure(con=con)
        populate_product_store(con=con)
        populate_resource_type(con=con)
    except ValueError as e:
        print(e)


if __name__ == '__main__':
    parser = argparse.ArgumentParser('Populating the database')

    args = parser.parse_args()
    db_obj = DbSession(**settings.DATABASE)
    session = db_obj.session
    engine = db_obj.engine
    run(con=engine)
