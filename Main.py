import pandas as pd
from tqdm import tqdm
import time
import re
import math
import numpy as np


class SearchEngine:
    def __init__(self):
        start = time.time()
        # self.PATH = 'IR_Spring2021_ph12_7k.xlsx'
        self.PATH = 'demo data.xlsx'
        self.MOKASSAAR_PLURALS = 'mokassar_plurals.txt'
        self.BON_FILE = 'stemming_conversion.txt'

        # constants
        self.FA_NUMS = '۱ ۲ ۳ ۴ ۵ ۶ ۷ ۸ ۹ ٠ ۰'.split()
        self.EN_NUMS = '1 2 3 4 5 6 7 8 9 0 0'.split()
        self.SYMBOLS_TO_BE_REMOVED = '_ + = & ؟ ^ % $ . : ، \" \' | \\ / * ) ( ! - ؛'.split()
        self.SUFFIXES_TO_BE_REMOVED = ['ترین', 'تر', 'ات', 'ها', 'ی', '‌شان', 'ان']
        self.STOPWORDS_LIMIT = 20
        self.CHARACTERS_MODIFICATION = {
            'آ': 'ا',
            'ي': 'ی',
            'ك': 'ک',
        }

        # getting data from excel file
        self.data = pd.read_excel(self.PATH)
        self.doc_id = self.data['id'].tolist()
        self.content = self.data['content'].tolist()
        self.url = self.data['url'].tolist()

        # dictionaries and lists
        self.stemming_conversion_dictionary = self.get_stemming_dictionary()
        self.mokassar_plurals_dictionary = self.get_mokassar_plurals_dictionary()
        self.all_tokens_frequencies = {}
        self.stopwords = []
        self.term_frequency = dict()  # access: self.term_frequency[DOC_ID][TERM]
        self.document_frequency = dict()  # access: self.document_frequency[TERM]

        # reading exception words from file
        with open('normalization_exceptions.txt', 'r', encoding='utf-8') as file:
            self.normalization_exceptions = file.read().split('\n')

        # create term-DocID dictionary
        self.term_doc_id = []
        # for i in tqdm(range(100), "PROCESSING ALL DOCUMENTS"):
        for i in tqdm(range(len(self.content)), "PROCESSING ALL DOCUMENTS"):

            # used for calculating term frequency
            tf_temp = dict()

            # make a list of words retrieved from content
            doc_terms = self.content[i].split()

            # process tokens
            position_index = 0
            for term in doc_terms:
                term = self.normalize(term)

                # creating a list from distinct tokens
                if term not in self.all_tokens_frequencies.keys():
                    self.all_tokens_frequencies.update({term: 1})
                else:
                    self.all_tokens_frequencies.update({term: self.all_tokens_frequencies[term] + 1})

                # creating a list from distinct tokens for term frequency
                if term not in tf_temp.keys():
                    tf_temp.update({term: 1})
                else:
                    tf_temp.update({term: tf_temp[term] + 1})

                # creating a list from distinct tokens for documnet frequency
                if term not in self.document_frequency.keys():
                    l = [i]
                    self.document_frequency.update({term: l})
                else:
                    if i not in self.document_frequency[term]:
                        l = self.document_frequency[term]
                        l.append(i)
                        self.document_frequency.update({term: l})

                # add {TERM: (DocID, PositionalIndex}) to our dictionary
                self.term_doc_id.append((term, (i + 1, position_index)))
                position_index += 1

            self.term_frequency.update({i + 1: tf_temp})

        # sort term-DocID dictionary by terms
        self.term_doc_id = self.sort_tuple(self.term_doc_id)

        # creating inverted indexes
        self.inverted_index = self.create_inverted_index()
        self.all_tokens_frequencies = dict(sorted(self.all_tokens_frequencies.items(), key=lambda x: x[1]))
        self.inverted_index.pop('')
        self.all_tokens_frequencies.pop('')

        # calculating vector space
        # self.vector_space = np.zeros((2, 3))
        # print(self.vector_space)

        self.vector_space = np.array([
            [
                self.tf_idf(T, D) for D in self.doc_id
            ]
            for T in tqdm(self.all_tokens_frequencies.keys(), 'CREATING DOC. VEC. SPACE')
        ]).transpose()

        # print(np.array(self.vector_space).shape)
        # for i in self.vector_space:
        #     print(i)
        #     print('*'*20)


        # removing stopwords
        [self.stopwords.append(list(self.all_tokens_frequencies.keys())[-1 - sw])
         for sw in tqdm(range(self.STOPWORDS_LIMIT), desc='FINDING ALL OF STOPWORDS')]
        self.stopwords_count = []
        [self.stopwords_count.append(self.all_tokens_frequencies[sw])
         for sw in self.stopwords]
        [self.inverted_index.pop(sw) for sw in tqdm(self.stopwords, desc='REMOVING SOME STOPWORDS ')]
        end = time.time()
        self.process_time = end - start

        # t = 'دریافت'
        # for i in self.doc_id:
        #     print("doc", i)
        #     print(self.tf_idf(t, i))

        # print(self.inverted_index[t])
        # print(self.document_frequency)
        # print(self.vector_space.shape)
        # q = self.query_vector_space('دریافت یارانه نقدی علی')
        # print(q)

    def print_tf(self):
        for i in self.term_frequency.keys():
            for j in self.term_frequency[i].keys():
                print('{}\t{}: {}'.format(i, j, self.term_frequency[i][j]))
            print()

    def tf_idf(self, t, d):
        try:
            tf = 1 + math.log(self.term_frequency[d][t])
        except (KeyError, ValueError):
            tf = 0
        try:
            idf = math.log((len(self.doc_id) / len(self.document_frequency[t])), 10)
        except KeyError:
            idf = 0
        return tf * idf

    def query_vector_space(self, query):
        vector = []
        for T in tqdm(self.all_tokens_frequencies.keys(), 'CREATING QUERY VEC.SPACE'):
            try:
                tf = 1 + math.log(query.count(T))
            except (KeyError, ValueError):
                tf = 0
            try:
                idf = math.log((len(self.doc_id) / len(self.document_frequency[T])), 10)
            except KeyError:
                idf = 0
            vector.append(tf * idf)
        return np.array(vector)

    # cosine similarity method
    def cosine_similarity(self, a, b):
        return np.dot(a, b)/(np.linalg.norm(a)*np.linalg.norm(b))

    def query_similarity(self, user_query_vector_space):
        i = 1
        lst = []
        for doc in tqdm(self.vector_space, 'CALCULATING SIMILARITY'):
            similarity = self.cosine_similarity(doc, user_query_vector_space)
            if similarity != 0.0 and not math.isnan(similarity):
                lst.append((i, similarity))
            i += 1
        return sorted(lst, key=lambda x: x[1])[::-1]

    # Function to sort the list by second item of tuple
    def sort_tuple(self, tup):
        return sorted(tup, key=lambda x: x[0])

    # 'this is the "table of content" of our text' => ['table of content', 'this', 'is', 'the', 'of', 'our', 'text']
    def exstract_substring(self, text):
        match = re.search("\"(.+?)\"", text, flags=re.IGNORECASE)
        try:
            substring = match.group(1)
        except:
            substring = ""
        string_without_substring = text.replace(substring, '').replace("\"", "").strip()
        return substring, string_without_substring.split()

    def get_stemming_dictionary(self):
        with open(self.BON_FILE, 'r', encoding='utf-8') as stems:
            dictionary = dict()
            maazi_suffixes = ['م', 'ی', '', 'یم', 'ید', 'ند', 'ن']
            mozare_suffixes = ['م', 'ی', 'د', 'یم', 'ید', 'ند']
            lines = stems.readlines()
            for l in tqdm(lines, 'VERBS\' STEMMING PROCESS '):
                bon_maazi, bon_mozare = l.split()
                for s in maazi_suffixes:
                    dictionary.update({bon_maazi + s: bon_maazi})  # خواستم خواستی خواست ...
                    dictionary.update({'ن' + bon_maazi + s: bon_maazi})  # نخواستم نخواستی نخواست ...
                    dictionary.update({'می‌' + bon_maazi + s: bon_maazi})  # میخواستم میخواستی میخواست ...
                    dictionary.update({'می' + bon_maazi + s: bon_maazi})  # می‌خواستم می‌خواستی می‌خواست ...
                    dictionary.update({'نمی‌' + bon_maazi + s: bon_maazi})  # نمیخواستم نمیخواستی نمیخواست ...
                    dictionary.update({'نمی' + bon_maazi + s: bon_maazi})  # نمی‌خواستم نمی‌خواستی نمی‌خواست ...
                    dictionary.update({bon_maazi + 'ه‌ا' + s: bon_maazi})  # خواسته‌ام خواسته‌ای ...
                    dictionary.update({bon_maazi + 'ه‌بود' + s: bon_maazi})  # خواسته‌بودم خواسته‌بودی ...
                for s in mozare_suffixes:
                    dictionary.update({bon_mozare + s: bon_mozare})  # خواهم خواهی خواهد ...
                    dictionary.update({'ب' + bon_mozare + s: bon_mozare})  # بخواهم بخواهی بخواهد ...
                    dictionary.update({'ن' + bon_mozare + s: bon_mozare})  # نخواهم نخواهی نخواهد ...
                    dictionary.update({'نمی‌' + bon_mozare + s: bon_mozare})  # نمیخواهم نمیخواهی نمیخواهد ...
                    dictionary.update({'نمی' + bon_mozare + s: bon_mozare})  # نمی‌خواهم نمی‌خواهی نمی‌خواهد ...
                    dictionary.update({'می‌' + bon_mozare + s: bon_mozare})  # میخواهم میخواهی میخواهد ...
                    dictionary.update({'می' + bon_mozare + s: bon_mozare})  # می‌خواهم می‌خواهی می‌خواهد ...
                    dictionary.update({bon_maazi + 'ه‌باش' + s: bon_maazi})  # خواسته‌باشم خواسته‌باشی ...
            return dictionary

    def get_mokassar_plurals_dictionary(self):
        with open(self.MOKASSAAR_PLURALS, 'r', encoding='utf-8') as stems:
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
        for s in self.SUFFIXES_TO_BE_REMOVED:
            if word.endswith(s):
                if word not in self.normalization_exceptions:
                    word = self.remove_suffix(word, s)
        return word

    def create_inverted_index(self):
        res = {}
        for x in tqdm(self.term_doc_id, desc='CREATING INVERTED INDEX '):
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

    def change_characters(self, term):
        for c in self.CHARACTERS_MODIFICATION.keys():
            term = term.replace(c, self.CHARACTERS_MODIFICATION[c])
        return term

    def normalize(self, term):
        """
        1 - changing characters
            1.1 - case folding (only for english words)
            1.2 - change persian numbers into english numbers
            1.3 - change some persian/arabic characters
        2 - removing characters
        3 - removing suffixes
        4 - changing verbs to stems
        5 - change mokassar plurals into singular form

        :param term:
        :return: modified term
        """
        # removing whitespaces
        term = term.strip()

        # case folding for english words
        term = term.lower()

        # change persian numbers into english numbers
        for fa, en in zip(self.FA_NUMS, self.EN_NUMS):
            term = term.replace(fa, en)

        # change some characters
        term = self.change_characters(term)

        # removing symbols
        for symbol in self.SYMBOLS_TO_BE_REMOVED:
            term = term.replace(symbol, '')

        # removing suffixes
        term = self.removing_suffixes(term)

        # changing verbs to stems ( بن مضارع / بن ماضی )
        term = self.stemming_processing(term)

        # change mokassar plurals into singular form
        term = self.mokassar_plurals_processing(term)
        return term

    def main(self):
        time.sleep(.6)

        print('SEARCH ENGINE IS READY ({} seconds)'.format(self.process_time))
        print(' ├─ {} DOCUMENTS '.format(len(self.content)))
        print(' ├─ {} TOKENS '.format(len(self.term_doc_id)))
        print(' ├─ {} STOPWORDS'.format(len(self.stopwords)))
        for sw in range(len(self.stopwords)):
            if sw != len(self.stopwords) - 1:
                print(' │  ├─ {}/{}:\t({}) \"{}\"'
                      .format(sw + 1, len(self.stopwords), self.stopwords_count[sw], self.stopwords[sw]))
            else:
                print(' │  └─ {}/{}:\t({}) \"{}\"'
                      .format(sw + 1, len(self.stopwords), self.stopwords_count[sw], self.stopwords[sw]))
        print(' └─ {} DISTINCT VALUES WITHOUT STOPWORDS'.format(len(self.inverted_index)))

        while True:
            user_queries = input('enter a query \n'
                                 '(\"\\q\": quit the program)\n'
                                 '(you can use \"[a substring]\" in search)\n> '.upper())
            substring, string_without_substring = self.exstract_substring(user_queries)
            user_query_vector_space = self.query_vector_space(user_queries)

            print(self.query_similarity(user_query_vector_space))

            start_time = time.time()
            if user_queries == '':
                print("EMPTY QUERY!")
                continue
            if user_queries[0].split() == '\\Q' and len(user_queries) == 1:
                break
            else:
                set_of_answers = []
                missing_words = []
                substring_results = set()

                # processing substring
                if len(substring) != 0:
                    try:
                        print('processing substring...'.upper())
                        substring = substring.split()
                        candidates = []
                        for s in substring:
                            candidate = self.inverted_index[self.normalize(s)]
                            candidates.append(candidate)
                        docs = []
                        for c in candidates:
                            cc = []
                            for ccc in c:
                                cc.append(ccc[0])
                            docs.append(set(cc))
                        docs = list(set.intersection(*docs))
                        if len(docs) == 0:
                            pass
                        else:
                            # first element of substring
                            for base in candidates[0]:
                                if base[0] in docs:
                                    flag = True
                                    doc = base[0]
                                    index = base[1]
                                    for i in range(len(candidates) - 1):
                                        if (doc, index + i + 1) not in candidates[i + 1]:
                                            flag = False
                                            break
                                    if flag:
                                        substring_results.add(doc)
                        set_of_answers.append(substring_results)
                    except KeyError:
                        msg = ''
                        for s in substring:
                            msg += s + " "
                        print('SUBSTRING \"{}\" NOT FOUND.'.format(msg))
                try:
                    print(string_without_substring)
                    for query in string_without_substring:
                        try:
                            if query in self.stopwords:
                                print('term \"{}\" :\tstopword!'.format(query).upper())
                            else:
                                result = sorted(list(set(self.inverted_index[self.normalize(query)])))
                                print('term \"{}\" :\t{} result(s)'.format(query.upper(), len(result)).upper())
                                result_docs = []
                                for i in result:
                                    result_docs.append(i[0])
                                set_of_answers.append(set(result_docs))
                        except KeyError:
                            print('term \"{}\" :\tno result'.upper().format(query).upper())
                            missing_words.append(query)
                except IndexError:
                    pass
            print('combining results...'.upper())
            try:
                result = list(set.intersection(*set_of_answers))
            except TypeError:
                print('NO ANSWERS')
                print(45 * '- ')
                continue
            if len(result) == 0:
                print('NO ANSWERS')
                print(45 * '- ')
                continue
            end_time = time.time()
            print(len(result), 'RESULT(S) ({} seconds)'.format((end_time - start_time)))
            for r in range(len(result)):
                if r != len(result) - 1:
                    print(' ├─ {}'.format(result[r]))
                else:
                    print(' └─ {}'.format(result[r]))
            if len(missing_words) != 0:
                print('( missing words: '.upper(), end='')
                for i in range(len(missing_words)):
                    if i == len(missing_words) - 1:
                        print(missing_words[i], ')')
                    else:
                        print(missing_words[i], end=', ')
            while True:
                res = input('select on of the results to show the information (-1 to cancel)\n> '.upper())
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
            print(45 * '- ')


if __name__ == '__main__':
    SearchEngine().main()
