from textblob import TextBlob

text="This is a sample text. It contains multiple sentences."

blob = TextBlob(text)

sentiment=blob.sentiment
print(sentiment.polarity)

noun_phrases = blob.noun_phrases
print(noun_phrases)

#Part-of-speech tagging: TextBlob can identify the parts of speech in a sentence, such as nouns, verbs, adjectives, adverbs, etc.

# Noun phrase extraction: TextBlob can extract noun phrases from a sentence, which can be useful for tasks such as text classification and information extraction.

# Sentiment analysis: TextBlob can determine the sentiment of a piece of text, such as whether it is positive or negative.

# Spelling correction: TextBlob can correct spelling mistakes in a piece of text using a built-in spelling correction algorithm.

# Language translation: TextBlob can translate text from one language to another using the Google Translate API.

# Text classification: TextBlob can classify text into predefined categories based on its content, such as spam vs. non-spam emails.

# Tokenization: TextBlob can break up a piece of text into individual words or tokens.

# Lemmatization: TextBlob can convert words to their base form, which can be useful for tasks such as text classification and information retrieval.

# Parsing: TextBlob can parse sentences to identify their grammatical structure, such as subject, verb, and object.