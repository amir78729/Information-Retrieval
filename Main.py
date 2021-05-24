import pandas as pd
from tqdm import tqdm


class SearchEngine:
    def __init__(self):
        path = 'IR_Spring2021_ph12_7k.xlsx'
        # path = 'demo data.xlsx'

        self.data = pd.read_excel(path)
        self.doc_id = self.data['id'].tolist()
        self.content = self.data['content'].tolist()
        self.url = self.data['url'].tolist()

        # constants
        self.FA_NUMS = '۱ ۲ ۳ ۴ ۵ ۶ ۷ ۸ ۹ ٠ ۰'.split()
        self.EN_NUMS = '1 2 3 4 5 6 7 8 9 0 0'.split()
        self.SYMBOLS_TO_BE_REMOVED = '_ + = & ؟ ^ % $ . : ، \" \' | \\ / * ) ( ! - ؛'.split()
        self.STOPWORDS_LIMIT = 10

        # dictionaries
        self.stemming_conversion_dictionary = self.get_stemming_dictionary()
        self.mokassar_plurals_dictionary = self.get_mokassar_plurals_dictionary()

        self.all_tokens_frequencies = {}

        self.stopwords = []

        # reading exception words from file
        with open('normalization_exceptions.txt', 'r', encoding='utf-8') as file:
            self.normalization_exceptions = file.read().split('\n')

        # create term-DocID dictionary
        self.term_doc_id = []
        # for i in tqdm(range(len(self.content)), "PROCESSING ALL DOCUMENTS"):
        for i in tqdm(range(100), "PROCESSING ALL DOCUMENTS"):
            # make a list of words retrieved from content
            doc_terms = self.content[i].split()

            # process tokens
            for term in doc_terms:

                term = self.normalize(term)

                # add {TERM: DocID} to our dictionary
                self.term_doc_id.append((term, i + 1))

                # creating a list from distinct tokens
                if term not in self.all_tokens_frequencies.keys():
                    self.all_tokens_frequencies.update({term: 1})
                else:
                    self.all_tokens_frequencies.update({term: self.all_tokens_frequencies[term] + 1})

        # sort term-DocID dictionary by terms
        self.term_doc_id = self.sort_tuple(self.term_doc_id)

        # creating inverted indexes
        self.inverted_index = self.create_inverted_index(self.term_doc_id)

        self.all_tokens_frequencies = dict(sorted(self.all_tokens_frequencies.items(), key=lambda x: x[1]))

        # removing stopwords
        [self.stopwords.append(list(self.all_tokens_frequencies.keys())[-1 - sw])
         for sw in tqdm(range(self.STOPWORDS_LIMIT), desc='FINDING ALL OF STOPWORDS')]
        print('STOPWORDS: {  ', end='')
        [print(sw, end='\t') for sw in self.stopwords]
        print('}')
        [self.inverted_index.pop(sw) for sw in tqdm(self.stopwords, desc='REMOVING SOME STOPWORDS ')]





    # Function to sort the list by second item of tuple
    def sort_tuple(self, tup):
        return sorted(tup, key=lambda x: x[0])

    def get_stemming_dictionary(self):
        with open('stemming_conversion.txt', 'r', encoding='utf-8') as stems:
            dictionary = dict()
            maazi_suffixes = ['م', 'ی', '', 'یم', 'ید', 'ند', 'ن']
            mozare_suffixes = ['م', 'ی', 'د', 'یم', 'ید', 'ند']
            lines = stems.readlines()
            for l in tqdm(lines, 'VERBS\' STEMMING PROCESS '):
                bon_maazi, bon_mozare = l.split()
                for s in maazi_suffixes:
                    dictionary.update({bon_maazi + s: bon_maazi})
                    dictionary.update({'ن' + bon_maazi + s: bon_maazi})
                    dictionary.update({'می‌' + bon_maazi + s: bon_maazi})
                    dictionary.update({'نمی‌' + bon_maazi + s: bon_maazi})
                    dictionary.update({bon_maazi + 'ه‌ا' + s: bon_maazi})
                for s in mozare_suffixes:
                    dictionary.update({bon_mozare + s: bon_mozare})
                    dictionary.update({'ب' + bon_mozare + s: bon_mozare})
                    dictionary.update({'ن' + bon_mozare + s: bon_mozare})
                    dictionary.update({'نمی‌' + bon_mozare + s: bon_mozare})
                    dictionary.update({'می‌' + bon_mozare + s: bon_mozare})
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

    def removing_suffixes(self, word):
        suffixes = ['ترین', 'تر', 'ات', 'ها', 'ی', '‌شان', 'ان']
        for s in suffixes:
            if word.endswith(s):
                if word not in self.normalization_exceptions:
                    # print(word)
                    word = self.remove_suffix(word, s)
                    # print(word)
        return word

    def calculate_frequency(self, all_tokens_, term_doc_id_):
        count = {}
        for i in tqdm(all_tokens_, desc='CALCULATING FREQUENCIES '):
            # print(i)
            freq = 0
            for j in term_doc_id_:
                if j[0] == i:
                    freq += 1
            count.update({i: freq})
        return count

    def create_inverted_index(self, term_doc_id):
        res = {}
        for x in tqdm(term_doc_id, desc='CREATING INVERTED INDEX '):
            if not x[0] in res.keys():
                list_ = []
            else:
                list_ = res[x[0]]
            list_.append(x[1])
            res.update({x[0]: list_})

        return res

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

    def normalize(self, term):
        # removing whitespaces
        term = term.strip()

        # case folding for english words
        term = term.lower()

        # removing symbols
        for symbol in self.SYMBOLS_TO_BE_REMOVED:
            term = term.replace(symbol, '')

        # removing suffixes
        term = self.removing_suffixes(term)

        # changing verbs to stems ( بن مضارع / بن ماضی )
        term = self.stemming_processing(term)

        # change mokassar plurals into singular form
        term = self.mokassar_plurals_processing(term)

        # change persian numbers into english numbers
        for fa, en in zip(self.FA_NUMS, self.EN_NUMS):
            term = term.replace(fa, en)

        return term

    def main(self):
        print('NUMBER OF TOKENS: {} ({} DISTINCT VALUES WITHOUT STOPWORDS)'
              .format(len(self.term_doc_id), len(self.inverted_index)))
        # for i in self.all_tokens_frequencies.keys():
        #     print(i, self.all_tokens_frequencies[i])
        # for i in self.inverted_index.keys():
        #     print(i, self.inverted_index[i])
        while True:
            query = self.normalize(input('enter a query (\"\\q\": quit the program)'.upper()))
            if query == '\\Q':
                break
            else:
                try:
                    if query in self.stopwords:
                        print('this word is a stopword'.upper())
                    else:
                        result = list(set(self.inverted_index[query]))
                        print('{} result(s):'.format(len(result)).upper())
                        print(result)
                        while True:
                            res = input('select on of the results to show the information (-1 to cancel)'.upper())
                            for fa, en in zip(self.FA_NUMS, self.EN_NUMS):
                                res = res.replace(fa, en)
                            if res == '-1':
                                print('canceled'.upper())
                                break
                            else:
                                try:
                                    if int(res) in result:
                                        print('DOC-ID : ' + str(self.doc_id[int(res) - 1]))
                                        print('LINK   : ' + self.url[int(res) - 1])
                                        print('CONTENT: \n' + self.content[int(res) - 1])

                                    else:
                                        print('bad input!'.upper())
                                except Exception as e:
                                    print(e)
                                    print('bad input!'.upper())

                except KeyError:
                    print('no result'.upper())
            print(45 * '- ')


if __name__ == '__main__':
    SearchEngine().main()
