#model to look at intra-day variation within a mini-grid system

#====================

#====================

"""Plan:

1. Isolation data: Call from renwables ninja, select the first 24 entries under the irradation category. 
2. Demand data: Have a demand profile inserted at this stage as raw power data at each hour. 
3. Create the generation profile from inserted data, that matches power and gives excess amount of power. 
4. The battery is able to store and monitor and give energy. 

"""
import requests
import pandas as pd

def insolation_request(year,month,day):


	token = '2e610f4b1bd4ad25dc59afcdc1580ffd8d781fce'
	api_base = 'https://www.renewables.ninja/api/'

	s = requests.session()
	s.headers = {'Authorization': 'Token ' + token}
	url = api_base + 'data/pv'

	args = {
	    'lat': 34.125,
	    'lon': 39.814,
	    'date_from': str(year)+'-'+str(month)+'-'+str(day),
	    'date_to': str(year)+'-'+str(month)+'-'+str(day+1),
	    'dataset': 'merra2',
	    'capacity': 1.0,
	    'system_loss': 10,
	    'tracking': 0,
	    'tilt': 35,
	    'azim': 180,
	    'format': 'csv',
	    'metadata': False,
	    'raw': True
	}

	r = s.get(url, params=args)

	print(r)

	#Parse csv to get a pandas.DataFrame
	df = pd.read_csv(r.text, orient='index')

#print(df)

#====================

insolation_request(2014,01,01)
