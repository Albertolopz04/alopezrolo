
import streamlit as st
import pandas as pd
import numpy as np
#import matplotlib.pyplot as plt

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
wecs = pd.read_csv('300_wecsdata.csv', delimiter=';',  error_bad_lines=False, encoding='latin-1')

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

# Filterig data
wecs_selected = wecs[(wecs['datavp']==('v')) & (wecs['power'].between(rated_power_min,rated_power_max, inclusive=False)) & (wecs["type"].isin(type_selected)) & (wecs["offshore?"]==of)]

# - Displaying the data
st.write('These are the WECS that match your parameters: ' + str(wecs_selected.shape[0]) + ' WECS.' )
#df_selected_wecs.loc[:,['Names','RatedPower','Rotor Diameter','Type']]
wecs_selected.loc[:,['name','power','bladediameter','type','web']]

'---'

# - Plotting the data
'### Plotting the results'

if st.checkbox('Show the Power Curve of each WECS'):
	for i in range(wecs_selected.shape[0]):
		st.write(str(i+1),'/',str(wecs_selected.shape[0]),'   -   ',wecs_selected.iloc[i,3])
		#wecs_selected.iloc[i,1],wecs_selected.iloc[i,3], wecs_selected.iloc[i,4], 'kW'
		w = wecs_selected.iloc[i,1]
		w = w*2 - 2
		
		# Store the wind and power data of the wecs in two variables
		wecsV=wecs.iloc[w,9:(9+90)]
		wecsP=wecs.iloc[(w+1),9:(9+90)]

		# Plotting the power curve of the wecs
		fig, ax = plt.subplots()
		ax.plot(wecsV,wecsP)
		ax.set(xlabel='Wind Speed (m/s)', ylabel='Power Output (KW)',
		       title=wecs.iloc[w,3])
		ax.grid()
		plt.show()
		st.pyplot(fig=fig)

		plt.scatter(wecsV,wecsP)
		plt.xlabel("copy")
		plt.ylabel("paste")
		st.pyplot(fig)

		wecs.iloc[w,0:7]
''
st.write('---')
# - Download all the data
'### Get all the data 📥'
# - Data unfiltered (hidden in a button)
':paperclip: You can also check the full database here:'
if st.checkbox('Show  unfiltered WECS list'):
	wecs
''

'⬇️ Or download the full database:'
if st.button('Download data'):
    st.write('...downloading data...')
else:
    st.write('')

st.write('---')
