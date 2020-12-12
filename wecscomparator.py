
import streamlit as st
import pandas as pd
import numpy as np
#from matplotlib import pyplot as plt

# - Setting web configuration
st.set_page_config(
    page_title="Wecs Comparator v2",
    page_icon=':cyclone:',    
    initial_sidebar_state="expanded",)

# - Heading
st.title('🔎 WECS Comparator v.2')
st.write("""
In this website you can *explore* the **wind turbine** that best suits your needs.
"""	)

'This project is a webapp able to provide a list of candidate wind turbines (WECS) to the user once he has decided what he is looking for. The user is able to observe and compare freely any turbine of the library whenever he wants. Once the WECS are filtered the following values will be displayed'
'* Manufacturer name'
'* Nominal Power'
'* Type'
'* Blades Diameter'
'* Onshore/Offshore'
'* Power and performance (cp) curve'
' '

# - Loading the data
st.cache()
wecs = pd.read_csv('300_wecsdata.csv', delimiter=',', error_bad_lines=False, encoding='latin-1')

# - Selecting the parameters
st.write("""	### Select the rated power	""")
rated_power_selected = st.slider('Rated Power (kW)', 0, 10000,2500,500 )
'You selected a ', rated_power_selected/1000, 'MW WECS'

# 1.Definir intervalo del rated power
interval = 501
rated_power_min = rated_power_selected - interval
rated_power_max = rated_power_selected + interval
'The app will show you WECS between ', rated_power_min + 1, ' and ', rated_power_max - 1, 'kW'

# 2.Seleccionar el tipo
st.write("""	### Select the type of generator	""")
type_selected=st.multiselect('Type', ['1','2','3','4'],['1','2','3','4'])

# 3.Seleccionar Onshore/Offshore
st.write("""	### Select whether the WECS is designed for Onshore/Offshore	""")
#offshore_selected = st.selectbox('Onshore/Offshore',['Onshore', 'Offshore'])
shore = st.radio("",('Onshore','Offshore'))
of = shore
if of == 'Offshore':
	of = 1
elif of == 'Onshore':
	of = 0
''
''

'### Results 📊'

# - Loading the data
#df = pd.read_csv('99_wecs_data.csv', delimiter=';', error_bad_lines=False, encoding='latin-1')
# Filterig data
#df_selected_wecs = df[(df['RatedPower'].between(rated_power_min,rated_power_max, inclusive=False)) & (df["Type"].isin(type_selected)) & (df["Offshore?"]==of)]
#df_selected_wecs = df[(df.Type.isin(type_selected)) & (df.RatedPower == rated_power_selected) & (df["Offshore?"]==of)]
wecs_selected = wecs[(wecs['datavp']==('v')) & (wecs['power'].between(rated_power_min,rated_power_max, inclusive=False)) & (wecs["type"].isin(type_selected)) & (wecs["offshore?"]==of)]

# - Displaying the data
st.write('These are the WECS that match your parameters: ' + str(df_selected_wecs.shape[0]) + ' WECS.' )
#df_selected_wecs.loc[:,['Names','RatedPower','Rotor Diameter','Type']]
wecs_selected.loc[:,['wecsID','name','power','bladediameter','type']]

'---'

# - Plotting the data
'### Plotting the results'


st.write('---')
# - Data unfiltered (hidden in a button)
''
':paperclip: You can also check the full database here:'
if st.checkbox('Show  unfiltered WECS list'):
	df

if st.button('Download data'):
    st.write('...downloading data...')
else:
    st.write('')

st.write('---')
