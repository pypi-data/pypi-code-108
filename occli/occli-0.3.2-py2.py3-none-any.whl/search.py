import requests
from occli import colors,output

# Searching for compan(ies)(y) on OpenCorporates
def search(args,api):
	api = api+f"companies/search?q={args.search}*"	    
	interval = 0
	response = requests.get(api).json()
	for number in range(interval, int(response['results']['per_page'])+1):
		interval += 1
		data = {"Company No#": response['results']['companies'][number]['company']['company_number'],
		             "Jurisdiction code": response['results']['companies'][number]['company']['jurisdiction_code'],
		             "Incorporation date": response['results']['companies'][number]['company']['incorporation_date'],
		             "Dissolution date": response['results']['companies'][number]['company']['dissolution_date'],
		             "Company type": response['results']['companies'][number]['company']['company_type'],
		             "Registry URI": response['results']['companies'][number]['company']['registry_url'],
		             "Branch": response['results']['companies'][number]['company']['branch'],
		             "Branch status": response['results']['companies'][number]['company']['branch_status'],
		             "Is inactive?": response['results']['companies'][number]['company']['inactive'],
		             "Current status": response['results']['companies'][number]['company']['current_status'],
		             "Created at": response['results']['companies'][number]['company']['created_at'],
		             "Updated at": response['results']['companies'][number]['company']['updated_at'],
		             "Previous name(s)": response['results']['companies'][number]['company']['previous_names'],
		             "Registered address": response['results']['companies'][number]['company']['registered_address'],
		             "Address in full": response['results']['companies'][number]['company']['registered_address_in_full'],
		             "Industry code(s)": response['results']['companies'][number]['company']['industry_codes'],
		             "Restricted for marketing": response['results']['companies'][number]['company']['restricted_for_marketing'],
		             "Native company No#": response['results']['companies'][number]['company']['native_company_number'],
		             "OpenCorporates URI": response['results']['companies'][number]['company']['opencorporates_url']
		}
		print(f"\n\n{colors.white}{response['results']['companies'][number]['company']['name']}{colors.reset}")
		for key, value in data.items():
		    print(f"{colors.white} ├─ {key}: {colors.green}{value}{colors.reset}")
		
		if args.output:
		   print(output.write(args,data,number,response))
				    	
		if number == int(response['results']['per_page'])-1:
			break