
import nltk
import numpy as np
from nltk.stem import WordNetLemmatizer
import json
import pickle
import warnings
import numpy
import tensorflow as tf
from keras.models import Sequential
from keras.layers import Dense, Activation, Dropout
from tensorflow.keras.optimizers import SGD
import random

lemmatizer = WordNetLemmatizer()
warnings.filterwarnings('ignore')

# Preprocessing

words =[]
classes = []
documents = []
ignore_words = ['?', '!']
data_file = open('data/dataset/inputs.json').read() # open and read the json file
intents = json.loads(data_file) # load the json file

for intent in intents['intents']:
    for pattern in intent['patterns']:
        # Tokenize each word
        word = nltk.word_tokenize(pattern)
        words.extend(word) # add each tokenized word into the list of words

        documents.append((word, intent['tag'])) # add a single element into the end of the list
        # add to tag in our classes list
        if intent['tag'] not in classes:
            classes.append(intent['tag'])

# lemmatize, lower each word and remove duplicates

words = [lemmatizer.lemmatize(word.lower()) for word in words if word not in ignore_words]
words = sorted(list(set(words)))

# sort classes

classes = sorted(list(set(classes)))
# Note that the document is the combitation between the patterns and intents
# And the classes are the intents[tag]

pickle.dump(words, open('words.pkl', 'wb'))
pickle.dump(classes, open('classes.pkl', 'wb'))

# Training the model

# Create the training data
training = []

# create an empty array for the output

output_empty = [0] * len(classes)

# training set, bag of words for each sentence

for doc in documents:
    # initialize our bag of words
    bag = []
    # list of tokenzied words
    pattern_words = doc[0]

    # convert pattern_words in lower case
    pattern_words = [lemmatizer.lemmatize(word.lower()) for word in pattern_words]

    # create bag of words array, if word match found in current pattern, then put 1 otherwise 0.
    for word in words:
        bag.append(1) if word in pattern_words else bag.append(0)

    output_row = list(output_empty)
    output_row[classes.index(doc[1])] = 1

    training.append([bag, output_row])

random.shuffle(training)
training = np.array(training)

train_x = list(training[:,0])
train_y = list(training[:, 1])


model = Sequential()
model.add(Dense(128, input_shape=(len(train_x[0]),), activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(64, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(len(train_y[0]), activation='softmax'))
print("First layer:",model.layers[0].get_weights()[0])


# Compile model. Stochastic gradient descent with Nesterov accelerated gradient gives good results for this model
# sgd = SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)
model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

#fitting and saving the model
hist = model.fit(np.array(train_x), np.array(train_y), epochs=200, batch_size=5, verbose=1)
model.save('model.h5', hist)

print("model created")


