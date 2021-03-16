import os
from os.path import isfile, join
import sys
import subprocess
import csv
import pandas as pd
from output_visual import output_visual

def visual(table_value):
    table=table_value[0]
    path=table_value[1]
    f_name=table_value[2]
    # file=file_name.split('/')[-1]
    # f_name, f_ext = os.path.splitext(file)

    # reader = csv.reader(open(file_name, "r"), delimiter="\t")
    # df=pd.DataFrame(reader)
    # df.columns=['Id','Count','Foam','KO']
    # table=preprocess_data(df)
    print(table)
    FT=table[table['Type']=='Foam'].drop(['Type'],axis=1)
    KO=table[table['Type']=='KO'].drop(['Type'],axis=1)
    FT_main=FT.copy()
    KO_main=KO.copy()
    FT1=FT[FT['Layer']==1].sort_values(by=['Count'],ascending=False).head(10)
    FT2=FT[FT['Layer']==2].sort_values(by=['Count'],ascending=False).head(10)
    FT3=FT[FT['Layer']==3].sort_values(by=['Count'],ascending=False).head(10)
    FT4=FT[FT['Layer']==4].sort_values(by=['Count'],ascending=False).head(10)

    KO1=KO[KO['Layer']==1].sort_values(by=['Count'],ascending=False).head(10)
    KO2=KO[KO['Layer']==2].sort_values(by=['Count'],ascending=False).head(10)
    KO3=KO[KO['Layer']==3].sort_values(by=['Count'],ascending=False).head(10)
    KO4=KO[KO['Layer']==4].sort_values(by=['Count'],ascending=False).head(10)
    FT=pd.concat([FT1,FT2,FT3,FT4])
    KO=pd.concat([KO1,KO2,KO3,KO4])
    f_path=os.path.join(path + os.sep,f_name+'_output.xlsx')
    csv_path=os.path.join(path + os.sep, f_name+'_output')
    table.to_excel (f_path, index = False, header=True)
    table.to_csv (csv_path, index = False, header=True)
    output_visual(path,f_name,FT,KO,FT_main,KO_main,table)