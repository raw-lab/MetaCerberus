# Welcome to Cerberus
Python code for versatile Functional Ontology Assignments for Metagenomes via Hidden Markov Model (HMM) searching with environmental focus of shotgun metaomics data

Input formats:
-----
- From any NextGen sequencing technology (from Illumina, Pacbio, Oxford Nanopore)
- type 1 raw reads (.fastq format)
- type 2 nucleotide fasta (.fasta, .fa, .fna, .ffn format), assembled raw reads into contigs
- type 3 protein fasta (.faa format), assembled contigs which genes are converted to amino acid sequence 

Options in config
-----
- - euk (for eukaryotes FGS++)
- - mic (for microbes)

Table of Contents
-------

Installing Cerberus: 
-------
- needs a pip installer
`pip install cerberus`

- needs a conda installer
`conda install cerberus`

- needs source installer (github)
```
git clone https://github.com/raw-lab/cerberus.git
cd cerberus
python cerberus-setup.py
```

Step 0 - Setup.py
-------
looks okay. I don’t like the folder on the desktop.

## OSF link to FOAM databases </br>
https://osf.io/5ba2v/

Double check this pulls

- check  Install_Dependencies.py and Install_osf_Files.py 
- This will replace config file, it will install the program dependances (pulling directly from source) 
- install in path, and downloading/formatting the databases. 
- Then will work with pip and conda and source install

Step 1 - Cerberus-master.py (control center of cerberus)
-------

- calls all the individual scripts etc
- Refactor cerberus to call our functions

    get_args.py (put in here)
    def args() ()

### Add the config file user uses here. 

Step 2 - QC.py (Fastqc script from Rhea)
-------
→ qc raw fastq
→ qc trim fastq

Step 3 - Trim.py (fastp and porecrop from Rhea)
-------
- https://github.com/rrwick/Filtlong (in future?)

Step 4 - Decon.py (bbduk from Rhea)
-------
- We need to do a map based for nanopore and pacbio
- https://github.com/wdecoster/nanolyse (in future?)

Step 5 - format.py
-------
- Convert fq to fna post trim
- Removes the quality scores post trim
- Removes N's from scaffold contigs (make an options in config)

## Example function (fq -> fna)
    def fastq_processing(fq_path, path, f_name):
    trim_path=path+'/'+f_name+"_trim.fastq"
    trim_fna=path+'/'+f_name+"_trim.fna"
    cmd1 = "sed -n '1~4s/^@/>/p;2~4p' "+trim_path+" > "+trim_fna ##I wrote this reg expression sed
    subprocess.call(cmd1,shell=True)
    return trim_fna


## REMOVE N’S here (from a scaffold or contig input)
- LIKELY an easier way then this
#### For example 
>seq1 
TAGAGTGTAGTGNNNNNNTTTAAA
splits to 
>seq1 
TAGAGTGTAGTG
>seq2
TTTAAA

### example from Thrilok
    def Ndeletion(input_file,output_file):
    # input_file='./one.fna'
    # output_file=open('./out.txt','w')
    counter=1
    mark=0
    past=1
    with open(input_file) as lines:
        temp=''
        for line in lines:
            if line[0]=='>':
                print('>contig' + str(counter),file=output_file)
                counter+=1
                continue
            for char in line:
                if char not in ['N',' ','\n']:
                    past=0
                    temp+=char
                    mark=0
                elif char=='N':
                    mark=1
            if mark==1 and past==0:
                    past=1
                    mark=0
                    print(temp)
                    print('>contig' + str(counter),file=output_file)
                    if len(temp)<=51:
                        print(temp,file=output_file)
                        temp=''
                    counter+=1
            if len(temp)>51:
                
                
                print(temp[:51],file=output_file)
                temp=temp[51:]
            mark=0
        
    output_file.close()


Step 6 - GeneCall.py (RheaGeneCall.py from Rhea)
-------
- prodigal 
- FGS (FGS++)
- prokka? if it ever works again (future)
- orfM if its good? (future)


Step 6 - hmmer.py (uniquely cerberus)
-------
- Searches using hmmer3
- Command
```hmm_cmd = "hmmsearch --cpu %s --domtblout %s.FOAM.out %s %s" %(nCPU, output_path, hmm_file, faa_path)```

### example command I wrote (no worries if you have a better way !)

    def faa_processing(faa_path, path, f_name):
    output_path=path+os.sep+f_name+"_output"
    os.makedirs(output_path)
    output_path=os.path.join(output_path + os.sep, f_name)
    script_dir = os.path.dirname(os.path.realpath(__file__))
    hmm_file = os.path.join(script_dir, "osf_Files/FOAM-hmm_rel1a.hmm.gz")
    nCPU = int(os.cpu_count()/2)
    hmm_cmd = "hmmsearch --cpu %s --domtblout %s.FOAM.out %s %s" %(nCPU, output_path, hmm_file, faa_path)
    subprocess.run(hmm_cmd, shell=True, stdout=open("process_faa.out", 'w'))

    BH_dict = {}
    BS_dict = {}
    minscore = 25
    reader = open(output_path + ".FOAM.out", "r").readlines()
    for line in reader:
        if line[0] == "#": continue
        line = line.split()
        score = float(line[13])
        if score < minscore: continue
        query = line[0]
        try:
            best_score = BS_dict[query]
        except KeyError:
            BS_dict[query] = score
            BH_dict[query] = line
            continue
        if score > best_score:
            BS_dict[query] = score
            BH_dict[query] = line

    KO_ID_dict = {}
    for BH in BH_dict:
        line = BH_dict[BH]
        KO_IDs = [KO_ID.split(":")[1].split("_")[0] for KO_ID in line[3].split(",") if "KO:" in KO_ID]
        for KO_ID in KO_IDs:
            try:
                KO_ID_dict[KO_ID] += 1
            except KeyError:
                KO_ID_dict[KO_ID] = 1
    
    rollup_file = "%s.FOAM.out.sort.BH.KO.rollup" %(output_path)
    return roll_up(KO_ID_dict, rollup_file)

Step 7 - Parser.py
-------
Parse output from hmmer search

### Sorted for parsing (top value on top)
```sort XXX.faa.FOAM.out > XXX.faa.FOAM.out.sort```  

### Grab top hit from sorted output
```python bmn-HMMerBestHit_p3.py XXX.faa.FOAM.out.sort > XXX.faa.FOAM.out.sort.BH``` 

### Grab fouth column
```awk '{print $4}' XXX.faa.FOAM.out.sort.BH > XXX.faa.FOAM.out.sort.BH.tmp1```

### counts elements 
```python bmn-CountEachElement_p3.py XXX.faa.FOAM.out.sort.BH.tmp1 > XXX.faa.FOAM.out.sort.BH.tmp2``` 
- Maybe preprocess_before_visual.py? 

### count and adds up KO
```python bmn-KOoneCount_p3.py XXX.faa.FOAM.out.sort.BH.tmp2 | sed s/KO://g | sort -k 1 > XXX.faa.FOAM.out.sort.BH.KO```
- Maybe preprocess_before_visual.py? 

### The Rollup function post parsing here
- ROLL-up of the .ko and .foam function

        def roll_up(KO_ID_dict, rollup_file):
        script_dir = os.path.dirname(os.path.realpath(__file__))
        FOAM_file = os.path.join(script_dir, "osf_Files/FOAM-onto_rel1.tsv")
        FOAM_dict = {}
        reader = csv.reader(open(FOAM_file, "r"), delimiter="\t")
        header = next(reader)
        for line in reader:
        KO_ID = line[4]
        FOAM_info = line[0:4]
        FOAM_dict[KO_ID] = FOAM_info

        KEGG_file = ospath.join(script_dir, "osf_Files/KO_classification.txt")
        KEGG_dict = {}
        reader = csv.reader(open(KEGG_file, "r"), delimiter="\t")
        for line in reader:
        if line[0] != "":
            tier_1 = line[0]
            continue
        if line[1] != "":
            tier_2 = line[1]
            continue
        if line[2] != "":
            pathway = line[3]
            continue
        KO_ID = line[3]
        KEGG_info = [tier_1, tier_2, pathway] + line[4:]
        KEGG_dict[KO_ID] = KEGG_info

        KO_ID_list = [key for key in KO_ID_dict]
        KO_ID_list.sort()

        outfile = open(rollup_file, "w")
        for KO_ID in KO_ID_list:
        try:
            FOAM_info = FOAM_dict[KO_ID]
        except KeyError:
            FOAM_info = ["NA"]
        try:
            KEGG_info = KEGG_dict[KO_ID]
        except KeyError:
            KEGG_info = ["NA"]
        outline = "\t".join([str(s) for s in [KO_ID, KO_ID_dict[KO_ID], FOAM_info, KEGG_info]])
        outfile.write(outline + "\n")
        return rollup_file

### UNSURE what preprocess_before_visual.py
### Formating the rollup prior to plotting?

Step 8 - visualization.py (merge single and multiple file visual.py)
-------
Clean up PCA.py (really bad)

Notes:
------
Time_g.py and mem_usage.py are for time and memory usage. Should be here. But, we can use them for testing. 
