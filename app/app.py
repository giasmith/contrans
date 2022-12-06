#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import dash
from jupyter_dash import JupyterDash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import psycopg2
from sqlalchemy import create_engine
import os
import plotly.graph_objects as go
import plotly.express as px
import pymongo
from bson.json_util import loads, dumps


# In[2]:


postgres_password = os.environ['POSTGRES_PASSWORD']
mongo_username = os.environ['MONGO_INITDB_ROOT_USERNAME']
mongo_password = os.environ['MONGO_INITDB_ROOT_PASSWORD']
mongo_init_db = os.environ['MONGO_INITDB_DATABASE']
email = 'nqj5zk@virginia.edu'


# In[3]:


engine = create_engine("postgresql+psycopg2://{user}:{pw}@postgres:5432/{db}"
                       .format(user="postgres", pw=postgres_password, db="contrans"))
myclient = pymongo.MongoClient(f"mongodb://{mongo_username}:{mongo_password}@mongo:27017/{mongo_init_db}?authSource=admin")

contrans_db = myclient['contrans']
bills = contrans_db['bills']


# In[7]:


myquery='''
SELECT *
FROM members
'''
members = pd.read_sql_query(myquery, con=engine)


# In[ ]:


members['last_name'] = [x.title() for x in members['last_name']]
members['full_name'] = members['first_name'] + ' ' + members['last_name'] + ' (' + members['party'] + '-' + members['state'] + ')'
members['full_name']


# In[9]:


members = pd.read_sql_query(myquery, con=engine)


# In[10]:


member_list = [{'label':x, 'value':y} for x , y in zip(members['full_name'], members['propublica_id']) ]


# In[ ]:


def membergraph(propub):
    df = members.query(f"propublica_id == '{propub}'")

    fig = px.scatter(members, x='DWNOMINATE', y='votes_with_party_pct', labels = {'DWNOMINATE':'Left/Right Politcal Ideology', 
                                                                                  'votes_with_party_pct':'percent of time votes majority with party'},
                                                                         height = 600, width =600,
                                                                         hover_data = ['full_name'],
                                                                         color = 'party',
                                                                         symbol = 'chamber',
                                                                         opacity = .5,)

    fig.add_traces(x=df['DWNOMINATE', y=df[y='votes_with_party_pct'],
                        marker = dict(size=12),
                        marker_symbol='star')

return fig


# In[2]:


#external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
external_stylesheets = ['dbc.themes.LUX']


# ## Initialize the App

# In[3]:


app = JupyterDash(__name__, external_stylesheets=external_stylesheets)


# ## Specify Contents of dashboard

# In[4]:


app.layout = html.Div(
[
    
    html.H1("Congress Data Dashboards"), 
   
    #html.Div(
    
#    [dcc.Markdown(id='memberdata')]
#    style={'width':'65%', 'float':'right'} 
    
#    )
    
    
    #html.Div(
    
#    [dcc.Markdown(id='displaytable')]
#    style={'width':'30%', 'float':'left'} 
    
#    )
    
 #dcc.Dropdown(id='memberselect', options-memberlist, value=''),

    
dcc.Tab([
        
        dcc.Tab(label='Contact Info and Ideology',
               children=[ html.Div([
                   
                   #dcc.Markdown(id='displaytable')
                   #dcc.Graph(id='membergraph')

                  ])
               ])
            ])
    
dcc.Tab([
    label='Bills and Characteristics',
    children = [
        html.Div([
        dcc.Markdown['**These words best describe the bills this individual has sponsored!**']
        dcc.Markdown(id='charwords')
    ], style = {'width': '30%', 'float': 'left'},
            html.Div([
                dcc.Markdown('**This individual has sponsored the following bills**')
                dcc.Mardown
            ], style = width:'65%', )
        )]
])
    
    


# ## Callbacks

# In[5]:


#@app.callback([outputs to go back to dashboard], [inputs from the dashboard to next function] ) called a decorator
@app.callback(Output(component_id="displaydata", component_property='children'), 
              Input(component_id='memberselect', component_property='value')

def memberstats(name):
    df = members.query(f"propublica_id == {propub}")
    


# In[ ]:


propub = ''
df = members.query(f"propublica_id == '{propub}'")
df.columns
df = df[['']] # put all the col names you need for user to view
df.T
df.columns =['']
return df.to_markdown()


# In[6]:


@app.callback(Output(component_id="membergraph", component_property='figure'), 
              Input(component_id='memberselect', component_property='value')


def membergraph(propub):
    df = members.query(f"propublica_id == '{propub}'")

    fig = px.scatter(members, x='DWNOMINATE', y='votes_with_party_pct', labels = {'DWNOMINATE':'Left/Right Politcal Ideology', 
                                                                                  'votes_with_party_pct':'percent of time votes majority with party'},
                                                                         height = 600, width =1000,
                                                                         hover_data = ['full_name'],
                                                                         color = 'party',
                                                                         symbol = 'chamber',
                                                                         opacity = .5,)

    fig.add_traces(x=df['DWNOMINATE', y=df[y='votes_with_party_pct'],
                        marker = dict(size=12),
                        marker_symbol='star')

return fig


# In[ ]:


@app.callback(Output(component_id="charwords", component_property='children'), 
              Input(component_id='memberselect', component_property='value')
              
def charwords(propub):
    myquery=f'''
    SELECT word, tf_idf
    FROM charwords
    WHERE sponsor_id = '{propub}'
    '''
    tab= pd.read_sql_query(myquery, con=engine)
    return tab.to_markdown()

@app.callback(Output(component_id="bills", component_property='children'), 
              Input(component_id='memberselect', component_property='value')
              
def get_bills(propub):
    myquery = bills.find({'sponsor_id':propub},
                         {'_id' : 0,
                          'number': 1,
                          'short_title' : 1,
                          'house_passage':1,
                          'senate_passage':1,
                          'enacted': 1,
                          'latest_major_action':1
                         })
    tab = pd.DataFrame.from_records(loads(dumps(myquery)))
    return tab.Markdown(propub)


# ## Run the App

# In[7]:


if __name__== "__main__":
    app.run_server(mode= 'external', host = "0.0.0.0", debug=True)
    # mode = 'inline' shows in jupyter notebook, 'external' shows on webpage?


# In[13]:

