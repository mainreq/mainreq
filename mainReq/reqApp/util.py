# -*- encoding: utf-8 -*-
from reqApp.models import *
from django.http import Http404
from django.http import HttpResponseRedirect
from django.core.mail import EmailMessage

def getUserOr404(request):
    if request.user.is_authenticated():
        return request.user
    else:
        raise Http404

def getProject(request):
    if 'project' not in request.session:
        raise Http404
    index = int(request.session['project'])
    projects = request.user.userprofile.projects
    if (index < 0) or (projects.count() < 1) or (index >= projects.count()):
        raise Http404
    else:
        return projects.all().order_by('-id')[index]
 
def myFilter(s,val):
    # used for statistics
    # use:
    #   ...filter(**myFilter('property',val))
    dic = {}
    dic[s] = val
    return dic
    
def sendEmail2User(user, subject, message):
    email = EmailMessage(subject, message, to=[user.email])
    try:
        email.send()
        return True
    except Exception, e:
        return False
    
def orderingList(model):
    if model == UserType:
        return [
            {'order':'identifier', 'label':'identificador', 'up':'&#x25B5;', 'down':'&#x25BF;', 'span':'col-sm-2',},
            {'order':'name', 'label':'nombre', 'up':'&#x25B5;', 'down':'&#x25BF;', 'span':'col-sm-2',},
        ]
    elif model == UserRequirement:
        return [
            {'order':'identifier', 'label':'identificador', 'up':'&#x25B5;', 'down':'&#x25BF;', 'span':'col-sm-2',},
            {'order':'name', 'label':'nombre', 'up':'&#x25B5;', 'down':'&#x25BF;', 'span':'col-sm-1',},
            {'order':'state', 'label':'estado', 'up':'&#x25B5;', 'down':'&#x25BF;', 'span':'col-sm-1',},
            {'order':'-cost', 'label':'costo', 'up':'&#x25BF;', 'down':'&#x25B5;', 'span':'col-sm-1',},
            {'order':'priority', 'label':'urgencia', 'up':'&#x25BF;', 'down':'&#x25B5;', 'span':'col-sm-2',},
            {'order':'reqType', 'label':'tipo', 'up':'&#x25B5;', 'down':'&#x25BF;', 'span':'col-sm-2',},
            {'order':'increment', 'label':'hito', 'up':'&#x25B5;', 'down':'&#x25BF;', 'span':'col-sm-3',},
        ]
    elif model == SoftwareRequirement:
        return [
            {'order':'identifier', 'label':'identificador', 'up':'&#x25B5;', 'down':'&#x25BF;', 'span':'col-sm-2',},
            {'order':'name', 'label':'nombre', 'up':'&#x25B5;', 'down':'&#x25BF;', 'span':'col-sm-1',},
            {'order':'state', 'label':'estado', 'up':'&#x25B5;', 'down':'&#x25BF;', 'span':'col-sm-1',},
            {'order':'-cost', 'label':'costo', 'up':'&#x25BF;', 'down':'&#x25B5;', 'span':'col-sm-1',},
            {'order':'priority', 'label':'urgencia', 'up':'&#x25BF;', 'down':'&#x25B5;', 'span':'col-sm-2',},
            {'order':'reqType', 'label':'tipo', 'up':'&#x25B5;', 'down':'&#x25BF;', 'span':'col-sm-2',},
            {'order':'increment', 'label':'hito', 'up':'&#x25B5;', 'down':'&#x25BF;', 'span':'col-sm-3',},
        ]
    elif model == Module:
        return [
            {'order':'identifier', 'label':'identificador', 'up':'&#x25B5;', 'down':'&#x25BF;', 'span':'col-sm-2',},
            {'order':'name', 'label':'nombre', 'up':'&#x25B5;', 'down':'&#x25BF;', 'span':'col-sm-4',},
            {'order':'-cost', 'label':'costo', 'up':'&#x25BF;', 'down':'&#x25B5;', 'span':'col-sm-2',},
            {'order':'priority', 'label':'urgencia', 'up':'&#x25BF;', 'down':'&#x25B5;', 'span':'col-sm-4',},
        ]
    elif model == TestCase:
        return [
            {'order':'identifier', 'label':'identificador', 'up':'&#x25B5;', 'down':'&#x25BF;', 'span':'col-sm-2',},
            {'order':'name', 'label':'nombre', 'up':'&#x25B5;', 'down':'&#x25BF;', 'span':'col-sm-1',},
            {'order':'state', 'label':'estado', 'up':'&#x25B5;', 'down':'&#x25BF;', 'span':'col-sm-3',},
            {'order':'requirement', 'label':'requisito', 'up':'&#x25B5;', 'down':'&#x25BF;', 'span':'col-sm-6',},
        ]
    elif model == Increment:
        return [
            {'order':'identifier', 'label':'identificador', 'up':'&#x25B5;', 'down':'&#x25BF;', 'span':'col-sm-2',},
            {'order':'name', 'label':'nombre', 'up':'&#x25B5;', 'down':'&#x25BF;', 'span':'col-sm-2',},
        ]
    elif model == Task:
        return [
            {'order':'state', 'label':'estado', 'up':'&#x25B5;', 'down':'&#x25BF;', 'span':'col-sm-2',},
            {'order':'deadlineDate', 'label':'revisión', 'up':'&#x25B5;', 'down':'&#x25BF;', 'span':'col-sm-5 col-sm-offset-5',},
        ]
    return []
    
def deleteWarning(el):
    # text displayed in delete confirmation box
    if el.__class__ == Increment:
        urn = UserRequirement.objects.valids(el.project).filter(increment=el).count()
        srn = SoftwareRequirement.objects.valids(el.project).filter(increment=el).count()
        return (u"%s Requisitos de Usuario y %s Requisitos de Software quedarán sin Hito asociado." % (urn, srn))
    if el.__class__ == UserType:
        urn = UserRequirement.objects.valids(el.project).filter(userTypes=el).count()
        srn = SoftwareRequirement.objects.valids(el.project).filter(userTypes=el).count()
        tcn = TestCase.objects.valids(el.project).filter(userTypes=el).count()
        return (u"%s Requisitos de Usuario, %s Requisitos de Software y %s Casos de Prueba dejarán de estar asociados a este Tipo de Usuario." % (urn, srn, tcn))
    if el.__class__ == UserRequirement:
        srn = SoftwareRequirement.objects.valids(el.project).filter(userRequirements=el)
        tcn = TestCase.objects.valids(el.project).filter(requirement=el)
        
        src = 0
        srs = ""
        for sr in srn:
            src = src + 1
            srs = srs + u"\\n • " + sr.__unicode__()
        
        tcc = 0
        tcs = ""
        for tc in tcn:
            tcc = tcc + 1
            tcs = tcs + u"\\n • " + tc.__unicode__()
        
        return (u"%s Requisitos de Software y %s Casos de Prueba dejarán de estar asociados a este Requisito de Usuario:%s%s" % (src, tcc, srs, tcs))
    if el.__class__ == SoftwareRequirement:
        urn = el.userRequirements.filter(validity=True)
        tcn = TestCase.objects.valids(el.project).filter(requirement=el)
        mdn = Module.objects.valids(el.project).filter(softwareRequirements=el)
        
        urc = 0
        urs = ""
        for ur in urn:
            urc = urc + 1
            urs = urs + u"\\n • " + ur.__unicode__()
        
        tcc = 0
        tcs = ""
        for tc in tcn:
            tcc = tcc + 1
            tcs = tcs + u"\\n • " + tc.__unicode__()
            
        mdc = 0
        mds = ""
        for md in mdn:
            mdc = mdc + 1
            mds = mds + u"\\n • " + md.__unicode__()
        
        return (u"%s Requisitos de Usuario, %s Casos de Prueba y %s Módulos dejarán de estar asociados a este Requisito de Software:%s%s%s" % (urc, tcc, mdc, urs, tcs, mds))
    if el.__class__ == TestCase:
        return (u"El Requisito ( %s ) dejará de estar asociado a este Caso de Prueba." % el.requirement.__unicode__())
    if el.__class__ == Module:
        srn = el.softwareRequirements.filter(validity=True)
        srs = ""
        c = 0
        for sr in  srn:
            c = c + 1
            srs = srs + u"\\n • " + sr.__unicode__()
        return (u"%s Requisitos de Software dejarán de estar asociados a este Módulo:%s" % (c, srs))
    return ""
    
def getPermissionCodename(model):
    return model._meta.permissions[0][0]
    
def isEditor(request, model):
    user = getUserOr404(request)
    project = getProject(request)
    if not project.is_active() and not user.is_staff:
        return False
    return user.has_perm('reqApp.'+getPermissionCodename(model))
    
def elementsFilters(model, project, actualFilters=None):
    if model == UserRequirement or model == SoftwareRequirement:
        if actualFilters is None:
            actualFilters = {
                'increment':'',
                'state':'',
                'priority':'',
                'stability':'',
                'reqtype':'',
            }
            
        incrementList = [('no_filter', 'Todos', False)]
        for ic in Increment.objects.valids(project):
            key = str(ic.identifier)
            incrementList.append((key, ic.__unicode__(), (actualFilters['increment'] == key)))
        
        stateList = [('no_filter', 'Todos', False)]
        for state, name in STATE_CHOICES:
            stateList.append((state, name, (actualFilters['state'] == state)))
            
        priorityList = [('no_filter', 'Todos', False)]
        for priority, name in PRIORITY_CHOICES:
            priorityList.append((priority, name, (actualFilters['priority'] == priority)))
            
        stabilityList = [('no_filter', 'Todos', False)]
        for stability, name in STABILITY_CHOICES:
            stabilityList.append((stability, name, (actualFilters['stability'] == stability)))
            
        if model == UserRequirement:
            typeChoices = UR_TYPE_CHOICES
        else:
            typeChoices = SR_TYPE_CHOICES
        reqTypeList = [('no_filter', 'Todos', False)]
        for reqType, name in typeChoices:
            reqTypeList.append((reqType, name, (actualFilters['reqtype'] == reqType)))
            
        return [
            {'title':'Selecciona Hito','key':'increment','list':incrementList},
            {'title':'Selecciona Estado','key':'state','list':stateList},
            {'title':'Selecciona Urgencia','key':'priority','list':priorityList},
            {'title':'Selecciona Estabilidad','key':'stability','list':stabilityList},
            {'title':'Selecciona Tipo','key':'reqtype','list':reqTypeList},
        ]
    if model == TestCase:
        if actualFilters is None:
            actualFilters = {
                'increment':'',
                'state':'',
                'requirement':'',
            }
        
        incrementList = [('no_filter', 'Todos', False)]
        for ic in Increment.objects.valids(project):
            key = str(ic.identifier)
            incrementList.append((key, ic.__unicode__(), (actualFilters['increment'] == key)))
        
        stateList = [('no_filter', 'Todos', False)]
        for state, name in STATE_CHOICES:
            stateList.append((state, name, (actualFilters['state'] == state)))
            
        requirementList = [
            ('no_filter', 'Todos', False),
            ('ur', 'Requisitos de Usuario', (actualFilters['requirement'] == 'ur')),
            ('sr', 'Requisitos de Software', (actualFilters['requirement'] == 'sr')),
        ]
        
        return [
            {'title':'Selecciona Hito','key':'increment','list':incrementList},
            {'title':'Selecciona Estado','key':'state','list':stateList},
            {'title':'Selecciona Requisitos','key':'requirement','list':requirementList},
        ]
    if model == Module:
        if actualFilters is None:
            actualFilters = {'priority':'',}
            
        priorityList = [('no_filter', 'Todos', False)]
        for priority, name in PRIORITY_CHOICES:
            priorityList.append((priority, name, (actualFilters['priority'] == priority)))
            
        return [{'title':'Selecciona Urgencia','key':'priority','list':priorityList}]
    return False
    
def filterElements(model, project, elements, request):
    actualFilters = None
    if model == UserRequirement or model == SoftwareRequirement:
        actualFilters = {}
        
        incrementInentifier = request.GET.get('increment','no_filter')
        actualFilters.update({'increment':incrementInentifier})
        if incrementInentifier != 'no_filter':
            elements = elements.filter(increment__identifier=int(incrementInentifier))
            
        state = request.GET.get('state','no_filter')
        actualFilters.update({'state':state})
        if state != 'no_filter':
            elements = elements.filter(state=state)
            
        priority = request.GET.get('priority','no_filter')
        actualFilters.update({'priority':priority})
        if priority != 'no_filter':
            elements = elements.filter(priority=priority)
            
        stability = request.GET.get('stability','no_filter')
        actualFilters.update({'stability':stability})
        if stability != 'no_filter':
            elements = elements.filter(stability=stability)
            
        reqType = request.GET.get('reqtype','no_filter')
        actualFilters.update({'reqtype':reqType})
        if reqType != 'no_filter':
            elements = elements.filter(reqType=reqType)

    elif model == TestCase:
        actualFilters = {}
        
        incrementInentifier = request.GET.get('increment','no_filter')
        actualFilters.update({'increment':incrementInentifier})
        if incrementInentifier != 'no_filter':
            elements = elements.filter(requirement__userrequirement__increment__identifier=int(incrementInentifier)) | elements.filter(requirement__softwarerequirement__increment__identifier=int(incrementInentifier))
        
        state = request.GET.get('state','no_filter')
        actualFilters.update({'state':state})
        if state != 'no_filter':
            elements = elements.filter(state=state)
            
        requirement = request.GET.get('requirement','no_filter')
        actualFilters.update({'requirement':requirement})
        if requirement == 'ur':
            elements = elements.filter(requirement__is_UR=True)
        elif requirement == 'sr':
            elements = elements.filter(requirement__is_UR=False)
    elif model == Module:
        actualFilters = {}
        
        priority = request.GET.get('priority','no_filter')
        actualFilters.update({'priority':priority})
        if priority != 'no_filter':
            elements = elements.filter(priority=priority)
    return (elements, elementsFilters(model, project, actualFilters), "&filter=true" + dict2GetQuery(actualFilters))
    
def dict2GetQuery(dic):
    query = ""
    for key in dic:
        query = query + "&" + key + "=" + dic[key]
    return query
    
def hasDangerousChars(s):
    # avoid posible problems inserting strings into js/html variables
    if s.find("\"") >= 0:return True
    if s.find("\'") >= 0:return True
    if s.find("\\") >= 0:return True
    if s.find("/") >= 0:return True
    return False
    
def getHost(request):
    return unicode(request.build_absolute_uri("/")[:-1])# http://localhost:8000
