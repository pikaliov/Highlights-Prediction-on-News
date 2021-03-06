
import csv
import requests
from goose import Goose
import difflib
import re



def is_ascii(s):
    return all(ord(c) < 128 for c in s)

# read file
with open('../data/output/news_data.csv','rb') as csvfile:
     reader = csv.reader(csvfile)
     urls = [row[0] for row in reader]
csvfile.close()

with open('../data/output/news_data.csv','rb') as csvfile:
     reader = csv.reader(csvfile)
     selections = [row[1] for row in reader]
csvfile.close()

print len(urls)
print len(selections)

# remove none english
new_urls = []
new_selections = []
for i in range(0,len(urls)):
    selection = selections[i]
    if is_ascii(selection):
        new_urls.append(urls[i])
        new_selections.append(selection)
urls = new_urls
selections = new_selections

# build url-selections pair
url_selection = {}
for i in range(0,len(urls)):
    if url_selection.has_key(urls[i]):
        url_selection[urls[i]].append(selections[i])
    else:
        url_selection[urls[i]] = []
        url_selection[urls[i]].append(selections[i])
# print url_selectio

print len(urls)
print len(selections)
urls = list(set(urls))
print urls[0]
print urls[1]
print len(urls)
print len(selections)


#
sum = 0
writefile = file('../data/output/news_gra_sen_title.csv', 'w')
writer = csv.writer(writefile)

writefile2 = file('../data/output/news_doc_sen_title.csv', 'w')
writer2 = csv.writer(writefile2)
j = 0

strinfo = re.compile('\n')
for url in urls:
    j += 1
    try:
        # extract information of a web page, content, title
        response = requests.get(url, timeout=20)
        g = Goose()
        article = g.extract(url=url)
        content = article.cleaned_text
        title = article.title

        super_super_flag = 0
        blocks = content.split('\n\n')
        block_i = 0

        # data3 = []
        data2 = []

        # flat content lists into one list
        flatten_content = strinfo.sub('',content)
        flatten_content = "".join(flatten_content.encode('ascii','ignore').lower())

        # for every paragraph
        for block in blocks:

            # data = []
            data1 = []

            super_flag = 0
            block_i += 1
            # print block_i,"  ",len(blocks),"  ",block_i/floatlen(blocks))
            block = block.strip()
            # split sentences
            sens = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', block)
            sens = [" ".join(sen.encode('ascii','ignore').lower().split()) for sen in sens]
            selections = [" ".join(sen.encode('ascii','ignore').lower().split()) for sen in url_selection[url]]
            title = title.encode('ascii','ignore').lower()
            block = block.encode('ascii','ignore').lower()
            for sen in sens:
                flag = 0
                if len(sen.split(" ")) > 3:
                    for selection in selections:
                        if difflib.SequenceMatcher(None, sen, selection).ratio() >= 0.6 or difflib.SequenceMatcher(None,selection, sen).ratio() >= 0.6:
                            flag = 1
                            super_flag = 1
                    # restore each piece of data
                    data1.append((flag, url, block, sen, title,block_i, block_i/float(len(blocks))))
                    data2.append((flag, url,flatten_content, sen, title,block_i, block_i/float(len(blocks))))
            # if the selection can be found in the paragraph, then write it into the new file
            if super_flag == 1:
                writer.writerows(data1)
                super_super_flag = 1
        # if the selection can be found in the document, then write it into the new file
        if super_super_flag == 1:
            print j, "   ", "valid", "   ", url
            # print data
            writer2.writerows(data2)
            sum += 1
        else:
            print j,"   ","not valid","   ", url
    except Exception as e:
        print j,"   ","Exception",   "   ", url

writefile.close()
writefile2.close()