import nltk

def word_tokenize(string):
    return nltk.word_tokenize(string, "english")

def sent_tokenize(string):
    return nltk.sent_tokenize(string, "english")

def word_tokenize_return_string_and_length(string):
    tokenized = word_tokenize(string)
    return " ".join(tokenized), len(tokenized)

def sent_tokenize_return_string_and_length(string):
    """
    return sentence + word tokenized string
    number of sentences
    number of words
    :param string:
    :return:
    """
    sentences = sent_tokenize(string)
    tokenized_text = []
    words_per_sentence = []
    for sent in sentences:
        words = word_tokenize(sent)
        tokenized_text.extend(words)
        words_per_sentence.append(len(words)) # not used for now

    return " ".join(tokenized_text), len(sentences), len(tokenized_text)