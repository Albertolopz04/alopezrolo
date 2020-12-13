
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# - Setting web configuration
st.set_page_config(
    page_title="Wecs Easy Choice v.2",
    page_icon=':cyclone:',    
    initial_sidebar_state="expanded",)

# - Heading
st.title('🔎 WECS Easy Choice v.2')
st.write("""
In this webapp you can *find* the **wind turbine** that best suits your needs.
"""	)

'This project is a webapp able to provide a list of candidate Wind Energy Conversion System (WECS) to the user after he has selected a couple parameters. The user is able to observe and compare freely any turbine of the around 300 WECS database whenever he wants.' 
'Once the WECS are filtered the following values will be displayed'
'* Manufacturer name'
'* Nominal Power'
'* Type'
'* Blades Diameter'
'* Onshore/Offshore'
'* Website of the manufacturer'
'* Power and performance (cp) curve'
' '
'---'
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
# 4.Seleccionar el fabricante
manufacturer_selected = 'All'
if st.checkbox('Select manufacturer'):
	st.write("""	### Filter by manufacturer	""")
	st.write('This is optional, if you don\'t want to filter by manufacturer deselect the checkbox')
	# Convert the csv file into a list to display it on the select box
	manufacturer = pd.read_csv('manufacturerList.csv', delimiter=';', error_bad_lines=False, encoding='utf-8')
	brand = manufacturer['manufacturerName'].tolist()
	brand.append(' ')
	manufacturer_selected = st.selectbox('Choose the manufacturer', brand,58)

	if manufacturer_selected == ' ':
		manufacturer_selected = 0
	elif manufacturer_selected == 'Acciona':
		manufacturer_selected = 1
	else:
		manufacturer_selected = manufacturer[manufacturer['manufacturerName']==manufacturer_selected].iloc[0,0]


'## Results 📊'

# - Loading the data
df = pd.read_csv('99_wecs_data.csv', delimiter=';', error_bad_lines=False, encoding='latin-1')
# Filterig data
if manufacturer_selected != 'All':
	wecs_selected = wecs[(wecs.brandID==manufacturer_selected) & (wecs.datavp=='v') & (wecs['power'].between(rated_power_min,rated_power_max, inclusive=False)) & (wecs["type"].isin(type_selected)) & (wecs["offshore?"]==of)]
else:
	wecs_selected = wecs[(wecs.datavp=='v') & (wecs['power'].between(rated_power_min,rated_power_max, inclusive=False)) & (wecs["type"].isin(type_selected)) & (wecs["offshore?"]==of)]


# - Displaying the data
if (wecs_selected.shape[0]) == 0:
	st.error('There are no WECS that match your criteria')
	st.write('Modify the parameters that you have selected.')
else:
	st.success(str(wecs_selected.shape[0]) + ' WECS meet your criteria.')
	st.write('These are the WECS that match your parameters: ')
	wecs_selected.loc[:,['wecsID','name','power','bladediameter','type']]
	

'---'


# - Plotting the data
'### Plotting the results'
wecsSeries = pd.DataFrame()
legend = []
st.warning('You should only check this once you have narrowed down the search to a handful number of WECS.\n Otherwise, the app will be slowed down.')
if st.checkbox('Show the power curve of the results'):
	'#### Graph of all the WECS that meet the user criteria'
	fig, ax = plt.subplots()
	for i in range(wecs_selected.shape[0]):
		w = wecs_selected.iloc[i,1]
		w = w*2 - 2
		
		# Store the wind and power data of the wecs in two variables
		wecsV=wecs.iloc[w,9:(9+90)]
		wecsP=wecs.iloc[(w+1),9:(9+90)]
		wecsSeries = pd.concat([wecsSeries,wecsV,wecsP], axis = 1)
		a = int(2*i+1)
		b = int(2*i)
		ax.plot(wecsSeries.iloc[:,b],wecsSeries.iloc[:,a])
		legend.append(wecs_selected.iloc[i,3])
		


	ax.set(xlabel='Wind Speed (m/s)', ylabel='Power Output (KW)', title='WECS Comparator')
	ax.grid()
	plt.legend(legend)
	#plt.legend(wecs_selected.iloc[i,3].tolist())
	plt.show()
	st.pyplot(fig=fig)



	'#### Individual WECS power curve'
	# 1. Select the WECS that is going to be plotted
	wecs_plotted = st.selectbox('Choose the WECS to plot',wecs_selected['name'].tolist())
	# Find the wecsID of the selected WECS
	w = wecs_selected[wecs_selected['name']==wecs_plotted].iloc[0,1]
	# Find it in the dataframe
	w = w*2 - 2

	# Store the wind and power data of the wecs in two variables
	wecsV=wecs.iloc[w,9:(9+90)]
	wecsP=wecs.iloc[(w+1),9:(9+90)]

	# Plotting the power curve of the wecs
	fig, ax = plt.subplots()
	ax.plot(wecsV,wecsP)
	ax.set(xlabel='Wind Speed (m/s)', ylabel='Power Output (KW)', title=wecs.iloc[w,3])
	ax.grid()
	plt.show()
	st.pyplot(fig=fig)

	# Giving additional information of the WECS
	if st.checkbox('Show details'):
		st.write('Database references:')
		st.table(wecs.iloc[w,1:9])

	wecsSeries = pd.concat([wecsV,wecsP], axis = 1)
	'---'

	# 2. Allow the user to see the plot of all the WECS that meet the user criteria.
	'#### Power curve of all the WECS found'
	''
	if st.checkbox('Show the all the Power Curve of each WECS'):
		for i in range(wecs_selected.shape[0]):
			st.write(str(i+1),'/',str(wecs_selected.shape[0]),'   -   ',wecs_selected.iloc[i,3])
			#wecs_selected.iloc[i,1],wecs_selected.iloc[i,3], wecs_selected.iloc[i,4], 'kW'
			w = wecs_selected.iloc[i,1]
			w = w*2 - 2
			
			# Store the wind and power data of the wecs in two variables
			wecsV=wecs.iloc[w,9:(9+90)]
			wecsP=wecs.iloc[(w+1),9:(9+90)]
			wecsSeries = pd.concat([wecsSeries,wecsV,wecsP], axis = 1)
			

			# Plotting the power curve of the wecs
			fig, ax = plt.subplots()
			ax.plot(wecsV,wecsP)
			ax.set(xlabel='Wind Speed (m/s)', ylabel='Power Output (KW)', title=wecs.iloc[w,3])
			ax.grid()
			plt.show()
			st.pyplot(fig=fig)

			# Giving additional information of the WECS
			st.write('Database references:')
			st.table(wecs.iloc[w,1:9])




''
st.write('---')
# - Download all the data
'### Get all the data 📥'
# - Data unfiltered (hidden in a button)
':paperclip: You can also check the full database here:'
if st.checkbox('Show  unfiltered WECS list'):
	st.dataframe(wecs[(wecs.datavp=='v')].iloc[:,1:9])
''

'⬇️ Or download the full database:'
if st.button('Download data'):
    st.write('...downloading data...')
else:
    st.write('')

st.write('---')
