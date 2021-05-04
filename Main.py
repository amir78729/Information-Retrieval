import pandas as pd
from nltk import ngrams, FreqDist


data = pd.read_excel(r'IR_Spring2021_ph12_7k.xlsx')
doc_id = data['id'].tolist()
content = data['content'].tolist()
url = data['url'].tolist()
print(content)
tokens = []

all_counts = dict()
for size in 1, 2:
    all_counts[size] = FreqDist(ngrams(content, size))
tokens.append(all_counts[1].B())

print(tokens)
# df = pd.DataFrame(data, columns=['id'])
# print(df)