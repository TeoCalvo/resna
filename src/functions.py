import requests
from bs4 import BeautifulSoup
import pandas as pd

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