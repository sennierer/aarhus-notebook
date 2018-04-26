from django import forms
import autocomplete_light
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.core.urlresolvers import reverse
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, Div
from models import nb_texts,nb2_peopleInstitution,nb2_peoplePeople,nb_institution,nb_user_report,nb2_peopleTexts,nb4_edit
from django.core.validators import RegexValidator
from django.utils.translation import ugettext_lazy as _

class form_add_text(forms.Form):
	title = forms.CharField(label="Title of text",widget=forms.TextInput)
	title_en = forms.CharField(label="English title",required=False,help_text="Use the field only when needed (no need to retype an English title).",widget=forms.TextInput)
	sub_title = forms.CharField(label="Subtitle",required=False,widget=forms.TextInput,max_length=255)
	volume = forms.CharField(label="Volume",required=False,widget=forms.TextInput,max_length=10)
	issue = forms.CharField(label="Issue",required=False,widget=forms.TextInput,max_length=10)
	sec_source = forms.BooleanField(label='Secondary source?',required=False)
	pub_date=forms.DateField(label="Date of publication",required=False)
	kind = forms.ChoiceField(label="Kind of text",choices=((nb_texts.ONL,'Online'),(nb_texts.BK,'Book'),(nb_texts.JN,'Journal article'),(nb_texts.ART,'Article'),(nb_texts.NA,'Newspaper article'),(nb_texts.SP,'Speech'),(nb_texts.MB,'Membership list'),(nb_texts.LT,'Letter')),required=False)
	publisher = forms.CharField(label="Publisher",required=False,widget=autocomplete_light.TextWidget('publisher_text'))
	p_place = forms.CharField(label="Publishing place", required=False,widget=autocomplete_light.TextWidget('p_place'))
	pages = forms.CharField(label="Pages",required=False,validators=[RegexValidator(regex='^\d{1,4}-?\d{1,4}$',message='Please use a valid format (e.g. "1-10")',code='invalid_format')])
	recipient = forms.CharField(label="Recipient",required=False,help_text="Please use the field for recipients of letters.")
	language = forms.ChoiceField(label="Original language",choices=((nb_texts.DE,'German'),(nb_texts.EN,'English'),(nb_texts.RO,'Romanian'),(nb_texts.FR,'French')))
	keywords = forms.CharField(label="Keywords",help_text="Use ';' as delimiter",required=False,widget=forms.TextInput)
	info = forms.CharField(label="Abstract", required=False,widget=forms.Textarea)
	txt_file = forms.FileField(label='Select a file', required=False, help_text='Use only txt or pdfs.')
	file_ocr = forms.BooleanField(label='Is the file machine readable?',help_text='If you can copy text from the file it is machine readable. A txt is always machine readable, for pdfs try to copy text from the file.',required=False)
	#terms = forms.CharField(label='Specify terms used in the text',required=False ,widget=autocomplete_light.TextWidget('termsautocomplete'))
#widget=autocomplete_light.MultipleChoiceWidget('termsautocomplete')
	def __init__(self, *args, **kwargs):
		super(form_add_text, self).__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.form_method = 'post'
		self.helper.form_tag = False
		self.helper.disable_csrf = True
		

		#elf.helper.add_input(Submit('submit', 'Submit'))
	
class form_user_login(forms.Form):
	username = forms.CharField(label='Username',widget=forms.TextInput)
	password = forms.CharField(label='Password',widget=forms.PasswordInput)

	def __init__(self, *args, **kwargs):
		super(form_user_login, self).__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.add_input(Submit('submit','Login'))


class form_add_pers_text(forms.Form):
	kind = forms.ChoiceField(label="Person is",choices=((nb2_peopleTexts.AUT,'Author'),(nb2_peopleTexts.PUB,'Publisher'),(nb2_peopleTexts.EDT,'Editor')),help_text='Please specify the role of the Person in relation to the text.')
	name = forms.CharField(label="Person", required=False,widget=autocomplete_light.TextWidget('pers_name_text'),validators=[RegexValidator(regex='^[^,]+,\s?[^,]+$',message='Please use the correct format: "Surname, First name"')])

class form_upload_text(forms.Form):
	txt_file = forms.FileField(label='Select a file', help_text='max. 42 megabytes')
	info = forms.CharField(label="Short info on file",widget=forms.TextInput)
	pub_date=forms.DateField(label="Date of publication",required=False)
	title = forms.CharField(label="Title of text",widget=forms.TextInput)
	def __init__(self, *args, **kwargs):
		super(form_upload_text, self).__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.add_input(Submit('submit','Upload'))

class form_add_sem_field(forms.Form):
	name = forms.CharField(label="Concept to add", required=False,widget=autocomplete_light.TextWidget('semantic_field'))
	def __init__(self, *args, **kwargs):
		super(form_add_sem_field, self).__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.add_input(Submit('submit','Add Concept'))

class form_add_term(forms.Form):
	name = forms.CharField(label="Term to add", required=False,widget=autocomplete_light.TextWidget('term'))
	def __init__(self, *args, **kwargs):
		super(form_add_term, self).__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.form_tag = False

class form_edit_person(forms.Form):
	first_name = forms.CharField(label="First name",widget=autocomplete_light.TextWidget('pers_first_name'))
	last_name = forms.CharField(label="Surname")
	citizenship = forms.CharField(label="Citizenship",required=False,widget=autocomplete_light.TextWidget('pers_citizenship'))
	profession = forms.CharField(label="Profession",required=False,help_text="Use this field to specify the persons main profession (e.g. Journalist or Economist). You can specify other professions in the career steps down below.",widget=autocomplete_light.TextWidget('profession'))
	birth = forms.DateField(label="Date of birth",required=False)
	death = forms.DateField(label="Date of death",required=False)
	url = forms.URLField(label='Personal website', required=False)
	twitter = forms.CharField(label="Twitter account",help_text="Dont forget the '@'!",required=False,validators=[RegexValidator(regex='^@.+$',message='Twitter must be a valid user!',code='invalid_username')])
	f_sec_source = forms.CharField(label="Secondary sources",widget=forms.Textarea,help_text="You can paste bibliography information here. The citations should be delimited by a line break. They will be automatically parsed and connected to the person as a secondary source. Please note that the parsing is not 100% accurate, you should review the database entries (left menu under 'need review')",required=False)
	def __init__(self, *args, **kwargs):
		super(form_edit_person, self).__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.form_tag = False

class form_pers_add_career(forms.Form):
	kind = forms.ChoiceField(label="Kind of position",required=False,choices=((nb2_peopleInstitution.EMP,'Employee'),(nb2_peopleInstitution.SCO,'Scholar'),(nb2_peopleInstitution.STU,'Student'),(nb2_peopleInstitution.BO,'Board Member'),(nb2_peopleInstitution.LEA,'Leading Employee (CEO etc.)'),(nb2_peopleInstitution.MEM,'Member'),(nb2_peopleInstitution.CON,'Contractor (Authors etc.)')))
	pos_text = forms.CharField(label="Name of position",required=False,widget=autocomplete_light.TextWidget('position_text'))
	inst = forms.CharField(label="Name of institution",required=False,help_text='Add the English name in square brackets.',widget=autocomplete_light.TextWidget('publisher_text'))
	time = forms.CharField(label="Timeperiod",required=False,validators=[RegexValidator(regex='^\d{2,4}-{,1}\d{,4}$',message='Please give a valid time frame (yyyy-yyyy)')])

class form_pers_add_peer(forms.Form):
	kind = forms.ChoiceField(label="Kind of connection",required=False,choices=((nb2_peoplePeople.MEN,'Mentor'),(nb2_peoplePeople.MET,'Mentee'),(nb2_peoplePeople.PEE,'Peer'),(nb2_peoplePeople.PRO,'Professor'),(nb2_peoplePeople.STU,'Student')))
	kind_freeT = forms.CharField(label="Free text - connection",required=False,help_text='Use this field to give a more detailed description of the relationship.')
	pers = forms.CharField(label="Person",required=False, help_text='Please use "Surname, first name(s)".',widget=autocomplete_light.TextWidget('pers_name_text'),validators=[RegexValidator(regex='^[^,]+,\s?[^,]+$',message='Please use the correct format: "Surname, First name"')])
	time = forms.CharField(label="Timeperiod",required=False,validators=[RegexValidator(regex='^\d{2,4}-{,1}\d{,4}$',message='Please give a valid time frame (yyyy-yyyy)')])

class form_inst_add_emp(forms.Form):
	kind = forms.ChoiceField(label="Kind of connection",required=False,choices=((nb2_peopleInstitution.EMP,'Employee'),(nb2_peopleInstitution.SCO,'Scholar'),(nb2_peopleInstitution.STU,'Student'),(nb2_peopleInstitution.BO,'Board member'),(nb2_peopleInstitution.LEA,'Leading Employee (CEO etc.)'),(nb2_peopleInstitution.MEM,'Member'),(nb2_peopleInstitution.CON,'Contractor (Authors etc.)')))
	kind_freeT = forms.CharField(label="Free text - connection",required=False,help_text='Use this field to give a more detailed description of the relationship.')
	pers = forms.CharField(label="Person",required=False, help_text='Please use "Surname, first name(s)".',widget=autocomplete_light.TextWidget('pers_name_text'),validators=[RegexValidator(regex='^[^,]+,\s?[^,]+$',message='Please use the correct format: "Surname, First name"')])
	time = forms.CharField(label="Timeperiod",required=False,validators=[RegexValidator(regex='^\d{2,4}-{,1}\d{,4}$',message='Please give a valid time frame (yyyy-yyyy)')])

class form_edit_institution(forms.ModelForm):

	class Meta:
		model = nb_institution
		fields = ['name','name_en','kind','url','found_year','budget','emp_numb','twitter','address','abstract']
		labels = {
            'name': _('Name'),
            'name_en': _('English name'),
            'kind': _('Kind'),
            'url': _('Website'),
            'found_year': _('Foundation'),
            'emp_numb': _('Employees'),
            'twitter': _('Twitter'),
            'address': _('Address'),
            'abstract': _('Abstract'),
            'budget': _('Budget')
		}
		help_texts = {
        	'name_en': _('If you used the original name please specify an English name here.'),
        	'twitter': _('Dont forget the "@"!'),
        	'found_year': _('Please specify the year of foundation (YYYY)'),
        	'emp_numb': _('Please specify the number of employees.'),
        	'abstract': _('Use this field to give a short description of the institution.'),
        	'budget': _('Please specify the budget (in Eur) for the most recent year available.')
		}
		widgets = {'address': forms.Textarea(attrs={'cols': 20, 'rows': 5})}
	def __init__(self, *args, **kwargs):
		super(form_edit_institution, self).__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.form_tag = False
		#self.helper.add_input(Submit('submit','Add/Edit institution'))

class form_explain_edit(forms.ModelForm):
	class Meta:
		model = nb4_edit
		fields = ('explanation',)
		labels ={
		'explanation': _('Edit summary'),
		}
		help_texts = {
		'explanation': _('Other people might follow this entry. Please use this field to explain your edits.')
		}
		widgets = {'explanation': forms.Textarea(attrs={'cols': 20, 'rows': 5})}
	def __init__(self, *args, **kwargs):
		super(form_explain_edit, self).__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.form_method = 'post'
		self.helper.form_tag = False
		self.helper.disable_csrf = True

class form_translate_terms(forms.Form):
	term_id = forms.CharField(widget=forms.HiddenInput)
	name = forms.CharField(label='Term',widget = forms.TextInput(attrs={'readonly':'readonly','class':'termsTform'}))
	english = forms.CharField(label='English translation',required=False,widget = forms.TextInput(attrs={'class':'termsTformr'}))

class form_add_report(forms.ModelForm):

	class Meta:
		model = nb_user_report
		exclude = ['implemented','impl_note','user']
		labels = {
			'report': _('Explanation'),
		}
		help_texts = {
			'report': _('Please explain the suggestions you have or the bug you encountered. Your username is automatically saved in case I need to contact you.'),
		}
	def __init__(self, *args, **kwargs):
		super(form_add_report, self).__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.add_input(Submit('submit','Submit report'))

class form_search_crossrefs(forms.Form):
	search = forms.CharField(label="Search",help_text="Crossrefs will be searched.")
	def __init__(self, *args, **kwargs):
		
		self.helper = FormHelper()
		self.helper.form_class = 'form-inline'
		self.helper.field_template = 'bootstrap3/layout/inline_field.html'
		self.helper.layout = Layout(
			'search',
			self.helper.add_input(Submit('submit','Search',css_class='search_btn')),)
		#self.helper.add_input(Submit('submit','Search'))
		super(form_search_crossrefs, self).__init__(*args, **kwargs)


class FormSet1Helper(FormHelper):
	def __init__(self, *args, **kwargs):
		super(FormSet1Helper, self).__init__(*args, **kwargs)
		self.helper=FormHelper()
		#self.form_method = 'post'
		#self.form_action=reverse('add_text_crispy')
		self.form_tag = False
		#self.layout = Layout(
			#Fieldset(Div('formset1',css_id='Formset1')))
		self.render_required_fields = True
		self.disable_csrf = True
		#self.add_input(Submit('submit', 'Submit'))

class FormSet2Helper(FormHelper):
	def __init__(self, *args, **kwargs):
		super(FormSet2Helper, self).__init__(*args, **kwargs)
		self.helper=FormHelper()
		#self.form_method = 'post'
		#self.form_action=reverse('add_text_crispy')
		self.form_tag = True
		self.form_class = 'termsTform2'
		#self.layout = Layout(
			#Fieldset(Div('formset1',css_id='Formset1')))
		#self.render_required_fields = True
		self.add_input(Submit('submit','Add translations'))
