import os
import csv
import pandas as pd


def preprocess_data(path, file_name, table_list):
    file=file_name.split('/')[-1]
    f_name, f_ext = os.path.splitext(file)

    reader = csv.reader(open(file_name, "r"), delimiter="\t")
    df=pd.DataFrame(reader)
    if df.empty:
        return
    df.columns=['Id','Count','Foam','KO']
    dict1={}
    dict2={}
    for i in range(len(df['Foam'])):
        df['Count'][i]=int(df['Count'][i])
        df['Foam'][i] = df['Foam'][i].strip('][').split("', ")
        df['KO'][i] = df['KO'][i].strip('][').split("', ")
        for m in ['Foam','KO']:
            for j in range(len(df[m][i])):
                if df[m][i][j][-1]!="'":
                    df[m][i][j]=df[m][i][j][1:]
                    continue
                if df[m][i][j][0]!="'":
                    df[m][i][j]=df[m][i][j][:-1]
                    continue

                df[m][i][j]=df[m][i][j][1:-1]

    for i in range(len(df)):
        for j in range(len(df['Foam'][i])):
            dict1[df['Foam'][i][j]]=dict1.get(df['Foam'][i][j],["",0])
            n,m=dict1[df['Foam'][i][j]]
            dict1[df['Foam'][i][j]]=[j+1,m+df['Count'][i]]
        for j in range(len(df['KO'][i])):
            dict2[df['KO'][i][j]]=dict2.get(df['KO'][i][j],["",0])
            n,m=dict2[df['KO'][i][j]]
            dict2[df['KO'][i][j]]=[j+1,m+df['Count'][i]]
    a={'Type':'Foam','Name':list(dict1.keys()),'Layer':[x[0] for x in dict1.values()],'Count':[x[1] for x in dict1.values()]}
    FT=pd.DataFrame(data=a)

    a2={'Type':'KO','Name':list(dict2.keys()),'Layer':[x[0] for x in dict2.values()],'Count':[x[1] for x in dict2.values()]}
    KT=pd.DataFrame(data=a2)
    table=pd.concat([FT,KT])

    table.drop(table[table['Name']==''].index,inplace=True)
    table.drop(table[table['Name']=="'"].index,inplace=True)
    table.drop(table[table['Name']=='NA'].index,inplace=True)
    table_list.append([table,path,f_name])
    return table
    