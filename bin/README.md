RoadMap:
-----
- cerberus.py --> It is like of master of all the below files. All the below files are called here and Cerberus functions here based on the flow code written in this file.
- get_args --> catches the arguments given by the user
- get_file_list --> It collects all the files based on the file path which is given in argument -i
- sequence_processors --> All the Raw sequence processors are stored here and called in cerberus based on the type of input data.
- preprocess_before_visual--> after getting output from hmmer, the data should be preprocessed so that we can analyse the data easily.
- single_file_visual --> if only one file is given as input, this visual functionality executes.
- multi_file_visual --> for multi input file type, this visual functionality executes.
- PCA_graph --> for Principal Component Analysis Graph

- mem_usage --> to know how much memory you have used while executing cerberus.
- time_g --> to know how much time taken to run cerberus.
