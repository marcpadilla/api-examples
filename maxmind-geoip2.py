'''MaxMind GeoIP2 web service API example by Marc Padilla (marc@padil.la)'''

import geoip2.webservice
import ipaddress
import json
import pandas as pd

def add_features(df):
    '''Takes specific data from the MaxMind GeoIP2 response and makes them features.

        Parameters:
            df (pandas DataFrame): A pandas DataFrame created in main().

        Returns: None
    '''
    features = { \
    'Country': df['GeoIp2'].apply(lambda x: x.registered_country.name), \
    'Subdivision': df['GeoIp2'].apply(lambda x: x.subdivisions.most_specific.name), \
    'Isp': df['GeoIp2'].apply(lambda x: x.traits.isp), \
    'Anonymous': df['GeoIp2'].apply(lambda x: x.traits.is_anonymous), \
    'AnonymousVpn': df['GeoIp2'].apply(lambda x: x.traits.is_anonymous_vpn), \
    'HostingProvider': df['GeoIp2'].apply(lambda x: x.traits.is_hosting_provider), \
    'TorExitNode': df['GeoIp2'].apply(lambda x: x.traits.is_tor_exit_node) \
    }
    count = 1
    for key in features:
        df.insert(loc=count, column=key, value=features[key])
        count += 1
    return None

#====
def main(ips):
    '''Takes a list of valid IP addresses and returns a pandas Series containing MaxMind lookup data.

        Parameters:
            ips (list): A list of valid IP addresses.

        Returns:
            None if no valid global IP addressess are in ips.
            result (pandas DataFrame)
    '''
    ips = [ip for ip in ips if ipaddress.ip_address(ip).is_global] # Remove private IPs from list.
    if len(ips) == 0:
        return None
    with open('config.json') as f:
        api_config = json.load(f)
    f.close()
    userid = api_config['userid']
    apikey = api_config['apikey']
    client = geoip2.webservice.Client(userid, apikey)
    result = pd.DataFrame(data=ips, index=None, columns=['IpAddress'])
    result['GeoIp2'] = result['IpAddress'].apply(lambda x: client.insights(x))
    add_features(result) # Make selected MaxMind response attributes features.
    #result.to_csv('maxmind-geoip2-output.csv', index=False) # Save output to CSV.
    return result

if __name__ == '__main__':
    main()