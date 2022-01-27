
import unittest

from sasdbpy.sasdbreader.SasDbReader import SasDbReader






# test we get all the files from the folder

# fot the subfolder, make sure we also get the file

# for each of the file, make sure we get the right meta data : fields, fields details, size in rows and columns

class TestSasDbReader(unittest.TestCase):


    @classmethod
    def setUpClass(cls):
        
        FOLDER_PATH = './sasdbpy/test/test_data/'

        cls.sasReader = SasDbReader(FOLDER_PATH)
        cls.LIST_ALL_FILES = [
                    'demand.sas7bdat',
                    'sheep.sas7bdat',
                    'airline.sas7bdat',
                    'insur.sas7bdat']
        cls.SEARCH_FIELD_RESULTS = [
            ('A', {
                'XBAR': 'average expenditure on labor, materials, service and rent',
                'QBAR': 'average wool and lamb output',
                'LBAR': 'average number of livestock',
                'KBAR': 'average land and capital input',
                'YEAR': 'year',
                'INSURANCE': 'household insurance in thousands of dollars'}),
            ('D', {
                'DISTRICT': 'district number'
            }),
            ('INSURANCE',{
                'INSURANCE': 'household insurance in thousands of dollars'
            })
            ]
        cls.SEARCH_FIELD_DESCRIPTION_RESULTS = [
            ('household',{
                'INSURANCE': 'household insurance in thousands of dollars',
                'INCOME': 'household income in thousands of dollars'
            }),
            ('quantity', {
                'Q1': 'quantity of meat',
                'Q2': 'quantity of fruit and vegetables',
                'Q3': 'quantity of cereal and bakery products'
            }),
            ('input',{
                'KBAR': 'average land and capital input',
                'L': 'labor input',
                'K': 'capital input'
            })
        ]

        cls.DETAIL_FIELDS_MAPS = [
            ('demand', {
                'P1': 'price of meat',
                'P2': 'price of fruit and vegetables',
                'P3': 'price of cereal and bakery products',
                'Y': 'income',
                'Q1': 'quantity of meat',
                'Q2': 'quantity of fruit and vegetables',
                'Q3': 'quantity of cereal and bakery products'
            }),
            ('sheep', {
                'XBAR': 'average expenditure on labor, materials, service and rent',
                'QBAR': 'average wool and lamb output',
                'N': 'number of grazing properties in district',
                'LBAR': 'average number of livestock',
                'KBAR': 'average land and capital input',
                'DISTRICT': 'district number'
            }),
            ('airline', {
                'YEAR': 'year',
                'Y': 'level of output',
                'W': 'wage rate',
                'R': 'interest rate',
                'L': 'labor input',
                'K': 'capital input'
            }),
            ('insur', {
                'INSURANCE': 'Household insurance in thousands of dollars',
                'INCOME': 'Household income in thousands of dollars'
            })
        ]
        

    def test_list_files(self):
        self.assertEqual(
            [r[1] for r in self.sasReader.all_files],
            self.LIST_ALL_FILES
        )
    
    def test_search_field(self):
        for search_field, expected_result in self.SEARCH_FIELD_RESULTS:
            actual_result = self.sasReader.search_field(search_field)
            self.assertEqual(
                actual_result,
                expected_result
            )
    def test_search_field_description(self):
        for search_field, expected_result in self.SEARCH_FIELD_DESCRIPTION_RESULTS:
            actual_result = self.sasReader.search_field_description(search_field)
            self.assertEqual(
                actual_result,
                expected_result
            )
    def test_detail_fields_maps(self):
        for db_name, expected_detail_fields in self.DETAIL_FIELDS_MAPS:
            actual_detail_fields = self.sasReader.res_data[db_name]['detail_fields']
            self.assertEqual(
                actual_detail_fields,
                expected_detail_fields
            )

if __name__ == "__main__":
    unittest.main()
