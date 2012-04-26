Google Voice Analysis
=====================

A collection of scripts to parse and analyze exported Google Voice data.

So far it just parses the data and runs a few [Naive Bayes classifiers](http://en.wikipedia.org/wiki/Naive_Bayes_classifier), but
I'm looking to expand.

Usage
-----

0. [Download](https://www.google.com/takeout/?pli=1#custom:voice) and extract your Google Voice data.

1. Install the dependencies with something like `pip install -r requirements.txt`.

2. Copy `settings_example.py` to `settings.py` and configure appropriately.

3. Run `gv_to_db.py` to load everything into a SQLite database.

4. Run `who_from.py` to run a few simple analyzers using Naive Bayes.

Classifiers
---------

- `people_with_many_texts(n)` classifies the texts of people who have sent more than `n` texts.

- `recipient_is(name)` classifies texts into either `name` or `not_name`.

- `split_me_not_me()` classifies texts into either `me` or `not_me` depending on the sender.

Interactive Mode
----------------

1. Get your training and test sets from one of the classifiers.

2. Run `build_classifier(training_set)`.

3. Run `interactive` on your classifier.

4. Enter some messages.

License
-------

MIT/X11 licensed, except for `emoticons.py` and `twokenize.py`.

`emoticons.py` and `twokenize.py` are copyright Brendan O'Connor, Michel Krieger, and David Ahn and licensed under the Apache License 2.0.
