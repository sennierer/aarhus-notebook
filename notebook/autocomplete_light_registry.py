import autocomplete_light
from django.db.models import Q
#from py2neo import neo4j
from .models import *


class publisher_text(autocomplete_light.AutocompleteListBase):

	def choices_for_request(self):
		choices=[]
		q = self.request.GET.get('q','')
		#db = neo4j.GraphDatabaseService()
		#query = neo4j.CypherQuery(db,'MATCH (n:_Institution) WHERE n.name =~ "'+q+'.*" RETURN DISTINCT n.name')
		#for x in query.stream():
		#	choices.append(x[0])
		x = nb_institution.objects.filter(Q(name__icontains=q)|Q(name_en__icontains=q)).exclude(name="UNKNOWN").distinct()
		for xx in x:
			if xx.name_en:
				choices.append(xx.name+'['+xx.name_en+']')
			else:
				choices.append(xx.name)
		return choices



class pers_name_text(autocomplete_light.AutocompleteListBase):

	def choices_for_request(self):
		choices=[]
		q = self.request.GET.get('q','')
		x = nb_people.objects.filter(first_name__icontains=q)
		y = nb_people.objects.filter(last_name__icontains=q)
		for xx in x:
			choices.append(xx.last_name+', '+xx.first_name)
		for yy in y:
			choices.append(yy.last_name+', '+yy.first_name)
		return choices

class termsautocomplete(autocomplete_light.AutocompleteListBase):

	def choices_for_request(self):
		choices=[]
		q = self.request.GET.get('q','')
		q1 = q.split(';')
		if len(q1)>1:

			term = q1.pop()
			q2=';'.join(q1)+';'
		else:
			term=q
			q1=q
			q2=''
		x = nb_term.objects.filter(name__icontains=term)
		for xx in x:
			choices.append(q2+xx.name)
		return choices

class semantic_field(autocomplete_light.AutocompleteListBase):

	def choices_for_request(self):
		choices=[]
		q = self.request.GET.get('q','')
		x = nb_semanticField.objects.filter(name__icontains=q).distinct()
		for xx in x:
			choices.append(xx.name)
		return choices

class term(autocomplete_light.AutocompleteListBase):

	def choices_for_request(self):
		choices=[]
		q = self.request.GET.get('q','')
		x = nb_term.objects.filter(name__icontains=q).distinct()
		for xx in x:
			choices.append(xx.name)
		return choices

class p_place(autocomplete_light.AutocompleteListBase):

	def choices_for_request(self):
		choices = []
		q = self.request.GET.get('q','')
		x = nb_place.objects.filter(place__icontains=q).distinct()
		for xx in x:
			choices.append(xx.place)
		return choices

class pers_first_name(autocomplete_light.AutocompleteListBase):

	def choices_for_request(self):
		choices = []
		q = self.request.GET.get('q','')
		x = nb_people.objects.filter(first_name__icontains=q)
		for xx in x:
			if xx.first_name not in choices:
				choices.append(xx.first_name)
		return choices


class position_text(autocomplete_light.AutocompleteListBase):

	def choices_for_request(self):
		choices = []
		q = self.request.GET.get('q','')
		x = nb2_peopleInstitution.objects.filter(pos_text__icontains=q)
		for xx in x:
			if xx.pos_text not in choices:
				choices.append(xx.pos_text)
		return choices

class profession(autocomplete_light.AutocompleteListBase):

	def choices_for_request(self):
		choices = []
		q = self.request.GET.get('q','')
		x = nb_people.objects.filter(profession__icontains=q)
		for xx in x:
			if xx.profession not in choices:
				choices.append(xx.profession)
		return choices

class pers_citizenship(autocomplete_light.AutocompleteListBase):

	def choices_for_request(self):
		choices = []
		q = self.request.GET.get('q','')
		x = nb_people.objects.filter(citizenship__icontains=q)
		for xx in x:
			if xx.citizenship not in choices:
				choices.append(xx.citizenship)
		return choices



autocomplete_light.register(publisher_text,autocomplete_js_attributes={
	'minimum_characters':3,
	'placeholder': 'Type to get suggestions',
	})

autocomplete_light.register(pers_name_text,autocomplete_js_attributes={
	'minimum_characters':3,
	'placeholder': 'Type to get suggestions',
	})

autocomplete_light.register(termsautocomplete,autocomplete_js_attributes={
	'minimum_characters':3,
	'placeholder': 'Type to get suggestions',
	})

autocomplete_light.register(semantic_field,autocomplete_js_attributes={
	'minimum_characters':3,
	'placeholder': 'Type to get suggestions',
	})

autocomplete_light.register(term,autocomplete_js_attributes={
	'minimum_characters':3,
	'placeholder': 'Type to get suggestions',
	})

autocomplete_light.register(p_place,autocomplete_js_attributes={
	'minimum_characters':3,
	'placeholder': 'Type to get suggestions',
	})

autocomplete_light.register(pers_first_name,autocomplete_js_attributes={
	'minimum_characters':3,
	'placeholder': 'Type to get suggestions',
	})

autocomplete_light.register(position_text,autocomplete_js_attributes={
	'minimum_characters':3,
	'placeholder': 'Type to get suggestions',
	})

autocomplete_light.register(profession,autocomplete_js_attributes={
	'minimum_characters':3,
	'placeholder': 'Type to get suggestions',
	})

autocomplete_light.register(pers_citizenship,autocomplete_js_attributes={
	'minimum_characters':3,
	'placeholder': 'Type to get suggestions',
	})
