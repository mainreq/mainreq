# -*- encoding: utf-8 -*-
from django.db import models
from django.db.models import Max
from django.db.models import F
from django.contrib.auth.models import User,Group
from django.db.models.signals import post_save
from reqApp.choices import *
from django.utils import timezone
from django.utils.dateformat import DateFormat
from tinymce import models as tinymce_models

# admin permission prefix
PERM_PRE = u"EDITOR_"


class Role(Group):
    def __unicode__(self):
        return u'%s' % (self.name)

class Project(models.Model):
    """
    name = models.CharField(max_length=64)
    description = models.CharField(max_length=140)
    date = models.DateTimeField(default=timezone.now,blank=True)
    
    class Meta:
        ordering = ['-id']
    
    def creationDate(self):
        df = DateFormat(self.date)
        return df.format('Y-m-d')
    
    def __unicode__(self):
        return u'[%s] %s' % (self.creationDate(), self.name)
    """
    name = models.CharField(max_length=64)
    description = models.CharField(max_length=140)
    startDate = models.DateTimeField(default=timezone.now)
    projectSemester = models.CharField(max_length=140, choices=SEMESTER_CHOICES)
    closingDate = models.DateTimeField()
    semester = models.CharField(max_length=140, blank=True)
    
    class Meta:
        ordering = ['-semester','-id']
        
    def is_active(self):
        if timezone.now() >= self.closingDate:
            return False
        return True
    
    def status(self):
        if self.is_active():
            return 'Open'
        return 'Closed'
        
    def __unicode__(self):
        return u'%s: %s' % (self.semester, self.name)

class UserProfile(models.Model):
    """
    >>> u = User.objects.get(username='fred')
    >>> fredProjects = u.userprofile.projects
    """
    user = models.OneToOneField(User)
    projects = models.ManyToManyField(Project, null=True, blank=True)
    
    
    
def profile(sender, **kwargs):
    if kwargs.get('created', False):
        UserProfile.objects.create(
            user=kwargs.get('instance')
            )
post_save.connect(profile, sender=User)

class RegistryManager(models.Manager):
    def registered(self, project, identifier=None):
        if identifier ==  None:
            return self.model.objects.filter(project=project).order_by('-date')
        else:
            return self.model.objects.filter(project=project).filter(identifier=identifier).order_by('-date')
    
    def valids(self, project, order='identifier'):
        return self.model.objects.filter(project=project).filter(validity=True).order_by(order,'identifier')
        
    def valid(self, project, identifier):
        try:
            resp = self.model.objects.filter(project=project).filter(validity=True).filter(identifier=identifier)[:1].get()
        except self.model.DoesNotExist:
            resp = None
        return resp
    
    def newIdentifier(self, project):
        elements = self.model.objects.all().filter(project=project)
        
        if elements.count() > 0:
            return elements.aggregate(Max('identifier'))['identifier__max'] + 1 # TODO: might have concurrency problems!
        return 1

class Registry(models.Model):
    name = models.CharField(max_length=100)
    identifier = models.PositiveIntegerField(default=0, blank=True, null=False)
    description = tinymce_models.HTMLField(blank=True)#models.CharField(max_length=5000, blank=True)
    reason = models.CharField(max_length=140, blank=True)
    project = models.ForeignKey(Project, blank=True, null=False)
    date = models.DateTimeField()
    user = models.ForeignKey(User, null=True)
    validity = models.BooleanField()
    
    def __unicode__(self):
        return u'%s' % self.name
        
    def m2mValids(self):
        # create a dict with m2m valids references
        return {}
        
    def copyM2MValids(self, m2mValidsDict):
        # create a copy of m2m valids references
        pass
    
    def registerElementCopy(self, project, identifier):
        # register a no-valid copy of element
        previousElement = self.__class__.objects.valid(project, identifier)
        if previousElement == None:
            # TODO: ERROR
            print "ERROR:666"
        # https://docs.djangoproject.com/en/1.6/topics/db/queries/#copying-model-instances
        m2mValids = previousElement.m2mValids()
        
        if self.__class__ == UserRequirement or self.__class__ == SoftwareRequirement:
            # necessary step to get a new ID and PK with the Requirement model
            previousElement = previousElement.dummyCopy()
        else:
            previousElement.pk = None
            previousElement.id = None
            previousElement.save()
            
        previousElement.copyM2MValids(m2mValids)
        previousElement.validity = False
        previousElement.save()
        
    
    def registerElement(self, user, reason=None):
        # register guilty user
        self.user = user
        
        # register modification date
        self.date = timezone.now()
        
        # register reason of modifications...
        if reason is not None:
            self.setReason(reason)
        
        self.save()
     
    def registerNewElement(self, project, user):
        self.identifier = self.__class__.objects.newIdentifier(project)
        self.validity = True
        self.project = project
        
        if self.__class__ == UserRequirement:
            self.is_UR = True
        elif self.__class__ == SoftwareRequirement:
            self.is_UR = False
            
        self.registerElement(user)

    def registerDeletedElement(self, user, deletionReason):
        # register no-valid element copy
        self.registerElementCopy(self.project, self.identifier)
        
        # a deleted element is not valid anymore
        self.validity = False
        
        # store changes
        self.registerElement(user, deletionReason)
        
    def setReason(self, reason):
        self.reason = reason.replace('"','\\"').replace("'","\\'")[:140]

class Increment(Registry):
    initDate = models.DateTimeField(default=timezone.now)
    endDate = models.DateTimeField(default=timezone.now)
    
    objects = RegistryManager()
    
    class Meta:
        permissions = ((PERM_PRE+'IC', "Editor Hitos"),)
    
    def identifierText(self):
        return u'HT%04d' % self.identifier
    
class UserType(Registry):
    quantity = models.PositiveIntegerField(default=1)
    userSamples = models.CharField(max_length=200, default='', blank=True)
    
    objects = RegistryManager()
    
    class Meta:
        permissions = ((PERM_PRE+'UT', "Editor Tipos Usuario"),)
    
    def __unicode__(self):
        return u'TU%04d %s' % (self.identifier, self.name)
       
    def identifierText(self):
        return u'TU%04d' % self.identifier


class Requirement(Registry):
    is_UR = models.BooleanField(blank=True)
    
    def __unicode__(self):
        if self.is_UR:
            return self.userrequirement.__unicode__()
        else:
            return self.softwarerequirement.__unicode__()
        
    def state(self):
        if self.is_UR:
            return self.userrequirement.state
        else:
            return self.softwarerequirement.state
    
class UserRequirement(Requirement):
    source = models.CharField(max_length=140, blank=True)
    cost = models.IntegerField(default=0)
    
    stability = models.CharField(max_length=30, choices=STABILITY_CHOICES)
    reqType = models.CharField(max_length=30, choices=UR_TYPE_CHOICES)
    priority = models.CharField(max_length=30, choices=PRIORITY_CHOICES)
    state = models.CharField(max_length=30, choices=STATE_CHOICES)
    
    userTypes = models.ManyToManyField(UserType, null=True, blank=True)
    increment = models.ForeignKey(Increment, blank=False, null=False)
    
    objects = RegistryManager()
    
    class Meta:
        permissions = ((PERM_PRE+'UR', "Editor Req. Usuario"),)
    
    def identifierText(self):
        return u'RU%04d' % self.identifier
    
    def __unicode__(self):
        return u'RU%04d %s' % (self.identifier, self.name)
    
    def m2mValids(self):
        return {
            'userTypes':self.userTypes.filter(validity=True),
        }
        
    def copyM2MValids(self, m2mValidsDict):
        self.userTypes = m2mValidsDict['userTypes']
        
    def dummyCopy(self):
        # creates a new registry from self, necessary for registerElementCopy
        dummy = UserRequirement()
        
        dummy.name = self.name
        dummy.identifier = self.identifier
        dummy.description = self.description
        dummy.project = self.project
        dummy.date = self.date
        dummy.user = self.user
        dummy.validity = False
        
        dummy.source = self.source
        dummy.cost = self.cost
        dummy.stability = self.stability
        dummy.reqType = self.reqType
        dummy.priority = self.priority
        dummy.state = self.state
        dummy.increment = self.increment
        
        dummy.is_UR = True
        
        dummy.save()
        
        return dummy
    
class SoftwareRequirement(Requirement):
    source = models.CharField(max_length=140)
    cost = models.IntegerField(default=0)
    
    stability = models.CharField(max_length=30, choices=STABILITY_CHOICES)
    reqType = models.CharField(max_length=30, choices=SR_TYPE_CHOICES)
    priority = models.CharField(max_length=30, choices=PRIORITY_CHOICES)
    state = models.CharField(max_length=30, choices=STATE_CHOICES)
    
    userTypes = models.ManyToManyField(UserType, null=True, blank=True)
    userRequirements = models.ManyToManyField(UserRequirement, null=True, blank=True)
    increment = models.ForeignKey(Increment, blank=False, null=False)
    
    objects = RegistryManager()
    
    class Meta:
        permissions = ((PERM_PRE+'SR', "Editor Req. Software"),)
    
    def identifierText(self):
        return u'RS%04d' % self.identifier
    
    def __unicode__(self):
        return u'RS%04d %s' % (self.identifier, self.name)
        
    def m2mValids(self):
        return {
            'userTypes':self.userTypes.filter(validity=True),
            'userRequirements':self.userRequirements.filter(validity=True),
        }
        
    def copyM2MValids(self, m2mValidsDict):
        self.userTypes = m2mValidsDict['userTypes']
        self.userRequirements = m2mValidsDict['userRequirements']
        
    def dummyCopy(self):
        dummy = SoftwareRequirement()
        
        dummy.name = self.name
        dummy.identifier = self.identifier
        dummy.description = self.description
        dummy.project = self.project
        dummy.date = self.date
        dummy.user = self.user
        dummy.validity = False
        
        dummy.source = self.source
        dummy.cost = self.cost
        dummy.stability = self.stability
        dummy.reqType = self.reqType
        dummy.priority = self.priority
        dummy.state = self.state
        dummy.increment = self.increment
        
        dummy.is_UR = False
        
        dummy.save()
        
        return dummy

class TestCase(Registry):
    acceptableResult = models.CharField(max_length=140)
    optimumResult = models.CharField(max_length=140)
    
    state = models.CharField(max_length=30, choices=STATE_CHOICES)
    
    userTypes = models.ManyToManyField(UserType, null=True, blank=True)
    softwareRequirement = models.ForeignKey(SoftwareRequirement, null=False, blank=False)
    #requirement = models.ForeignKey(Requirement, null=False, blank=False)
    
    objects = RegistryManager()
    
    class Meta:
        permissions = ((PERM_PRE+'TC', "Editor Casos de Prueba"),)
    
    def identifierText(self):
        return u'CP%04d' % self.identifier
    
    def __unicode__(self):
        return u'CP%04d %s' % (self.identifier, self.name)
    
    def m2mValids(self):
        return {
            'userTypes':self.userTypes.filter(validity=True),
        }
        
    def copyM2MValids(self, m2mValidsDict):
        self.userTypes = m2mValidsDict['userTypes']
        
class Module(Registry):
    cost = models.IntegerField(default=0)
    
    priority = models.CharField(max_length=30, choices=PRIORITY_CHOICES)
    
    softwareRequirements = models.ManyToManyField(SoftwareRequirement, null=True, blank=True)
    
    objects = RegistryManager()
    
    class Meta:
        permissions = ((PERM_PRE+'MD', "Editor Modulos"),)
    
    def identifierText(self):
        return u'MD%04d' % self.identifier
    
    def __unicode__(self):
        return u'MD%04d %s' % (self.identifier, self.name)
        
    def m2mValids(self):
        return {
            'softwareRequirements':self.softwareRequirements.filter(validity=True),
        }
        
    def copyM2MValids(self, m2mValidsDict):
        self.softwareRequirements = m2mValidsDict['softwareRequirements']
        
############ Documents #############
class DocsManager(models.Manager):
    def versions(self, project, sectionType, limit=-1):
        if limit < 0:
            # all registered
            return self.model.objects.filter(project=project).filter(sectionType=sectionType).order_by('-id')
        else:
            # only last registered (limit)
            return self.model.objects.filter(project=project).filter(sectionType=sectionType).order_by('-id')[:limit]
    
    def valid(self, project, sectionType):
        try:
            resp = self.model.objects.filter(project=project).filter(sectionType=sectionType).order_by('-id')[:1].get()
        except self.model.DoesNotExist:
            resp = None
        return resp

class DocumentSection(models.Model):
    content = tinymce_models.HTMLField(blank=True)
    
    project = models.ForeignKey(Project, null=False)
    date = models.DateTimeField()
    user = models.ForeignKey(User)
    sectionType = models.CharField(max_length=30, choices=SECTION_CHOICES)
    
    objects = DocsManager()
    
    class Meta:
        permissions = ((PERM_PRE+'DC', "Editor Documentos"),)
    
    def registerDocumentSection(self, project, user, sectionType):
        self.project = project
        self.user = user
        self.sectionType = sectionType
        self.date = timezone.now()
        
        self.save()
        
############ Tasks #############
class TaskManager(models.Manager):
    def getTask(self, project, id):
        try:
            resp = self.model.objects.filter(project=project).filter(id=id)[:1].get()
            #resp = resp.checkDeadline()
        except self.model.DoesNotExist:
            resp = None
        return resp
        
    def getTasks(self, project, user=None, order='state'):
        q = self.model.objects.filter(project=project)
        if user is not None:
            q = q.filter(user=user)
        #for task in q.filter(state='t1_to_do'):
        #    task.checkDeadline()
        return q.order_by(order,'deadlineDate')
        
    def getWorkerUsers(self, project):
        return User.objects.filter(is_active=True).filter(is_staff=False).filter(userprofile__projects=project).exclude(groups__permissions__codename=Task._meta.permissions[0][0])
        
    def filterByIsLate(self, tasks):
        return tasks.filter(state__in=['t0_doing','t1_to_do','t2_done','t4_approved','t5_reprobate','t6_discarded']).filter(doneDate__gt=F('deadlineDate')) # | tasks.filter(state='t3_not_done')
        
class Task(models.Model):
    name = models.CharField(max_length=100)
    project = models.ForeignKey(Project, null=False)
    initDate = models.DateTimeField(default=timezone.now)
    deadlineDate = models.DateTimeField(default=timezone.now)
    doneDate = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(User)
    description = models.CharField(max_length=5000, blank=True)
    state = models.CharField(max_length=30, choices=TASK_CHOICES)
    
    requirements = models.ManyToManyField(Requirement, null=True, blank=True)
    
    objects = TaskManager()
    
    class Meta:
        permissions = ((PERM_PRE+'TK', "Asignar Tareas"),)
        
    def __unicode__(self):
        return u'%s' % (self.name)
       
    def createTask(self, project):
        self.project = project
        self.initDate = timezone.now()
        self.state = 't1_to_do'
        self.save()
    
    """
    def checkDeadline(self):
        if self.state == 't1_to_do' and  (self.deadlineDate < timezone.now()):
            self.state = 't3_not_done'
            self.save()
        return self
    """
    
    def isDone(self):
        return self.state == 't2_done'
    
    def setDone(self):
        self.state = 't2_done'
        self.doneDate = timezone.now()
        self.save()
        
    def isDoing(self):
        return self.state == 't0_doing'
    
    def setDoing(self):
        self.state = 't0_doing'
        self.save()
        
    def isApproved(self):
        return self.state == 't4_approved'
        
    def setApproved(self):
        self.state = 't4_approved'
        self.save()
    
    def isReprobated(self):
        return self.state == 't5_reprobate'
    
    def setReprobated(self):
        self.state = 't5_reprobate'
        self.save()
        
    def setDiscarded(self):
        self.state = 't6_discarded'
        self.save()
        
    def isToDo(self):
        return self.state == 't1_to_do'
        
    #def isNotDone(self):
    #    return self.state == 't3_not_done'
    
    """    
    def isLate(self):
        if self.isToDo():
            return False
        elif self.isNotDone():
            return True
        elif self.doneDate > self.deadlineDate:
            return True
        return False
    """
    def isLate(self):
        return self.doneDate > self.deadlineDate
