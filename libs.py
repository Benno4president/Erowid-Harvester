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