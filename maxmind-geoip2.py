# MaxMind GeoIP2 web service API example by Marc Padilla (marc@padil.la)

import geoip2.webservice
import ipaddress
import json
import pandas as pd

def add_features(df):
    # Takes specific data from the MaxMind GeoIP2 response and makes them features.
    features = { \
    'Country': df['GeoIp2'].apply(lambda x: x.registered_country.name), \
    'Subdivision': df['GeoIp2'].apply(lambda x: x.subdivisions.most_specific.name), \
    'Isp': df['GeoIp2'].apply(lambda x: x.traits.isp), \
    'Anonymous': df['GeoIp2'].apply(lambda x: x.traits.is_anonymous), \
    'AnonymousVpn': df['GeoIp2'].apply(lambda x: x.traits.is_anonymous_vpn), \
    'HostingProvider': df['GeoIp2'].apply(lambda x: x.traits.is_hosting_provider), \
    'TorExitNode': df['GeoIp2'].apply(lambda x: x.traits.is_tor_exit_node)
    }
    count = 1
    for key in features:
        df.insert(loc = count, column = key, value = features[key])
        count += 1
    return None

#====
def main(ips):
    '''
    Takes a list of ip addresses and returns a pandas Series containing MaxMind lookup data.

    Parameters:
        ips = list of valid IP addresses

    Returns:
        None if no ips can be queried.
        result = pandas DataFrame
    '''
    # remove private ips
    ips = [ip for ip in ips if ipaddress.ip_address(ip).is_global]
    if len(ips) == 0:
        return None
    # maxmind api key from api_config.json file
    with open('config.json') as f:
        api_config = json.load(f)
    f.close()
    # geoip2 client
    userid = api_config['userid']
    apikey = api_config['apikey']
    client = geoip2.webservice.Client(userid, apikey)
    # create dataframe and create a feature of maxmind responses
    result = pd.DataFrame(data=ips, index=None, columns=['IpAddress'])
    result['GeoIp2'] = result['IpAddress'].apply(lambda x: client.insights(x))
    # make selected maxmind response attributes features in the dataframe
    add_features(result)
    return result

if __name__ == '__main__':
    main()