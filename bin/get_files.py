import os
from os.path import isfile, join
import csv

def get_file_list(args):
    in_file_path = args.i
    if os.path.isfile(in_file_path):
        if isfile(join(os.getcwd(), in_file_path)):
            path, file = os.path.split(join(os.getcwd(), in_file_path))
        else:
            path, file = os.path.split(in_file_path)
        file_list = [file]
    if os.path.isdir(in_file_path):
        if os.path.isdir(join(os.getcwd(), in_file_path)):
            path = join(os.getcwd(), in_file_path)
            file_list = [f for f in os.listdir(path) if isfile(join(path, f))]
        else:
            path = in_file_path
            file_list = [f for f in os.listdir(in_file_path) if isfile(join(in_file_path, f))]
    
    return path, file_list,args.virus