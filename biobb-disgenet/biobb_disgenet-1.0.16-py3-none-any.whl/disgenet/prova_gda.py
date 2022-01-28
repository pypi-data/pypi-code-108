from biobb_disgenet.disgenet.vda_disgenet import vda_disgenet

prop = {
        'disease_id': 'C0002395',
        'min_score': '0.2',
        'max_score': '0.8',
        'limit': '10',
        'format': 'json'
        }

vda_disgenet(output_file_path='output_genes', retrieve_by="evidences", properties=prop)
