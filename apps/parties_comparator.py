import streamlit as st
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
from matplotlib.backends.backend_agg import RendererAgg
from datetime import date
 
#Loading the data
@st.cache
def get_data_deputies():
    df = pd.read_csv(os.path.join(os.getcwd(), 'data', 'df_dep.csv'))
    #create the value age from the date of birth of the deputies
    df['age']  = df['date of birth'].astype(str).str[0:4]
    df['age']  = date.today().year - df['age'].astype(int)
    df = df.drop(columns=['family name', 'first name', 'date of birth'])
    return df

@st.cache
def get_data_political_parties():
    df = pd.read_csv(os.path.join(os.getcwd(), 'data', 'df_polpar.csv'))
    df = df.drop(columns=['code'])
    df = df.rename(columns={"abreviated_name": "pol party"})
    return df

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
def get_data_vote_total():
    df = pd.read_csv(os.path.join(os.getcwd(), 'data', 'df_vote_total.csv'),
    dtype={
        'pour': bool,
        'contre': bool,
        'non votants' : bool,
        'abstentions' : bool,
        'par delegation' : bool
            })
    #df['scrutin'] = df['scrutin'].map(lambda x: x.lstrip('VTANR5L15V'))
    df['cause'] = df['cause'].fillna('none')
    df['cause'] = df['cause'].astype("category")
    df['deputy code'] = df['deputy code'].astype("category")
    df['scrutin'] = df['scrutin'].astype("category")
    return df

def apply_grey_filter(df, party):
    df_2 = df.copy(deep=True)
    df_2.loc[df_2['pol party'] != party, 'color'] = 'lightgrey'
    return df_2['color'].tolist()

def get_party_description(party):
    parties = {
        'LAREM': 'La République En Marche! (translatable as "The Republic...On the Move). It is a centrist and liberal political party in France. The party was founded on 6 April 2016 by Emmanuel Macron. Presented as a pro-European party, Macron considers LREM to be a progressive movement, uniting both the left and the right',
        'PS' : 'The Socialist Party (PS) is a French political party historically classified on the left and more recently on the center left of the political spectrum. Launched in 1969, it has its origins in the socialist school of thought.',
        'REP' : 'Les Républicains (LR) is a French Gaullist and liberal-conservative political party, classified on the right and center right of the political spectrum. It emerged from the change of name and statutes of the Union for a Popular Movement (UMP) in 2015. It is in line with the major conservative parties.',
        'MODEM' : 'The Democratic Movement (MODEM) is a French political party of the center created by François Bayrou (then president of the UDF) following the presidential election of 2007. The MODEM aims to bring together democrats concerned with an independent and central position on the political scene.',
        'FI' : 'La France insoumise (FI) is a French political party founded on February 10, 2016 by Jean Luc Mélanchon. Its political positioning is mainly considered radical left, but also sometimes far left.',
        'ND' : 'Not declared. This category represents all the people not affiliated to a political party or affiliated to a political party but with less than 7 deputies at the national assembly.',
        'RPS' : 'Régions et peuples solidaires (RPS) is a political party that federates regionalist or autonomist political organizations in France. The political currents represented range from centrism to democratic socialism with a strong environmentalist sensibility.',
        'UDRL' : 'The Union of Democrats and Independents (UDI, also called Union des Démocrates Radicaux et Libéraux; UDRL) is a French center-right political party, founded by Jean-Louis Borloo on October 21, 2012. Until 2018, the UDI is composed of different parties that retain their existence, forming a federation of parties.',
        'PCF' : "The French Communist Party (French: Parti communiste français, PCF) is a communist party in France. Founded in 1920 by the majority faction of the socialist French Section of the Workers' International (SFIO).",
        'EELV' : 'Europe Écologie Les Verts (abbreviated to EELV) is a French environmentalist political party that succeeded the party Les Verts on November 13, 2010, following a change of statutes to bring together the activists who came as part of the lists Europe Écologie in the European elections of 2009 and regional elections of 2010.'    
    }
    return parties[party]


def app():
    #configuration of the page
    #st.set_page_config(layout="wide")
    matplotlib.use("agg")
    _lock = RendererAgg.lock

    SPACER = .2
    ROW = 1

    #load dataframes
    df_deputies = get_data_deputies()
    df_pol_parties = get_data_political_parties()
    df_votes = get_data_votes()
    df_vote_total = get_data_vote_total()

    title_spacer1, title, title_spacer_2 = st.beta_columns((.1,ROW,.1))
    with title:
        st.title('Compare groups of deputies depending on their political party')

    ### Select box and description
    row0_spacer1, row0_1, row0_spacer2, row0_2, row0_spacer3 = st.beta_columns((SPACER,ROW,SPACER,ROW, SPACER))
    with row0_1, _lock:
        party_1 = st.selectbox('Select political party', df_deputies['pol party'].unique(), key='1')
        st.write(get_party_description(party_1))

    with row0_2, _lock:
        party_2 = st.selectbox('Select political party', df_deputies['pol party'].unique(), key='2')
        st.write(get_party_description(party_2))

    ### Political parties
    row1_spacer1, row1_1, row1_spacer2, row1_2, row1_spacer3 = st.beta_columns((SPACER,ROW,SPACER,ROW, SPACER))

    with row1_1, _lock:
        deputies_group_1 = df_deputies[df_deputies['pol party'] == party_1]
        df = df_pol_parties.sort_values(by=['members'], ascending=False)
        df.loc[df['pol party'] != party_1, 'color'] = 'lightgrey'
        colors = df['color'].tolist()
        df = df[df['pol party'] == party_1]
        color_1 = df['color'].to_list()

        st.header("Number of members")
        fig, ax = plt.subplots(figsize=(5, 5))
        ax.pie(df_deputies['pol party'].value_counts(), labels=(df_deputies['pol party'].value_counts().index), 
            wedgeprops = { 'linewidth' : 7, 'edgecolor' : 'white' }, colors=colors)
        p = plt.gcf()
        c2 = plt.Circle( (0,0), 0.7, color='white')
        text = deputies_group_1['pol party'].value_counts().index[0] + ' : ' 
        text = text + deputies_group_1['pol party'].value_counts().map(str).to_list()[0] + '\n('
        text = text + str(round(100*deputies_group_1['pol party'].value_counts().to_list()[0]/len(df_deputies.index),2)) + '%)'
        label = ax.annotate(text, xy=(0,-0.15), fontsize=22, ha='center')
        p.gca().add_artist(plt.Circle( (0,0), 0.7, color='white'))
        st.pyplot(fig)

    with row1_2, _lock:
        deputies_group_2 = df_deputies[df_deputies['pol party'] == party_2]
        df = df_pol_parties.sort_values(by=['members'], ascending=False)
        df.loc[df['pol party'] != party_2, 'color'] = 'lightgrey'
        colors = df['color'].tolist()
        df = df[df['pol party'] == party_2]
        color_2 = df['color'].to_list()

        st.header("Number of members")
        fig, ax = plt.subplots(figsize=(5, 5))
        ax.pie(df_deputies['pol party'].value_counts(), labels=(df_deputies['pol party'].value_counts().index), 
            wedgeprops = { 'linewidth' : 7, 'edgecolor' : 'white' }, colors=colors)
        p = plt.gcf()
        c2 = plt.Circle( (0,0), 0.7, color='white')
        text = deputies_group_2['pol party'].value_counts().index[0] + ' : ' 
        text = text + deputies_group_2['pol party'].value_counts().map(str).to_list()[0] + '\n('
        text = text + str(round(100*deputies_group_2['pol party'].value_counts().to_list()[0]/len(df_deputies.index),2)) + '%)'
        label = ax.annotate(text, xy=(0,-0.15), fontsize=22, ha='center')
        p.gca().add_artist(plt.Circle( (0,0), 0.7, color='white'))
        st.pyplot(fig)

    ### Age repartition
    row2_spacer1, row2_1, row2_spacer2, row2_2, row2_spacer3 = st.beta_columns((SPACER,ROW, SPACER,ROW, SPACER))

    with row2_1, _lock:
        st.header('Age repartition')
        fig, ax = plt.subplots(figsize=(5, 5))
        ax = sns.histplot(data=deputies_group_1, x="age", bins=12, stat="probability", palette = color_1)
        st.pyplot(fig)

    with row2_2, _lock:
        st.header('Age repartition')
        fig, ax = plt.subplots(figsize=(5, 5))
        ax = sns.histplot(data=deputies_group_2, x="age", bins=12, stat="probability", palette = color_2)
        st.pyplot(fig)

    ### Percentage of women per parties
    row3_spacer1, row3_1, row3_spacer2, row3_2, row3_spacer3 = st.beta_columns((SPACER,ROW,SPACER,ROW, SPACER))

    #caluculate the proportion of women per parties
    df_sex = pd.concat([df_deputies.drop(columns=['code', 'activity', 'age']),pd.get_dummies(df_deputies.drop(columns=['code', 'activity', 'age'])['sex'], prefix='sex')],axis=1)
    df_sex = df_sex.groupby(['pol party']).agg({'sex_female':'sum','sex_male':'sum'})
    df_sex['pol party'] = df_sex.index
    df_sex['total'] = df_sex['sex_female'].astype(int) + df_sex['sex_male'].astype(int)
    df_sex['sex_female'] = df_sex['sex_female'].astype(int)/df_sex['total']

    #prepare df_sex for color selection
    df_sex = df_sex.reset_index(drop=True)
    df_sex = df_sex.sort_values(by=['pol party'])
    df_with_selected_pol_parties = df_pol_parties[df_pol_parties['pol party'].isin(df_sex['pol party'].unique().tolist())].sort_values(by=['pol party'])
    df_sex['color'] = df_with_selected_pol_parties['color'].tolist()
    df_sex = df_sex.sort_values(by=['sex_female'], ascending=False).reset_index(drop=True)


    with row3_1, _lock:
        st.header('Percentage of women deputies')
        fig, ax = plt.subplots(figsize=(5, 5))
        sns.barplot(x="sex_female", y="pol party", data=df_sex, ax=ax, palette=apply_grey_filter(df_sex, party_1))

        i = 0
        text = (df_sex['sex_female'].round(2)*100).astype(int).to_list()
        for rect in ax.patches:
            if i == int(np.where(df_sex['pol party']==party_1)[0]):
                height = rect.get_height()
                ax.text(rect.get_x() + rect.get_width() / 2., rect.get_y() + height * 3 / 4.,
                        str(text[i])+'%', ha='center', va='bottom', rotation=0, color='black', fontsize=12)
            i = i + 1
        ax.set(xlabel=None)
        ax.set(ylabel=None)
        ax.set(xticklabels=[])
        st.pyplot(fig)

    with row3_2, _lock:
        st.header('Percentage of women deputies')
        fig, ax = plt.subplots(figsize=(5, 5))
        sns.barplot(x="sex_female", y="pol party", data=df_sex, ax=ax, palette=apply_grey_filter(df_sex, party_2))

        i = 0
        text = (df_sex['sex_female'].round(2)*100).astype(int).to_list()
        for rect in ax.patches:
            if i == int(np.where(df_sex['pol party']==party_2)[0]):
                height = rect.get_height()
                ax.text(rect.get_x() + rect.get_width() / 2., rect.get_y() + height * 3 / 4.,
                        str(text[i])+'%', ha='center', va='bottom', rotation=0, color='black', fontsize=12)
            i = i + 1
        ax.set(xlabel=None)
        ax.set(ylabel=None)
        ax.set(xticklabels=[])
        st.pyplot(fig)


    ### Job repartition
    row4_spacer1, row4_1, row4_spacer2, row4_2, row4_spacer3 = st.beta_columns((SPACER,ROW, SPACER,ROW, SPACER))

    with row4_1, _lock:
        st.header('Previous job repartition')
        fig, ax = plt.subplots(figsize=(5, 5))
        ax.pie(deputies_group_1['activity'].value_counts(), labels=(deputies_group_1['activity'].value_counts().index + ' (' + deputies_group_1['activity'].value_counts().map(str) + ')'), wedgeprops = { 'linewidth' : 7, 'edgecolor' : 'white' })
        p = plt.gcf()
        p.gca().add_artist(plt.Circle( (0,0), 0.7, color='white'))
        st.pyplot(fig)

    with row4_2, _lock:
        st.header('Previous job repartition')
        fig, ax = plt.subplots(figsize=(5, 5))
        ax.pie(deputies_group_2['activity'].value_counts(), labels=(deputies_group_2['activity'].value_counts().index + ' (' + deputies_group_2['activity'].value_counts().map(str) + ')'), wedgeprops = { 'linewidth' : 7, 'edgecolor' : 'white' })
        p = plt.gcf()
        p.gca().add_artist(plt.Circle( (0,0), 0.7, color='white'))
        st.pyplot(fig)

    ### Average presence / average vote (for, against, absent)
    row5_spacer1, row5_1, row4_spacer2, row5_2, row5_spacer3 = st.beta_columns((SPACER,ROW, SPACER,ROW, SPACER))

    nb_votes = len(df_vote_total['scrutin'].unique())

    df_vote_total = pd.merge(df_vote_total, df_deputies.drop(columns=['sex', 'activity','age']), left_on='deputy code', right_on='code')
    df_vote_total['vote'] = 1
    columns = ['pour', 'contre', 'abstentions', 'non votants', 'par delegation']
    for column in columns:
        df_vote_total[column] = df_vote_total[column].astype(int)

    df_vote_total = df_vote_total.drop(columns=['scrutin', 'deputy code']).groupby(['pol party']).agg({'pour':'sum','contre':'sum', 'abstentions':'sum', 'non votants':'sum', 'par delegation':'sum', 'vote':'sum'})
    df_vote_total = pd.merge(df_vote_total, df_pol_parties.drop(columns=['name']), left_on='pol party', right_on='pol party')

    columns = ['vote', 'pour', 'contre', 'abstentions', 'non votants', 'par delegation']
    for column in columns:
        df_vote_total[column] = df_vote_total[column]/(df_vote_total['members']*nb_votes)
    df_vote_total = df_vote_total.sort_values(by=['vote'], ascending=False).reset_index(drop=True)

    #st.text(df_vote_total)

    with row5_1, _lock:
        st.header('Percentage of the deputies at each vote')
        fig, ax = plt.subplots(figsize=(5, 5))
        sns.barplot(x="vote", y="pol party", data=df_vote_total, ax=ax, palette=apply_grey_filter(df_vote_total, party_1))
        i = 0
        text = (df_vote_total['vote'].round(4)*100).astype(float).round(4).to_list()
        for rect in ax.patches:
            if i == int(np.where(df_vote_total['pol party']==party_1)[0]):
                height = rect.get_height()
                ax.text(rect.get_x() + rect.get_width() / 2., rect.get_y() + height * 3 / 4.,
                        str(text[i])+'%', ha='center', va='bottom', rotation=0, color='black', fontsize=12)
            i = i + 1
        ax.set(xlabel='Percentage of deputies to each vote')
        ax.set(ylabel=None)
        ax.set(xticklabels=[])
        st.pyplot(fig)
        

    with row5_2, _lock:
        st.header('Percentage of the deputies at each vote')
        fig, ax = plt.subplots(figsize=(5, 5))
        sns.barplot(x="vote", y="pol party", data=df_vote_total, ax=ax, palette=apply_grey_filter(df_vote_total, party_2))
        i = 0
        text = (df_vote_total['vote'].round(4)*100).astype(float).round(4).to_list()
        for rect in ax.patches:
            if i == int(np.where(df_vote_total['pol party']==party_2)[0]):
                height = rect.get_height()
                ax.text(rect.get_x() + rect.get_width() / 2., rect.get_y() + height * 3 / 4.,
                        str(text[i])+'%', ha='center', va='bottom', rotation=0, color='black', fontsize=12)
            i = i + 1
        ax.set(xlabel='Percentage of deputies to each vote')
        ax.set(ylabel=None)
        ax.set(xticklabels=[])
        st.pyplot(fig)
        


