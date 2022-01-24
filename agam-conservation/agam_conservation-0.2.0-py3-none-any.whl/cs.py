import sys
import requests
import h5py

import allel
import numpy as np
import pandas as pd

import matplotlib as mpl
import seaborn as sns
import matplotlib.pyplot as plt
import humanize

class ConservationScore:
        
    def __init__(self, data_path = None) -> None:
        self.data_link = 'https://zenodo.org/record/4304586/files/AgamP4_conservation.h5'
        self.data_path = None
        if data_path:
            self.data_path = data_path

    def download(self, file_name='data/AgamP4_conservation.h5'):
        with open(file_name, "wb") as f:
            print(f'Downloading {file_name}')
            response = requests.get(self.data_link, stream=True)
            total_length = response.headers.get('content-length')

            if total_length is None: # no content length header
                f.write(response.content)
            else:
                dl = 0
                total_length = int(total_length)
                for data in response.iter_content(chunk_size=4096):
                    dl += len(data)
                    f.write(data)
                    done = int(50 * dl / total_length)
                    finished = int(dl / total_length * 100)
                    sys.stdout.write("\rProgress: [%s%s] %s%%\t" % ('=' * done, ' ' * (50-done), finished))    
                    sys.stdout.flush()

                self.data_path = file_name

    def _parse_region(self, region_string):
        
        chr_sizes = pd.read_csv('data/chr_sizes.txt', sep='\t')

        if ':' in region_string:
            chromosome, positions = region_string.split(':')
            if chromosome not in chr_sizes['chrom'].values:
                print(f'Chromosome {chromosome} does not exist in the dataset.')
                print(f'Available chromosomes are: 2L, 2R, 3L, 3R and X.')
                exit()

            positions = positions.split('-')
            if len(positions) < 2:
                start = positions[0]
                end = None
            else:
                start, end = positions
        else:
            print('No chromosome defined. You need to define genomic region in the following format CHR:START-END or CHR:POS')
            exit()

        return (chromosome, start, end)
    
    def extract(self, region_str, array='Cs'):
        chromosome, start, end = self._parse_region(region_str)
        if self.data_path:
            with h5py.File(self.data_path, mode='r+') as root:
                start, end = int(start), int(end)
                values = root[chromosome][array][:,start-1:end-1]
                row_names = root[chromosome][array].attrs['rows']

                df = pd.DataFrame(values.T)
                df.columns = [row_names]
                df['chromosome'] = chromosome
                df['pos'] = np.arange(start, end)

                cols = df.columns.tolist()
                df = df.loc[:, cols[-2:] + cols[:-2]]

                return df
        else:
            raise ValueError('Dataset file does not exist. Download it with `CS.download()` or check the path to the dataset.')
        
        
    def _plot_transcripts(self, geneset, chrom, start, stop, height=.2, label_transcripts=True, label_exons=False, label_exon_size=False,
                     label_codons=False, highlight_exons=None, label_cdss=False, highlight_color='red', ax=None,
                     title=None):
        """Plot all transcripts for all genes overlapping a given region.
            Authored by: Alistar Miles (https://alimanfoo.github.io/) """

        start, stop = int(start), int(stop)
        
        if ax is None:
            fig, ax = plt.subplots(figsize=(14, 6))
            sns.despine(ax=ax, left=True, offset=5)
            
        if title:
            ax.set_title(title, va='bottom')

        # find genes overlapping the given region 
        genes = geneset.query("((type == 'gene') or (type == 'ncRNA_gene')) and (seqid == %r) and (end >= %s) and (start <= %s)" % (chrom, start, stop)).sort_values('start')
        # iterate over genes
        for _, gene in genes.iterrows():

            # find child transcripts
            transcripts = geneset.query("(type == 'mRNA') and (Parent == %r)" % gene.ID).sort_values('ID')

            if gene.type == 'ncRNA_gene':
                nc_transcripts = geneset.query("(type == 'ncRNA_gene') and (seqid == %r) and (end >= %s) and (start <= %s)" % (chrom, start, stop)).sort_values('start')
                transcripts = pd.concat([nc_transcripts, transcripts]).sort_values('ID')
            
            # iterate over transcripts
            for i, (_, transcript) in enumerate(transcripts.iterrows()):
                # coordinates for plotting the transcript
                if transcript.strand == '+':
                    y = i
                else:
                    y = -i - 1

                # annotate with transcript ID
                text_y = y + height + (height / 10)
                if label_transcripts == 'right':
                    text_x = min(stop, int(transcript.end))
                    ha = 'right'
                else:
                    text_x = max(start, int(transcript.start))
                    ha = 'left'
                if label_transcripts:
                    if transcript.strand == '+':
                        text = '%s >' % transcript.ID
                    else:
                        text = '< %s' % transcript.ID
                    ax.text(text_x, text_y, text, ha=ha, va='bottom')
                            
                # find child exons
                exons = geneset.query("type == 'exon' and Parent == %r" % transcript.ID).sort_values('start')

                # iterate over exons to plot introns
                last_exon = None
                for i, (_, exon) in enumerate(exons.iterrows()):
                    x = exon.start
                    width = exon.end - x
                    # plot intron
                    if last_exon is not None:
                        ax.plot([last_exon.end, (last_exon.end + exon.start) / 2, exon.start], [y + height / 2, y + height / 1.5, y + height / 2], 'k-')
                    last_exon = exon
                    
                    # exon number
                    n = i + 1 if exon.strand == '+' else len(exons) - i
                    
                    # label exons
                    if label_exons and exon.end > start and exon.start < stop:
                        text_x = (exon.start + exon.end) / 2
                        ha = 'center'
                        if text_x < start:
                            text_x = start
                            ha = 'left'
                        elif text_x > stop:
                            text_x = stop
                            ha = 'right'
                        s = str(n)
                        if label_exon_size:
                            s += ' (%s)' % (exon.end - exon.start + 1)
                        if label_exons == 'center':
                            ax.text(text_x, y + height / 2, s, ha=ha, va='center', color='w', zorder=20, fontweight='bold')
                        else:
                            ax.text(text_x, text_y, s, ha=ha, va='bottom', color='k', zorder=20)
                    
                    # highlight exons
                    if highlight_exons and (transcript.ID, n) in highlight_exons:
                        patch = plt.Rectangle((x, y), width, height, color=highlight_color, alpha=0.4, zorder=10)
                        ax.add_patch(patch)

                # find child CDSs
                cdss = geneset.query("(type == 'CDS' or type == 'rRNA') and Parent == %r" % transcript.ID)
                if transcript.strand == '+':
                    cdss = cdss.sort_values('start', ascending=True)
                else:
                    cdss = cdss.sort_values('end', ascending=False)
                
                # keep track of CDS position
                cds_pos = 0
                
                # plot CDSs
                for _, cds in cdss.iterrows():
                    x = cds.start
                    width = cds.end - x
                    
                    # plot CDS
                    patch = plt.Rectangle((x, y), width, height, color='k')
                    ax.add_patch(patch)
                    
                    if label_codons:
                        # report 1-based numbers
                        s = '%s (%s)' % ((cds_pos // 3) + 1, cds_pos + 1)
                        if transcript.strand == '+':
                            text_x = x
                            ha = 'left'
                        else:
                            text_x = x + width
                            ha = 'right'
                        if text_x > start and text_x < stop:
                            ax.text(text_x, text_y, s, ha=ha, va='bottom')
                                    
                    # label CDSs
                    if label_cdss and cds.end > start and cds.start < stop:
                        text_x = (cds.start + cds.end) / 2
                        ha = 'center'
                        if text_x < start:
                            text_x = start
                            ha = 'left'
                        elif text_x > stop:
                            text_x = stop
                            ha = 'right'
                        s = cds.ID
                        if label_cdss == 'center':
                            ax.text(text_x, y + height / 2, s, ha=ha, va='center', color='w', zorder=20, fontweight='bold')
                        else:
                            ax.text(text_x, text_y, s, ha=ha, va='bottom', color='k', zorder=20)
                    
                    # accumulate CDS positions
                    cds_pos += width + 1  # N.B., GFF coords are 1-based end-inclusive

                # find child UTRs
                utrs = geneset.query("(type == 'three_prime_UTR' or type == 'five_prime_UTR') and Parent == %r" % transcript.ID).sort_values('start')
                for _, utr in utrs.iterrows():
                    x = utr.start
                    width = utr.end - x
                    utr_height = height * .8
                    utr_y = y + (height - utr_height) / 2
                    patch = plt.Rectangle((x, utr_y), width, utr_height, facecolor='#cccccc', edgecolor='k')
                    ax.add_patch(patch)

        ax.set_yticks([])
        ax.set_xlim(start, stop)
        ax.set_xticklabels([humanize.intcomma(int(x)) for x in ax.get_xticks()])
        ax.axhline(0 - (height / 2), color='k', linestyle='--')
        ax.set_xlabel('Chromosome %s position (bp)' % chrom)
        ax.autoscale(axis='y', tight=True)
        
        return ax


    def _geneset_to_pandas(self, geneset):
        """Life is a bit easier when a geneset is a pandas DataFrame."""
        items = []
        for n in geneset.dtype.names:
            v = geneset[n]
            # convert bytes columns to unicode (which pandas then converts to object)
            if v.dtype.kind == 'S':
                v = v.astype('U')
            items.append((n, v))
        return pd.DataFrame.from_dict(dict(items))


    def _plot_guides(self, guides, start, ax):
        # guides = [(start, end, colour)]
        for guide in guides:
            if len(guide) == 3:
                colour = guide[2]
            else:
                colour = 'orange'

            ax.axvspan(guide[0] - start, guide[1] - start, ymax=95, color=colour, alpha=0.5)


    def plot(self, region_str, array='Cs', include_arrays=['Cs'], save_to=None):
        # Load geneset and save it to pandas dataframe
        
        geneset_agam = allel.FeatureTable.from_gff3('data/AgamP4.12.gff3',
                                                    attributes=['ID', 'Parent', 'Name'])

        array_names={'Cs': 'Conservation score', 'phyloP': 'pyhloP', 'snp_density': "SNP density (bp-1)"}
        array_limits={'Cs': 1, 'phyloP': 3, 'snp_density': 1}

        geneset_agam = self._geneset_to_pandas(geneset_agam)
        chromosome, start, end = self._parse_region(region_str)
        start, end = int(start), int(end)
        
        fig, ax = plt.subplots(len(include_arrays) + 1,1, figsize=(20, (len(include_arrays) + 1) * 4))

        self._plot_transcripts(geneset_agam, chromosome, start, end, label_codons=False, label_exons=True, ax=ax[0])
        
        with h5py.File(self.data_path, mode='r+') as data_h5:
            for i, array in enumerate(include_arrays):
                if array in ['Cs', 'phyloP', 'snp_density']:
                    data = data_h5[chromosome][array][0,start:end]
                    ax[i+1].plot(data, color='gray', alpha=.7)
                    ax[i+1].set_ylabel(array_names[array])
                    ax[i+1].set_ylim(0, array_limits[array])
                    ax[i+1].set_xlim(0, len(data))
                    sns.despine(ax=ax[i+1], offset=5)
                else:
                    raise ValueError(f'{array} not in the database.')

        sns.despine(ax=ax[0], left=True, offset=5)
        
        if save_to:
            plt.savefig(f'{save_to}', dpi=300)