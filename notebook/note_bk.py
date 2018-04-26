#!/usr/bin/python
# -*- coding: utf-8 -*-
#from py2neo import neo4j, node
#import nltk
#from nltk.stem import SnowballStemmer
#from nltk.tokenize import word_tokenize, wordpunct_tokenize, sent_tokenize, LineTokenizer
import re
import csv
import urllib
import urllib2
import codecs
import collections
import json
import sys
import os,glob
#import AlchemyAPI
#from goose import Goose
import xml.etree.ElementTree as ET
import time
#from bs4 import BeautifulSoup as BS


db = neo4j.GraphDatabaseService("http://localhost:7474/db/data/")

def add_text_2(t_title,t_pub_date,t_kind,t_keywords,t_file,publisher,authors,**kwargs):
	#Texts are our root nodes. Texts therefore keep everything together. In a first version it wont be possible
	ind_text = db.get_or_create_index(neo4j.Node, "Text")
	text = ind_text.get_or_create("Title",t_title,{"title":t_title,"pub_date":t_pub_date,"kind":t_kind,"file":t_file})
	text.add_labels("_Text")
	
	for x in t_keywords:
		text.add_labels(x)
	
	for z in authors:
		aut=add_person(True,z['name'])
		path = neo4j.Path(aut,"is_author_of",text)
		path.get_or_create(db)

	pub = add_institution(True,publisher)
	path2 = neo4j.Path(pub,"is_publisher_of",text)
	path2.get_or_create(db)

	if 'terms' in kwargs:
		for z in terms:
			term,exist=add_term(True,z)
			if exist == True:
				r = db.create((term,"prel_is_used_in",text))
			else:
				r = db.create((term,"is_used_in",text))

def add_person(prel,name,**kwargs):
	ind_peop = db.get_or_create_index(neo4j.Node, "People")
	res = ind_peop.get_or_create("Name",name,{"name":name})
	res.add_labels("_Person")
	if prel == True:
		res.add_labels("_prelim")
	if prel == False:
			if "_prelim" in res.get_labels():
				res.remove_labels("_prelim")
	return res

def add_institution(prel,name,**kwargs):
	ind_inst = db.get_or_create_index(neo4j.Node, "Institution")
	res = ind_inst.get_or_create("Name",name,{"name":name})
	res.add_labels("_Institution")
	if prel == True:
		res.add_labels("_prelim")
	if prel == False:
			if "//prelim" in res.get_labels():
				res.remove_labels("_prelim")
	return res

def add_argument(prel,argument,**kwargs):
	ind_arg = db.get_or_create_index(neo4j.Node, "Argument")

def add_semantic_field(prel,sem_field,**kwargs):
	ind_sem_field = db.get_or_create_index(neo4j.Node, "Semantic Field")

def add_term(prel,term,**kwargs):
	ind_term = db.get_or_create_index(neo4j.Node, "Term")

	res = ind_term.create_if_none("Term",term,{"term":term})
	if res:
		res.add_labels("_Term")
		if prel == True:
			res.add_labels("_prelim")
		
		return res,False
	else:
		res=ind_term.get_or_create("Term",term,{"term":term})
		if prel == False:
			if "_prelim" in res.get_labels():
				res.remove_labels("_prelim")
		return res,True

#def query_database():

