import configparser
import os
import shutil
import textwrap
from pathlib import Path

from phylofisher import help_formatter, subset_tools


def make_subset_tsv():
    df = gene_comp.to_frame()
    df = df.rename(columns={0: 'Completeness'})
    df = df = df.sort_values(by=['Completeness'], ascending=False)
    df = df.round({'Completeness': 3})
    to_keep = ['no' for k in df.index]
    df['Include in Subset'] = to_keep

    if args.gene_number:
        num_to_keep = args.gene_number
    else:
        if args.percent_complete > 1:
            args.percent_complete = args.percent_complete / 100
        num_to_keep = int(round(args.percent_complete * len(df)))

    i = 1
    for gene, row in df.iterrows():
        if i <= num_to_keep:
            df.at[gene, 'Include in Subset'] = 'yes'
        i += 1

    df.to_csv(f'{args.output}/orthologs_subset.tsv', sep='\t')


def parse_subset_tsv():
    """

    :param tsv_file:
    :return:
    """
    with open(args.subset, 'r') as infile:
        infile.readline()
        genes_to_include = []
        for line in infile:
            line = line.strip()
            taxon, _, include = line.split('\t')
            if include == 'yes':
                genes_to_include.append(taxon)

    return genes_to_include


def gene_subsetter():
    if os.path.isdir(args.output) is False:
        os.makedirs(args.output)

    genes = parse_subset_tsv()
    files = [os.path.join(args.input, x) for x in os.listdir(args.input) if x.endswith('.fas')]
    for gene in genes:
        for file in files:
            if gene == os.path.basename(file).split('.')[0]:
                src = file
                dest = f'{args.output}/{os.path.basename(file)}'
                shutil.copy(src, dest)


if __name__ == '__main__':
    description = 'Subsets gene based on gene completeness.'
    parser, optional, required = help_formatter.initialize_argparse(name='subset_orthologs.py',
                                                                    desc=description,
                                                                    usage='subset_orthologs.py '
                                                                          '[OPTIONS] -i <input>')

    # Optional Arguments
    optional.add_argument('--subset', type=str, metavar='orthologs_subset.tsv', default=None,
                          help=textwrap.dedent("""\
                          Subset input genes
                          """))
    optional.add_argument('-n', '--gene_number', type=int, metavar='<N>', default=None,
                          help=textwrap.dedent("""\
                          Number of genes in subset.
                          This will be ignored if not used with --subset.
                          Cannot be used with percent_complete.
                          """))
    optional.add_argument('-c', '--percent_complete', type=float, metavar='<N>', default=None,
                          help=textwrap.dedent("""\
                          Threshold for percent missing when subsetting.
                          This will be ignored if not used with --subset.
                          Cannot be used with gene_number.
                          """))

    args = help_formatter.get_args(parser, optional, required, pre_suf=False)

    config = configparser.ConfigParser()
    config.read('config.ini')
    dfo = str(Path(config['PATHS']['dataset_folder']).resolve())
    metadata = f'{dfo}/metadata.tsv'

    if not os.path.isdir(args.output):
        os.makedirs(args.output)

    if not args.subset:
        gene_comp, taxa_count = subset_tools.completeness(args=args, input_dir=args.input, genes=True)
        # subset_tools.make_plot(gene_comp, f'{args.output}/gene_comp', y_count=taxa_count, genes=True)
        make_subset_tsv()
    else:
        gene_subsetter()
