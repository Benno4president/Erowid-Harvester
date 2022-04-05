from libs import dict_to_csv
import urllib.request, json

EROWID_BASE_URL = 'https://www.erowid.org/experiences/'
ALL_DRUG_EXP_URL = EROWID_BASE_URL + 'exp_list.shtml'

config = {
        'substance': 'Mushrooms - ',
        'skip_subcategories': [
            'First Times',
            'Families'
        ]
    }

with urllib.request.urlopen(ALL_DRUG_EXP_URL) as res:
    page = res.read().decode("ISO-8859-1")
substance_raw = page.split('<!-- Start ')

for drug in substance_raw:
    if not drug.startswith(config['substance']):
        continue
    drug_name = drug.split(' -->')[0].replace(' ', '').replace('.', '_')
    categories = drug.split('<LI><A HREF=\"')[1:]
    for cat in categories:
        category_suburl, category_name = cat.split('</A>')[0].split('\">')
        print(drug_name, category_name, category_suburl)
        

