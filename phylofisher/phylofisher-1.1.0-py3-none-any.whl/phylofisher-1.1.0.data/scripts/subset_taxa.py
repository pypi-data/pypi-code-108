import configparser
import os
import textwrap
from collections import defaultdict
from pathlib import Path

from Bio import SeqIO

from phylofisher import help_formatter, subset_tools


def parse_metadata():
    """
    Parses metadata.csv to get all org names in each group and subtax
    Input: NONE
    Output: (1) dictionary with groups/subtax as keys and sets of orgs in those groups/subtax as values
            (2) list of all orgs in metadata
    """
    taxa_dict = {}
    with open(metadata, 'r') as infile:
        for line in infile:
            line = line.strip()
            if "Full Name" not in line:
                org, _, group, subtax, _, _ = line.split('\t')
                taxa_dict[org] = [group, subtax]

    return taxa_dict


def parse_user_inc_exc(input_file):
    """

    :return:
    """
    with open(input_file, 'r') as infile:
        user_set = set()
        for line in infile:
            line = line.strip()
            user_set.add(line)

        return user_set


def make_subset_tsv():
    """

    :return:
    """
    taxa = parse_metadata()
    df = taxa_comp.to_frame()
    df = df.rename(columns={0: 'Completeness'})

    # Add Taxonomic Groups to DataFrame
    high_tax_list = [taxa[ind][0] for ind in df.index]
    df['Higher Taxonomy'] = high_tax_list
    low_tax_list = [taxa[ind][1] for ind in df.index]
    df['Lower Taxonomy'] = low_tax_list

    # Reorder DataFrame putting completeness in last column and sort
    cols = df.columns.tolist()
    cols = cols[1:] + cols[:1]
    df = df.round({'Completeness': 3})
    df = df[cols]
    df = df.sort_values(by=['Higher Taxonomy', 'Lower Taxonomy', 'Completeness'])

    # Add "Include in Subset" column to DataFrame and pre-fill out
    to_keep = ['yes' for k in df.index]
    df['Include in Subset'] = to_keep

    if args.to_include:
        include_set = parse_user_inc_exc(args.to_include)
    else:
        include_set = set()

    if args.to_exclude:
        exclude_set = parse_user_inc_exc(args.to_exclude)
    else:
        exclude_set = set()

    for taxon, row in df.iterrows():
        if (row['Lower Taxonomy'] in exclude_set) or (row['Higher Taxonomy'] in exclude_set) or (taxon in exclude_set):
            df.at[taxon, 'Include in Subset'] = 'no'

        if (row['Lower Taxonomy'] in include_set) or (row['Higher Taxonomy'] in include_set) or (taxon in include_set):
            df.at[taxon, 'Include in Subset'] = 'yes'

    df.to_csv(f'{args.output}/taxa_subset.tsv', sep='\t')


def parse_subset_tsv():
    """

    :param tsv_file:
    :return:
    """
    with open(args.subset, 'r') as infile:
        infile.readline()
        taxa_to_include = []
        for line in infile:
            line = line.strip()
            taxon, _, _, _, include = line.split('\t')
            if include == 'yes':
                taxa_to_include.append(taxon)

    return taxa_to_include


def taxa_subsetter():
    """

    :param taxa: List of taxa included in subset
    :return:
    """
    taxa = parse_subset_tsv()

    files = [file for file in os.listdir(orthologs_dir)]
    for file in files:
        with open(f'{orthologs_dir}/{file}', 'r') as infile, open(f'{args.output}/{file}', 'w') as outfile:
            records = []
            for record in SeqIO.parse(infile, 'fasta'):
                if record.description in taxa:
                    records.append(record)

            SeqIO.write(records, outfile, 'fasta')


if __name__ == '__main__':
    description = 'Subsets taxa to be included in super matrix construction'
    parser, optional, required = help_formatter.initialize_argparse(name='subset_taxa.py',
                                                                    desc=description,
                                                                    usage='subset_taxa.py '
                                                                          '[OPTIONS] -i <input>')

    # Optional Arguments
    optional.add_argument('--subset', type=str, metavar='taxa_subset.tsv', default=None,
                          help=textwrap.dedent("""\
                          Subset input genes
                          """))
    optional.add_argument('--to_include', type=str, metavar='inc_taxa.txt', default=None,
                          help=textwrap.dedent("""\
                          List of taxa to include.
                          """))
    optional.add_argument('--to_exclude', type=str, metavar='exc_taxa.txt', default=None,
                          help=textwrap.dedent("""\
                          List of taxa to exclude
                          """))

    args = help_formatter.get_args(parser, optional, required, inp_dir=False, pre_suf=False)

    if os.path.isdir(args.output) is False:
        os.mkdir(args.output)

    config = configparser.ConfigParser()
    config.read('config.ini')
    dfo = str(Path(config['PATHS']['dataset_folder']).resolve())
    metadata = f'{dfo}/metadata.tsv'
    orthologs_dir = f'{dfo}/orthologs/'

    if not args.subset:
        taxa_comp, gene_count = subset_tools.completeness(args=args, input_dir=orthologs_dir, genes=False)
        subset_tools.make_plot(taxa_comp, f'{args.output}/taxa_comp', y_count=gene_count, genes=False)
        make_subset_tsv()
    else:
        taxa_subsetter()