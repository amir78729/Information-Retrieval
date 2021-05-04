import pandas as pd
from nltk import ngrams, FreqDist


# Function to sort the list by second item of tuple
def sort_tuple(tup):
    return (sorted(tup, key=lambda x: x[0]))

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
        term_doc_id.append((term, i + 1))

# sort by term
term_doc_id = sort_tuple(term_doc_id)

for i in term_doc_id:
    print(i)
# for size in 1, 2:
#     all_counts[size] = FreqDist(ngrams(content, size))
# tokens.append(all_counts[1].B())


# df = pd.DataFrame(data, columns=['id'])
# print(df)