import requests
from bs4 import BeautifulSoup
import csv


def soup_from_url(url):
    res = requests.get(url)
    soup = BeautifulSoup(res.content, 'html.parser')
    return soup


def target_tree_structure(row_soup, tree_path):
    tree_path = tree_path.split(':')
    current_step = row_soup
    for inc in tree_path:
        if current_step is None:
            return None
        elif inc == 'href':
            return current_step['href']
        else:
            target = inc.split(';')
            if len(target) == 1:
                current_step = current_step.find(target[0])
            else:
                current_step = current_step.find(target[0], target[1].split('=')[1])
    if current_step is None:
        return None
    return current_step.getText()


def soup_table_to_dict(soup_table, row_cl='topic-surround', 
                       list_of_columns=[
                           'td;class=topic-name:a', 
                           'td;class=topic-name:a:href', 
                           'td;class=topic-common:i', 
                           'td;class=topic-desc'], 
                       headers=['1','2','3','4']):
    assert len(list_of_columns) == len(headers)
    rows = soup_table.find_all('tr', row_cl)
    table_dict = {}
    for row_num, row in enumerate(rows):
        row_dct = {}
        for col_num, col in enumerate(list_of_columns):
            item = target_tree_structure(row, col)
            if item:
                row_dct[headers[col_num]] = str(item)
        if row_dct:
            table_dict[row_num] = row_dct
    return table_dict


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
    s = soup_from_url('https://erowid.org/plants/')
    s = s.find('table', 'topic-chart-surround')
    s = soup_table_to_dict(s)
    s.popitem()
    print(s)
    #dict_to_csv(s)
    #print(s)
