import pandas

class virtual_network_table_std:
    def split_id(df):
        subscriptions = []
        resource_groups = []
        for row in df['id']:
            splited = row.split('/')
            subscriptions.append(splited[2].lower())
            resource_groups.append(splited[4].lower())

        df['subscription_id'] = subscriptions
        df['resource_group_id'] = resource_groups        
        return df

    def expand_properties(df):
        properties = pandas.json_normalize(df['properties'].values)
        df = df.drop('properties', axis=1)
        df = pandas.concat([df, properties], axis=1)
        return df

    def rename_properties(subdf):
        subdf.columns = subdf.columns.str.replace('properties.', '')
        return subdf

    def extract_subnets(df):
        subnets_arr = []
        for val in df['subnets'].values:
            subnets_arr += val

        subdf = pandas.json_normalize(subnets_arr)
        subdf = virtual_network_table_std.rename_properties(subdf)
        df.loc[:,'subnets'] = df.subnets.apply(lambda x: [i['id'] for i in x])
        return df, subdf[subdf.columns[0:9]]

    def extract_peers(df):
        df.loc[:, 'virtualNetworkPeerings'] = \
            df['virtualNetworkPeerings'].apply(lambda x: [i['id'] for i in x])
        return df

    def stringify(df, subdf):
        # stringifying df
        array_columns = [
            'subnets', 
            'virtualNetworkPeerings',
            'addressSpace.addressPrefixes',
            'dhcpOptions.dnsServers'
        ]
        for column in array_columns:
            df[column] = df[column].apply(
                lambda x: ';'.join(x) if type(x) == list else x)

        df.loc[:,'tags'] = df['tags'].apply(lambda x: str(x))

        # stringifying subdf
        subdf['ipConfigurations'] = subdf['ipConfigurations'].apply(
            lambda x: ';'.join([i['id'] for i in x]) if type(x) == list else x)

        subdf['serviceEndpoints'] = subdf['serviceEndpoints'].apply(
            lambda x: ';'.join([i['service'] for i in x]) if \
                type(x) == list else x)
        return df, subdf

    def rm_columns(df, subdf):
        df.pop('id')
        df.pop('etag')
        df.pop('type')
        df.pop('resourceGuid') 
        subdf.pop('id')
        subdf.pop('etag')
        subdf.pop('type')
        return df, subdf

    def format(data):
        df = pandas.json_normalize(data, max_level=0)
        df = virtual_network_table_std.split_id(df)
        df = virtual_network_table_std.expand_properties(df)
        df = virtual_network_table_std.extract_peers(df)
        df, subdf = virtual_network_table_std.extract_subnets(df)
        df, subdf = virtual_network_table_std.stringify(df, subdf)
        df['scan_date'] = pandas.Timestamp.today().strftime("%m-%d-%Y")
        df, subdf = virtual_network_table_std.rm_columns(df, subdf)
        df = df.fillna('')
        subdf = subdf.fillna('')
        return df, subdf

