#!/usr/bin/env python

# configs
FROMID = 1 
TOID = 25 # 67000 maybe max. research needed.
FILTER_BY_WORD_SET = True # all stories will be saved if false, b/c the word list is ignored.
TARGET_WORD_SET = set([ # don't use spaces, they have no effect.
    'mushroom', 
    'mushrooms', 
    'shroom', 
    'shrooms', 
    '$hroom', 
    '$hrooms', 
    '\'rooms',
    'psilocybin',
    'psilocyn',
    'magic mush',
    'boomers',
    'mushies',
    'caps'
    ])
SAVE_AS_CSV = True # OBS: only saved if code is executed to the end.
SAVE_EACH_TXT = False


# IMPORTS, HELPERS AND SETUP
import os, sys, csv, time, urllib.request, re

def writeFile(fn,data):
    f = open(fn,'w'); f.write(data); f.close()

def removeHTML(s):
    htmlRegexes = ['</?.{1,30}?>']
    for htmlRegex in htmlRegexes:
        s = re.sub(htmlRegex, '', s)
    return s

baseurl = 'http://www.erowid.org/experiences/exp.php?ID=%s'
dir = 'text/'
if not os.path.exists(dir):
    os.mkdir(dir)

# MAIN
print('---------------------------------------------------------------------------------\\')
print('Downloading Erowid experience reports')
story_list = []
for i in range(FROMID, TOID + 1):
    fn = dir + 'erowid_' + str(i) + '.txt'
    id = i
    url = baseurl % id

    if SAVE_EACH_TXT and os.path.exists(fn):
        print('We already downloaded that one.  Skipping #'+str(i))
        continue

    print('-----')
    print('Fetching url: %s'%url)
    with urllib.request.urlopen(url) as res:
        page = res.read().decode("ISO-8859-1")

    # sleeping to not get ip banned for spam, after continue calls.
    time.sleep(0.5)
    if 'Unable to view experience' in page:
        print('No report at that ID number.')
        continue
    intrsec = set(page.lower().split()).intersection(TARGET_WORD_SET)  
    if not FILTER_BY_WORD_SET:
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

    story_list.append({'title':title, 'author':author, 'substance':substance, 'story': body})

    if SAVE_EACH_TXT:
        writeFile(fn, title + '\n\n' + body + '\n')

# This converts and saves the data as csv if true
if SAVE_AS_CSV:
    with open(f'scraped_{len(story_list)}.csv', 'w') as csv_file:  
        writer = csv.writer(csv_file)
        writer.writerow(list(story_list[0].keys()))
        for story_page in story_list:
            writer.writerow([story_page['title'], story_page['author'], story_page['substance'], story_page['story']])
    