from analyst import DataWorker, DataSource, Pointer, Command, Analyst
from session import framework


# Pandas Test
frameworks = framework()

identity = Analyst("Alice", port=65441, host="127.0.0.1")
b = DataWorker(port=65441, host="127.0.0.1")
a = DataSource(identity, b, "Sample Data").init_pointer()

nltk = frameworks.nltk

# split into sentences
sentences = nltk.sent_tokenize(a)
print(sentences[0])

# split into words
tokens = nltk.word_tokenize(a)

# remove all tokens that are not alphabetic
# words = [word for word in tokens if word.isalpha()]
# print(words[:100])


stop_words = nltk.corpus.stopwords.words("english")
words = [w for w in tokens if not w in stop_words]
# print(words[:100])


porter = nltk.stem.porter.PorterStemmer()
stemmed = [porter.stem(word) for word in tokens]
