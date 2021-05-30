import pandas as pd
from tqdm import tqdm
import time
import re


def strikedthrough(text):
    result = ''
    for c in text:
        result = result + c + '\u0336'
    return result


class SearchEngine:
    def __init__(self):
        start = time.time()
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
        self.STOPWORDS_LIMIT = 20

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
            position_index = 0
            for term in doc_terms:

                term = self.normalize(term)

                # add {TERM: (DocID, PositionalIndex}) to our dictionary
                self.term_doc_id.append((term, (i+1, position_index)))
                position_index += 1
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
        # time.sleep(.1)
        # print('STOPWORDS: {  ', end='')
        # [print(sw, end='\t') for sw in self.stopwords]
        # print('}')
        [self.inverted_index.pop(sw) for sw in tqdm(self.stopwords, desc='REMOVING SOME STOPWORDS ')]
        end = time.time()
        self.process_time = end - start

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
                    dictionary.update({'می' + bon_maazi + s: bon_maazi})
                    dictionary.update({'نمی‌' + bon_maazi + s: bon_maazi})
                    dictionary.update({'نمی' + bon_maazi + s: bon_maazi})
                    dictionary.update({bon_maazi + 'ه‌ا' + s: bon_maazi})
                for s in mozare_suffixes:
                    dictionary.update({bon_mozare + s: bon_mozare})
                    dictionary.update({'ب' + bon_mozare + s: bon_mozare})
                    dictionary.update({'ن' + bon_mozare + s: bon_mozare})
                    dictionary.update({'نمی‌' + bon_mozare + s: bon_mozare})
                    dictionary.update({'نمی' + bon_mozare + s: bon_mozare})
                    dictionary.update({'می‌' + bon_mozare + s: bon_mozare})
                    dictionary.update({'می' + bon_mozare + s: bon_mozare})

                # dictionary.update({'ب' + bon_mozare: bon_mozare})
                # dictionary.update({'ن' + bon_mozare: bon_mozare})
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

        term = term.replace('آ', 'ا')

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

        time.sleep(1)
        print('SEARCH ENGINE IS READY ({} seconds)'.format(self.process_time))
        print(' ├─ {} STOPWORDS'.format(len(self.stopwords)))
        print(' ├─ {} TOKENS '.format(len(self.term_doc_id)))
        print(' └─ {} DISTINCT VALUES WITHOUT STOPWORDS'.format(len(self.inverted_index)))
        # for i in self.all_tokens_frequencies.keys():
        #     print(i, self.all_tokens_frequencies[i])
        # for i in self.inverted_index.keys():
        #     print(i, self.inverted_index[i])
        while True:
            user_queries = input('enter a query \n'
                                 '(\"\\q\": quit the program)\n'
                                 '(you can use \"[a substring]\" in search)\n> '.upper())
            substring, string_without_substring = self.exstract_substring(user_queries)
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
                    print('processing substring...'.upper())
                    substring = substring.split()
                    # print(substring)
                    candidates = []
                    for s in substring:
                        candidate = self.inverted_index[self.normalize(s)]
                        candidates.append(candidate)

                    # only docs
                    # print(candidates)
                    docs = []
                    for c in candidates:
                        cc = []
                        for ccc in c:
                            cc.append(ccc[0])
                        docs.append(set(cc))
                    # print(docs)

                    docs = list(set.intersection(*docs))
                    # print(docs)

                    if len(docs) == 0:
                        pass
                    else:
                        # first element of substring
                        for base in candidates[0]:
                            if base[0] in docs:
                                flag = True
                                doc = base[0]
                                index = base[1]
                                for i in range(len(candidates)-1):
                                    if (doc, index + i + 1) not in candidates[i+1]:
                                        flag = False
                                        break
                                if flag:
                                    substring_results.add(doc)

                    set_of_answers.append(substring_results)
                try:
                    for query in string_without_substring:
                        try:
                            if query in self.stopwords:
                                print('{} is a stopword'.format(query).upper())
                            else:
                                result = sorted(list(set(self.inverted_index[self.normalize(query)])))
                                print('{} result(s) founded for {}.'.format(len(result), query).upper())
                                result_docs = []
                                for i in result:
                                    result_docs.append(i[0])
                                set_of_answers.append(set(result_docs))

                        except KeyError:
                            print('no result for'.upper(), query)
                            missing_words.append(query)
                except IndexError:
                    pass
            # print(set_of_answers)
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
                    if i == len(missing_words)-1:
                        print(missing_words[i], ')')
                    else:
                        print(strikedthrough(missing_words[i]), end=', ')

            while True:
                res = input('select on of the results to show the information (-1 to cancel)\n> '.upper())
                for fa, en in zip(self.FA_NUMS, self.EN_NUMS):
                    res = res.replace(fa, en)
                if res == '-1':
                    print('canceled'.upper())
                    break
                else:
                    try:
                        # result_docs = []
                        # for i in result:
                        #     result_docs.append(i[0])
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
