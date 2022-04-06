import csv

def dict_to_csv(dct, filename='data.csv', column_names=[]):
    dict_list = []
    for key in dct:
        cont = dct[key]
        dict_list.append(cont)
    if not column_names:    
        column_names = [str(i) for i in dict_list[0].keys()]
    with open(filename, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=column_names)
        writer.writeheader()
        writer.writerows(dict_list)
        
if __name__ == '__main__':
    EROWID_BASE_URL = 'https://www.erowid.org/experiences/'
    REPORT_QUERY_LIST_URL = EROWID_BASE_URL + 'exp.cgi?S=%d&C=1&Start=0&Max=1' 
    import requests
    for i in range(1):
        res = requests.get(REPORT_QUERY_LIST_URL%i).content
        title = str(res).find('title').string
        print(title)
