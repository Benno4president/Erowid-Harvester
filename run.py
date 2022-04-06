import urllib.request, json

EROWID_BASE_URL = 'https://www.erowid.org/experiences/'
ALL_DRUG_EXP_URL = EROWID_BASE_URL + 'exp_list.shtml'
REPORT_QUERY_LIST_URL = EROWID_BASE_URL + 'exp.cgi?S=%d&C=%d&start=%d&stop=%d' 
config = {
        'substance': 'Mushrooms - ',
        'skip_subcategories': [
            'First Times',
            'Families'
        ]
    }
def url(url):
    with urllib.request.urlopen(url) as res:
        return res.read().decode("ISO-8859-1")


# first segment - generate drugs-to-do list/index :))))

substance_raw = url(ALL_DRUG_EXP_URL).split('<!-- Start ')

target_drug_dict = {}

for drug in substance_raw:
    if not drug.startswith(config['substance']):
        continue
    drug_name = drug.split(' -->')[0].replace(' ', '').replace('.', '_')
    target_drug_dict[drug_name] = {}
    categories = drug.split('<LI><A HREF=\"')[1:]
    for cat in categories:
        category_suburl, category_name = cat.split('</A>')[0].split('\">')
        if not category_name in config['skip_subcategories']:
            target_drug_dict[drug_name].update({'name':category_name, 'suburl':category_suburl})
with open('erowid_current_drug_index.json', 'w') as fp:
    json.dump(target_drug_dict, fp, indent=2)
print('saved working drug index')

del substance_raw
del target_drug_dict


# second segment - scrape each category if not already

with open('erowid_current_drug_index.json', 'r') as fp:
    drug_dict = json.load(fp)    





