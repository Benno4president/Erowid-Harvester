import json, re, time, csv, os, traceback, random
from datetime import datetime
import requests
from bs4 import BeautifulSoup


config = {
        # The categories E.g. 'general', 'first times' etc..
        # are located by id. 
        'category_start': 1,
        'category_stop': 3, # 3 is ok, 20+ is thorough, 45+ is endpoint mapping... but fun :))
        # These start+stop is for the span of ids, which will be scraped
        # for each id and subcategory.
        'start_at': 0,
        'stop_at': 5,
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
        # This takes ids of erowid drugs and scrapes categories,
        # and stories based on above settings.
        'ids': [], #[118, 856, 844, 66, 67, 193, 90, 123, 133, 127, 185],
        # Urls placed here are scraped with no reguard for start and stop limits,
        # they should be set in the url query.
        'urls': [
                 # these are now examples of how to use url input.
                 #'https://www.erowid.org/experiences/exp.cgi?S1=193&Max=100',
                 #'https://www.erowid.org/experiences/exp.cgi?S1=90&Max=100'
                 
                 # Below is the 'all results' from mushrooms and lsd.
                 #'https://www.erowid.org/experiences/exp.cgi?S1=39&Max=2400', # Mushrooms
                  #'https://www.erowid.org/experiences/exp.cgi?S1=26&Max=500', # HB woodrose
                 'https://erowid.org/experiences/exp.cgi?S1=2&Max=2'          # LSD
                 ]
    }

# global declarations and setup.
EROWID_BASE_URL = 'https://www.erowid.org/experiences/'
EXP_BASE_URL = 'http://www.erowid.org/experiences/exp.php?ID=%s'
REPORT_QUERY_LIST_URL = EROWID_BASE_URL + 'exp.cgi?S=%d&C=%d&Start=%d&Max=%d' 

# Helper functions 
def get_soup(url):
    html_doc = requests.get(url).content
    return BeautifulSoup(html_doc, 'html.parser')

def removeHTML(s):
    htmlRegexes = ['</?.{1,30}?>']
    for htmlRegex in htmlRegexes:
        s = re.sub(htmlRegex, '', s)
    return s

def mdy_to_ymd(stringdate):
    return datetime.strptime(stringdate, '%b %d, %Y').strftime('%Y-%m-%d')

def save_csv(fp, data_ldict):
    csv_columns = data_ldict[0].keys()
    with open(fp, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()
        for data in data_ldict:
            writer.writerow(data)

# a messy erowid html table scraper, which enters the experiences
# and collects the data. Returns a list of jsonlines.
def scrape_exp_table(table_url:str):
    exp_table_soup = get_soup(table_url)
    head_title = exp_table_soup.find('title').string
    entries = exp_table_soup.find_all('a', href=True)
    eid_list = []
    for entry in entries:
        eid = entry.get('href').split('ID=')
        if len(eid) > 1:
            eid_list.append(eid[1])
    print('Found ids:', len(eid_list))

    if len(eid_list) == 0:
        return 'none', False

    story_list = []
    for expid in eid_list:
        print('Fetching id: %s' % expid, end=', ')
        page = str(requests.get(EXP_BASE_URL % expid).content)

        # sleeping to not get ip banned for spam
        time.sleep(random.randint(1,2)-0.5) # 0.5
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

        try:
            title = page.split('class="title">')[1].split('</div>')[0].replace('\n', '')
            substance = page.split('class="substance">')[1].split('</div>')[0].replace('\n', '')
            author = page.split('class="author">')[1].split('</a>')[0].split('>')[1].replace('\n', '')
            published = page.split('<td>Published: ')[1].split('</td>')[0].replace('\n', '')
            published = mdy_to_ymd(published)
        except:
            print('\n'+'#'*20, '\nFailed on:', EXP_BASE_URL % expid,'\n'+'#'*20)
            continue
        
        print('Title: %s, Substance: %s'%(title,substance))
        
        # get main text and remove common unicode characters
        body = page.split('Start Body -->')[1].split('<!-- End Body')[0]
        body = body.replace('\\r',' ')
        body = body.replace('\\n',' ')
        body = body.replace('\\x92','')
        body = body.replace('\\x93','')
        body = body.replace('\\x94','')
        body = body.replace('\\x96',' ')
        body = body.replace('\\x97',' ')
        body = body.replace('\\xe9',' ')
        body = body.replace('\\xe0',' ')
        body = removeHTML(body)
        body = body.strip()

        story_list.append({'id':expid, 'title':title, 'author':author, 'published':published, 'substance':substance, 'story': body})
    return head_title, story_list

# a main function which creates a folder,
# loops through ids and urls set the the config,
# and generates a .csv file for each, name based on title.
if __name__ == '__main__':
    files, exps = 0, 0
    filename = './table_csvs/%s.csv'
    if not os.path.exists('./table_csvs/'):
        os.mkdir('./table_csvs/')
        print('created dir ./table_csvs')
    
    def scrapensave(url):
        global files, exps
        title, data = scrape_exp_table(url)
        if title == 'none':
            return
        files += 1
        exps += len(data)
        title = title.split(':')[0].replace(' ', '_').replace('.', '').replace('/', '')+str(files)
        save_csv(filename%title, data)
        print('table saved to', filename%title)


    for table_urltag in config['urls']:
        scrapensave(table_urltag)

    for table_id in config['ids']:
        for i in range(config['category_start'], config['category_stop']+1): 
            _input = REPORT_QUERY_LIST_URL % (table_id, i, config['start_at'], config['stop_at'])
            print('_input:', _input)
            scrapensave(_input)
            
    print('\nFinished scraping:\nexperience tables:', files, '\ntotal experiences:', exps)    
