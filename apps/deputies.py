import streamlit as st
import pandas as pd
import base64
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
from matplotlib.backends.backend_agg import RendererAgg
from datetime import date
from PIL import Image
  
#Loading the data
@st.cache
def get_data_votes():
    df = pd.read_csv(os.path.join(os.getcwd(), 'data', 'df_vote_descr.csv'))
    df['year'] = df['date'].astype(str).str[0:4]
    df['month'] = df['date'].astype(str).str[5:7]
    df['day'] = df['date'].astype(str).str[8:10]
    df['datetime'] = pd.to_datetime(df[['year', 'month', 'day']], errors = 'coerce')
    df['percentage of votes in favor'] = 100*df['pour']/df['nb votants']
    df['accepted'] = 'no'
    df.loc[df['pour'] >= df['requis'], 'accepted'] = 'yes'
    df = df.drop(columns=['date'])
    df.columns = df.columns.str.replace('demandeur ', '')
    return df

@st.cache
def get_data_deputies():
    df = pd.read_csv(os.path.join(os.getcwd(), 'data', 'df_dep.csv'))
    #create the value age from the date of birth of the deputies
    df['age']  = df['date of birth'].astype(str).str[0:4]
    df['age']  = date.today().year - df['age'].astype(int)
    df['departement'] = df['dep'].astype(str) + ' ('+ df['num_dep'] + ')'
    df['full_name'] = df['first name'].astype(str) + ' '+ df['family name']
    df['title'] = 'Mr.'
    df.loc[df['sex']=='female', 'title'] = 'Mme.'
    return df

@st.cache
def get_data_political_parties():
    df = pd.read_csv(os.path.join(os.getcwd(), 'data', 'df_polpar.csv'))
    df = df.drop(columns=['code'])
    return df

@st.cache
def get_data_organs():
    df = pd.read_csv(os.path.join(os.getcwd(), 'data', 'df_organs.csv'))
    return df

@st.cache
def get_data_deputies_in_organs():
    df = pd.read_csv(os.path.join(os.getcwd(), 'data', 'df_deputies_in_organs.csv'))
    return df

@st.cache
def get_data_vote_total():
    df = pd.read_csv(os.path.join(os.getcwd(), 'data', 'df_vote_total.csv'),
    dtype={
        'pour': float,
        'contre': float,
        'non votants' : float,
        'abstentions' : float,
        'par delegation' : float
            })
    df['vote'] = 1
    df['cause'] = df['cause'].fillna('none')
    df['cause'] = df['cause'].astype("category")
    df['deputy code'] = df['deputy code'].astype("category")
    df['scrutin'] = df['scrutin'].astype("category")
    return df

#def app():
    #configuration of the page
st.set_page_config(layout="wide")
matplotlib.use("agg")
_lock = RendererAgg.lock

SPACER = .2
ROW = 1

#Load dataframes
df_dep = get_data_deputies()
df_votes = get_data_votes()
df_polpar = get_data_political_parties()
df_vote_total = get_data_vote_total()
df_organs = get_data_organs()
df_deputies_in_organs = get_data_deputies_in_organs()

departement_list = ['']
for i in range(len(df_dep.sort_values(by=['num_dep'])['departement'].unique())):
    departement_list.append(df_dep.sort_values(by=['num_dep'])['departement'].unique()[i])


# Sidebar 
#selection box for the different features
st.sidebar.header('Select what to display')
departement_selected = st.sidebar.selectbox('Select departement', departement_list, help='Select a region to filter out deputies')
if(departement_selected == ''):
    departement_selected = df_dep.sort_values(by=['num_dep'])['departement'].unique()
else:
    departement_selected = [departement_selected]
sex_selected = st.sidebar.selectbox('Select sex', ['both','female','male'])
sex_selected = [sex_selected]
if sex_selected == ['both']:
    sex_selected = ['female', 'male']
pol_party_selected = st.sidebar.multiselect('Select political parties', df_polpar['abreviated_name'].unique().tolist(), df_polpar['abreviated_name'].unique().tolist(),
                                            help='Select one or multiple political parties to filter out deputies')

#creates masks from the sidebar selection widgets
mask_departement = df_dep['departement'].isin(departement_selected)
mask_sex = df_dep['sex'].isin(sex_selected)
mask_pol_parties = df_dep['pol party'].isin(pol_party_selected)

#Apply the mask
display_df = df_dep[mask_departement & mask_sex & mask_pol_parties]

#Make a selection box with pre-selected deputies
deputy_selected = st.sidebar.selectbox('List of deputies corresponding', display_df.sort_values(by=['sex', 'full_name'])['full_name'].unique())
deputy = df_dep[df_dep['full_name'].isin([deputy_selected])].reset_index()

#get all the organs the deputy selected is belonging to
df_dep_in_org = df_deputies_in_organs.loc[df_deputies_in_organs['code_deputy'] == deputy['code'][0]]
df_org = pd.merge(df_dep_in_org, df_organs, left_on='code_organe', right_on='code').drop(columns=['code_organe', 'code_deputy', 'code'])
drop_list = ['GA', 'PARPOL', 'ASSEMBLEE', 'GP']
for item in drop_list:
    df_org = df_org.drop(df_org[(df_org['type'] == item)].index)
df_org = df_org.drop_duplicates()

title_spacer1, title, title_spacer_2 = st.beta_columns((.1,ROW,.1))
with title:
    st.title('Deputy information')
st.header('')

img_path = os.path.join(os.getcwd(), 'data', 'pictures', deputy['code'][0]+ '.png')
st.write(img_path)

img = np.array(Image.open(img_path))

st.image(img)


### Vote repartition
row1_spacer1, row1_1, row1_spacer2, row1_2, row1_spacer3 = st.beta_columns((SPACER,ROW, SPACER,ROW, SPACER))

with row1_1:
    
    st.write(deputy['title'][0] + ' ' + deputy['full_name'][0])
    st.write('Deputy of ' + deputy['pol party'][0] + ', elected in the circumscription number ' + str(deputy['circo'][0]) + ' in the region of ' + deputy['dep'][0])
    st.write('Part of the ' + df_org.loc[df_org['type'] == 'COMPER']['name'].to_list()[0])

study_groups_list = df_org.loc[df_org['type'] == 'GE']['name'].to_list()
text = ''
for study_group in study_groups_list:
    text = text + '\n* ' + study_group

with row1_2:
    st.markdown('Also part of the study groups on : ' + text[0:-2])


#calculate presence to vote
#get the average presence to the votes and average position of each party

nb_votes = len(df_vote_total['scrutin'].unique())
nb_deputies = len(df_vote_total['deputy code'].unique())
for column in ['pour', 'contre', 'abstentions', 'non votants', 'par delegation']:
    df_vote_total[column] = df_vote_total[column].astype(float)

selected_deputy_vote_information = df_vote_total.loc[df_vote_total['deputy code'] == deputy['code'][0]]
selected_deputy_vote_information = selected_deputy_vote_information.agg({'pour':'sum','contre':'sum', 'abstentions':'sum', 'non votants':'sum', 'par delegation':'sum', 'vote':'sum'})
for column in ['pour', 'contre', 'abstentions', 'non votants', 'par delegation']:
    selected_deputy_vote_information[column] = (selected_deputy_vote_information[column]/selected_deputy_vote_information['vote'])
selected_deputy_vote_information['vote percentage'] = selected_deputy_vote_information['vote']/nb_votes

all_deputy_vote_information = df_vote_total
all_deputy_vote_information = all_deputy_vote_information.agg({'pour':'sum','contre':'sum', 'abstentions':'sum', 'non votants':'sum', 'par delegation':'sum', 'vote':'sum'})
all_deputy_vote_information['vote percentage'] = all_deputy_vote_information['vote']/(nb_votes*nb_deputies)


st.text(selected_deputy_vote_information)
st.text(all_deputy_vote_information)

# #Sum all votes of deputies
# df_vote_total = df_vote_total.drop(columns=['scrutin', 'deputy code']).groupby(['pol party']).agg({'pour':'sum','contre':'sum', 'abstentions':'sum', 'non votants':'sum', 'par delegation':'sum', 'vote':'sum'})
# df_vote_total = pd.merge(df_vote_total, df_pol_parties.drop(columns=['name']), left_on='pol party', right_on='pol party')

# #calculate the average presence to the votes and average position of each party
# for column in ['vote', 'pour', 'contre', 'abstentions', 'non votants', 'par delegation']:
#     df_vote_total[column] = df_vote_total[column]/(df_vote_total['members']*nb_votes)
# df_vote_total = df_vote_total.sort_values(by=['vote'], ascending=False).reset_index(drop=True)


### Participation to votes
row2_spacer1, row2_1, row2_spacer2, row2_2, row2_spacer3 = st.beta_columns((SPACER,ROW,SPACER,ROW, SPACER))
with row2_1, _lock:
    
    vote_percentage = round(selected_deputy_vote_information['vote percentage']*100,2)
    st.write(vote_percentage)

    st.header("Participation to votes")
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.pie([vote_percentage, 100-vote_percentage], wedgeprops = { 'linewidth' : 7, 'edgecolor' : 'white' })
    label = ax.annotate(str(vote_percentage)+'%', xy=(0,-0.15), fontsize=22, ha='center')
    plt.gcf().gca().add_artist(plt.Circle( (0,0), 0.7, color='white'))
    st.pyplot(fig)


#vote 
row3_spacer1, row3_1, row3_spacer2, row3_2, row3_spacer3 = st.beta_columns((SPACER,ROW,SPACER,ROW, SPACER))
with row3_1, _lock:
    st.header("Vote")
    vote = [selected_deputy_vote_information['pour'], selected_deputy_vote_information['contre'], selected_deputy_vote_information['abstentions']]
    vote.append(selected_deputy_vote_information['pour'] + selected_deputy_vote_information['contre'] + selected_deputy_vote_information['abstentions'])
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.pie(vote, labels=['pour', 'contre', 'abstention', ''], wedgeprops = { 'linewidth' : 7, 'edgecolor' : 'white' }, colors= ['green', 'red', 'blue', 'white'])
    plt.gcf().gca().add_artist(plt.Circle( (0,0), 0.7, color='white'))
    st.pyplot(fig)