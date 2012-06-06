import random
import math
import operator
from collections import Counter, defaultdict
import twokenize
import peewee
from models import database, SMS, Contact


class NaiveBayes(object):
    def __init__(self):
        self.doccounts = Counter()
        self.classcounts = Counter()
        self.wordcounts = defaultdict(lambda: Counter())
        self.vocab = set()

        self.priors = {}
        self._condprobs = defaultdict(lambda: dict())

    def calculate_probs(self):
        for c in self.doccounts:
            self.priors[c] = (1.0 * self.doccounts[c]) / \
                              sum(self.doccounts.values())

    def get_condprob(self, word, class_):
        if not self._condprobs[word].get(class_):
            num = self.wordcounts[class_].get(word, 0) + 1.0
            denom = len(self.vocab) + 1.0 + \
                    sum(self.wordcounts[class_].values())
            self._condprobs[word][class_] = num / denom

        return self._condprobs[word][class_]

    def classify(self, words):
        if not self.priors:
            self.calculate_probs()

        score = {}

        for c in self.priors:
            score[c] = math.log(self.priors[c])
            for w in words:
                score[c] += math.log(self.get_condprob(w, c))

        return max(score.iteritems(), key=operator.itemgetter(1))[0]

    def add_example(self, klass, words):
        self.doccounts[klass] += 1
        self.vocab.update(words)
        self.classcounts[klass] += len(words)
        self.wordcounts[klass].update(words)


def split_set(s, SIZE):
    a = set(random.sample(s, int(SIZE * len(s))))
    b = s - a

    return a, b


def split_me_not_me(TRAIN_SIZE=0.9):
    train, test = {}, {}

    not_me = SMS.select().where(from_me=False)
    me = SMS.select().where(from_me=True)

    not_me = set(not_me)
    me = set(me)

    train['me'], test['me'] = split_set(me, TRAIN_SIZE)
    train['not_me'], test['not_me'] = split_set(not_me, TRAIN_SIZE)

    return train, test


def recipient_is(name, TRAIN=0.9):
    #: TRAIN = percent of the data to have in training set
    train = {}
    test = {}
    person = Contact.get(name=name)
    recipient = set(SMS.select().where(contact=person).where(from_me=False))
    not_recipient = set(SMS.select().where(contact__ne=person)
                        .where(from_me=False))

    train[person.name], test[person.name] = split_set(recipient, TRAIN)
    train['not_' + person.name], test['not_' + person.name] = \
            split_set(not_recipient, TRAIN)

    return train, test


def people_with_many_texts(n, TRAIN=0.9):
    # TRAIN = percent of data to have in training set
    contacts = peewee.RawQuery(Contact, '''SELECT * from sms, contact
    where from_me=0 and contact.id=contact_id GROUP BY contact_id
    HAVING count(*) >= ?;''', n)

    data = {}
    for c in contacts:
        data[c.name] = set(SMS.select().where(contact=c))

    train = {}
    test = {}

    for c in data:
        train[c], test[c] = split_set(data[c], TRAIN)

    print 'There are %d people with >= %d texts.' % (len(data), n)

    return train, test


def tokenize(words):
    return twokenize.tokenize(words)


def build_classifier(train):
    n = NaiveBayes()
    for klass in train:
        for sms in train[klass]:
            n.add_example(klass, tokenize(sms.text))

    n.calculate_probs()
    # print 'PRIORS ARE', n.priors
    print 'EXPECTED ACCURACY:', max(n.priors.values())
    return n


def run_test(classifier, test):
    correct = 0
    incorrect = 0
    for klass in test:
        for sms in test[klass]:
            classification = classifier.classify(tokenize(sms.text))
            if classification == klass:
                correct += 1
            else:
                incorrect += 1

    accuracy = correct / float(correct + incorrect)
    print 'Classified %d correctly and %d incorrectly for an accuracy of %f.' \
            % (correct, incorrect, accuracy)

    return accuracy


def run_naive_bayes(train, test):
    classifier = build_classifier(train)
    run_test(classifier, test)


def interactive(classifier):
    try:
        while True:
            print 'CLASSIFY YOUR MESSAGE:'
            text = raw_input('enter a text: ')
            print 'result:', classifier.classify(tokenize(text))
            print
    except KeyboardInterrupt:
        database.close()


if __name__ == '__main__':
    database.connect()
    train, test = split_me_not_me(0.9)

    print 'ME AND NOT ME:'
    run_naive_bayes(train, test)

    threshold = 200
    print
    print 'PEOPLE WITH OVER %d TEXTS:' % threshold
    run_naive_bayes(*people_with_many_texts(threshold))
    print

    # train, test = split_me_not_me(1.0)
    # train, test = people_with_many_texts(threshold)
    # classifier = build_classifier(train)
    # interactive(classifier)

    database.close()
