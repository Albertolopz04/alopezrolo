
import streamlit as st
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt

from collections import Counter


# - Heading

st.title('🔎 WECS Comparator v.2')
st.write("""
In this website you can *explore* the **wind turbine** that best suits your needs
"""	)

'This project is a program able to provide a list of candidate wind turbines (WECS) to the user once he has decided what he is looking for. The user is able to observe and compare freely any turbine of the library whenever he wants. The software is mainly an array with different types of inputs which are filtered depending on the user choice. The wanted values from this array are extracted with pointers and located with for and if. Once the WECS are filtered the following values will be displayed'
'* Manufacturer name'
'* Nominal Power'
'* Type'
'* Blades Diameter'
'* Onshore/Offshore'
'* Power and performance (cp) curve'
' '



# - Selecting the parameters
st.write("""	### Select the rated power	""")
rated_power_selected = st.slider('Rated Power (kW)', 0, 10000,2500,500 )
'You selected a ', rated_power_selected/1000, 'MW WECS'

# Definir intervalo del rated power
interval = 501
rated_power_min = rated_power_selected - interval
rated_power_max = rated_power_selected + interval
'The app will show you WECS between ', rated_power_min + 1, ' and ', rated_power_max - 1, 'kW'

st.write("""	### Select the type of generator	""")
type_selected=st.multiselect('Type', ['1','2','3','4'],['1','2','3','4'])

st.write("""	### Select whether the WECS is designed for Offshore/Onshore	""")
offshore_selected = st.selectbox('Onshore/Offshore',
	['Onshore', 'Offshore'])

#offshore_selected=st.multiselect('Offshore?', ['Onshore','Offshore'],['Onshore'])

of = offshore_selected
if of == 'Offshore':
	of = 1
elif of == 'Onshore':
	of = 0
''
''

'### Results 📊'

# - Loading the data
df = pd.read_csv('99_wecs_data.csv', delimiter=';', error_bad_lines=False, encoding='latin-1')
# Filterig data
df_selected_wecs = df[(df['RatedPower'].between(rated_power_min,rated_power_max, inclusive=False)) & (df["Type"].isin(type_selected)) & (df["Offshore?"]==of)]
#df_selected_wecs = df[(df.Type.isin(type_selected)) & (df.RatedPower == rated_power_selected) & (df["Offshore?"]==of)]

# - Displaying the data
st.write('These are the WECS that match your parameters: ' + str(df_selected_wecs.shape[0]) + ' WECS.' )
df_selected_wecs.loc[:,['Names','RatedPower','Rotor Diameter','Type']]

# - Data unfiltered (hidden in a button)
''
'📍 You can also check the full database here:'
if st.checkbox('Show  unfiltered WECS list'):
	df


st.write('---')

# - Plotting the data
'### Plotting the results'
grades = [83,95,91,87,70,0,85,82,100,67,73,77,0]
decile = lambda grade: grade // 10 * 10
histogram = Counter(decile(grade) for grade in grades)
plt.bar([x - 4 for x in histogram.keys()], # shift each bar to the left by 4
histogram.values(), # give each bar its correct height
8) # give each bar a width of 8
plt.axis([-5, 105, 0, 5]) # x-axis from -5 to 105,
# y-axis from 0 to 5
plt.xticks([10 * i for i in range(11)]) # x-axis labels at 0, 10, ..., 100
plt.xlabel("Decile")
plt.ylabel("# of Students")
plt.title("Distribution of Exam 1 Grades")
st.area_chart(grades)
plt.show() 
