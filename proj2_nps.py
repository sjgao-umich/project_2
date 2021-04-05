#################################
##### Name: Shijie Gao
##### Uniqname: sjgao
#################################

from bs4 import BeautifulSoup
import requests
import json
import secrets # file that contains your API key


class NationalSite:
    '''a national site

    Instance Attributes
    -------------------
    category: string
        the category of a national site (e.g. 'National Park', '')
        some sites have blank category.
    
    name: string
        the name of a national site (e.g. 'Isle Royale')

    address: string
        the city and state of a national site (e.g. 'Houghton, MI')

    zipcode: string
        the zip-code of a national site (e.g. '49931', '82190-0168')

    phone: string
        the phone of a national site (e.g. '(616) 319-7906', '307-344-7381')
    '''
    def __init__(self,category,name,address,zipcode,phone):
        self.category = category
        self.name = name
        self.address = address
        self.zipcode = zipcode
        self.phone = phone
    def info(self):
        return f'{self.name} ({self.category}): {self.address} {self.zipcode}'


def build_state_url_dict():
    ''' Make a dictionary that maps state name to state page url from "https://www.nps.gov"

    Parameters
    ----------
    None

    Returns
    -------
    dict
        key is a state name and value is the url
        e.g. {'michigan':'https://www.nps.gov/state/mi/index.htm', ...}
    '''

    html_text = requests.get('https://www.nps.gov/index.htm')
    soup = BeautifulSoup(html_text.text,'html.parser')

    dropdown_states = soup.find_all(class_='dropdown-menu SearchBar-keywordSearch')

    states_name_list = []
    states_url_list = []
    states_dict = {}
    all_states_list = dropdown_states[0].find_all('li')
    for item in all_states_list:
        states_name_list.append(item.text.strip().lower())

    for a in dropdown_states[0].find_all('a', href=True):
        states_url_list.append(a['href'])

    for i in range(len(states_name_list)):
        states_dict[states_name_list[i]] = f'https://www.nps.gov{states_url_list[i]}'

    return states_dict


def get_site_instance(site_url):
    '''Make an instances from a national site URL.
    
    Parameters
    ----------
    site_url: string
        The URL for a national site page in nps.gov
    
    Returns
    -------
    instance
        a national site instance
    '''
    response = requests.get(site_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    category = soup.find_all(class_='Hero-designation')[0].string
    name = soup.find_all(class_='Hero-title')[0].string
    address = soup.find_all(itemprop='addressLocality')[0].string + ', ' + soup.find_all(itemprop='addressRegion')[0].string
    phone = soup.find_all(class_='tel')[0].string.strip()
    zipcode = soup.find_all(itemprop='postalCode')[0].string.strip()

    national_site = NationalSite(category,name,address,zipcode,phone)
    return national_site

FIB_CACHE = {}
def get_sites_for_state(state_url):
    '''Make a list of national site instances from a state URL.
    
    Parameters
    ----------
    state_url: string
        The URL for a state page in nps.gov
    
    Returns
    -------
    list
        a list of national site instances
    '''
    a_list = []
    response = requests.get(state_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    list_parent = soup.find('div',id='parkListResultsArea')
    list_li = list_parent.find_all('li', class_='clearfix')

    for li in list_li:
        state_link_tag = li.find('a')
        state_link_path = state_link_tag['href']
        #print(state_link_path)
        a_list.append(state_link_path)

    instances_list = []
    for item in a_list:
        site_url = f'https://www.nps.gov{item}index.htm'
        instance = get_site_instance(site_url)
        instances_list.append(instance)
    return instances_list


def get_sites_for_state_with_cache(state_url):
    if state_url in FIB_CACHE:
        print('Using Cache')
        return FIB_CACHE[state_url]
    else:
        FIB_CACHE[state_url] = get_sites_for_state(state_url)
        print('Fetching')
        return FIB_CACHE[state_url]


def get_nearby_places(site_object):
    '''Obtain API data from MapQuest API.
    
    Parameters
    ----------
    site_object: object
        an instance of a national site
    
    Returns
    -------
    dict
        a converted API return from MapQuest API
    '''
    base_url = 'http://www.mapquestapi.com/search/v2/radius'
    key = secrets.API_KEY
    origin = site_object.zipcode
    radius = 10
    maxMatches = 10
    ambiguities = 'ignore'
    outFormat = 'json'

    params = {'key':key, 'origin':origin, 'radius':radius, 'maxMatches': maxMatches, 'ambiguities':ambiguities, 'outFormat':outFormat}
    response = requests.get(base_url,params)
    results = response.json()
    return results


if __name__ == "__main__":

#step 1
    states_dict = build_state_url_dict()
    def step_1():
        state_name = input('Enter a state name (e.g. Michigan, michigan) or "exit": ').lower()
        if state_name == 'exit':
            exit()
        else:
            while state_name not in states_dict.keys():
                state_name = input('[Error] Enter proper state name: ').lower()
        return state_name

#step 2
    state_name = step_1()
    def step_2():
        
        print('----------------------------------')
        print(f'List of national sites in {state_name}')
        print('----------------------------------')
        state_url = states_dict[state_name]
        site_list = []
        list_of_site_instances = get_sites_for_state_with_cache(state_url)
        for each_site in list_of_site_instances:
            num = list_of_site_instances.index(each_site)+1
            site_list.append(f'[{num}] {each_site.info()}')
        for item in site_list:
            print(item)
        return site_list

#step 3
    site_list = step_2()
    input_number = input('Choose the number for detail search or "exit" or "back": ')
    option_dict = {}
    for item in site_list:
        option_dict[item.replace('[',']').split(']')[1]] = item[4:]
    if input_number == 'exit':
        exit()
    elif input_number == 'back':
        step_1()
        site_list = step_2()
        input_number = input('Choose the number for detail search or "exit" or "back": ')
        while input_number not in option_dict.keys():
            input_number = input('[Error] Invalid input ')
    else:
        while input_number not in option_dict.keys():
            input_number = input('[Error] Invalid input ')

#step 4 
    state_url = states_dict[state_name]
    list_of_site_instances = get_sites_for_state_with_cache(state_url)
    if input_number.isdigit():
        site_object = list_of_site_instances[int(input_number)-1]
    else:
        pass

    nearby_results = get_nearby_places(site_object)
    nearby_results_list = nearby_results['searchResults']

    nearby_places_output = []
    for item in nearby_results_list:
        name = item['name']
        if item['fields']['group_sic_code_name_ext']:
            category = item['fields']['group_sic_code_name_ext']
        else:
            category = 'no category'
        if item['fields']['address']:
            street_address = item['fields']['address']
        else:
            street_address = 'no address'
        if item['fields']['city']:
            city_name = item['fields']['city']
        else:
            city_name = 'no city'

        output = f'{name} ({category}): {street_address}, {city_name}'
        nearby_places_output.append(output)
    print('----------------------------------')
    print(f'Places near {site_object.name} ')
    print('----------------------------------')
    for output in nearby_places_output:
        print(f'- {output}')


