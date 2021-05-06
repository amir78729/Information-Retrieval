import pandas as pd
from nltk import ngrams, FreqDist


# Function to sort the list by second item of tuple
def sort_tuple(tup):
    return (sorted(tup, key=lambda x: x[0]))


def get_list_without_redundancy(lst):
    return list(dict.fromkeys(lst))

def create_inverted_index(term_doc_id):
    res = {}
    for x in term_doc_id:
        if not x[0] in res.keys():
            list = []
            list.append(x[1])
            res.update({x[0]: list})
        else:
            list = res[x[0]]
            list.append(x[1])
            res.update({x[0]: list})

    # print(type(res))
    for r in res.keys():
        print(r, res[r])
    # print(res)

path = 'IR_Spring2021_ph12_7k.xlsx'
path = 'demo data.xlsx'

data = pd.read_excel(path)
doc_id = data['id'].tolist()
content = data['content'].tolist()
url = data['url'].tolist()
# print(content)
tokens = []
# print(content[0])
# print(content[0].split())

all_counts = dict()
term_doc_id = []
for i in range(2):
    doc_terms = content[i].split()
    for term in doc_terms:
        term = term.replace('.', '')
        term = term.replace(':', '')
        term = term.replace('،', '')
        term_doc_id.append((term, i + 1))

term_doc_id = sort_tuple(term_doc_id)

create_inverted_index(term_doc_id)

all_tokens = list(dict.fromkeys([t[0] for t in get_list_without_redundancy(term_doc_id)]))
# print(all_tokens)

count = {}
for i in all_tokens:
    # print(i)
    freq = 0
    for j in term_doc_id:
        if j[0] == i:
            freq += 1
    # print(freq)
    count.update({i: freq})


# print(count["و"])
# for size in 1, 2:
#     all_counts[size] = FreDist(ngrams(content, size))
# tokens.append(all_counts[1].B())


# df = pd.DataFrame(data, columns=['id'])
# print(df)