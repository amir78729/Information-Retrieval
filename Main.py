import pandas as pd
from tqdm import tqdm
from nltk import ngrams, FreqDist


class SearchEngine:
    def __init__(self):
        path = 'IR_Spring2021_ph12_7k.xlsx'
        path = 'demo data.xlsx'

        self.data = pd.read_excel(path)
        self.doc_id = self.data['id'].tolist()
        self.content = self.data['content'].tolist()
        self.url = self.data['url'].tolist()

        self.symbols_to_be_removed = ' . : ، \" \' | \\ / * ) ( ! -'.split()

        self.stemming_conversion_dictionary = self.get_stemming_dictionary()
        self.mokassar_plurals_dictionary = self.get_mokassar_plurals_dictionary()



        # reading exception words from file
        with open('normalization_exceptions.txt', 'r', encoding='utf-8') as file:
            self.normalization_exceptions = file.read().split('\n')

    # Function to sort the list by second item of tuple
    def sort_tuple(self, tup):
        return sorted(tup, key=lambda x: x[0])

    def get_stemming_dictionary(self):
        with open('stemming_conversion.txt', 'r', encoding='utf-8') as stems:
            dictionary = dict()
            maazi_suffixes = ['م', 'ی', '', 'یم', 'ید', 'ند', 'ن']
            mozare_suffixes = ['م', 'ی', 'د', 'یم', 'ید', 'ند']
            lines = stems.readlines()
            for l in tqdm(lines, 'STEMMING PROCCESS'):
                bon_maazi, bon_mozare = l.split()
                for s in maazi_suffixes:
                    dictionary.update({bon_maazi + s: bon_maazi})
                    dictionary.update({'ن' + bon_maazi + s: bon_maazi})
                for s in mozare_suffixes:
                    dictionary.update({bon_mozare + s: bon_mozare})
                    dictionary.update({'ب' + bon_mozare + s: bon_mozare})
                    dictionary.update({'ن' + bon_mozare + s: bon_mozare})
                    # print('خواه' + s + " " + bon_maazi)
            return dictionary

    def get_mokassar_plurals_dictionary(self):
        with open('mokassar_plurals.txt', 'r', encoding='utf-8') as stems:
            dictionary = dict()
            lines = stems.readlines()
            for l in tqdm(lines, 'GETTING MOKASSAR PLURALS'):
                singular, plural = l.split()
                dictionary.update({plural: singular})
            return dictionary


    def remove_suffix(self, s, suffix):
        if suffix and s.endswith(suffix):
            return s[:-len(suffix)]
        return s

    # [a, a, b, c, d, d] => [a, b, c, d]
    def get_list_without_redundancy(self, lst):
        return list(dict.fromkeys(lst))


    def normalize(self, word):
        suffixes = ['ترین', 'تر', 'ات', 'ها', 'ی']
        for s in suffixes:
            if word.endswith(s):
                if word not in self.normalization_exceptions:
                    # print(word)
                    word = self.remove_suffix(word, s)
                    # print(word)
        return word


    def calculate_frequency(self, all_tokens_, term_doc_id_):
        count = {}
        for i in tqdm(all_tokens_, desc='CALCULATING FREQUENCIES'):
            # print(i)
            freq = 0
            for j in term_doc_id_:
                if j[0] == i:
                    freq += 1
            # print(freq)
            count.update({i: freq})
        return count


    def create_inverted_index(self, term_doc_id):
        res = {}
        for x in tqdm(term_doc_id, desc='CREATING INVERTED INDEXES'):
            if not x[0] in res.keys():
                list_ = []
            else:
                list_ = res[x[0]]
            list_.append(x[1])
            res.update({x[0]: list_})

        # print(type(res))
        for r in res.keys():
            print(r, res[r])
        # print(res)

    def main(self):

        all_counts = dict()

        term_doc_id = []

        for i in tqdm(range(len(self.content)), "PROCESSING DOCS"):

            # make a list of words retrieved from content
            doc_terms = self.content[i].split()

            # process tokens
            for term in doc_terms:
                term = term.strip()
                # term = term.replace('.', '')
                # term = term.replace(':', '')
                # term = term.replace('،', '')
                # term = term.replace('"', '')
                # term = term.replace('*', '')
                # term = term.replace(')', '')
                # term = term.replace('(', '')
                # term = term.replace('!', '')
                # term = term.replace('-', '')
                for symbol in self.symbols_to_be_removed:
                    term = term.replace(symbol, '')

                term = self.normalize(term)

                term = self.stemming_processing(term)

                term = self.mokassar_plurals_processing(term)

                # add {TERM: DocID} to our dictionary
                term_doc_id.append((term, i + 1))

        term_doc_id = self.sort_tuple(term_doc_id)

        self.create_inverted_index(term_doc_id)

        all_tokens = list(dict.fromkeys([t[0] for t in self.get_list_without_redundancy(term_doc_id)]))
        # print(all_tokens)

        frequency = self.calculate_frequency(all_tokens, term_doc_id)

        # print(frequency)

        # print(count["و"])
        # for size in 1, 2:
        #     all_counts[size] = FreDist(ngrams(content, size))
        # tokens.append(all_counts[1].B())


        # df = pd.DataFrame(data, columns=['id'])
        # print(df)

    def stemming_processing(self, term):
        if term in self.stemming_conversion_dictionary.keys():
            return self.stemming_conversion_dictionary[term]
        else:
            return term

    def mokassar_plurals_processing(self, term):
        if term in self.mokassar_plurals_dictionary.keys():
            return self.mokassar_plurals_dictionary[term]
        else:
            return term


if __name__ == '__main__':
    SearchEngine().main()
