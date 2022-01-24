import pandas
from datetime import datetime

class virtual_machine_table_comprehensive:
    def replace_ip_id_with_ip_val(id_list, pipdf):
        ip_vals = []
        for i in id_list:
            row = pipdf.loc[pipdf['public_ip_id']==i]
            if not row.empty:
                ip_val = row['public_ip_address'].values[0]
            else:
                ip_val = 'public_ip_id not found'
            ip_vals.append(ip_val)
        return ip_vals

    def vm_network_table(data):
        # Creates an auxiliary table by joining public and private
        # IPs, using network card ID as primary key.
        # Useful for retrieving IP data for each VM through their
        # network cards.
        private_vnw = [
            {
                'networkCard_id': id,
                'private_ip': data['network']['private'][id]
            } for id in data['network']['private'].keys()
        ]
        private_vnw_df = pandas.json_normalize(private_vnw)
        public_nw = [
            {
                'networkCard_id': id,
                'public_ip_ids': data['network']['public'][id]
            } for id in data['network']['public'].keys()
        ]

        for item in public_nw:
            item['public_ip_ids'] = [
                ip_resource['id'] for ip_resource in item['public_ip_ids']
            ]

        public_nw_df = pandas.json_normalize(public_nw)
        public_ip_addr = [
            {
                'public_ip_id': id,
                'public_ip_address': data['public_ip_address'][id]
            } for id in data['public_ip_address'].keys()
        ]
        public_ip_df = pandas.json_normalize(public_ip_addr)
        ids = public_nw_df['public_ip_ids']
        ips = ids.apply(virtual_machine_table_comprehensive\
            .replace_ip_id_with_ip_val, args=(public_ip_df,))
        ips = ips.rename('public_ips')
        public_nw_df = pandas.concat([public_nw_df, ips], axis=1)
        vm_network_df = pandas.merge(private_vnw_df, public_nw_df, 
                                 how='outer',
                                 on='networkCard_id')
        return vm_network_df


    def instance_type_info(name, it_df):
        name = name.upper()
        return it_df[it_df['name']\
                .apply(lambda x: x.upper()) == name.upper()]

    def query_addresses(net_cards, nwdf, public=False):
        addresses = []
        if public:
            for net_card in net_cards:
                ips = nwdf[nwdf['networkCard_id'] == net_card['id']]\
                    ['public_ips'].values[0]
                if type(ips) == list:
                    addresses += ips
        else:    
            for net_card in net_cards:
                ips = nwdf[nwdf['networkCard_id'] == net_card['id']]\
                    ['private_ip'].values[0]
                addresses += ips
        return ';'.join(addresses)

    def create_table(data):
        # ----- auxiliary data
        vm_network_df = virtual_machine_table_comprehensive.vm_network_table(data)
        instance_type_df = pandas.json_normalize(data['instance_type'])
        vms = pandas.json_normalize(data['virtual_machine'])
        date = datetime.today().strftime('%Y-%m-%d')

        tags = vms['id'].apply(
                lambda x: 
                    data['resource_group'][x.split('/')[4].upper()])

        subscription_id_name = vms['id'].apply(
                lambda x: 
                    data['subscription'].get(x.split('/')[2]))

        project_id = tags.apply(
                lambda x: 
                    x['ProjectName'] if 'ProjectName' in x.keys()
                    else '')

        it_df = pandas.json_normalize(data['instance_type'])
        it_info = vms['properties.hardwareProfile.vmSize']\
                .apply(virtual_machine_table_comprehensive.instance_type_info,
                       args=(it_df,))
        it_info = pandas.concat(it_info.values, axis=0)
        # -----

        # Data to be saved in tables. Each key in the DataFrame roughly
        # corresponds to a column in the database.
        vmTable = pandas.DataFrame({ 
            'vm_msid': vms['properties.vmId'],

            'networkcard_count': vms['properties.networkProfile'\
                '.networkInterfaces'].apply(lambda x: len(x)),

            'private_ip_address': vms['properties.networkProfile.networkInterfaces']\
                .apply(virtual_machine_table_comprehensive.query_addresses, args=(vm_network_df, False,)),

            'public_ip_address': vms['properties.networkProfile.networkInterfaces']\
                .apply(virtual_machine_table_comprehensive.query_addresses, args=(vm_network_df, True,)),

            'computer_name': vms['name'],

            'resource_name': vms['properties.osProfile.computerName'],
            
            'operating_system_id': vms['properties.storageProfile'\
                '.osDisk.osType'],

            'subscription_id.name': subscription_id_name,

            'subscription_id.subscription_msid': vms['id']\
                .apply(lambda x: x.split('/')[2]),

            'image_id.name': vms['properties.storageProfile'\
                '.imageReference.offer'],

            'image_id.publisher': vms['properties.storageProfile'\
                '.imageReference.publisher'],

            'image_id.sku': vms['properties.storageProfile'\
                '.imageReference.sku'],

            'image_id.version': vms['properties.storageProfile'\
                '.imageReference.version'],

            'image_id.exact_version': vms['properties.storageProfile'\
                '.imageReference.exactVersion'],

            'zone_id': ['SAZ' for i in range(len(vms))],

            'region_id': vms['location'],

            'host_id': ['Azure' for i in range(len(vms))],

            'resource_group_id': vms['id'].apply(lambda x: x.split('/')[4]),

            'device_type_id': ['Virtual Machine' for i in range(len(vms))],

            'tags': tags,

            'project_id': project_id,

            'environment_id': [
                'Prod' if subscription_id_name[i] == 'ABI BR Prod'
                else 'Non-Prod' if subscription_id_name[i] == 'ABI BR Non-Prod'
                else f'{subscription_id_name[i]} - {project_id[i]}'
                for i in range(len(vms))
            ],

            'azure_status_id': [
                item['properties']['instanceView']\
                    ['statuses'][1]['displayStatus']
                    for item in data['status']
            ],

            'instance_type_id.name': it_info['name'].values,

            'instance_type_id.core_count':  it_info['numberOfCores'].values,

            'instance_type_id.os_disk_size_mb': \
                it_info['osDiskSizeInMB'].values,

            'instance_type_id.resource_disk_size_mb': \
                it_info['resourceDiskSizeInMB'].values,

            'instance_type_id.memory_mb': \
                it_info['memoryInMB'].values,

            'instance_type_id.max_data_disk_count': \
                it_info['maxDataDiskCount'].values,

            'scan_date': [date for i in range(len(vms))]
        }).fillna('')
        return vmTable

    def filter_vms(data):
        new_data = []
        for item in data:
            resource_group = item["id"].split("/")[4].lower()
            computer_name = item["name"].lower()
            conditions = [
                "databricks-rg" in resource_group 
                or "mc_aks-" in resource_group,
                "aks_nodepool" in computer_name 
                or "rtr-" in computer_name,
            ]
            condition = True in conditions
            if not condition:
                new_data.append(item)
        return new_data

    def format(data):
        data['virtual_machine'] = virtual_machine_table_comprehensive\
            .filter_vms(data['virtual_machine'])
        data['status'] = virtual_machine_table_comprehensive\
            .filter_vms(data['status'])
        return virtual_machine_table_comprehensive.create_table(data)
