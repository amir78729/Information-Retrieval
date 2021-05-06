import pandas as pd
from nltk import ngrams, FreqDist


# Function to sort the list by second item of tuple
def sort_tuple(tup):
    return (sorted(tup, key=lambda x: x[0]))


def get_list_without_redundancy(lst):
    return list(dict.fromkeys(lst))


def normalize(word):
    suffixes = ['ات', 'ها', 'ی']
    exceptions = ['انتها', 'زحمات', 'ملی']
    for s in suffixes:
        if word.endswith(s):
            if word not in exceptions:
                print(word)
                word = word.replace(s, '')
                print(word)
    return word

def calculate_frequency(all_tokens_, term_doc_id_):
    count = {}
    for i in all_tokens_:
        # print(i)
        freq = 0
        for j in term_doc_id_:
            if j[0] == i:
                freq += 1
        # print(freq)
        count.update({i: freq})
    return count

def create_inverted_index(term_doc_id):
    res = {}
    for x in term_doc_id:
        if not x[0] in res.keys():
            list = []
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
        term = normalize(term)
        term_doc_id.append((term, i + 1))

term_doc_id = sort_tuple(term_doc_id)

create_inverted_index(term_doc_id)

all_tokens = list(dict.fromkeys([t[0] for t in get_list_without_redundancy(term_doc_id)]))
# print(all_tokens)


frequency = calculate_frequency(all_tokens, term_doc_id)
print(frequency)

# print(count["و"])
# for size in 1, 2:
#     all_counts[size] = FreDist(ngrams(content, size))
# tokens.append(all_counts[1].B())


# df = pd.DataFrame(data, columns=['id'])
# print(df)