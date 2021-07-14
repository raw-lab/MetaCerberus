# -*- coding: utf-8 -*-
"""cerberusParser.py Parses HMMER output and identifies KOs with FOAM and KEGG DB info
1) Get best hits
2) Save rollup file
3) Convert rollup file to table
"""

import os
import csv
import pandas as pd


def parseHmmer(fileHmmer, config, subdir):
    path = os.path.join(config['DIR_OUT'], subdir)
    os.makedirs(path, exist_ok=True)

    minscore = config["MINSCORE"]

    top5File = os.path.join(path, "HMMER_BH.tsv")
    rollupFileFOAM = os.path.join(path, "HMMER_BH_FOAM.rollup")
    rollupFileKEGG = os.path.join(path, "HMMER_BH_KO.rollup")

    # Calculate Best Hit
    BH_dict = {}
    BH_top5 = {}
    with open(fileHmmer, "r") as reader:
        for line in reader:
            if line.startswith("#"):        # Skip commented lines
                continue
            line = line.split()
            try:
                query = line[0]             # Column 0 is our query
                line[13] = float(line[13])  # Column 14 is the score, convert to float
            except:
                continue
            score = line[13]
            if score < minscore:            # Skip scores less than minscore
                continue

            # store top 5 per query
            if query not in BH_top5:
                BH_top5[query] = [line]
            elif len(BH_top5[query]) < 5:
                BH_top5[query].append(line)
            else:
                BH_top5[query].sort(key = lambda x: x[13])
                if score > BH_top5[query][0][13]:
                    BH_top5[query][0] = line

            # Check for Best Score per query
            if query not in BH_dict:
                BH_dict[query] = line
            elif score > BH_dict[query][13]:
                BH_dict[query] = line

    # Save Top 5 hits tsv rollup
    if config['REPLACE'] or not os.path.exists(top5File):
        with open(top5File, 'w') as writer:
            for query in sorted(BH_top5.keys()):
                BH_top5[query].sort(key = lambda x: x[13])
                for line in BH_top5[query]:
                    print(line[0], line[3], line[13], file=writer, sep='\t')

    # Create dictionary with found KO IDs and counts
    KO_ID_counts = {}
    for line in BH_dict.values():
        KO_IDs = [KO_ID.split(":")[1].split("_")[0] for KO_ID in line[3].split(",") if "KO:" in KO_ID]
        for KO_ID in KO_IDs:
            if KO_ID not in KO_ID_counts:
                KO_ID_counts[KO_ID] = 0
            KO_ID_counts[KO_ID] += 1

    # Write rollup files to disk
    if config['REPLACE'] or not os.path.exists(rollupFileFOAM):
        rollupFOAM(KO_ID_counts, os.path.join(config["PATH"], "cerberusDB", "FOAM-onto_rel1.tsv"), rollupFileFOAM)
    if config['REPLACE'] or not os.path.exists(rollupFileKEGG):
        rollupKEGG(KO_ID_counts, os.path.join(config["PATH"], "cerberusDB", "KO_classification.txt"), rollupFileKEGG)

    return (rollupFileFOAM, rollupFileKEGG)


######### FOAM Roll-Up #########
def rollupFOAM(KO_ID_dict, dbFile, outFile):
    # Read FOAM information
    FOAM_dict = {}
    with open(dbFile, "r") as csvFile:
        reader = csv.reader(csvFile, delimiter="\t")
        next(reader)    # Skip header
        for line in reader:
            KO_ID = line[4]
            FOAM_info = line[0:4]
            if KO_ID not in FOAM_dict:
                FOAM_dict[KO_ID] = []
            if FOAM_info not in FOAM_dict.values():
                FOAM_dict[KO_ID].append(FOAM_info)

    # Match FOAM info with found KO
    with open(outFile, "w") as fileWriter:
        for KO_ID in sorted(KO_ID_dict.keys()):
            FOAM_info = FOAM_dict[KO_ID] if KO_ID in FOAM_dict else [['NA']]
            for info in FOAM_info:
                outline = "\t".join([str(s) for s in [KO_ID, KO_ID_dict[KO_ID], info]])
                fileWriter.write(outline + "\n")
    return


######### KEGG Roll-Up #########
def rollupKEGG(KO_ID_dict, dbFile, outFile):
    # Read KEGG information
    KEGG_dict = {}
    with open(dbFile, "r") as csvFile:
        reader = csv.reader(csvFile, delimiter="\t")
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
            if KO_ID not in KEGG_dict:
                KEGG_dict[KO_ID] = []
            KEGG_dict[KO_ID].append(KEGG_info)

    # Match FOAM and KEGG info with found KO
    with open(outFile, "w") as fileWriter:
        for KO_ID in sorted(KO_ID_dict.keys()):
            KEGG_info = KEGG_dict[KO_ID] if KO_ID in KEGG_dict else [['NA']]
            for info in KEGG_info:
                outline = "\t".join([str(s) for s in [KO_ID, KO_ID_dict[KO_ID], info]])
                fileWriter.write(outline + "\n")
    return


########## createTables #########
def createTables(fileRollup):
    df_FOAM = pd.read_csv(fileRollup[0], names=['Id','Count','Info'], delimiter='\t')
    df_KEGG = pd.read_csv(fileRollup[1], names=['Id','Count','Info'], delimiter='\t')

    # Reformat data. This lambda method avoids chained indexing
    # Splits string into list, strips brackets and quotes
    helper = lambda x : [i.strip("'") for i in x.strip('[]').split("', ")]
    # call helper method to reformat 'FOAM' and 'KO' columns
    df_FOAM['Info'] = df_FOAM['Info'].apply(helper)
    df_KEGG['Info'] = df_KEGG['Info'].apply(helper)
    # Convert 'Count" column to numeric
    df_FOAM["Count"] = pd.to_numeric(df_FOAM["Count"])
    df_KEGG["Count"] = pd.to_numeric(df_KEGG["Count"])
    
    # Calculate Level and Count #TODO: Refactor this section for clarity
    #def countLevels(df):
    #    dictDF = {}
    #    for row in range(len(df)):
    #        for j in range(len(df['Info'][row])):
    #            dictDF[df['Info'][row][j]] = dictDF.get(df['Info'][row][j],["",0])
    #            n,m = dictDF[df['Info'][row][j]]
    #            dictDF[df['Info'][row][j]] = [j+1,m+df['Count'][row]]
    #    return dictDF

    #dictFoam = countLevels(df_FOAM)
    #dictKEGG = countLevels(df_KEGG)
    #for key,value in dictFoam.items():
    #    print('\t'*value[0], key, value)

    # Enumerate data TODO: Replaced counting method with this.
    # Need to make sure not getting off by one error in counting
    dictFOAM = {}
    for row in range(len(df_FOAM)):
        for level,name in enumerate(df_FOAM['Info'][row], 1):
            if name not in dictFOAM:
                dictFOAM[name] = [level, df_FOAM['Count'][row], df_FOAM['Id'][row]]
            dictFOAM[name][1] += 1
    dictKEGG = {}
    for row in range(len(df_KEGG)):
        for level,name in enumerate(df_KEGG['Info'][row], 1):
            if name not in dictKEGG:
                dictKEGG[name] = [level, df_KEGG['Count'][row], df_KEGG['Id'][row]]
            dictKEGG[name][1] += 1
    #for key,value in dictFoam.items():
    #    print('\t'*value[0], key, value)


    # Create Level and Count Columns
    dataFOAM = {'Type':'Foam',
        'Name':list(dictFOAM.keys()),
        'Id':[x[2] for x in dictFOAM.values()],
        'Level':[x[0] for x in dictFOAM.values()],
        'Count':[x[1] for x in dictFOAM.values()]}
    FT = pd.DataFrame(data=dataFOAM)
    FT.drop(FT[FT['Name']==''].index, inplace=True)
    FT.drop(FT[FT['Name']=='NA'].index, inplace=True)
    
    dataKO = {'Type':'KO',
        'Name':list(dictKEGG.keys()),
        'Id':[x[2] for x in dictKEGG.values()],
        'Level':[x[0] for x in dictKEGG.values()],
        'Count':[x[1] for x in dictKEGG.values()]}
    KT = pd.DataFrame(data=dataKO)
    KT.drop(KT[KT['Name']==''].index, inplace=True)
    KT.drop(KT[KT['Name']=='NA'].index, inplace=True)

    # TODO: Debug info, don't print this in final. Exports to excel and CSV in visual.py
    #print("FOAM")
    #print(FT)
    #print("KEGG")
    #print(KT)
    
    return pd.concat([FT,KT])
