from biobb_disgenet.disgenet.dda_disgenet import dda_disgenet

prop = {
        'disease_id': 'C0002395',
        'pvalue': '0.3',
        'limit': '10',
        'format': 'json'
        }

dda_disgenet(output_file_path='output_genes', shared_by="variants", properties=prop)
