#!/usr/bin/env python
# -*- coding: utf-8 -*-

import lxml
from lxml import etree
import time
from notebook.models import nb_texts,nb2_peopleTexts,nb_people,nb2_institutionTexts,nb_institution,nb_place
from time import mktime
from datetime import datetime
import re
import requests


def parse_citations(cit_1,sec_source=False):
	headers = {'accept': 'text/xml'}
	citation = {'citation[]':cit_1}
	r = requests.post('http://freecite.library.brown.edu/citations/create',params=citation,headers=headers)
	tree = etree.fromstring(r.text)
	res_pk = []
	for x in tree.iterfind('.//citation'):
		if x.find('title') != None:
			pubdate=None
			volume=''
			issue=''
			pages=''
			if x.find('date') != None:
				pubdate = x.find('date').text+'-01-01'
				print(pubdate)
				pubdate = datetime.fromtimestamp(mktime(time.strptime(pubdate,'%Y-%m-%d')))
				print(pubdate)
			if x.find('volume') != None:
				volume = x.find('volume').text
			if x.find('issue') != None:
				issue = x.find('issue').text
			if x.find('pages') != None:
				pages = x.find('pages').text.replace('--','-')
			if x.find('location') != None:
				p_place,created=nb_place.objects.get_or_create(place=x.find('location').text)
				if sec_source:
					text,created = nb_texts.objects.get_or_create(title=x.find('title').text,pubdate=pubdate,volume=volume,pages=pages,language='en',p_place=p_place,issue=issue,defaults={'sec_source':True,'update':True})
				else:
					text,created = nb_texts.objects.get_or_create(title=x.find('title').text,pubdate=pubdate,volume=volume,pages=pages,language='en',p_place=p_place,issue=issue,defaults={'sec_source':False,'update':True})
				#text.save()
			else:
				text,created = nb_texts.objects.get_or_create(title=x.find('title').text,pubdate=pubdate,volume=volume,pages=pages,language='en',issue=issue,defaults={'sec_source':True,'update':True})
				#text.save()
			if x.find('publisher') != None:
				pub,created=nb_institution.objects.get_or_create(name=x.find('publisher').text,defaults={'kind':'pub','update':True})
				t,created=nb2_institutionTexts.objects.get_or_create(texts=text,institution=pub,kind='pub')
				#t.save()
			if x.find('journal') != None:
				pub,created=nb_institution.objects.get_or_create(name=x.find('journal').text,defaults={'kind':'pub'})
				t,created=nb2_institutionTexts.objects.get_or_create(texts=text,institution=pub,kind='pub')
				#t.save()

			if x.find('authors') != None:
				authors=[]
				for z in x.iterfind('./authors/author'):
					name_1 = z.text.split(' ')
					try:
						last_name = name_1.pop()
						first_name = ' '.join(name_1)
					except:
						last_name = name_1
						first_name = ''
					aut,created = nb_people.objects.get_or_create(last_name=last_name,first_name=first_name,defaults={'update':True})
					authors.append(aut)
			for i in authors:
				o,created = nb2_peopleTexts.objects.get_or_create(kind='aut',texts=text,people=i)
				#o.save()
			res_pk.append(text)
	return res_pk

