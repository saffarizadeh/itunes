In this research project we extract mobile applications' information and their user reviews from iTunes and then using document similarity methods measure the contribution of users' feedback to app success.

Requirements
-----------------------
General
-----------------------
sudo apt-get install python-pip python-dev

-----------------------
Numpy, Scipy, Pandas, and matplotlib
-----------------------
sudo apt-get install build-essential gfortran libatlas-base-dev
sudo pip install --upgrade pip
sudo pip install numpy
sudo pip install scipy
sudo pip install matplotlib
sudo pip install pandas

-----------------------
Django
-----------------------
sudo pip install Django==1.9.7

-----------------------
PostgreSQL adapter for the Python
-----------------------
sudo pip install psycopg2

-----------------------
Python driver for MongoDB
-----------------------
sudo pip3 install pymongo

-----------------------
lxml
-----------------------
sudo pip install lxml

-----------------------
NLTK
-----------------------
sudo pip install nltk

import nltk
nltk.download()

-----------------------
gensim
-----------------------
sudo pip install --upgrade gensim

-----------------------
sklearn
-----------------------
sudo pip install -U scikit-learn

-----------------------
XlsxWriter
-----------------------
sudo pip install XlsxWriter

-----------------------


Optional
-----------------------
PiCloud
-----------------------
sudo pip install cloud

-----------------------
TextBlob
-----------------------
sudo pip install -U textblob

-----------------------
TensorFlow and Six
-----------------------
https://www.tensorflow.org/versions/r0.9/get_started/os_setup.html

-----------------------
Java JRE
-----------------------
http://askubuntu.com/questions/521145/how-to-install-oracle-java-on-ubuntu-14-04
sudo apt-add-repository ppa:webupd8team/java
sudo apt-get update
sudo apt-get install oracle-java8-installer

-----------------------
stanford parser (2015-04-20, which is compatible with NLTK)
-----------------------
http://nlp.stanford.edu/software/stanford-parser-full-2015-04-20.zip

path = '/home/kaminem64/stanford'
os.environ['CLASSPATH'] = '%s/stanford-postagger-full-2015-04-20/stanford-postagger.jar:%s/stanford-ner-2015-04-20/stanford-ner.jar:%s/stanford-parser-full-2015-04-20/stanford-parser.jar:%s/stanford-parser-full-2015-04-20/stanford-parser-3.6.0-models.jar' %(path, path, path, path)
os.environ['STANFORD_MODELS'] = '%s/stanford-postagger-full-2015-04-20/models:%s/stanford-ner-2015-04-20/classifiers' %(path, path)

-----------------------
