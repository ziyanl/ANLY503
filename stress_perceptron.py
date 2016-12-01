#!/usr/bin/env python3
"""
Adapted from ENLP A1 Part II: Perceptron

Usage: python stress_perceptron.py NITERATIONS

(Adapted from Alan Ritter)
"""
import sys, os, glob
from evaluation import Eval
from collections import Counter
import re
import json
import pickle
import resources
import utilities as util

def load_dict():
    """Loads words and labels from cmudict."""
    words = []
    labels = []

    for word, pron in resources.cmudict().items():
        label = ''
        for phoneme in pron:
            if phoneme[-1].isdigit():
                if phoneme[-1] == '0':
                    label += '0'
                else:
                    label += '1'
        if len(label) > 5:
            label = 'too_long'
        words.append(extract_feats(word))
        labels.append(label)
    return words, labels


def extract_feats(word):
    """
    Extract input features (percepts) for a given word.
    Each percept is a pairing of a name and a boolean, integer, or float value.
    A document's percepts are the same regardless of the label considered.
    """
    ff = Counter()

    # feature type 1: CV pattern
    cv = ''
    for letter in word:
        if letter in ['A', 'E', 'I', 'O', 'U', 'Y']:
            cv += 'V'
        elif letter in ['B', 'C', 'D', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'N', 'P', 'Q', 'R', 'S', 'T', 'V', 'W', 'X',
                        'Z']:
            cv += 'C'
        else:
            cv += 'X'
    ff[cv] += 1

    # feature type 2: ending features
    if word[-4:] == 'ABLE':
        ff['able'] += 1
    elif word[-1] == 'E':
        ff['e'] += 1
    elif word[-3:] == 'OUS':
        ff['ous'] += 1
    elif word[-4:] == 'NESS':
        ff['ness'] += 1
    elif word[-1] == 'S':
        ff['s'] += 1
    elif word[-3:] == 'ING':
        ff['ing'] += 1
    elif word[-2:] == 'LY':
        ff['ly'] += 1
    elif word[-2:] == 'ED':
        ff['ed'] += 1
    elif word[-3:] == 'ION':
        ff['ion'] += 1
    elif word[-2:] == 'ER':
        ff['er'] += 1
    elif word[-2:] == 'OR':
        ff['or'] += 1
    elif word[-3:] == 'EST':
        ff['est'] += 1
    elif word[-1] == 'Y':
        ff['y'] += 1
    elif word[-3:] == 'FUL':
        ff['ful'] += 1
    elif word[-3:] == 'ISH':
        ff['ish'] += 1

    # plain vowel pattern, with a space where there are consonants
    vowel = re.sub(r'[^AEIOUY]+', r' ', word)
    ff[vowel] += 1

    # likely number of syllables by reducing pairs of consecutive vowels that are likely one phoneme/diphthong
    sylls = re.sub(r'AE|AI|AU|AY|EA|EE|EI|EU|EY|IE|OA|OI|OU|OY', r'D', vowel)
    #sylls = re.sub(r' E$', r'', sylls)
    sylls = re.sub(r' ', r'', sylls)
    ff['syll_' + str(len(sylls))] += 1
    ff['syll'] = len(sylls)

    # length
    ff['len_' + str(len(word))] += 1
    ff['len'] = len(word)

    #print(word, ff)
    return ff


def add_syll(list):
    new_list = []
    for item in list:
        new_list.append('0' + item)
        new_list.append('1' + item)
    return new_list

class Perceptron:
    def __init__(self, train_docs=None, train_labels=None, MAX_ITERATIONS=100, dev_docs=None, dev_labels=None, weights=None, biases=None):
        pre_syll = ['']
        self.CLASSES = ['too_long']
        for i in range(1,6):
            next_syll = add_syll(pre_syll)
            pre_syll = next_syll
            self.CLASSES += next_syll
        #print(self.CLASSES)
        self.MAX_ITERATIONS = MAX_ITERATIONS
        if weights is not None and biases is not None:
            with open(util.path_to_scraping_directory() + weights, 'rb') as wfile:
                self.weights = pickle.load(wfile)
            with open(util.path_to_scraping_directory() + biases, 'rb') as bfile:
                self.biases = pickle.load(bfile)
        else:
            #self.dev_docs = dev_docs
            #self.dev_labels = dev_labels
            self.weights = {l: Counter() for l in self.CLASSES}
            self.biases = {l: 0 for l in self.CLASSES}
            self.learn(train_docs, train_labels)

    def copy_weights(self):
        """
        Returns a copy of self.weights.
        """
        return {l: Counter(c) for l,c in self.weights.items()}

    def learn(self, train_docs, train_labels):
        """
        Train on the provided data with the perceptron algorithm.
        Up to self.MAX_ITERATIONS of learning.
        At the end of training, self.weights should contain the final model
        parameters.
        """
        for i in range(self.MAX_ITERATIONS):
            updates = 0
            for t in range(len(train_docs)):
                doc = train_docs[t]
                pred = self.predict(doc)
                gold = train_labels[t]
                if pred != gold:
                    self.weights[gold] += doc
                    self.weights[pred] -= doc
                    self.biases[gold] += 1
                    updates += 1
            trainAcc = self.test_eval(train_docs, train_labels)
            #devAcc = self.test_eval(dev_docs, dev_labels)
            print('iteration:', i, 'updates:', updates, 'trainAcc:', trainAcc, file=sys.stderr)
            if updates == 0:
                break
        with open(util.path_to_scraping_directory() + 'weights_5.pk', 'wb') as wfile:
            pickle.dump(self.weights, wfile, 3)
        with open(util.path_to_scraping_directory() + 'biases_5.pk', 'wb') as bfile:
            pickle.dump(self.biases, bfile, 3)
        return


    def score(self, doc, label):
        """
        Returns the current model's score of labeling the given document
        with the given label.
        """
        score = self.biases[label]
        for feature in doc:
            score *= doc[feature] * self.weights[label][feature]
        return score

    def predict(self, doc):
        """
        Return the highest-scoring label for the document under the current model.
        """
        scores = []
        for y in self.CLASSES:
            scores.append(self.score(doc, y))

        return self.CLASSES[scores.index(max(scores))]


    def test_eval(self, test_docs, test_labels):
        pred_labels = [self.predict(d) for d in test_docs]
        ev = Eval(test_labels, pred_labels)
        return ev.accuracy()
    #
    # def analyze_errors(self, test_docs, gold_labels):
    #     pred_labels = [self.predict(d) for d in test_docs]
    #
    #     # confusion matrix
    #     matrix = [[0 for con in range(len(self.CLASSES))] for row in range(len(self.CLASSES))]
    #     for p, g in zip(pred_labels, gold_labels):
    #         p_index = self.CLASSES.index(p)
    #         g_index = self.CLASSES.index(g)
    #         matrix[p_index][g_index] += 1
    #     with open('confusion.tsv', 'w') as confusion_file:
    #         first_row = ' \t' + '\t'.join(self.CLASSES) + '\n'
    #         confusion_file.write(first_row)
    #         for x in range(len(self.CLASSES)):
    #             new_row = self.CLASSES[x] + '\t' + '\t'.join([str(c) for c in matrix[x]]) + '\n'
    #             confusion_file.write(new_row)
    #
    #     with open('stats.txt', 'w') as stats_file:
    #         for l in range(len(self.CLASSES)):
    #             # highest, lowest, and bias features for each language
    #             lang = self.CLASSES[l]
    #             weights = self.weights[lang]
    #             sorted_weights = weights.most_common()
    #             highest = sorted_weights[:10]
    #             lowest = sorted_weights[-10:]
    #             stats_file.write(lang + '\n')
    #             stats_file.write("highest-weighted features: " + str(highest) + '\n')
    #             stats_file.write("lowest-weighted features: " + str(lowest) + '\n')
    #             stats_file.write("bias: " + str(self.biases[lang]) + '\n\n')
    #
    #             # precision, recall, and F1 for each language
    #             tp = matrix[l][l]
    #             fp = sum([matrix[y][l] for y in range(len(matrix)) if y!=l])
    #             fn = sum([matrix[l][y] for y in range(len(matrix)) if y!=l])
    #             precision = tp / (tp + fp)
    #             recall = tp / (tp + fn)
    #             f1 = (2 * precision * recall) / (precision + recall)
    #             stats_file.write("precision: " + str(precision) + '\n')
    #             stats_file.write("recall: " + str(recall) + '\n')
    #             stats_file.write("F1: " + str(f1) + '\n\n')


if __name__ == "__main__":
    args = sys.argv[1:]
    niters = int(args[0])

    train_docs, train_labels = load_dict()
    print(len(train_docs), 'training docs with',
        sum(len(d) for d in train_docs)/len(train_docs), 'percepts on avg', file=sys.stderr)

    # dev_docs,  dev_labels  = load_featurized_docs('dev')
    # print(len(dev_docs), 'dev docs with',
    #     sum(len(d) for d in dev_docs)/len(dev_docs), 'percepts on avg', file=sys.stderr)
    #
    #
    # test_docs,  test_labels  = load_featurized_docs('test')
    # print(len(test_docs), 'test docs with',
    #     sum(len(d) for d in test_docs)/len(test_docs), 'percepts on avg', file=sys.stderr)

    ptron = Perceptron(train_docs, train_labels, MAX_ITERATIONS=niters)
    #acc = ptron.test_eval(test_docs, test_labels)
    #print(acc, file=sys.stderr)
    #ptron.analyze_errors(test_docs, test_labels)
