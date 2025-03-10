## Author: Clarence Brian Le, Ph.D.
## Date: August 25, 2025
## Contact: ClarenceBLe@gmail.com

import pandas as pd
from Bio import SeqIO
import matplotlib.pyplot as plt
import logomaker as lma

def splice_logo(des_file, fasta_file):
    
    def get_features(des_file):
        # read in gene description file and return for downstream use/documentation
        des_df =  pd.read_csv(des_file, sep='\t', header=None, comment='#', low_memory=False) 
        des_df.columns = ['name', 'method', 'feature', 'f_start', 'f_end', 'score', 'strand','f_readframe', 'attributes'] 
        exon_df = des_df[des_df.feature=='exon'][['name', 'strand', 'feature', 'f_start', 'f_end']]  

        # identify coordinates for donor/acceptor regions - separately for '+' and '-'
        # (+): DONOR -- (exon_END+1 , exon_START-1)  ACCEPTOR 
        # (-): DONOR -- (exon_START-1 , exon_END+1)  ACCEPTOR
        for index, row in exon_df.iterrows():
            if row['feature'] == 'exon': 

                # (+): DONOR -- (exon_END+1 , exon_START-1) -- ACCEPTOR
                if row['strand'] == '+':
                    exon_df.at[index, 'donor_index'] = int(row['f_end'])+1 if pd.notna(row['f_end']) else 0   
                    exon_df.at[index, 'acceptor_index'] = row['f_start']-1 if pd.notna(row['f_end']) else 0     

                # (-): DONOR -- (exon_START-1 , exon_END+1) -- ACCEPTOR
                elif row['strand'] == '-':
                    exon_df.at[index, 'donor_index'] = row['f_start']-1 if pd.notna(row['f_end']) else 0 
                    exon_df.at[index, 'acceptor_index'] = row['f_end']+1 if pd.notna(row['f_end']) else 0

        return exon_df

    def make_seqdict(fasta_file):
        sequence_dict = {}
        for record in SeqIO.parse(fasta_file, 'fasta'):
            sequence_dict[str(record.id)]=str(record.seq)

        return sequence_dict
    
    def parse_fasta(exon_df, fasta_file, sequence_dict):
        # list of names
        records = [x for x in exon_df.name]
        
        # create sequence list
        rec_list = []
        seq_list = []

        # iterate through each row to extract donor-acceptor region 
        for index, row in exon_df.iterrows():                   
            rec_list.append(row['name'])
            seq_list.append(sequence_dict[row['name']][int(row['donor_index']):int(row['acceptor_index'])])

        # pad shorter sequences to normalize sequence length
        max_len = max(len(seq) for seq in seq_list)
        pad_seqs = [seq.ljust(max_len, 'N') for seq in seq_list] # adds 'N' to missing data
    
        return pad_seqs

    def make_logo(pad_seqs):
        # create a frequency matrix based on padded sequences
        seq_count = lma.alignment_to_matrix(pad_seqs, to_type='counts')
    
        # create logo plot
        lma.Logo(seq_count)
        plt.show()

    # call functions
    exon_df = get_features(des_file)
    sequence_dict = make_seqdict(fasta_file)
    pad_seqs = parse_fasta(exon_df, fasta_file, sequence_dict)
    make_logo(pad_seqs)

# Download and unzip gene description and fasta files into base directory
#wget ftp://ftp.ensembl.org/pub/release-110/fasta/homo_sapiens/dna/Homo_sapiens.GRCh38.dna.primary_assembly.fa.gz
#wget ftp://ftp.ensembl.org/pub/release-110/gtf/homo_sapiens/Homo_sapiens.GRCh38.110.gtf.gz
#gunzip ftp://ftp.ensembl.org/pub/release-110/fasta/homo_sapiens/dna/Homo_sapiens.GRCh38.dna.primary_assembly.fa.gz
#gunzip ftp://ftp.ensembl.org/pub/release-110/gtf/homo_sapiens/Homo_sapiens.GRCh38.110.gtf.gz

# base directory where gene description (.gtf) and fasta (.fa) datasets stored 
description_file = ' '                # replace with full file-path to 'Homo_sapiens.GRCh38.110.gtf'
sequence_file = ' '                   # replace with full file-path to 'Homo_sapiens.GRCh38.dna.primary_assembly.fa'

# call main function
splice_logo(description_file, sequence_file)
