import pandas as pd
from nltk import ngrams, FreqDist


# Function to sort the list by second item of tuple
def sort_tuple(tup):
    return (sorted(tup, key=lambda x: x[0]))


def get_list_without_redundancy(lst):
    return list(dict.fromkeys(lst))


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

all_tokens = list(dict.fromkeys([t[0] for t in get_list_without_redundancy(sort_tuple(term_doc_id))]))
print(all_tokens)
term_doc_id = (sort_tuple(term_doc_id))

for i in all_tokens:
    print(i)
# for size in 1, 2:
#     all_counts[size] = FreqDist(ngrams(content, size))
# tokens.append(all_counts[1].B())


# df = pd.DataFrame(data, columns=['id'])
# print(df)