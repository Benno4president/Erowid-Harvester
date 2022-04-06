import json, re, time, csv, os
import requests
from bs4 import BeautifulSoup


EROWID_BASE_URL = 'https://www.erowid.org/experiences/'
EXP_BASE_URL = 'http://www.erowid.org/experiences/exp.php?ID=%s'
REPORT_QUERY_LIST_URL = EROWID_BASE_URL + 'exp.cgi?S=%d&C=%d&Start=%d&Max=%d' 
config = {
        'start_at': 1,
        'stop_at': 300,
        'use_filter': False, # all stories will be saved if false, because the word list is then ignored.
        'word_filter': set([ # don't use spaces, they have no effect.
            'mushroom', 
            'mushrooms', 
            'shroom', 
            'shrooms', 
            '$hroom', 
            '$hrooms', 
            '\'rooms',
            'psilocybin',
            'psilocyn',
            'boomers',
            'mushies',
            'caps'
            ]),
        # as of now the ids will only scrape the 'general' exp tab.
        'ids': [],
        # Urls placed here are scraped with no reguard for start and stop limits,
        # they should be set in the url query.
        'urls': ['https://www.erowid.org/experiences/exp.cgi?S1=193&Max=100',
                 'https://www.erowid.org/experiences/exp.cgi?S1=90&Max=100'
                 ]
    }

# Helper functions 
def get_soup(url):
    html_doc = requests.get(url).content
    return BeautifulSoup(html_doc, 'html.parser')

def removeHTML(s):
    htmlRegexes = ['</?.{1,30}?>']
    for htmlRegex in htmlRegexes:
        s = re.sub(htmlRegex, '', s)
    return s

def save_csv(fp, data_ldict):
    csv_columns = data_ldict[0].keys()
    with open(fp, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()
        for data in data_ldict:
            writer.writerow(data)

# a messy erowid html table scraper, which enters the experiences
# and collects the data. Returns a list of jsonlines.
def scrape_exp_table(input_key=66):
    if type(input_key) == str:
        exp_table_soup = input_key
    else:
        exp_table_soup = REPORT_QUERY_LIST_URL % (input_key, 1, config['start_at'], config['stop_at'])
    
    exp_table_soup = get_soup(exp_table_soup)
    head_title = exp_table_soup.find('title').string
    entries = exp_table_soup.find_all('a', href=True)
    eid_list = []
    for entry in entries:
        eid = entry.get('href').split('ID=')
        if len(eid) > 1:
            eid_list.append(eid[1])
    print('Found ids:', len(eid_list))

    story_list = []
    for expid in eid_list:
        print('Fetching id: %s' % expid)
        page = str(requests.get(EXP_BASE_URL % expid).content)

        # sleeping to not get ip banned for spam
        time.sleep(0.5)
        if 'Unable to view experience' in page:
            print('No report at that ID number.')
            continue
        intrsec = set(page.lower().split()).intersection(config['word_filter'])  
        if not config['use_filter']:
            pass
        elif not intrsec: 
            # this checks if a word from the list is in the page anywhere.
            print('No search keyword found.')
            continue 
        else:
            print('Matched on:', intrsec) 

        
        title = page.split('class="title">')[1].split('</div>')[0].replace('\n', '')
        substance = page.split('class="substance">')[1].split('</div>')[0].replace('\n', '')
        author = page.split('class="author">')[1].split('</a>')[0].split('>')[1].replace('\n', '')
        
        print('Title: %s'%title)
        print('Substance: %s'%substance)
        print('Author: %s'%author)

        # get main text and remove common unicode characters
        body = page.split('Start Body -->')[1].split('<!-- End Body')[0]
        body = body.replace('\r','')
        body = body.replace('\n','')
        body = body.replace('\x92',"'")
        body = body.replace('\x93','"')
        body = body.replace('\x94','"')
        body = body.replace('\x97',' -- ')
        body = removeHTML(body)
        body = body.strip()

        story_list.append({'id':expid, 'title':title, 'author':author, 'substance':substance, 'story': body})
    return head_title, story_list

# a main function which creates a folder,
# loops through ids and urls set the the config,
# and generates a .csv file for each, name based on title.
if __name__ == '__main__':
    filename = './table_csvs/%s.csv'
    if not os.path.exists('./table_csvs/'):
        os.mkdir('./table_csvs/')
        print('created dir ./table_csvs')
    for num, table_urltag in enumerate(config['ids'] + config['urls']):
        title, data = scrape_exp_table(table_urltag)
        title = title.replace(' ', '_').replace('.', '').split(':')[0]+str(num)
        save_csv(filename%title, data)
        print('table saved to', filename%title)
    
