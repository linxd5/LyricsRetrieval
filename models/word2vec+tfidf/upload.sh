#!/bin/bash

cd ~/Desktop/db_project

git pull

git add *

git commit -m "For change log, please check word2vec+TFIDF.md"

git push origin master

cd ~/Desktop/db_project/models/word2vec+tfidf
