import argparse
from Bio import SeqIO
from Bio.SeqIO.QualityIO import FastqGeneralIterator

#python fasta_to_fastq.py input.fasta output.fastq --cut_length 50 --representation_number 2

def cut_sequence(sequence, length):
    # Function to cut the sequence into smaller pieces of specified length
    return [sequence[i:i+length] for i in range(0, len(sequence), length)]

def generate_fastq(fasta_file, output_fastq, cut_length, representation_number):
    with open(output_fastq, 'w') as output_handle:
        for record in SeqIO.parse(fasta_file, "fasta"):
            cuts = cut_sequence(str(record.seq), cut_length)
            for idx, cut in enumerate(cuts, start=1):
                quality = "H" * len(cut)  # Assigning a quality score (H means high quality, you can adjust as needed)
                for _ in range(representation_number):
                    fastq_entry = f"@{record.id}_cut{idx}_{_}\n{cut}\n+\n{quality}\n"
                    output_handle.write(fastq_entry)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert fasta to fastq with specified sequence length and representation number')
    parser.add_argument('input_fasta', help='Input Fasta file')
    parser.add_argument('output_fastq', help='Output Fastq file')
    parser.add_argument('--cut_length', type=int, default=50, help='Length to cut the sequence (default: 50)')
    parser.add_argument('--representation_number', type=int, default=1, help='Number of representations for each cut sequence (default: 1)')

    args = parser.parse_args()

    generate_fastq(args.input_fasta, args.output_fastq, args.cut_length, args.representation_number)
