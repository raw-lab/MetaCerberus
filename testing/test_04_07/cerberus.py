import os
from os.path import isfile, join
import time


from preprocess_before_visual import preprocess_data
from time_g import time_graph
from multi_file_visual import new_visual
from single_file_visual import visual
from get_args import get_args
from sequence_processors import faa_processing,fastq_processing,fna_processing
from PCA_graph import PCA1
from get_files import get_file_list


def main(path, file,table_list,virus):
    f_name, f_ext = os.path.splitext(file)
    f_name=f_name.split('.')[0]
    fq_list = [".fq",".fastq"]
    fna_list = [".fa",".fna" ,".fasta",".ffn"]
    output_path=path+os.sep+f_name+"_output"
    if f_ext in fq_list:
        fq_path = os.path.join(path + os.sep, file)
        fna_path = fastq_processing(fq_path, path, f_name,file)
        faa_path,path = fna_processing(fna_path, path, f_name,file,virus)
        output_path=path+os.sep+f_name+"_output"
        rollup_file=faa_processing(faa_path,path,f_name)
        preprocess_data(output_path,rollup_file,table_list)
    elif f_ext in fna_list:
        fna_path = os.path.join(path + os.sep, file)
        faa_path,path = fna_processing(fna_path, path, f_name,file,virus)
        output_path=path+os.sep+f_name+"_output"
        rollup_file=faa_processing(faa_path,path,f_name)
        preprocess_data(output_path,rollup_file,table_list)
    elif f_ext in  [".faa"]:
        faa_path = os.path.join(path + os.sep, file)
        rollup_file=faa_processing(faa_path,path,f_name)
        preprocess_data(output_path,rollup_file,table_list)
    elif f_ext == ".rollup":
        # os.makedirs(path+os.sep+file)
        # print(path)
        preprocess_data(path,os.path.join(path + os.sep, file),table_list)
        # visual(file)
    elif f_ext == '.html':
        pass
    else:
        print("File extension \" %s \" not recognized. Please name file(s) appropriately." %(f_ext))

if __name__ == "__main__":
    parser, args = get_args()
    path, file_list,virus = get_file_list(args)
    print(virus,'thrilok')
    # print(parser,args)
    # return
    # print(file_list)
    table_list=[]
    time_list=[]
    for f in file_list:
        start_time = time.time()
        size=os.path.getsize(path+os.sep+f)
        size=round(size / (1024 * 1024), 2)
        main(path, f,table_list,virus)
        time_taken=time.time() - start_time
        time_taken=round(time_taken / (60), 2)
        time_list.append((time_taken,size))
    # print("--- %s seconds ---" % (time.time() - start_time))
    len_tab=len(table_list)
    time_graph(path,time_list)
    if len_tab==1:
        # visual(table_list[0])
        pass
    elif len_tab<=3:
        # new_visual()
        # PCA1()
        # new_visual(path,table_list)
        pass
    elif len_tab<=6:
        PCA1(path,table_list)
        # new_visual(path,table_list)
        pass
        
    elif len_tab>6:
        PCA1(path,table_list)
    print(time_list)
    
