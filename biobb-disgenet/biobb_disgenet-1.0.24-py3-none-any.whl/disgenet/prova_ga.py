from biobb_disgenet.disgenet.da_disgenet import da_disgenet

prop = {
        'disease_id': '331.0',
        'vocabulary': 'icd9cm',
        'limit': '10',
        'format': 'json'
        }

da_disgenet(output_file_path='output_genes', retrieve_by="mappings", properties=prop)
