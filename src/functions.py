import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

import networkx as nx

from bokeh.io import show, output_file, output_notebook, push_notebook
from bokeh.models import Plot, Range1d, MultiLine, Circle, HoverTool, TapTool, BoxSelectTool, BoxZoomTool, ResetTool
from bokeh.models.graphs import from_networkx, NodesAndLinkedEdges, EdgesAndLinkedNodes
from bokeh.palettes import Spectral4
from bokeh.plotting import gridplot

from ipywidgets import interact
import ipywidgets

def get_apparitions( url ):
    html = requests.get(url)
    bs_obj = BeautifulSoup( html.text, "lxml")
    h4 = bs_obj.find({"h4":"Aparições em títulos da série:"})
    apparitions = [ i.text.replace("/", "-") for i in h4.findNext().find_all("a") ]
    return apparitions

def get_persona( persona_url ):
    apparitions = get_apparitions( persona_url )
    persona = persona_url.split("/")[-2]
    dct = { "persona":[persona]*len(apparitions),
            "apparition":apparitions}
    df = pd.DataFrame(dct)
    return df

def get_personas_urls( url ):
    html = requests.get( url )
    bs_obj = BeautifulSoup( html.text, "lxml" )
    h3s = bs_obj.find_all( "h3", style="padding-left: 30px;" )
    personas_urls = []
    for i in h3s:
        personas_urls += [ j.attrs["href"] for j in i.findNext().find_all("a") ]
    return personas_urls

def get_all_personas():
    url = "http://www.residentevildatabase.com/personagens/"
    personas_urls = get_personas_urls( url )
    dfs = [ get_persona(i) for i in personas_urls ]
    df = pd.concat( dfs, ignore_index=True )
    return df

def sort_names( row ):
    'Method to drop same relationship, i.e., persona_1 -> persona_2, persona_2 -> persona_1'
    names = [ row["persona_1"], row["persona_2"] ]
    names.sort()
    names = ", ".join(names)
    return names

def fix_persona( person_name ):
    name = person_name.split("-")
    name = " ".join( [i[0].upper() + i[1:] for i in name  ] )
    return name

def plot_df(G, persona=None):

    plot = Plot(plot_width=650, plot_height=650,
                x_range=Range1d(-1.1,1.1), y_range=Range1d(-1.1,1.1))

    if persona:
        plot.title.text = "Resident Evil Graph - {persona} social network".format(persona=persona)
    else:
        plot.title.text = "Resident Evil Graph"
    
    tooltips=[ ("Persona 1", "@persona_1"),
               ("Persona 2", "@persona_2"),
               ("First Game", "@first_game"),
               ("Last Game", "@last_game"),
               ("Interactions", "@weight")]
    
    plot.add_tools(HoverTool(tooltips = tooltips), TapTool(),
                   BoxSelectTool(), BoxZoomTool(), ResetTool())

    graph_renderer = from_networkx(G, nx.spring_layout, scale=1, center=(0,0))

    graph_renderer.node_renderer.glyph = Circle(size=15, fill_color=Spectral4[0])
    graph_renderer.node_renderer.selection_glyph = Circle(size=15, fill_color=Spectral4[2])
    graph_renderer.node_renderer.hover_glyph = Circle(size=15, fill_color=Spectral4[1])

    graph_renderer.edge_renderer.glyph = MultiLine(line_color="#CCCCCC", line_alpha=0.8, line_width=5)
    graph_renderer.edge_renderer.selection_glyph = MultiLine(line_color=Spectral4[2], line_width=5)
    graph_renderer.edge_renderer.hover_glyph = MultiLine(line_color=Spectral4[1], line_width=5)

    graph_renderer.selection_policy = NodesAndLinkedEdges()
    graph_renderer.inspection_policy = EdgesAndLinkedNodes()

    plot.renderers.append( graph_renderer )

    output_notebook()
    show( plot, notebook_handle=True )

def plot_persona_network(df, persona):
    personas = np.append( df["persona_2"][ df["persona_1"] == persona ].unique() , df["persona_1"][ df["persona_2"] == persona ].unique() )
    personas = np.unique( personas )
    df_new = df[ (df[ 'persona_1' ].isin( personas )) & (df[ 'persona_2' ].isin( personas )) ].copy()
    G = nx.from_pandas_edgelist(df=df_new, source="persona_1", target="persona_2",
                                edge_attr=["persona_1", "persona_2", "first_game", "last_game", 'weight'],
                                create_using=nx.Graph())

    plot_df(G, persona)