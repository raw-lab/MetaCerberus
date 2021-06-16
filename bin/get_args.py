import argparse


def get_args():
    version="1.0"
    parser = argparse.ArgumentParser(description='Cerberus is used for versatile functional ontology assignments for metagenomes via HMM searching with environmental focus of shotgun meta-omics data')
    parser.add_argument('-i', type=str, required=True, help='path to file or directory \n <accepted formats {.faa,.fna,.ffn,.rollup} , for visualisation : {.rollup }>')
    parser.add_argument('--version', '-v', action='version',
                        version='Cerberus: \n version: {} December 24th 2020'.format(version),
                        help='show the version number and exit')
    parser.add_argument('-euk', action='store_true', help='euk-->eukaryote option (includes other viruses)')
    parser.add_argument('-mic', action='store_true', help='mic-->for microbial(includes bacteriophage)')
    args = parser.parse_args()

    return parser, args
