# -*- encoding: utf-8 -*-
from django import forms
from reqApp.models import *
from reqApp.util import *
from django.utils import timezone

from tinymce.widgets import TinyMCE

class RegistryForm(forms.ModelForm):
    validsProjectFields = []
    def assignProject(self, project):
        self.project = project
        
        # these fields only consider valids elements oredered by identifier
        for field in self.validsProjectFields:
            self.fields[field].queryset = self.fields[field].queryset.filter(validity=True).filter(project=self.project).order_by('identifier')
            
        return self
        
    def registerElement(self, user, identifier=None, reason=""):
        # https://docs.djangoproject.com/en/1.6/topics/forms/modelforms/#the-save-method
        element = self.save(commit=False)
        
        if identifier == None: # create new element
            element.registerNewElement(self.project, user)
            
        else: # edit element
            # register a no-valid copy
            element.registerElementCopy(self.project, identifier)
            
            # register new element
            element.registerElement(user, reason)
        
        # update many2many relations
        self.save_m2m()
        return element
    
    def createRegistryElement(self, user):
        return self.registerElement(user)
    
    def updateRegistryElement(self, user, identifier, updateReason):
        # copy previous state (no-valid) and update registry element
        self.registerElement(user, identifier, updateReason)
        
    def clean_name(self):
        # in order to avoid conflicts with js and html code
        name = self.cleaned_data['name']
        if hasDangerousChars(name):
            raise forms.ValidationError("No debe introducir comillas ni backslash")
        return name
        

class UTForm(RegistryForm):
    class Meta:
        model = UserType
        fields = [
            'name',
            'description',
            'quantity',
            'userSamples',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'cols': 100, 'rows': 4}),
            'name': forms.TextInput(attrs={'size': 74}),
            'quantity': forms.TextInput(attrs={'size': 5}),
            'userSamples': forms.Textarea(attrs={'cols': 50, 'rows': 4}),
        }

class URForm(RegistryForm):
    def __init__(self,*args,**kwargs):
        super (URForm,self).__init__(*args,**kwargs)
        self.validsProjectFields = [
            'userTypes',
            'increment',
        ]
        
    class Meta:
        model = UserRequirement
        
        fields = [
            'name',
            'description',
            'source',
            'cost',
            'stability',
            'reqType',
            'priority',
            'state',
            'userTypes',
            'increment',
        ]
        
        widgets = {
            'description': forms.Textarea(attrs={'cols': 100, 'rows': 4}),
            'name': forms.TextInput(attrs={'size': 74}),
        }

class SRForm(RegistryForm):
    def __init__(self,*args,**kwargs):
        super (SRForm,self).__init__(*args,**kwargs)
        self.validsProjectFields = [
            'userTypes',
            'userRequirements',
            'increment',
        ]
    
    class Meta:
        model = SoftwareRequirement
        fields = [
            'name',
            'description',
            'source',
            'cost',
            'stability',
            'reqType',
            'priority',
            'state',
            'userTypes',
            'userRequirements',
            'increment',
        ]
        
        widgets = {
            'description': forms.Textarea(),
            'name': forms.TextInput(),
            'userRequirements': forms.SelectMultiple(),
        }
        
class TCForm(RegistryForm):
    def __init__(self,*args,**kwargs):
        super (TCForm,self).__init__(*args,**kwargs)
        self.validsProjectFields = [
            'userTypes',
        ]
    
    def assignProject(self, project):
        self.project = project
        
        # these fields only consider valids elements oredered by identifier
        for field in self.validsProjectFields:
            self.fields[field].queryset = self.fields[field].queryset.filter(validity=True).filter(project=self.project).order_by('identifier')
            
        self.fields['requirement'].queryset = self.fields['requirement'].queryset.filter(validity=True).filter(project=self.project).order_by('-is_UR','identifier')
            
        return self
    
    class Meta:
        model = TestCase
        fields = [
            'name',
            'requirement',
            'description',
            'acceptableResult',
            'optimumResult',
            'userTypes',
            'state',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'cols': 100, 'rows': 4}),
            'name': forms.TextInput(attrs={'size': 74}),
            'acceptableResult': forms.Textarea(attrs={'cols': 70, 'rows': 2}),
            'optimumResult': forms.Textarea(attrs={'cols': 70, 'rows': 2}),
        }
        
class MDForm(RegistryForm):
    def __init__(self,*args,**kwargs):
        super (MDForm,self).__init__(*args,**kwargs)
        self.validsProjectFields = [
            'softwareRequirements',
        ]
    
    class Meta:
        model = Module
        fields = [
            'name',
            'description',
            'softwareRequirements',
            'cost',
            'priority',
            
        ]
        widgets = {
            'description': forms.Textarea(attrs={'cols': 100, 'rows': 4}),
            'name': forms.TextInput(attrs={'size': 74}),
            'softwareRequirements': forms.SelectMultiple(attrs={'size': 10}),
        }
        
class ICForm(RegistryForm):
    
    class Meta:
        model = Increment
        fields = [
            'name',
            'description',
            'initDate',
            'endDate',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'cols': 100, 'rows': 4}),
            'name': forms.TextInput(attrs={'size': 74}),
            'initDate': forms.DateTimeInput(format='%Y-%m-%d %H:%M',attrs={'datetimepicker':'yes','placeholder': 'YYYY-MM-DD hh:mm'}),
            'endDate': forms.DateTimeInput(format='%Y-%m-%d %H:%M',attrs={'datetimepicker':'yes','placeholder': 'YYYY-MM-DD hh:mm'}),
        }
        
    def clean_endDate(self):
        end = self.cleaned_data['endDate']
        if 'initDate' not in self.cleaned_data:
            return end
        ini = self.cleaned_data['initDate']
        if end < ini:
            raise forms.ValidationError("Fecha Fin es menor que Fecha Inicio!")
        return end
        

class DocForm(forms.ModelForm):
    def registerDocumentSection(self, project, user, sectionType):
        (self.save(commit=False)).registerDocumentSection(project, user, sectionType)
        
    class Meta:
        model = DocumentSection
        fields = [
            'content',
        ]
        widgets = {
            'content': TinyMCE(
                mce_attrs={
                    'theme':'advanced',
                    'width':'100%',# css
                    'height':'600px',# css
                    'plugins':'yenimg',# plugin propio para incorporar imagenes en el mce.
                    'theme_advanced_statusbar_location':None,
                    'theme_advanced_blockformats':"p,h3,h4,h5,h6",# no incluye h1 ni h2 para poder usarlo en el documento final.
                    'theme_advanced_buttons1':
                        "formatselect,|,bold,italic,underline,|,justifyleft,justifycenter,justifyright,justifyfull,|,outdent,indent,|,bullist,numlist,|,browseimg,imgurl,|,removeformat,|,undo,redo",
                    'theme_advanced_buttons2':"",
                    'theme_advanced_buttons3':"",
                    'relative_urls':False,
                    })
        }

class MceImageForm(forms.Form):
    file = forms.ImageField()
    
class TaskForm(forms.ModelForm):
    def createTask(self, project):
        # https://docs.djangoproject.com/en/1.6/topics/forms/modelforms/#the-save-method
        task = self.save(commit=False)
        task.createTask(project)
        return task
        
    def assignUsers(self, users):
        self.fields['user'].queryset = users
        return self
        
    class Meta:
        model = Task
        fields = [
            'user',
            'name',
            'description',
            'deadlineDate',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'cols': 100, 'rows': 4}),
            'name': forms.TextInput(attrs={'size': 74}),
            'deadlineDate': forms.DateTimeInput(format='%Y-%m-%d %H:%M',attrs={'datetimepicker':'yes','placeholder': 'YYYY-MM-DD hh:mm'}),
        }
        
    def clean_deadlineDate(self):
        now = timezone.now()
        end = self.cleaned_data['deadlineDate']
        if end < now:
            raise forms.ValidationError("Debe proporcionar una fecha en el futuro!")
        return end
    
    def clean_name(self):
        name = self.cleaned_data['name']
        if hasDangerousChars(name):
            raise forms.ValidationError("No debe introducir comillas ni backslash")
        return name
        
class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'email',
        ]
    
    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['email'].required = True
        
class NewPassForm(forms.ModelForm):
    newPassword = forms.CharField(widget=forms.PasswordInput())
    confirmPassword = forms.CharField(widget=forms.PasswordInput())
    class Meta:
        model = User
        fields = [
            'newPassword',
            'confirmPassword',
        ]
    
    def clean_confirmPassword(self):
        confirmPassword = self.cleaned_data['confirmPassword']
        if 'newPassword' not in self.cleaned_data:
            return confirmPassword
        newPassword = self.cleaned_data['newPassword']
        if newPassword != confirmPassword:
            raise forms.ValidationError("Error en la confirmación de contraseña.")
        return confirmPassword
