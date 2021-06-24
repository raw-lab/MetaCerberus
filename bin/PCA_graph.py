import plotly.graph_objs as go
from plotly.offline import plot
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import plotly.express as px
from sklearn.decomposition import PCA
from functools import reduce
import glob
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


def PCA1(path, table_list):
#     m='/home/taouk/Desktop/robo/data/prokka_results_N139.ffn/N139_output/N139.FOAM.out.sort.BH.KO_output'
#     z='/home/taouk/Desktop/robo/data/N139_output/N139.FOAM.out.sort.BH.KO_output'
#     x='/home/taouk/Desktop/robo/data/input_dir/prokka_results_Agro_10k_R1.fastq/Agro_10k_R1_output/Agro_10k_R1.FOAM.out.sort.BH.KO_output'
#     parent_dir = s
#     y='/home/taouk/Desktop/robo/data/input_dir/prokka_results_Agro_10k_R2.fastq/Agro_10k_R2_output/Agro_10k_R2.FOAM.out.sort.BH.KO_output'
# #     subject_dirs=s
#     subject_dirs = [os.path.join(parent_dir, dir) for dir in os.listdir(parent_dir) if os.path.isdir(os.path.join(parent_dir, dir))]
#     csv_files=[x,y,z,m]
    filelist = []
#     for dir in subject_dirs:
#         csv_files = [os.path.join(dir, csv) for csv in os.listdir(dir) if os.path.isfile(os.path.join(dir, csv)) and csv.endswith('_OUTPUT.XLSX.csv')]
    for file in table_list:
        a=file[0]
        y=file[2]
        # base=os.path.basename(file)
        # y=os.path.splitext(base)[0]
        # y = y.replace('_nucleotide_summary','').replace('_protein_summary','')
        a = a[['Name','Count']]
        a = a.rename(columns={'Count':y })
        filelist.append(a)
            
    print(filelist)
    df_merged2 = reduce(lambda  left,
                        right: pd.merge(left,
                        right,
                        on=['Name'],
                        how='outer'), filelist)
    result = df_merged2.replace(np.nan, 0)
    pivoted = result.T
    res = pivoted.rename(columns=pivoted.iloc[0])
    res1=res.drop(res.index[0])
    pca = PCA(n_components=3, svd_solver='randomized')
    X_train = pca.fit_transform(res1)
    labels = {
    str(i): ('PC '+str(i+1)+' (' +'%.1f'+ '%s'+')') % (var,'%')
    for i, var in enumerate(pca.explained_variance_ratio_ * 100)
    }
    fig = px.scatter_3d(
        X_train, x=0, y=1, z=2, color=res1.index,
        labels=labels
    )
    fig.update_layout({
    'plot_bgcolor' : '#7f7f7f',
    'paper_bgcolor': '#FFFFFF',
    'paper_bgcolor': "rgba(0,0,0,0)",
    'plot_bgcolor' : '#7f7f7f',
    
    })
    fig.update_layout(scene = dict(
            xaxis = dict(
                backgroundcolor="rgb(255,255, 255)",
                gridcolor="black",
                showbackground=True,
                zerolinecolor="black",),
            yaxis = dict(
                backgroundcolor="rgb(255,255, 255)",
                gridcolor="black",
                showbackground=True,
                zerolinecolor="black"),
            zaxis = dict(
                backgroundcolor="rgb(255,255, 255)",
                gridcolor="black",
                showbackground=True,
                zerolinecolor="black",),),
        
        )
    # fig.show()
    plot(fig, filename=path+'/'+'PCA_plot'+".html", auto_open=False)
