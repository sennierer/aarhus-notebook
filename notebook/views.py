from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.forms.formsets import formset_factory
from django.forms.forms import NON_FIELD_ERRORS
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login
from django.db.models import Q,Count
from django.core.exceptions import ValidationError
from django.forms.util import ErrorList
from django.db.utils import IntegrityError
from django.core.mail import send_mail
#from note_bk import add_text_2
#from note_bk import add_person
#from note_bk import add_institution
#from note_bk import add_term
from notebook.forms import form_add_text
#from notebook.forms import form_keyw_text
from notebook.forms import form_add_pers_text
from notebook.forms import FormSet1Helper,FormSet2Helper
from notebook.forms import form_upload_text
from notebook.forms import form_user_login
from notebook.forms import form_add_sem_field
from notebook.forms import form_add_term, form_edit_person, form_pers_add_career, form_pers_add_peer, form_edit_institution, form_translate_terms,form_add_report,form_search_crossrefs,form_explain_edit,form_inst_add_emp
from notebook.models import *
import random
import json
import glob
import subprocess
from kitchen.text.converters import to_unicode, to_bytes
import re
import os
import requests
from helper_scripts.parse_xml_2 import parse_citations
import bibtexparser
import StringIO
import math
from unidecode import unidecode
from django.core.mail import send_mail
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


def send_mails_follow(edit):
	email_text = ''
	if edit.c_people:
		email_text = '<p>The person entry <a href="http://aarhus.schloegl.net/notebook/people/show/%s">%s</a> you are following has been altered by <a href="mailto:%s?subject=Aarhus notebook edit request">%s</a>.<p>She/He has given the following reasons: %s</p>' % (edit.c_people.pk,unicode(edit.c_people),edit.user_name.email,edit.user_name.username,edit.explanation)
		email_text_plain = 'The person entry %s (http://aarhus.schloegl.net/notebook/people/show/%s) you are following has been altered by %s (%s).\n She/He has given the following reasons: %s' % (unicode(edit.c_people),edit.c_people.pk,edit.user_name.username,edit.user_name.email,edit.explanation)
		t = nb4_follow.objects.filter(c_people=edit.c_people)

	elif edit.c_institution:
		email_text = '<p>The institution entry <a href="http://aarhus.schloegl.net/notebook/institutions/show/%s">%s</a> you are following has been altered by <a href="mailto:%s?subject=Aarhus notebook edit request">%s</a>.<p>She/He has given the following reasons: %s</p>' % (edit.c_institution.pk,unicode(edit.c_institution),edit.user_name.email,edit.user_name.username,edit.explanation)
		email_text_plain = 'The institution entry %s (http://aarhus.schloegl.net/notebook/institutions/show/%s) you are following has been altered by %s (%s).\n She/He has given the following reasons: %s' % (unicode(edit.c_institution),edit.c_institution.pk,edit.user_name.username,edit.user_name.email,edit.explanation)
		t = nb4_follow.objects.filter(c_institution=edit.c_institution)

	elif edit.c_text:
		email_text = '<p>The text entry <a href="http://aarhus.schloegl.net/notebook/texts/show/%s">%s</a> you are following has been altered by <a href="mailto:%s?subject=Aarhus notebook edit request">%s</a>.<p>She/He has given the following reasons: %s</p>' % (edit.c_text.pk,unicode(edit.c_text),edit.user_name.email,edit.user_name.username,edit.explanation)
		email_text_plain = 'The text entry %s (http://aarhus.schloegl.net/notebook/texts/show/%s) you are following has been altered by %s (%s).\n She/He has given the following reasons: %s' % (unicode(edit.c_text),edit.c_text.pk,edit.user_name.username,edit.user_name.email,edit.explanation)
		t = nb4_follow.objects.filter(c_text=edit.c_text)

	email_addr = []
	for x in t:
		if edit.user_name != x.user_name:
			email_addr.append(x.user_name.email)
	send_mail('Aarhus notebook edit note - %s'%datetime.now().strftime("%d.%m.%Y %H:%M"), email_text_plain, 'aarhus@schloegl.net',email_addr, fail_silently=False, html_message=email_text)




# Create your views here.
@login_required(login_url='/login/')
def add_text(request,id_text=False):
	BASE_DIR = os.path.dirname(os.path.dirname(__file__))
	errors = []
	pers_formset = formset_factory(form_add_pers_text)
	#keyw_formset = formset_factory(form_keyw_text)
	if request.method == 'POST':
		form4 = form_explain_edit(request.POST)
		form = form_add_text(request.POST, request.FILES)
		formset1 = pers_formset(request.POST, request.FILES, prefix='pers')
		#formset2 = keyw_formset(request.POST, request.FILES, prefix='keyw')
		if form.is_valid() and formset1.is_valid() and form4.is_valid():
		#if form.is_valid():
			cd = form.cleaned_data
			cd_fs1 = formset1.cleaned_data
			#cd_fs2 = formset2.cleaned_data
			cd_keyw = []
			cd_pers = []
			file_1 = False
			if id_text:
				text = nb_texts.objects.get(pk=id_text)
				text.title = cd['title']
				text.title_en = cd['title_en']
				text.sub_title = cd['sub_title']
				text.volume = cd['volume']
				text.issue = cd['issue']
				text.pubdate = cd['pub_date']
				text.abstract = cd['info']
				text.language = cd['language']
				text.file_ocr = cd['file_ocr']
				text.sec_source = cd['sec_source']
				text.pages = cd['pages']
				text.kind = cd['kind']
				text.recipient = cd['recipient']
				text.update = False
				text.save()
				nb2_peopleTexts.objects.filter(texts=text).exclude(kind='sec').delete()
				nb2_institutionTexts.objects.filter(texts=text).delete()

			else:
				text = nb_texts(title=cd['title'],title_en=cd['title_en'],sub_title=cd['sub_title'],volume=cd['volume'],issue=cd['issue'],pubdate=cd['pub_date'],abstract=cd['info'],language=cd['language'],file_ocr=cd['file_ocr'],sec_source=cd['sec_source'],pages=cd['pages'],kind=cd['kind'],recipient=cd['recipient'],update=False)
				text.save()
			if cd['p_place']:
				j,created = nb_place.objects.get_or_create(place=cd['p_place'])
				j.save()
				text.p_place = j
				text.save()
			if 'txt_file' in request.FILES:
				dd = request.FILES['txt_file'].name.split('.')
				file_1 = nb_textfile(docfile = request.FILES['txt_file'],file_type=dd[-1])
				file_1.save()
				text.txt_file=file_1
				text.save()
				#filen = len(glob.glob('/Users/sennierer/CloudStation/Aarhus/Code/aarhus/Media/documents/txts'))+1
				filentxt = BASE_DIR+'/Media/documents/txt/'+str(text.pk)+'.txt'

				filehtml = BASE_DIR+'/Media/documents/html/'+str(text.pk)+'.html'
				filentif = BASE_DIR+'/Media/documents/tif/'+str(text.pk)+'.png'
				filenpdf = BASE_DIR+'/Media/'+file_1.docfile.name
				if dd[-1].lower() == 'pdf' and cd['file_ocr']==True:
					try:
						#subprocess.call(['pdf2txt.py','-o',filehtml,to_bytes(filenpdf)])
						subprocess.call(['pdf2txt.py','-o',filentxt,'-t','text',to_bytes(filenpdf)])
						file_1.saved = True
						file_1.save()
					except:
						file_1.saved = False
						file_1.message = 'Text extraction failed.'
						file_1.save()
				elif dd[-1].lower() == 'pdf' and cd['file_ocr']==False:
					try:
						subprocess.call(['convert',filenpdf,filentif])
						if cd['language'] == 'deu':
							subprocess.call(['tesseract',filentif,filentxt,'-l deu'])
						else:
							subprocess.call(['tesseract',filentif,filentxt])
						file_1.saved = True
						file_1.message = 'OCR failed.'
						file_1.save()
					except:
						file_1.saved = False
						file_1.save()
			if cd['publisher']:
				m = re.search(r'^([^\[]+)',cd['publisher'])
				mm = re.search(r'\[([^\]]+)\]',cd['publisher'])
				if mm:
					inst,created_pub = nb_institution.objects.get_or_create(name=m.group(1).strip(),name_en=mm.group(1).strip())
					#inst.name_en = mm.group(1).strip()
				else:
					inst,created_pub = nb_institution.objects.get_or_create(name=m.group(1).strip())
				if created_pub:
					inst.update = True
				inst.save()
				#publisher,created_pub = nb_institution.objects.get_or_create(name=cd['publisher'],update=True)
				con_text_inst=nb2_institutionTexts(institution=inst,texts=text,kind=nb2_institutionTexts.PUB)
				con_text_inst.save()

			for x in cd_fs1:
				try:
					nn = x['name'].split(',')
					pers,created_pers = nb_people.objects.get_or_create(first_name=nn[-1].strip(),last_name=nn[0].strip())
					if created_pers:
						pers.update=True
						pers.save()
					con_aut_text=nb2_peopleTexts(people=pers,texts=text,kind=x['kind'])
					con_aut_text.save()
				except:
					pass
				#cd_pers.append(x['name'])
			if len(cd['keywords'])>0:
				for z in cd['keywords'].split(';'):
					tt,created_tt = nb_term.objects.get_or_create(name=z)
					tt.translate = False
					tt.update = False
					tt.save()
					con_term_text = nb3_termTextSemfield(term=tt,kind=nb3_termTextSemfield.KEY)
					con_term_text.save()
					con_term_text.texts.add(text)
				#cd_keyw.append(z['keyword'])
			#add_text_2(cd['title'],cd['pub_date'],cd['kind'],cd_keyw,cd['publisher'],cd_pers,'test','test2')
			edit = form4.save(commit=False)
			edit.user_name = request.user
			edit.c_text = text
			edit.save()
			send_mails_follow(edit)
			return render(request,'message.html',{'message':'Saved!','redirect':'/notebook/texts/show/'+str(text.pk)})
		else:
			helper = FormSet1Helper()
			return render_to_response('save_text_crispy.html',{'form':form,'form4':form4,'formset1':formset1,'helper':helper}, context_instance=RequestContext(request))
	else:
		if id_text:
			text4 = nb_texts.objects.get(pk=id_text)
			if text4.p_place:
				p_place = text4.p_place.place
			else:
				p_place = None
			try:
				ll=nb2_institutionTexts.objects.filter(texts=text4,kind=nb2_institutionTexts.PUB)
				if ll[0].institution.name_en:
					publisher = ll[0].institution.name+'['+ll[0].institution.name_en+']'
				else:
					publisher = ll[0].institution.name
			except:
				publisher = None
			form = form_add_text(initial={'title':text4.title,'title_en':text4.title_en,'sub_title':text4.sub_title,'volume':text4.volume,'issue':text4.issue,'pub_date':text4.pubdate,'info':text4.abstract,'language':text4.language,'p_place':p_place,'publisher':publisher,'sec_source':text4.sec_source,'pages':text4.pages,'kind':text4.kind,'recipient':text4.recipient})
			initial = []
			for x in nb2_peopleTexts.objects.filter(texts=text4).exclude(kind='sec'):
				initial.append({'name':x.people.last_name+', '+x.people.first_name,'kind':x.kind})
			formset1 = pers_formset(initial=initial,prefix='pers')
		else:
			form = form_add_text()
			formset1 = pers_formset(prefix='pers')
		#formset2 = keyw_formset(prefix='keyw')
		helper = FormSet1Helper()
		form4 = form_explain_edit()
		return render_to_response('save_text_crispy.html',{'form':form,'form4':form4,'formset1':formset1,'helper':helper},context_instance=RequestContext(request))

@login_required(login_url='/login/')
def add_text_crispy(request):
	errors = []
	pers_formset = formset_factory(form_add_pers_text)
	if request.method == 'POST':
		form = form_add_text(request.POST, request.FILES)
		formset1 = pers_formset(request.POST, request.FILES, prefix='pers')
		if form.is_valid() and formset1.is_valid():
		#if form.is_valid():
			cd = form.cleaned_data
			cd_fs1=formset1.cleaned_data
			file_1 = textfile(docfile = request.FILES['txt_file'],title = cd['title'],pub_date=cd['pub_date'])
			file_1.save()
			add_text_2(cd['title'],cd['pub_date'],cd['kind'],cd['keywords'].split(';'),textfile.objects.get(title__exact=cd['title']).docfile.name,cd['publisher'],cd_fs1)
			return HttpResponse("Funkt: %s  //  %s"%(cd,cd_fs1))
		else:
			return HttpResponse("Fehler")

	else:
		form = form_add_text()
		formset1 = pers_formset(prefix='pers')
		helper = FormSet1Helper()
		return render(request,'save_text_crispy.html',{'form':form,'formset1':formset1,'helper':helper})

#@login_required(login_url='/login/')
def user_login(request):
	errors = []
	if request.method == 'POST':
		form = form_user_login(request.POST)
		if form.is_valid():
			cd = form.cleaned_data
			user = authenticate(username=cd['username'],password=cd['password'])
			if user is not None:
				if user.is_active:
					login(request, user)
					#return HttpResponse('logged in %s'%user)
					return HttpResponseRedirect(request.GET.get('next','/login/'))
				else:
					return HttpResponse('not active.')
			else:
				return HttpResponse('user does not exist')
	else:
		form = form_user_login()
		return render(request,'user_login.html',{'form':form})


@login_required(login_url='/login/')
def upload_text(request):
	errors=[]
	if request.method == 'POST':
		form = form_upload_text(request.POST, request.FILES)
		if form.is_valid():
			cd = form.cleaned_data
			file_1 = textfile(docfile = request.FILES['txt_file'],info = cd['info'],pub_date=cd['pub_date'])
			file_1.save()
		else:
			return HttpResponse("Fehler")
	else:
		form = form_upload_text()
		return render(request,'upload_file.html',{'form':form})

@login_required(login_url='/login/')
def highl(request,txt_id):
	text2 = nb_texts.objects.get(pk=int(txt_id))
	text = text2.pk
	if text2.txt_file:
		try:
			txt = open(BASE_DIR +'/Media/documents/txt/'+str(text)+'.txt','r').read()
			txt2 = to_unicode(txt)
			txt2 = txt2.replace(u'\u003C','')
			txt2 = txt2.replace(u'\u003E','')
			txt2 = txt2.replace('\n\n','<br />')
			txt2 = txt2.replace('-\n','')
			txt2 = txt2.replace('\n',' ')
			txt2 = re.sub(r'\s\s+',' ',txt2)
		except:
			txt2 = 'PDF'
	else:
		txt2 = 'There is no full-text available.'
	if request.method == 'POST':
		form = form_add_sem_field(request.POST)
		if form.is_valid():
			cd = form.cleaned_data
			sem_field,created = nb_semanticField.objects.get_or_create(name=cd['name'])
			text2.sem_fields.add(sem_field)
			text2.save()

	form = form_add_sem_field()
	form2 = form_add_term()
	sems = text2.sem_fields.all()
	terms_3=dict()
	count2=0
	for tt in sems:
		tt.terms_in = nb3_termTextSemfield.objects.filter(sem_fields=tt,texts=text,kind=nb3_termTextSemfield.TER)
		#terms_text = nb2_termTexts.objects.filter(text=text2)
		tt.terms_extra = nb3_termTextSemfield.objects.filter(sem_fields=tt,kind=nb3_termTextSemfield.TER).exclude(texts=text)



		#terms_3[tt.id]=terms
		if (txt2 != 'There is no full-text available.') and (txt2!='PDF'):
			for zz in tt.terms_in:
				count2+=1
				txt2=txt2.replace(zz.term.name,'<span class="hlSf_'+str(tt.pk)+' hlID_'+str(zz.term.pk)+' hlT_term highl_word hl_'+str(count2)+'">'+zz.term.name+'</span>')
	if text2.txt_file:
		pdf_2 = text2.txt_file.docfile
	else:
		pdf_2 = None
	return render(request, 'highlight.html',{'form':form,'txt':to_bytes(txt2),'sems':sems,'form2':form2,'id_text':str(text),'terms_3':terms_3,'pdf':pdf_2})

@login_required(login_url='/login/')
def highl_ajax(request):
	term2 = request.GET.get('term')
	save = request.GET.get('save')
	text2 = request.GET.get('text')
	test1=[]
	if save == 'institution':
		term,created = nb_institution.objects.get_or_create(name=term2.strip())
		if created:
			term.update=True
			term.save()
		test1.append(term2)
		test1.append(save)
		test1.append(text2)
		test1.append(term.pk)

	elif save == 'delete':
		term_id = request.GET.get('term_id')
		term = nb_term.objects.get(pk=int(term_id))
		text = nb_texts.objects.get(pk=int(text2))
		if len(nb3_termTextSemfield.objects.get(term=term).texts.all())>1:
			nb3_termTextSemfield.objects.get(term=term).texts.remove(text)
		elif len(nb3_termTextSemfield.objects.get(term=term).texts.all())==1:
			nb3_termTextSemfield.objects.filter(texts=text,term=term).delete()
			term.delete()
		test1.append(term2)
		test1.append(save)
		test1.append(text2)
		test1.append(term.pk)
	#elif save == 'person':

	else:
		term,created = nb_term.objects.get_or_create(name=term2)
		#if save == 'institution':
		#	pass
		#elif save == 'person':
		#	pass
		#else:
		sem_field = nb_semanticField.objects.get(pk=int(save))
		text = nb_texts.objects.get(pk=int(text2))
		if text.language != 'en' and created == True:
			term.translate = True
			term.update = True
			term.save()
		elif text.language == 'en' and created == True:
			term.translate = False
			term.update = False
			term.save()
		sem_field.terms.add(term)
		sem_field.save()
		conTermText,created = nb3_termTextSemfield.objects.get_or_create(term=term,kind=nb3_termTextSemfield.TER)
		conTermText.save()
		conTermText.texts.add(text)
		conTermText.sem_fields.add(sem_field)
		#return HttpResponseRedirect('/notebook/texts/highlight/')
		#return HttpResponse('success', content_type='application/json')

		test1.append(term2)
		test1.append(save)
		test1.append(text2)
		test1.append(term.pk)
		test1.append(sem_field.pk)
	return HttpResponse(json.dumps(test1), content_type='application/json')


@login_required(login_url='/login/')
def add_term(request):
	if request.method=='POST':
		form = form_add_term(request.POST)
		if form.is_valid():
			cd = form.cleaned_data
			term,created = nb_term.objects.get_or_create(name=cd['name'])
			sem_field = nb_semanticField.objects.get(pk=int(request.POST['id_sem_field']))
			text = nb_texts.objects.get(pk=int(request.POST['id_text']))
			if text.language != 'en' and created == True:
				term.translate = True
				term.update = True
				term.save()
			elif text.language == 'en' and created == True:
				term.translate = False
				term.update = False
				term.save()
			sem_field.terms.add(term)
			sem_field.save()
			conTermText,created = nb3_termTextSemfield.objects.get_or_create(term=term,kind=nb3_termTextSemfield.TER)
			conTermText.save()
			conTermText.texts.add(text)
			conTermText.sem_fields.add(sem_field)

			return HttpResponseRedirect('/notebook/texts/highlight/'+request.POST['id_text'])

def index(request):
	return render(request,'index.html')

@login_required(login_url='/login/')
def show_text(request,id_text):
	text = nb_texts.objects.get(pk=id_text)
	authors = nb_people.objects.filter(nb2_peopletexts__texts=text,nb2_peopletexts__kind='aut')
	publ_peop = nb_people.objects.filter(nb2_peopletexts__texts=text,nb2_peopletexts__kind='pub')
	editors = nb_people.objects.filter(nb2_peopletexts__texts=text,nb2_peopletexts__kind='edt')
	keywords = nb3_termTextSemfield.objects.filter(texts=text,kind=nb3_termTextSemfield.KEY)
	publisher = nb2_institutionTexts.objects.filter(texts=text,kind=nb2_institutionTexts.PUB)
	follow = nb4_follow.objects.filter(c_text=text,user_name=request.user).exists()
	return render(request,'show_text_entry.html',{'text':text,'authors':authors,'keywords':keywords,'publisher':publisher,'publ_peop':publ_peop,'editors':editors,'follow':follow})

@login_required(login_url='/login/')
def list_texts(request,secSource=False,update=False):
	if secSource:
		if update:
			texts = nb_texts.objects.filter(sec_source=True,update=True)
			title = 'List of secondary sources that need update'
		else:
			texts = nb_texts.objects.filter(sec_source=True)
			title = 'List of secondary sources'
	else:
		texts = nb_texts.objects.filter(sec_source=False)
		title = 'List of texts'
	for ind,x in enumerate(texts):
		peop1 = nb2_peopleTexts.objects.filter(texts=x.pk,kind='aut')
		peop2 = []
		for z in peop1:
			peop2.append(z.people)
		x.authors=peop2
	return render(request,'list_texts.html',{'texts':texts,'title':title})

@login_required(login_url='/login/')
def list_people(request,review=False):
	if review:
		people = nb_people.objects.filter(update=True)
	else:
		people = nb_people.objects.all()
	return render(request,'list_people.html',{'people':people})

@login_required(login_url='/login/')
def choose_people(request):
	people = nb_people.objects.all()
	return render(request,'choose_people.html',{'people':people})

@login_required(login_url='/login/')
def show_people(request,id_people):
	person = nb_people.objects.get(pk=id_people)
	articles = nb2_peopleTexts.objects.filter(people=person).exclude(kind='sec')
	institutions = nb2_peopleInstitution.objects.filter(people=person)
	people = nb2_peoplePeople.objects.filter(person1=person)
	sec_sources_2 = nb2_peopleTexts.objects.filter(people=person,kind='sec')
	sec_sources = []
	for x in sec_sources_2:
		aut = []
		z = nb2_peopleTexts.objects.filter(texts=x.texts,kind='aut')
		for zz in z:
			aut.append(zz.people)
		sec_sources.append({'text':x.texts,'authors':aut})
	#nodes_pre = []
	#nodes_pre2 =[]
	#connections_pre = []
	#nodes_pre.append({'id':'1','label':to_bytes(person.last_name+', '+person.first_name),'x':random.randint(1,30),'y':random.randint(1,30),'size':1})
	#nodes_pre2.append(person.pk)
	#for x in articles:
	#	for z in nb2_peopleTexts.objects.filter(texts=x.texts):
	#		if z.people.pk not in nodes_pre2:
	#			nodes_pre2.append(z.people.pk)
	#			nodes_pre.append({'id':str(len(nodes_pre)+1),'label':to_bytes(z.people.last_name+', '+z.people.first_name),'x':random.randint(1,30),'y':random.randint(1,30),'size':1})
	#			connections_pre.append({'id':'c'+str(len(connections_pre)+1),'source':'1','target':str(len(nodes_pre))})
	#graph = {'nodes':nodes_pre,'edges':connections_pre}
	#graph_test = {'nodes':[{'id':'1','label':'test1','x':1,'y':2,'size':1},{'id':'2','label':'test2','x':3,'y':5,'size':1},{'id':'3','label':'test4','x':7,'y':10,'size':1}],'edges':[{'id':'e1','source':'1','target':'2'},{'id':'e2','source':'1','target':'3'}]}
	follow = nb4_follow.objects.filter(c_people=person,user_name=request.user).exists()
	return render(request,'show_person_entry.html',{'person':person,'articles':articles,'institutions':institutions,'people':people,'sec_sources':sec_sources,'follow':follow})

@login_required(login_url='/login/')
def people_net_ajax(request):
	if request.POST.has_key('client_response'):
		x = request.POST['client_response']
		person = nb_people.objects.get(pk=x)
		articles = nb2_peopleTexts.objects.filter(people=x).exclude(kind='sec')
		nodes_pre = []
		nodes_pre2 =[]
		connections_pre = []
		nodes_pre.append({'id':'1','label':to_bytes(person.last_name+', '+person.first_name),'x':random.randint(1,30),'y':random.randint(1,30),'size':1})
		nodes_pre2.append(person.pk)
		for x in articles:
			for z in nb2_peopleTexts.objects.filter(texts=x.texts):
				if z.people.pk not in nodes_pre2:
					nodes_pre2.append(z.people.pk)
					nodes_pre.append({'id':str(len(nodes_pre)+1),'label':to_bytes(z.people.last_name+', '+z.people.first_name),'x':random.randint(1,30),'y':random.randint(1,30),'size':1})
					connections_pre.append({'id':'c'+str(len(connections_pre)+1),'source':'1','target':str(len(nodes_pre))})
		graph = {'nodes':nodes_pre,'edges':connections_pre}
		graph = json.dumps(graph)
		return HttpResponse(graph,content_type='application/javascript')

@login_required(login_url='/login/')
def analysis_class_ajax(request):
	if request.method == 'POST':
		d_checked = request.POST['checked']
		d_id = request.POST['pk_id'].split('_')[1]
		d_name = request.POST['analysis_name']
		d_type = request.POST['analysis_type']
		if len(d_name)>0:
			if d_type == 'person':
				pers = nb_people.objects.get(pk=d_id)
				nb4,created = nb4_analysisElement.objects.get_or_create(name=d_name,user_name=request.user)
				if d_checked == 'true':
					nb4.c_people.add(pers)
				else:
					nb4.c_people.remove(pers)
				mes = json.dumps({'mes':1,'pk':request.POST['pk_id']})
				return HttpResponse(mes,content_type='application/javascript')
		else:
			mes = json.dumps({'mes':2,'pk':request.POST['pk_id']})
			return HttpResponse(mes,content_type='application/javascript')

@login_required(login_url='/login/')
def analysis_networks_page(request):
	nb4 = nb4_analysisElement.objects.filter(user_name=request.user)
	return render(request,'analysis_graph.html',{'nb4':nb4})

@login_required(login_url='/login/')
def analysis_networks_ajax(request):
	if request.method == 'POST':
		co_inst = '#569'
		d_network = request.POST['network']
		if len(d_network)>0:
			nb4 = nb4_analysisElement.objects.get(name=d_network,user_name=request.user)
			nodes=[]
			edges=[]
			if nb4.c_people.all().count()>0:
				nodes_id = []
				for x in nb4.c_people.all():
					nodes_id.append(x.pk)
					nodes.append({'id':str(x.pk),'x':random.randint(1,30),'y':random.randint(1,30),'label':to_unicode(x.last_name+', '+x.first_name),'color':co_inst})
				for x in nodes_id:
					pers = nb_people.objects.get(pk=x)
					con = nb2_peoplePeople.objects.filter(person1=pers)
					for z in con:
						if z.person2.pk in nodes_id:
							edges.append({'id':'e'+str(len(edges)+1),'source':str(z.person1.pk),'target':str(z.person2.pk),'color':'#B2B2B2'})
					t1 = nb2_peopleTexts.objects.filter(people=pers)
					for x in t1:
						text = nb2_peopleTexts.objects.filter(texts=x.texts)
						for xx in text:
							if (xx.people.pk != pers.pk) and (xx.people.pk in nodes_id):
								edges.append({'id':'e'+str(len(edges)+1),'source':str(pers.pk),'target':str(xx.people.pk),'color':'#5eff17'})
			graph = json.dumps({'mes':True,'graph':{'nodes':nodes,'edges':edges}})
			return HttpResponse(graph,content_type='application/javascript')
		else:
			mes = json.dumps({'mes':False})
			return HttpResponse(mes,content_type='application/javascript')

@login_required(login_url='/login/')
def analysis_name_ajax(request):
	if request.method == 'POST':
		d_name = request.POST['name']
		d_type = request.POST['analysis_type']
		nb4 = nb4_analysisElement.objects.filter(name=d_name,user_name=request.user)
		if nb4.count() > 0:
			if d_type == 'person':
				res = []
				for x in nb4:
					for z in x.c_people.all():
						res.append(z.pk)
				res2 = json.dumps({'test':True,'res':res})
				return HttpResponse(res2,content_type='application/javascript')
		else:
			res2 = json.dumps({'test':False})
			return HttpResponse(res2,content_type='application/javascript')



@login_required(login_url='/login/')
def list_institutions(request,review=False):
	if review:
		inst = nb_institution.objects.filter(update=True).exclude(name="UNKNOWN")
	else:
		inst = nb_institution.objects.all().exclude(name="UNKNOWN")
	return render(request, 'list_institutions.html',{'institutions':inst})

@login_required(login_url='/login/')
def show_institution(request,id_institution):
	inst = nb_institution.objects.get(pk=id_institution)
	peop = nb2_peopleInstitution.objects.filter(institution=inst)
	follow = nb4_follow.objects.filter(c_institution=inst,user_name=request.user).exists()
	return render(request,'show_institution_entry.html',{'institution':inst,'people':peop,'follow':follow})

@login_required(login_url='/login/')
def edit_person(request,id_people=False):
	errors = []
	career_formset = formset_factory(form_pers_add_career)

	peers_formset = formset_factory(form_pers_add_peer)


	if request.method == 'POST':
		form4 = form_explain_edit(request.POST)
		form = form_edit_person(request.POST)
		formset1 = career_formset(request.POST,request.FILES, prefix='car')
		formset2 = peers_formset(request.POST,request.FILES, prefix='peer')
		if form.is_valid() and formset1.is_valid() and formset2.is_valid() and form4.is_valid():
		#if form.is_valid():
			cd = form.cleaned_data
			cd_fs1 = formset1.cleaned_data
			cd_fs2 = formset2.cleaned_data
			if id_people:
				sec_sources_raw_old = nb_people.objects.get(pk=id_people).sec_sources_raw
				peop = nb_people.objects.filter(pk=id_people).update(first_name=cd['first_name'],last_name=cd['last_name'],url=cd['url'],twitter=cd['twitter'],citizenship=cd['citizenship'],birth=cd['birth'],death=cd['death'],profession=cd['profession'],sec_sources_raw=cd['f_sec_source'],update=False)
				peop = nb_people.objects.get(pk=id_people)
				nb2_peopleInstitution.objects.filter(people=peop).delete()
				nb2_peoplePeople.objects.filter(person1=peop).delete()
			else:
				try:
					peop = nb_people(first_name=cd['first_name'],last_name=cd['last_name'],url=cd['url'],twitter=cd['twitter'],citizenship=cd['citizenship'],birth=cd['birth'],death=cd['death'],profession=cd['profession'],sec_sources_raw=cd['f_sec_source'],update=False)
					peop.save()
				except IntegrityError:
				    # The form passed validation so it has no errors.
				    # Use the `setdefault` function just in case.
					errors = ErrorList()
					errors = form._errors.setdefault(NON_FIELD_ERRORS, errors)
					errors.append('Entry already exists. Use an index number to make the entry unique (e.g. "Blair1").')
					return render_to_response('edit_person.html',{'formset1':formset1,'formset2':formset2,'helper':FormSet1Helper,'errors1':formset1.errors,'errors2':formset2.errors,'errors':errors,'form':form}, context_instance=RequestContext(request))
			for x in cd_fs1:
				if len(x['inst'])>0:
					m = re.search(r'^([^\[]+)',x['inst'])
					mm = re.search(r'\[([^\]]+)\]',x['inst'])
					if mm:
						inst,created = nb_institution.objects.get_or_create(name=m.group(1).strip(),name_en=mm.group(1).strip())
						#inst.name_en = mm.group(1).strip()
					else:
						inst,created = nb_institution.objects.get_or_create(name=m.group(1).strip())

					if created:
						inst.update = True

					inst.save()

					con = nb2_peopleInstitution(people=peop,institution=inst,time=x['time'],kind=x['kind'],pos_text=x['pos_text'])
					con.save()
				else:
					inst,created = nb_institution.objects.get_or_create(name='UNKNOWN',name_en='UNKNOWN')
					if created:
						inst.save()
					con = nb2_peopleInstitution(people=peop,institution=inst,time=x['time'],kind=x['kind'],pos_text=x['pos_text'])
					con.save()
			if cd['f_sec_source']:
				cit_1 = re.split(r'\n+',cd['f_sec_source'])
				if id_people:
					if cd['f_sec_source'] != sec_sources_raw_old:
						nb2_peopleTexts.objects.filter(kind='sec',people=peop).delete()
						list_texts_1 = parse_citations(cit_1,True)
						for z in list_texts_1:
							oo=nb2_peopleTexts(people=peop,texts=z,kind='sec')
							oo.save()

			for z in cd_fs2:
				if len(z['pers'])>0:
					kk=z['pers'].split(',')
					last_name=kk[0]
					first_name=kk[1]
					first_name=first_name.strip()
					peop2,created=nb_people.objects.get_or_create(first_name=first_name,last_name=last_name)
					if created:
						peop2.update=True
						peop2.save()
					con = nb2_peoplePeople(person1=peop,person2=peop2,time=z['time'],kind=z['kind'],kind_freeT=z['kind_freeT'])
					con.save()
			edit = form4.save(commit=False)
			edit.user_name = request.user
			edit.c_people = peop
			edit.save()
			send_mails_follow(edit)

			return render(request,'message.html',{'message':'Saved!','redirect':'/notebook/people/show/'+str(peop.pk)})

		else:
			return render_to_response('edit_person.html',{'formset1':formset1,'formset2':formset2,'helper':FormSet1Helper,'errors1':formset1.errors,'errors2':formset2.errors,'form':form,'form4':form4}, context_instance=RequestContext(request))
	else:
		if id_people:
			pp = nb_people.objects.get(pk=int(id_people))
			form = form_edit_person(initial={'first_name':pp.first_name,'last_name':pp.last_name,'twitter':pp.twitter,'citizenship':pp.citizenship,'birth':pp.birth,'death':pp.death,'url':pp.url,'profession':pp.profession,'f_sec_source':pp.sec_sources_raw})
			initial = []
			initial2 = []
			for d in nb2_peopleInstitution.objects.filter(people=pp):
				if d.institution.name == "UNKNOWN":
					initial.append({'kind':d.kind,'pos_text':d.pos_text,'inst':'','time':d.time})
				elif d.institution.name_en:
					initial.append({'kind':d.kind,'pos_text':d.pos_text,'inst':d.institution.name+'['+d.institution.name_en+']','time':d.time})
				else:
					initial.append({'kind':d.kind,'pos_text':d.pos_text,'inst':d.institution.name,'time':d.time})


			for i in nb2_peoplePeople.objects.filter(person1=pp):
				initial2.append({'kind':i.kind,'time':i.time,'pers':i.person2.last_name+', '+i.person2.first_name,'kind_freeT':i.kind_freeT})
			formset1 = career_formset(initial=initial,prefix='car')
			formset2 = peers_formset(initial=initial2,prefix='peer')
		else:
			form = form_edit_person()
			formset1 = career_formset(prefix='car')
			formset2 = peers_formset(prefix='peer')
		form4 = form_explain_edit()
		return render(request,'edit_person.html',{'formset1':formset1,'formset2':formset2,'helper':FormSet1Helper,'form':form,'form4':form4})

@login_required(login_url='/login/')
def edit_institution(request,id_institution=False):
	errors=[]
	emp_formset = formset_factory(form_inst_add_emp)
	if request.method == 'POST':
		form2 = form_explain_edit(request.POST)
		form = form_edit_institution(request.POST)
		formset1 = emp_formset(request.POST,request.FILES, prefix='emp')
		if form.is_valid() and form2.is_valid() and formset1.is_valid():
			cd_fs1 = formset1.cleaned_data
			if id_institution:
				inst = nb_institution.objects.get(pk=id_institution)
				f = form_edit_institution(request.POST,instance=inst)
				#f.save()
				nb2_peopleInstitution.objects.filter(institution=inst).delete()
			else:
				f = form_edit_institution(request.POST)
			edit = form2.save(commit=False)
			edit.user_name = request.user
			ff=f.save(commit=False)
			ff.update=False
			ff.save()
			edit.c_institution = ff
			edit.save()
			print(cd_fs1)
			for z in cd_fs1:
				if len(z['pers'])>0:
					kk=z['pers'].split(',')
					last_name=kk[0]
					first_name=kk[1]
					first_name=first_name.strip()
					peop2,created=nb_people.objects.update_or_create(first_name=first_name,last_name=last_name)
					if created:
						peop2.update=True
						peop2.save()
					con,created = nb2_peopleInstitution.objects.update_or_create(institution=ff,people=peop2,time=z['time'],kind=z['kind'],kind_freeT=z['kind_freeT'])
					con.save()
				#else:
				#	nb2_peopleInstitution.objects.filter(pk=z['id']).delete()
			send_mails_follow(edit)
			return render(request,'message.html',{'message':'Saved!','redirect':'/notebook/institutions/show/'+str(ff.pk)})
		else:
			return render_to_response('edit_institution.html',{'form':form,'form2':form2,'formset1':formset1}, context_instance=RequestContext(request))

	else:
		if id_institution:
			inst = nb_institution.objects.get(pk=id_institution)
			form = form_edit_institution(instance=inst)
			initial = []
			for i in nb2_peopleInstitution.objects.filter(institution=inst):
				initial.append({'kind':i.kind,'time':i.time,'pers':i.people.last_name+', '+i.people.first_name,'kind_freeT':i.kind_freeT})
			formset1 = emp_formset(initial=initial,prefix='emp')
		else:
			form = form_edit_institution()
			formset1 = emp_formset(prefix='emp')
		form2 = form_explain_edit()
		return render(request,'edit_institution.html',{'form':form,'form2':form2,'formset1':formset1,'helper':FormSet1Helper})

def translate_terms(request,id_text,include_all=False):
	errors = []
	trans_formset = formset_factory(form_translate_terms,extra=0)
	if request.method == 'POST':
		formset = trans_formset(request.POST)
		if formset.is_valid():
			cd = formset.cleaned_data
			for u in cd:
				if len(u['english'])>1:
					term = nb_term.objects.get(pk=u['term_id'])
					term.english = u['english']
					#term.translate = False
					term.update = False
					term.save()
			return render(request,'message.html',{'message':'Saved!','redirect':'/notebook/texts/highlight/'+str(id_text)})
		else:
			helper = FormSet2Helper
			return render_to_response('translate_terms.html',{'text':text,'formset':formset,'helper':helper},context_instance=RequestContext(request))

	else:
		text = nb_texts.objects.get(pk=id_text)
		if include_all:
			terms = nb3_termTextSemfield.objects.filter(term__translate=True,texts=text)

		else:
			terms = nb3_termTextSemfield.objects.filter(term__translate=True,term__update=True,texts=text)
		initial=[]
		for x in terms:
			initial.append({'term_id':x.term.pk,'name':x.term.name,'english':x.term.english})
		formset = trans_formset(initial=initial)
		helper = FormSet2Helper
		return render_to_response('translate_terms.html',{'text':text,'formset':formset,'helper':helper},context_instance=RequestContext(request))

@login_required(login_url='/login/')
def add_report(request):
	errors = []
	if request.method == 'POST':
		form = form_add_report(request.POST)
		if form.is_valid():
			rep = form.save(commit=False)
			rep.user = request.user.username
			rep.save()
			send_mail('Bug report aarhus tool',rep.report,'django@schloegl.net',['matthias@schloegl.net'],fail_silently=True)
			return render(request,'message.html',{'message':'Submitted!','redirect':'/notebook/report/add'})
		else:
			return render_to_response('submit_report.html',{'form':form}, context_instance=RequestContext(request))
	else:
		form = form_add_report()
		reports_fin = nb_user_report.objects.filter(implemented=True)
		reports = nb_user_report.objects.filter().exclude(implemented=True)
		return render(request,'submit_report.html',{'form':form,'reports_fin':reports_fin,'reports':reports})

@login_required(login_url='/login/')
def search_crossrefs(request):
	errors = []
	if request.method == 'POST':
		form = form_search_crossrefs(request.POST)
		if form.is_valid():
			cd = form.cleaned_data
			searchterm = cd['search']
	elif request.method == 'GET':
		searchterm = request.GET.get('q')
	else:
		form = form_search_crossrefs()
		return render(request,'search_crossrefs.html',{'form':form})
	if searchterm:
		st_2 = re.sub(r'\s+','+',searchterm)
	else:
		form = form_search_crossrefs()
		return render(request,'search_crossrefs.html',{'form':form})
	if request.GET.get('page'):
		page = request.GET.get('page')
	else:
		page = '1'
	r = requests.get('http://search.crossref.org/dois?q=%s&page=%s&header=true'%(st_2,page))
	r.encoding = 'utf8'
	r = r.json()
	for count,x in enumerate(r['items']):
		try:
			if nb_texts.objects.filter(Q(title__icontains=x['title'])|Q(doi_url=x['doi'])).count()>0:
				r['items'][count]['exists']=True
			else:
				r['items'][count]['exists']=False
		except:
			r['items'][count]['exists']=False

	page = int(page)
	l_1_low=(int(page)*20)-20
	l_1_high=int(page)*20
	pagin = dict()
	pagin['page'] = page
	if page > 1:
		pagin['prev'] = page-1
	if float(page) < (float(r['totalResults'])/20):
		pagin['nxt'] = page+1
	tot_pages = int(math.ceil(float(r['totalResults'])/20))
	pagin['tot_pages'] = tot_pages
	form = form_search_crossrefs()
	return render(request,'search_crossrefs.html',{'form':form,'result':r,'pagin':pagin,'search_term':st_2})

@login_required(login_url='/login/')
def search_crossrefs_ajax(request):
	if request.method == 'POST':
		d_url = request.POST['url']
		d_id = request.POST['id']
		d_title = request.POST['title']
		headers = {'accept': 'text/bibliography; style=bibtex'}
		try:
			r = requests.get(d_url,headers=headers)
		except:
			res2 = json.dumps({'id':d_id,'error':True})
			return HttpResponse(res2,content_type='application/javascript')
		r.encoding = 'utf8'
		bibtex2 = r.text.replace(', ',',\n')

		bib_database = bibtexparser.loads(bibtex2)
		ent = bib_database.entries
		#res2 = json.dumps({'id':d_id,'bibtex2':ent})
		#return HttpResponse(res2,content_type='application/javascript')
		if len(ent) == 0:
			res2 = json.dumps({'id':d_id,'error':True})
			return HttpResponse(res2,content_type='application/javascript')
		try:
			pages = unidecode(ent[0]['pages'])
			#pages = pages.replace('\u2013','-')
			#pages = re.search(r'\d+\-\d+',pages).group(0)
		except:
			pages = ''
		try:
			title2 = ent[0]['title']
		except:
			if d_title != None:
				title2 = d_title
			else:
				res2 = json.dumps({'id':d_id,'error':True})
				return HttpResponse(res2,content_type='application/javascript')
		try:
			year = ent[0]['year']+'-01-01'
		except:
			year = None
		try:
			doi_url = ent[0]['doi']
		except:
			doi_url = None
		text, created = nb_texts.objects.get_or_create(title=title2,defaults={'pages':pages,'doi_url':doi_url,'pubdate':year})
		if 'author' in ent[0].keys():
			if 'and' in ent[0]['author']:
				d = ent[0]['author'].split('and')
			else:
				d = [ent[0]['author'],]
			for x in d:
				if ',' in x:
					dd = x.split(',')
					aut, created = nb_people.objects.get_or_create(first_name=dd[1].strip(),last_name=dd[0].strip())
				else:
					dd = x.split(' ')
					l_name= dd.pop()
					f_name = ' '.join(dd)
					aut, created = nb_people.objects.get_or_create(first_name=f_name.strip(),last_name=l_name.strip())
				con_aut,created = nb2_peopleTexts.objects.get_or_create(people=aut,texts=text,kind='aut')

		if 'publisher' in ent[0].keys():
			pub,created=nb_institution.objects.get_or_create(name=ent[0]['publisher'],defaults={'kind':'pub','update':True})
			pub_con, created = nb2_institutionTexts.objects.get_or_create(institution=pub,kind='pub',texts=text)
		if 'journal' in ent[0].keys():
			pub,created=nb_institution.objects.get_or_create(name=ent[0]['journal'],defaults={'kind':'jo','update':True})
			pub_con, created = nb2_institutionTexts.objects.get_or_create(institution=pub,kind='pub',texts=text)


		res2 = json.dumps({'id':d_id,'bibtex2':to_unicode(bibtex2)})
		return HttpResponse(res2,content_type='application/javascript')

@login_required(login_url='/login/')
def trigger_follow(request):
	if request.method == "POST":
		d_kind = request.POST['kind']
		d_id = request.POST['id']
		if d_kind == "person":
			item = nb_people.objects.get(pk=d_id)
			if nb4_follow.objects.filter(user_name=request.user,c_people=item).exists():
				nb4_follow.objects.filter(user_name=request.user,c_people=item).delete()
				res2 = json.dumps({'follow':False})
			else:
				new = nb4_follow(user_name=request.user,c_people=item)
				new.save()
				res2 = json.dumps({'follow':True})

		elif d_kind == "institution":
			item = nb_institution.objects.get(pk=d_id)
			if nb4_follow.objects.filter(user_name=request.user,c_institution=item).exists():
				nb4_follow.objects.filter(user_name=request.user,c_institution=item).delete()
				res2 = json.dumps({'follow':False})
			else:
				new = nb4_follow(user_name=request.user,c_institution=item)
				new.save()
				res2 = json.dumps({'follow':True})
		elif d_kind == "text":
			item = nb_texts.objects.get(pk=d_id)
			if nb4_follow.objects.filter(user_name=request.user,c_text=item).exists():
				nb4_follow.objects.filter(user_name=request.user,c_text=item).delete()
				res2 = json.dumps({'follow':False})
			else:
				new = nb4_follow(user_name=request.user,c_text=item)
				new.save()
				res2 = json.dumps({'follow':True})
		return HttpResponse(res2,content_type='application/javascript')

@login_required(login_url='/login/')
def list_concepts(request):
	sem_fields = nb_semanticField.objects.annotate(num_text=Count('nb_texts'))
	return render(request, 'list_concepts.html',{'concepts':sem_fields})

@login_required(login_url='/login/')
def list_terms(request):
	#terms = nb_term.objects.annotate(numconc=Count('nb_semanticfield'),numtext=Count('nb3_termtextsemfield__texts')).filter(numconc__gt=0)
	terms = nb_term.objects.annotate(numconc=Count('nb_semanticfield')).filter(numconc__gt=0)
	return render(request, 'list_terms.html',{'terms':terms})

@login_required(login_url='/login/')
def show_concept(request,id_concept):
	conc = nb_semanticField.objects.get(pk=int(id_concept))
	txts = nb_texts.objects.filter(nb3_termtextsemfield__sem_fields=conc).distinct()
	terms = nb_term.objects.filter(nb_semanticfield=conc.pk)
	return render(request, 'show_concept_entry.html',{'concept':conc,'texts':txts,'terms':terms})

@login_required(login_url='/login/')
def show_term(request,id_term):
	term = nb_term.objects.get(pk=int(id_term))
	txts = nb_texts.objects.filter(nb3_termtextsemfield__term=term).distinct()
	conc = nb_semanticField.objects.filter(nb3_termtextsemfield__term=term).distinct()
	return render(request, 'show_term_entry.html',{'concepts':conc,'texts':txts,'term':term})
