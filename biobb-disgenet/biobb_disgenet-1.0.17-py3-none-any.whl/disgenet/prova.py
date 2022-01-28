from biobb_disgenet.disgenet.gda_disgenet import gda_disgenet

prop = {
        'disease_id':'331.0',
        'vocabulary': 'icd9cm',
        'format': 'json'
        }

gda_disgenet(output_file_path='output_genes', retrieve_by="disease", properties=prop)
