#!/bin/bash

# Download required NLTK data
python -m nltk.downloader vader_lexicon
python -m nltk.downloader punkt
python -m nltk.downloader averaged_perceptron_tagger 