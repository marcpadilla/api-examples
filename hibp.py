'''Have I Been Pwned API example by Marc Padilla (marc@padil.la)'''

import json
import pandas as pd
import requests

def check_response_codes(df):
    '''Takes a list of accounts and returns a pandas DataFrame containing HIBP response data.

        Parameters:
            df (pandas DataFrame): A pandas DataFrame created in main().

        Returns:
            None
    '''
    response_codes = {
        200: 'Ok -- everything worked and there\'s a string array of pwned sites for the account.',
        400: 'Bad Request -- The account does not comply with an acceptable format (i.e. it\'s an empty string)',
        401: 'Unauthorized -- Access denied due to invalid hibp-api-key.',
        403: 'Forbidden -- No user agent has been specified in the request.',
        404: 'Not found -- The account could not be found and has therefore not been pwned',
        429: 'Too Many Requests -- The rate limit has been exceeded.',
        503: 'Service unavailable -- Usually returned by Cloudflare if the underlying service is not available.'
    }
    bad_codes = {400, 401, 403, 429, 503}
    errors = list(set(df['Response'].apply(lambda x: x.status_code)).intersection(bad_codes))
    if len(errors) > 0:
        print('Bad response code(s) returned by HIBP API:')
        for i in range(len(errors)): # Be specific and print each bad response to screen.
            print('\t' + str(errors[i]) + ': ' + response_codes[errors[i]])
        print('\tMore information about HIBP response codes at https://haveibeenpwned.com/API/v3#ResponseCodes')
        raise ValueError('An error code was recieved by the HIBP API and printed to screen prior to this message.')
    df = df[df['Response'].apply(lambda x: x.status_code) == 200]
    return None

#====
def main(accounts):
    '''Takes a list of accounts and returns a pandas DataFrame containing HIBP response data.

        Parameters:
            accounts (list): A list of email addresses.

        Returns:
            None if no positive response AND no error recieved.
            result (pandas DataFrame) of pwned account data.
    '''
    with open('config.json') as f:
        api_config = json.load(f)
    f.close()
    api_key = api_config['hibp']['apikey']
    result = pd.DataFrame(data=accounts, columns=['Account'])
    result['Response'] = result['Account'].apply(lambda x: requests.get('https://haveibeenpwned.com/api/v3/breachedaccount/' + 
        x + '?truncateResponse=false', headers={'hibp-api-key': api_key, 'user-agent': 'None'}))
    check_response_codes(result)
    result['Result'] = result['Response'].apply(lambda x: pd.read_json(x.content))
    for row in result.index:
        result.loc[row, 'Result']['Account'] = result.loc[row, 'Account']
    result = pd.concat(list(result['Result'])).reset_index(drop=True)
    return result

if __name__ == '__main__':
    main()