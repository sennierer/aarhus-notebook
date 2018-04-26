from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import User

# Create your models here.

class Users(models.Model):
	user_name = models.CharField(max_length = 300)
	uq_hash = models.CharField(max_length = 200)

class nb_textfile(models.Model):
	docfile = models.FileField(upload_to='documents/%Y/%m/%d')
	#title = models.CharField(max_length = 255)
	file_type = models.CharField(max_length=3,blank=True)
	saved = models.BooleanField(default=True)
	message = models.CharField(max_length=255,blank=True,null=True)

class nb_user_report(models.Model):
	user = models.CharField(max_length = 300)
	report = models.TextField()
	date_created = models.DateTimeField(auto_now_add=True)
	date_modified = models.DateTimeField(auto_now=True)
	implemented = models.BooleanField(default=False)
	impl_note = models.TextField(blank=True,null=True)


class nb_institution(models.Model):
	TT = 'tt'
	GOV = 'gov'
	CORP = 'corp'
	UV = 'uv'
	NGO = 'ngo'
	PUB = 'pub'
	FOU = 'fou'
	JO = 'jo'
	inst_choices = ((TT,'Think Tank'),(GOV,'Governmental Body'),(CORP,'Corporation'),(UV,'University'),(NGO,'NGO'),(PUB,'Publisher'),(FOU,'Foundation'),(JO,'Journal'))
	name = models.CharField(max_length=255)
	name_en = models.CharField(max_length=255,blank=True,null=True)
	kind = models.CharField(max_length=4,choices=inst_choices,default=UV)
	url = models.URLField(blank=True,null=True)
	twitter = models.CharField(max_length=255,blank=True,null=True,validators=[RegexValidator(regex='^@.+$',message='Twitter must be a valid user!',code='invalid_username')])
	address = models.CharField(max_length=255,blank=True,null=True)
	update = models.BooleanField(default=True)
	abstract = models.TextField(blank=True,null=True)
	found_year = models.IntegerField(blank=True,null=True,max_length=4)
	emp_numb = models.IntegerField(blank=True,null=True,max_length=6)
	budget = models.IntegerField(blank=True,null=True,max_length=12)
	def __unicode__(self):
		return u'%s' % (self.name,)


class nb_term(models.Model):
	name = models.CharField(max_length=255,unique=True)
	english = models.CharField(max_length=255,blank=True,null=True)
	translate = models.BooleanField(default=True)
	update = models.BooleanField(default=True)
	#alchemy = models.CharField(max_length=3,blank=True,null=True)

class nb_semanticField(models.Model):
	name = models.CharField(max_length=255)
	period = models.CharField(max_length=8,validators=[RegexValidator(regex='^\d{4}-?\d{2,4}$',message='Use a proper Period!',code='invalid_period')])
	update = models.BooleanField(default=True)
	terms = models.ManyToManyField(nb_term)

class nb_place(models.Model):
	place = models.CharField(max_length=255)

class nb_texts(models.Model):
	ONL = 'onl'
	BK = 'bk'
	JN = 'jn'
	LT = 'lt'
	NA = 'na'
	SP = 'sp'
	ART = 'art'
	MB = 'mb'
	DE = 'deu'
	EN = 'en'
	RO = 'ro'
	FR = 'fr'
	kind_choices = ((ONL,'Online'),(BK,'Book'),(JN,'Journal article'),(MB,'Membership list'),(LT,'Letter'),(NA,'Newspaper article'),(SP,'Speech'),(ART,'Article'))
	lang_choices = ((DE,'German'),(EN,'English'),(RO,'Romanian'),(FR,'French'))
	kind = models.CharField(max_length=4,choices=kind_choices,default=ART)
	title = models.CharField(max_length=255)
	title_en = models.CharField(max_length=255,blank=True)
	sub_title = models.CharField(max_length=255,blank=True)
	volume = models.CharField(max_length=10,blank=True)
	issue = models.CharField(max_length=10,blank=True)
	recipient = models.CharField(max_length=255,blank=True,null=True)
	p_place = models.ForeignKey(nb_place,blank=True,null=True)
	language = models.CharField(max_length=3,choices=lang_choices,default=EN)
	pubdate = models.DateField(blank=True,null=True)
	abstract = models.TextField(blank=True,null=True)
	txt_file = models.ForeignKey(nb_textfile,blank=True,null=True)
	file_ocr = models.BooleanField(default=False,blank=True)
	sec_source = models.BooleanField(default=False)
	pages = models.CharField(max_length=10,blank=True,default=None,validators=[RegexValidator(regex='^\d{1,4}-?\d{2,4}$',message='Please use a valid format (e.g. "1-10"',code='invalid_format')])
	sem_fields = models.ManyToManyField(nb_semanticField)
	doi_url = models.URLField(blank=True,null=True)
	update = models.BooleanField(default=True)
	def __unicode__(self):
		return u'%s' % (self.title,)
	

class nb_people(models.Model):
	first_name = models.CharField(max_length=255,blank=True)
	last_name = models.CharField(max_length=255,blank=True)
	profession = models.CharField(max_length=255,blank=True)
	citizenship = models.CharField(max_length=255,blank=True,null=True)
	birth = models.DateField(blank=True,null=True)
	death = models.DateField(blank=True,null=True)
	url = models.URLField(blank=True,null=True)
	twitter = models.CharField(max_length=255,blank=True,null=True,validators=[RegexValidator(regex='^@.+$',message='Twitter must be a valid user!',code='invalid_username')])
	update = models.BooleanField(default=True)
	sec_sources_raw = models.TextField(blank=True,null=True)
	class Meta:
		unique_together = (('first_name','last_name'),)
	def __unicode__(self):
		return u'%s %s' % (self.first_name, self.last_name)

class nb_argument(models.Model):
	name = models.CharField(max_length=255)
	uses_term = models.ForeignKey(nb_term,blank=True)


class nb2_textsTextfile(models.Model):
	txt_file = models.ForeignKey(nb_textfile)
	text = models.ForeignKey(nb_texts)

class nb2_peopleInstitution(models.Model):
	EMP = 'emp'
	SCO = 'sco'
	STU = 'stu'
	BO = 'bo'
	LEA = 'lea'
	MEM = 'mem'
	CON = 'con'
	kind_choices =((EMP,'Employee'),(SCO,'Scholar'),(STU,'Student'),(BO,'Board Member'),(LEA,'Leading Employee (CEO etc.)'),(MEM,'Member'),(CON,'Contractor (Authors etc.)'))
	kind = models.CharField(max_length=4,choices=kind_choices,default=EMP)
	kind_freeT = models.CharField(max_length=255,blank=True,null=True)
	pos_text = models.CharField(max_length=255,blank=True,null=True)
	people = models.ForeignKey(nb_people)
	institution = models.ForeignKey(nb_institution)
	time = models.CharField(max_length=9,blank=True,null=True,validators=[RegexValidator(regex='^\d{2,4}-{,1}\d{,4}$',message='Please give a valid time frame (yyyy-yyyy)')])

class nb2_peoplePeople(models.Model):
	MEN = 'men'
	MET = 'met'
	PEE = 'pee'
	PRO = 'pro'
	STU = 'stu'
	kind_choices = ((MEN,'Mentor'),(MET,'Mentee'),(PEE,'Peer'),(PRO,'Professor'),(STU,'Student'))
	kind = models.CharField(max_length=4,choices=kind_choices,default=MEN)
	kind_freeT = models.CharField(max_length=255,blank=True,null=True)
	person1 = models.ForeignKey(nb_people,related_name='rev_peop2_p1')
	person2 = models.ForeignKey(nb_people,related_name='rev_peop2_p2')
	time = models.CharField(max_length=9,blank=True,null=True,validators=[RegexValidator(regex='^\d{2,4}-{,1}\d{,4}$',message='Please give a valid time frame (yyyy-yyyy)')])
	

class nb2_institutionTexts(models.Model):
	PUB = 'pub'
	CIT = 'cit'
	MEN = 'men'
	SEC = 'sec'
	kind_choices = ((PUB,'Publication'),(CIT,'Citation'),(MEN,'mentioned'),(SEC,'secondary source'))
	kind = models.CharField(max_length=4,choices=kind_choices,default=PUB)
	institution = models.ForeignKey(nb_institution)
	texts = models.ForeignKey(nb_texts)

class nb2_peopleTexts(models.Model):
	AUT = 'aut'
	CIT = 'cit'
	MEN = 'men'
	PUB = 'pub'
	EDT = 'edt'
	SEC = 'sec'
	kind_choices = ((AUT,'Author'),(CIT,'cited'),(MEN,'mentioned'),(PUB,'Publisher'),(EDT,'Editor'),(SEC,'secondary source'))
	kind = models.CharField(max_length=4,choices=kind_choices,default=AUT)
	people = models.ForeignKey(nb_people)
	texts = models.ForeignKey(nb_texts)

class nb2_textsArgument(models.Model):
	CRIT = 'crit'
	USE = 'use'
	kind_choices = ((CRIT,'criticizes'),(USE,'uses'))
	kind = models.CharField(max_length=4,choices=kind_choices,default=USE)
	text = models.ForeignKey(nb_texts)
	argument = models.ForeignKey(nb_argument)

class nb3_termTextSemfield(models.Model):
	KEY = 'key'
	TER = 'ter'
	kind_choices =((KEY,'Keyword'),(TER,'Term'))
	kind = models.CharField(max_length=4,choices=kind_choices,default=TER)
	term = models.ForeignKey(nb_term)
	sem_fields = models.ManyToManyField(nb_semanticField,blank=True)
	texts = models.ManyToManyField(nb_texts,blank=True)

class nb4_analysisElement(models.Model):
	name = models.CharField(max_length=255)
	user_name = models.ForeignKey(User,blank=True,null=True)
	c_people = models.ManyToManyField(nb_people,blank=True,null=True)
	c_institution = models.ManyToManyField(nb_institution,blank=True,null=True)
	c_text = models.ManyToManyField(nb_texts,blank=True,null=True)

class nb4_follow(models.Model):
	user_name = models.ForeignKey(User,blank=True,null=True)
	c_people = models.ForeignKey(nb_people,blank=True,null=True)
	c_institution = models.ForeignKey(nb_institution,blank=True,null=True)
	c_text = models.ForeignKey(nb_texts,blank=True,null=True)

class nb4_edit(models.Model):
	user_name = models.ForeignKey(User,blank=True,null=True)
	date = models.DateTimeField(auto_now=True)
	explanation = models.TextField(blank=True,null=True)
	c_people = models.ForeignKey(nb_people,blank=True,null=True)
	c_institution = models.ForeignKey(nb_institution,blank=True,null=True)
	c_text = models.ForeignKey(nb_texts,blank=True,null=True)



