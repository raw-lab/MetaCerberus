import plotly
import plotly.graph_objects as go
from plotly.offline import plot
def time_graph(path,time_list):
    time_list.sort()
    x = [i[0] for i in time_list]
    y = [i[1] for i in time_list]
    fig = go.Figure(data=go.Scatter(x=x, y=y))
    fig.update_layout(
        title="Memory-Time Graph",
        xaxis_title="Size of the Genome (in MB's)",
        yaxis_title="Time taken (in min)",
        font=dict(
            family="Courier New, monospace",
            size=18,
            color="RebeccaPurple"
        )
    )
    plot(fig, filename=path+'/'+'time_graph'+".html", auto_open=False)