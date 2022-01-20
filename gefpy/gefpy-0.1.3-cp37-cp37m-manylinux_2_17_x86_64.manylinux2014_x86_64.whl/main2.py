from gefpy.cell_exp_writer import CellExpWriterPy

def main():
    # gem_file = '/jdfssz2/ST_BIGDATA/Stereomics/autoanalysis_backup/P20Z10200N0157/null/FP200000617TL_B6_web_2_backup/result/FP200000617TL_B6_web_2/02.alignment/GetExp/barcode_gene_exp.txt'
    # mask_file = '/zfssz3/ST_BIGDATA/stereomics/PipelineTest/data/FP200000617TL_B6/7_result/FP200000617TL_B6_mask.tif'
    # gem_file = '../test_data/barCode.txt'
    mask_file=  '/getpy/test_data/mask.tif'
    gef_file = '/getpy/test_data/barCode_gef/stereomics.h5'
    out_file = '/getpy/test_data/barCode_output_test9.gef'
#    mask_file = '/getpy/test_data/FP200000617TL_B6_mask.tif'
#    out_file = '/getpy/test_data/output_test8.gef'
#    gef_file = '/getpy/test_data/barcode_gene_exp_gef/stereomics.h5'
    # gem_file = '/getpy/test_data/barcode_gene_exp.txt'
    # mask_file = '../test_data/FP200000617TL_B6_mask.tif'
    ce = CellExpWriterPy(gef_file, mask_file, out_file)
    ce.write()


if __name__ == '__main__':
    main()
