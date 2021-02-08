import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import base64, os
import altair

# - Setting web configuration
st.set_page_config(
    page_title="Wecs Easy Choice v.2",
    page_icon=':cyclone:',    
    initial_sidebar_state="expanded",)

# - Heading
st.title('🔎 WECS Easy Choice v.2')
st.write('In this webapp you can *find* the **wind turbine** that best suits your needs.')

# - Define a download formula
def download_link(object_to_download, download_filename, download_link_text):
	    """
	    Generates a link to download the given object_to_download.
	    """
	    if isinstance(object_to_download,pd.DataFrame):
	        object_to_download = object_to_download.to_csv(index=False)

	    # some strings <-> bytes conversions necessary here
	    b64 = base64.b64encode(object_to_download.encode()).decode()

	    return f'<a href="data:file/txt;base64,{b64}" download="{download_filename}"><input type="button" value="Download data sheet"></a>'

# - Loading the data
st.cache()
wecs = pd.read_csv('300_wecsdata.csv', delimiter=';',  error_bad_lines=False, encoding='latin-1')


# - Selecting the parameters
st.sidebar.write("""	## Filter Parameters	""")

# 1.Definir intervalo del rated power
st.sidebar.write("""	### Select the rated power	""")
rated_power_selected = st.sidebar.slider('Rated Power (kW)', 0, 10000, (500,5000), 500 )
rated_power_min = rated_power_selected[0]
rated_power_max = rated_power_selected[1]
st.sidebar.write('The app will show you WECS between ', rated_power_min, ' and ', rated_power_max, 'kW')

# 2.Seleccionar el tipo
st.sidebar.write("""	### Select the type of wind turbine	""")
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

# 5. Información sobre el proyecto 		
st.sidebar.write('---')
with st.beta_expander('More information'):
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
	

'## Results 📊'
# Filterig data
if manufacturer_selected != ' ':
	wecs_selected = wecs[(wecs.brandID==manufacturer_selected)  & (wecs['power'].between(rated_power_min,rated_power_max)) & (wecs["type"].isin(type_selected)) & (wecs["offshore?"]==of)]
else:
	wecs_selected = wecs[(wecs.datavp=='v') & (wecs['power'].between(rated_power_min,rated_power_max, inclusive=False)) & (wecs["type"].isin(type_selected)) & (wecs["offshore?"]==of)]

matching_wecs = int(wecs_selected.shape[0]/2)
wecs_selected_list = wecs_selected[(wecs_selected['datavp']=='v')]
# - Displaying the data
if (wecs_selected.shape[0]) == 0:
	st.error('There are no WECS that match your criteria')
	st.write('Modify the parameters that you have selected.')
else:
	matching_wecs = int(wecs_selected.shape[0]/2)
	st.success(str(matching_wecs) + ' WECS meet your criteria.')
	st.write('These are the WECS that match your parameters: ')
	wecs_selected[(wecs.datavp=='v')].loc[:,['wecsID','name','power','bladediameter','type']]
	wecs_selected_indexes=list(wecs_selected.iloc[:,1].index)   

'---'	


def get_binary_file_downloader_html(bin_file, file_label='File'):
    with open(bin_file, 'rb') as f:
        data = f.read()
    bin_str = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{os.path.basename(bin_file)}">Download {file_label}</a>'
    return href
	
	

# -- Plotting the data
'### Plotting the results'

if matching_wecs >10:
	st.info('Check once you have narrowed down the search to a handful of WECS.')
else:
	''
wecsSeries = pd.DataFrame()
legend = []	
with st.beta_expander('Show the power curve of the results'):
	'#### Graph of all the WECS that meet the user criteria'
	fig, ax = plt.subplots()
	for i in range(matching_wecs):
		w = wecs_selected.iloc[i,1]
		w = w*2 - 2
		
		# Store the wind and power data of the wecs in two variables
		wecsSeries = pd.concat([wecsSeries,wecs.iloc[w:(w+2),9:(9+90)]])
		a = int(2*i+1)
		b = int(2*i)
		ax.plot(wecsSeries.iloc[b,:],wecsSeries.iloc[a,:])
		legend.append(wecs_selected_list.iloc[i,3])
		
		
	ax.set(xlabel='Wind Speed (m/s)', ylabel='Power Output (KW)', title='WECS Comparator')
	ax.grid()
	plt.legend(legend)
	#plt.legend(wecs_selected.iloc[i,3].tolist())
	plt.show()
	st.pyplot(fig=fig)

	#Botón de descarga de la tabla
	wecs_selected_download = wecs[ (wecs['power'].between(rated_power_min,rated_power_max, inclusive=False)) & (wecs["type"].isin(type_selected)) & (wecs["offshore?"]==of)]
	wecs_selected_download = pd.concat([wecs_selected_download.iloc[:,([0,3,4,5,6])], wecs_selected_download.iloc[:,9:99]],axis = 1)
	tmp_download_link = download_link(wecs_selected_download.T,'WECS Comparator Results'+ '.csv', wecs.iloc[w,3])
	st.markdown(tmp_download_link, unsafe_allow_html=True)


	'#### Individual WECS power curve'
	# 1. Select the WECS that is going to be plotted
	wecs_plotted = st.selectbox('Choose the WECS to plot',wecs_selected_list['name'].tolist())
	lista = wecs_selected_list['name'].tolist()
	lista_indice = lista.index(wecs_plotted)
	# Assign the index of the WECS to find it in the DataFrame
	wi = lista_indice
	w = lista_indice
	w = w*2
	
	# Calculate Cp curve of the WECS
	v = wecsSeries.iloc[w,:]			# Wind Velocity 			[m/s]
	P = wecsSeries.iloc[w+1,:] * 1000	# WECS Power in Watts 		[w] 
	D = wecs_selected.iloc[wi,5]		# Blades diameter 			[m]
	Ba = (np.pi/4) * (D)*(D) 			# Blades cross-section-area [m2]
	rho = 1.225							# Air density 				[kg/km3]
	
	cp = (2*P)/(rho * Ba * (v*v*v))		# Performance Factor 		[W s3/kg m2]

	# Plotting the power curve of the wecs
	fig, ax1 = plt.subplots()
	color1 = 'tab:blue'
	ax1.set_xlabel('Wind velocity (m/s)')
	ax1.set_ylabel('Power Output (kW)') #color = color1)
	ax1.plot(v, wecsSeries.iloc[w+1,:], color = color1)
	
	ax2 = ax1.twinx() # initiate a second axes that shares the same x-axis

	color2 = 'tab:red'
	ax2.set_ylabel('Performance Factor (Cp)', color = color2)
	ax2.plot(v, cp, color = color2)
	ax2.tick_params(axis='y',labelcolor=color2)
	ax2.set_ylim([0,1])

	ax1.grid()
	ax1.set(title=wecs_selected_list.iloc[wi,3])
	fig.tight_layout()
	plt.show()
	st.pyplot(fig=fig)
	

	# Giving additional information of the WECS
	st.write('Database references:')
	st.table(wecs_selected_list.iloc[wi,1:9])
	'---'

	# 2. Allow the user to see the plot of all the WECS that meet the user criteria.
	'#### Compare all the selected WECS data'
	''
	if st.checkbox('Show a list of all the the WECS technical information'):
		for i in range(matching_wecs):
			st.write(str(i+1),'/',str(matching_wecs),'   -   ',wecs_selected_list.iloc[i,3])

			# Giving additional information of the WECS
			st.write('Database references:')
			st.table(wecs_selected_list.iloc[i,1:9])


'---'
'### Additional tools'
with st.beta_expander('Show additional analysis tools'):

	'Range of nominal power of each type in the database:'
	wecs_bien = wecs[(wecs.type==1) |(wecs.type==2) |(wecs.type==3) | (wecs.type==4)]
	wecs_bien['type'] = wecs_bien['type'].apply(str)

	click = altair.selection_multi(encodings=['color'])

	chart = altair.Chart(wecs_bien).mark_point().encode(
	    y = 'type',
	    x = 'power',
	    tooltip = [altair.Tooltip('name'),altair.Tooltip('type')],
	    color = 'type:N'
	    #shape = altair.condition(click, 'type:N', altair.value('set2'), legend = None)
	).properties(selection = click,width=680,height=200).interactive()



	hist = altair.Chart(wecs_bien).mark_point().encode(
	    y = 'type',
	    color = altair.condition(click, 'type:N', altair.value('lightgray'))
	).properties(selection = click, height = 100).interactive()

	chart #| hist

	# Blade Diameter vs Rated Power (categorized by type)
	multi = altair.selection_multi(fields=['type','offshore?'])
	color = altair.condition(multi,altair.Color('type:N'),
			altair.value('lightgray'))

	bladepower = altair.Chart(wecs_bien).mark_point().encode(
	    x = 'power',
	    y = 'bladediameter',
	    shape = altair.condition(multi, 'type:N', altair.value('lightgray')),
	    color = altair.condition(multi, 'type:N', altair.value('lightgray'),legend = None),
	    tooltip = [altair.Tooltip('name'),altair.Tooltip('type'),altair.Tooltip('bladediameter')],
	).properties(selection = multi,width =600,height=300).interactive()

	# Blade Diameter vs Rated Power (categorized by location offshore/onshore)
	bladepowerofs = altair.Chart(wecs_bien).mark_point().encode(
	    x = 'power',
	    y = 'bladediameter',
	    shape = altair.condition(multi, 'type:N', altair.value('lightgray')),
	    color = altair.condition(multi, 'offshore?:N', altair.value('lightgray')),
	    tooltip = [altair.Tooltip('name'),altair.Tooltip('type'),altair.Tooltip('offshore?')]
	).properties(selection = multi,width =600,height=300).interactive()

	st.write('**Blade Diameter vs Rated Power** (categorized by type and by onshore/offshore design)') 
	st.write(""" *Click* on any data point to *filter* by that category on both charts """)
	bladepower & bladepowerofs


st.write('---')

# - Check all the data
'### Check all the data 📥'
   
with st.beta_expander('Show  unfiltered WECS list'):
	wecs[(wecs.datavp=='v')].iloc[:,1:9]

st.write('---')

