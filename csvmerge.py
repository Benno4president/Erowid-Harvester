import sys, os, csv
ar = sys.argv[1:]
if len(ar) == 0:
    print("""
    Help:
    python3 csvmerge.py [FOLDER-PATH] [CSV-FILE-PATH]...
    This script looks for any csv in any path given.
    Then, it merges everything if compatible,
    and stores the output in current path.
    """)
    exit()

path_collection = []
for pa in ar:
    if os.path.isdir(pa):
        [path_collection.append(os.path.join(pa,x)) for x in os.listdir(pa) if x.endswith('.csv')]
    if not pa.endswith('.csv'):
        continue
    path_collection.append(pa)

fhs = [csv.reader(open(filename, 'r'), delimiter=',') for filename in path_collection]
headers_list = [next(fh) for fh in fhs] # column names for each csv
for header in headers_list:
    assert headers_list[0] == header # validation of columns

f = open('merge_out.csv', 'w')
out = csv.writer(f, delimiter=',')
out.writerow(headers_list[0])
for handle in fhs: # each file
    for row in handle: # each row          
        out.writerow(row)
f.close()