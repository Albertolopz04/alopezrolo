
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import base64
import os

# - Setting web configuration
st.set_page_config(
    page_title="Wecs Easy Choice v.2",
    page_icon=':cyclone:',    
    initial_sidebar_state="expanded",)

# - Heading
st.title('🔎 WECS Easy Choice v.2')
st.write("""In this webapp you can *find* the **wind turbine** that best suits your needs."""	)
# - Loading the data
st.cache()
wecs = pd.read_csv('300_wecsdata.csv', delimiter=';',  error_bad_lines=False, encoding='latin-1')

# - Selecting the parameters
st.sidebar.write("""	### Select the rated power	""")
rated_power_selected = st.sidebar.slider('Rated Power (kW)', 0, 10000,2500,500 )
#'You selected a ', rated_power_selected/1000, 'MW WECS'

# 1.Definir intervalo del rated power
interval = 501
rated_power_min = rated_power_selected - interval
rated_power_max = rated_power_selected + interval
st.sidebar.write('The app will show you WECS between ', rated_power_min + 1, ' and ', rated_power_max - 1, 'kW')

# 2.Seleccionar el tipo
st.sidebar.write("""	### Select the type of wind turbine	""")
#st.sidebar.write(
#""" If you dont know what this mean check this [article](https://solarfeeds.com/types-of-wind-turbine-generators-and-their-functions/)"""
#)
type_selected=st.sidebar.multiselect('Type', ['1','2','3','4'],['1','2','3','4'])

# 3.Seleccionar Onshore/Offshore
st.sidebar.write("""	### Select whether the WECS is designed for Onshore/Offshore""")
shore = st.sidebar.radio("Select if the WECS you are looking for is going to be at see or at land.",('Onshore','Offshore'))
of = shore
if of == 'Offshore':
	of = 1
elif of == 'Onshore':
	of = 0

# 4.Seleccionar el fabricante
st.sidebar.write("""	### Filter by manufacturer	""")
manufacturer_selected = ' '
if st.sidebar.checkbox('Select manufacturer'):
	
	# Convert the csv file into a list to display it on the select box
	manufacturer = pd.read_csv('manufacturerList.csv', delimiter=';', error_bad_lines=False, encoding='utf-8')
	brand = manufacturer['manufacturerName'].tolist()
	brand.append(' ')
	manufacturer_selected = st.sidebar.selectbox('Choose the manufacturer', brand,58)

	if manufacturer_selected == ' ':
		manufacturer_selected = ' '
	elif manufacturer_selected == 'Acciona':
		manufacturer_selected = 1
	else:
		manufacturer_selected = manufacturer[manufacturer['manufacturerName']==manufacturer_selected].iloc[0,0]

st.sidebar.write('---')
if st.sidebar.checkbox('More information'):
	st.sidebar.write('This project is a webapp able to provide a list of candidate Wind Energy Conversion System (WECS) to the user after he has selected a couple parameters. The user is able to observe and compare freely any turbine of the around 300 WECS database whenever he wants.' 
	'Once the WECS are filtered the following values will be displayed'
	'* Manufacturer name'
	'* Nominal Power'
	'* Type'
	'* Blades Diameter'
	'* Onshore/Offshore'
	'* Website of the manufacturer'
	'* Power and performance (cp) curve')
	' '

'## Results 📊'
# Filterig data
if manufacturer_selected != ' ':
	wecs_selected = wecs[(wecs.brandID==manufacturer_selected) & (wecs.datavp=='v') & (wecs['power'].between(rated_power_min,rated_power_max, inclusive=False)) & (wecs["type"].isin(type_selected)) & (wecs["offshore?"]==of)]
else:
	wecs_selected = wecs[(wecs.datavp=='v') & (wecs['power'].between(rated_power_min,rated_power_max, inclusive=False)) & (wecs["type"].isin(type_selected)) & (wecs["offshore?"]==of)]

	# Calculating the perfomrance coefficient
P = 1500000      				# Power in Watts [w]
rho = 1.225   					# Air density [kg/km3]
v = 10        					# Wind velocity [m/s]
D = 90        					# Blades diameter [m]
Ba = (3.14/4) * (90)*(90) 			# Blades cross-section-area [m2]

cp = (2*P)/(rho * Ba * v*v*v) 			# Performance Factor [W s3/kg m2]


# - Displaying the data
if (wecs_selected.shape[0]) == 0:
	st.error('There are no WECS that match your criteria')
	st.write('Modify the parameters that you have selected.')
else:
	st.success(str(wecs_selected.shape[0]) + ' WECS meet your criteria.')
	st.write('These are the WECS that match your parameters: ')
	wecs_selected.loc[:,['wecsID','name','power','bladediameter','type']]
	

''

# - Plotting the data
'### Plotting the results'
wecsSeries = pd.DataFrame()
legend = []
if wecs_selected.shape[0] > 10:
	st.info('Check once you have narrowed down the search to a handful of WECS.')
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



	'#### Individual WECS Power Curve'
	# 1. Select the WECS that is going to be plotted
	wecs_plotted = st.selectbox('Choose the WECS to plot',wecs_selected['name'].tolist())
	# Find the wecsID of the selected WECS
	w = wecs_selected[wecs_selected['name']==wecs_plotted].iloc[0,1]
	# Find it in the dataframe
	w = w*2 - 2

	# Store the wind and power data of the wecs in two variables
	wecsV=wecs.iloc[w,9:(9+90)]
	wecsP=wecs.iloc[(w+1),9:(9+90)]

	# Calculate Cp curve of the WECS
	v = wecsV
	P = wecsP * 1000 
	cp = (2*P)/(rho * Ba * v*v*v)

	# Plotting the power curve of the wecs
	fig, ax1 = plt.subplots()

	color1 = 'tab:blue'
	ax1.set_xlabel('Wind velocity (m/s)')
	ax1.set_ylabel('Power Output (kW)') #color = color1)
	ax1.plot(v, wecsP, color = color1)
	
	ax2 = ax1.twinx() # initiate a second axes that shares the same x-axis

	color2 = 'tab:red'
	ax2.set_ylabel('Performance Factor (Cp)', color = color2)
	ax2.plot(v, cp, color = color2)
	ax2.tick_params(axis='y',labelcolor=color2)
	ax2.set_ylim([0,1])

	ax1.grid()
	ax1.set(title=wecs.iloc[w,3])
	fig.tight_layout()
	plt.show()
	st.pyplot(fig=fig)
	
	# Giving additional information of the WECS
	if st.checkbox('Show more details'):
		st.write('Database references:')
		st.table(wecs.iloc[w,1:9])

	wecsSeries = pd.concat([wecsV,wecsP], axis = 1)
	'---'

	# 2. Allow the user to see the plot of all the WECS that meet the user criteria.
	'#### Power curve of all the WECS found'
	''
	if st.checkbox('Display all the power curves individually'):
		for i in range(wecs_selected.shape[0]):
			st.write(str(i+1),'/',str(wecs_selected.shape[0]),'   -   ',wecs_selected.iloc[i,3])
			#wecs_selected.iloc[i,1],wecs_selected.iloc[i,3], wecs_selected.iloc[i,4], 'kW'
			w = wecs_selected.iloc[i,1]
			w = w*2 - 2
			
			# Store the wind and power data of the wecs in two variables
			wecsV=wecs.iloc[w,9:(9+90)]
			wecsP=wecs.iloc[(w+1),9:(9+90)]
			wecsSeries = pd.concat([wecsSeries,wecsV,wecsP], axis = 1)
			

			# Calculate Cp curve of the WECS
			v = wecsV
			P = wecsP * 1000 
			cp = (2*P)/(rho * Ba * v*v*v)

			# Plotting the power curve of the wecs
			fig, ax1 = plt.subplots()

			color1 = 'tab:blue'
			ax1.set_xlabel('Wind velocity (m/s)')
			ax1.set_ylabel('Power Output (kW)') #color = color1)
			ax1.plot(v, wecsP, color = color1)

			ax2 = ax1.twinx() # initiate a second axes that shares the same x-axis

			color2 = 'tab:red'
			ax2.set_ylabel('Performance Factor (Cp)', color = color2)
			ax2.plot(v, cp, color = color2)
			ax2.tick_params(axis='y',labelcolor=color2)
			ax2.set_ylim([0,1])

			ax1.grid()
			ax1.set(title=wecs.iloc[w,3])
			fig.tight_layout()
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
if st.checkbox('Show complete WECS list unfiltered'):
	st.dataframe(wecs[(wecs.datavp=='v')].iloc[:,1:9])
''
''
'⬇️ Or download the full database:'
if st.button('Download data'):
	def get_binary_file_downloader_html(bin_file, file_label='File'):
		with open(bin_file, 'rb') as f:
			data = f.read()
			bin_str = base64.b64encode(data).decode()
			href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{os.path.basename(bin_file)}">Download {file_label}</a>'
		return href
	st.markdown(get_binary_file_downloader_html('300_wecsdata.xlsx', 'Excel'), unsafe_allow_html=True)
else:
    st.write('')


st.write('---')
