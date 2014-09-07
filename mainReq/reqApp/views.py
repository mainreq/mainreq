# -*- encoding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from reqApp.forms import *
from reqApp.util import *
from django.contrib.auth.models import User
import json

from django.http import HttpResponse
from django.http import Http404

from django.db.models import Sum

################ edit user profile ################
def editUser(request):
    user = getUserOr404(request)
    context = {'next':request.GET.get("next","/")}
    if request.method == 'GET':
        context.update({'form':UserForm(instance=user)})
    elif request.method == 'POST':
        form = UserForm(instance=user, data=request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user.first_name = data['first_name']
            user.last_name = data['last_name']
            user.email = data['email']
            user.save()
        else:
            context.update({'form':form})
    return render(request, 'reqApp/editUser.html', context)
    
def editPass(request):
    user = getUserOr404(request)
    context = {'next':request.GET.get("next","/")}
    if request.method == 'GET':
        context.update({'form':NewPassForm()})
    elif request.method == 'POST':
        form = NewPassForm(data=request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user.set_password(data['newPassword'])
            user.save()
        else:
            context.update({'form':form})
    return render(request, 'reqApp/newPass.html', context)

################ after login ################
def selectProject(request):
    user = getUserOr404(request)
    if request.method == 'GET':
        if user.userprofile.projects.count() == 1:
            request.session['project'] = 0
        else:
            projects = []
            for i,p in enumerate(user.userprofile.projects.all().order_by('-id')):
                projects.append((i,p))
            context = {
                'projects':projects,
            }
            return render(request, 'reqApp/selectProject.html', context)
    else:
        if 'index' in request.POST:
            index = int(request.POST['index'])
            request.session['project'] = index
    return HttpResponseRedirect(reverse('reqApp:IC'))

################ Project Elements ################

def getElementContent(request):
    elemType = {
        'IC':{
            'model':Increment,
            'modelForm':ICForm,
            'template':'reqApp/project/IC/IC_content.html',
            'form_template':'reqApp/project/IC/IC_form.html',
        },
        'UT':{
            'model':UserType,
            'modelForm':UTForm,
            'template':'reqApp/project/UT/UT_content.html',
            'form_template':'reqApp/project/UT/UT_form.html',
        },
        'UR':{
            'model':UserRequirement,
            'modelForm':URForm,
            'template':'reqApp/project/UR/UR_content.html',
            'form_template':'reqApp/project/UR/UR_form.html',
        },
        'SR':{
            'model':SoftwareRequirement,
            'modelForm':SRForm,
            'template':'reqApp/project/SR/SR_content.html',
            'form_template':'reqApp/project/SR/SR_form.html',
        },
        'MD':{
            'model':Module,
            'modelForm':MDForm,
            'template':'reqApp/project/MD/MD_content.html',
            'form_template':'reqApp/project/MD/MD_form.html',
        },
        'TC':{
            'model':TestCase,
            'modelForm':TCForm,
            'template':'reqApp/project/TC/TC_content.html',
            'form_template':'reqApp/project/TC/TC_form.html',
        },
    }

    user = getUserOr404(request)
    project = getProject(request)
    
    elType = request.GET['elemType']
    identifier = int(request.GET.get('identifier',0))
    model = elemType[elType]['model']
    try:
        element = model.objects.get(id=identifier)
        if 'getForm' in request.GET:# load form
            context = {
                'form':elemType[elType]['modelForm'](instance=element).assignProject(project),
                #'deleteWarning':deleteWarning(element),
                'identifier':element.identifier,
                'identifierText':element.identifierText(),
            }
            return render(request, elemType[elType]['form_template'], context)
        else:# load content        
            context = {
                'element':element,
                'registry':(int(request.GET.get('registry',0)) != 0),
                'canEdit':(int(request.GET.get('canEdit',0)) != 0),
                'deleteWarning':deleteWarning(element),
                'elemType':elType,
            }
            return render(request, elemType[elType]['template'], context)
    except model.DoesNotExist:
        return HttpResponse("?")

def ajax_form_valid(form, validated):
    if validated:
        response_dict = {'server_response': "OK" }
        return HttpResponse(json.dumps(response_dict), content_type='application/json')    
    else:
        err = []
        for field, errors in form.errors.items():
            for error in errors:
                err.append([field,error])
        response_dict = {'server_response': "FAIL", 'errors':err}
        return HttpResponse(json.dumps(response_dict), content_type='application/json')

def elementView(request, modelFormClass, elementTemplate, formTemplate, modelClass, navbar, pdfLink, helpLink, colorLabels):
    user = getUserOr404(request)
    project = getProject(request)
    msgs = []
    if request.method == 'POST':
        if 'identifier' in request.POST:# edit or delete
            identifier = request.POST['identifier']
            instance = modelClass.objects.valid(project, identifier)
            if instance is None:
                msgs.append(u'ERROR: El elemento había sido eliminado previamente.')
            elif 'delete' in request.POST:# delete element
                deletionReason = request.POST['deletionReason']
                instance.registerDeletedElement(user, deletionReason)
                msgs.append(instance.identifierText()+u' eliminado y registrado en la bitácora')
            else:# edit element
                form = modelFormClass(instance=instance, data=request.POST)
                form.assignIdentifier(instance.identifier)
                form.assignProject(project)
                if form.is_valid():
                    if request.POST.has_key("validate"):
                        return ajax_form_valid(form, True)
                    #form.assignProject(project)
                    updateReason = request.POST['updateReason']
                    form.updateRegistryElement(user, identifier, updateReason)
                    msgs.append(instance.identifierText()+u' modificado y registrado en la bitácora')
                else:
                    if request.POST.has_key("validate"):
                        return ajax_form_valid(form, False)
                    m=form.errors.as_text
                    msgs.append('datos inválidos!')
                    msgs.append(m)
        else:# create element
            form = modelFormClass(request.POST)
            form.assignProject(project)
            if form.is_valid():
                if request.POST.has_key("validate"):
                    return ajax_form_valid(form, True)
                #form.assignProject(project)
                instance = form.createRegistryElement(user)
                msgs.append(instance.identifierText()+u' creado y registrado en la bitácora')
            else:
                if request.POST.has_key("validate"):
                    return ajax_form_valid(form, False)
                msgs.append('datos inválidos!')
    
    actualOrder = 'identifier'
    if 'order' in request.GET:# order element list
        actualOrder = request.GET['order']
        elements = modelClass.objects.valids(project, actualOrder)
    else:
        elements = modelClass.objects.valids(project)
    
    if 'filter' in request.GET:# filters
        elements, filters, filtersQuery = filterElements(modelClass, project, elements, request)
    else:
        filters = elementsFilters(modelClass, project)
        filtersQuery = ""
        
    context = {
        'msgs': msgs,
        'elements': elements,
        'template':elementTemplate,
        'form': modelFormClass().assignProject(project),
        'form_template': formTemplate,
        'ordering_bar': 'reqApp/orderingBar.html',
        'ordering_attributes': orderingList(modelClass),
        'actual_order': actualOrder,
        'navbar':navbar,
        'pdfLink':pdfLink,
        'helpLink':helpLink,
        'canEdit':isEditor(request, modelClass),
        'elementsFilters':filters,
        'filtersQuery':filtersQuery,
        'colorLabels':colorLabels,
    }
    
    return render(request, 'reqApp/project/elements_list.html', context)

def viewUT(request):
    return elementView(request, UTForm, 'reqApp/project/UT/UT.html', 'reqApp/project/UT/UT_form.html', UserType, {'1':'project', '2':'UT'}, 'UT', 'UT', False)

def viewUR(request):
    return elementView(request, URForm, 'reqApp/project/UR/UR.html', 'reqApp/project/UR/UR_form.html', UserRequirement, {'1':'project', '2':'UR'}, 'UR', 'UR', True)

def viewSR(request):
    return elementView(request, SRForm, 'reqApp/project/SR/SR.html', 'reqApp/project/SR/SR_form.html', SoftwareRequirement, {'1':'project', '2':'SR'}, 'SR', 'SR', True)

def viewMD(request):
    return elementView(request, MDForm, 'reqApp/project/MD/MD.html', 'reqApp/project/MD/MD_form.html', Module, {'1':'project', '2':'MD'}, 'MD', 'MD', True)

def viewTC(request):
    return elementView(request, TCForm, 'reqApp/project/TC/TC.html', 'reqApp/project/TC/TC_form.html', TestCase, {'1':'project', '2':'TC'}, 'TC', 'TC', True)
    
def viewIC(request):
    return elementView(request, ICForm, 'reqApp/project/IC/IC.html', 'reqApp/project/IC/IC_form.html', Increment, {'1':'project', '2':'IC'}, 'IC', 'IC', False)
    
################################# Documents #############################
def docView(request, navbar, availables, shownSection, pdfLink, helpLink=None):
    user = getUserOr404(request)
    project = getProject(request)

    section =  request.GET.get('section', shownSection)
    if section not in availables:
        section = availables[0]
        
    sections = []
    for pa in SECTION_CHOICES:
        active = False
        if pa[0] in availables:
            active = True
        sections.append({'sType':pa[0], 'sName':pa[1], 'active':active})
    
    canEdit = isEditor(request, DocumentSection)
    
    context = {
        'navbar':navbar,
        'sections':sections,
        'section':section,
        'pdfLink':pdfLink,
        'helpLink':helpLink,
        'canEdit':canEdit,
    }
    
    id_version = -1 # no edition version selected
    if request.method == 'POST':
        form = DocForm(request.POST)
        if form.is_valid():
            form.registerDocumentSection(project, user, section) # save changes
    elif request.method == 'GET':
        id_version =  int(request.GET.get('id', -1))# selected edition version
    
    versions = DocumentSection.objects.versions(project, section, -1)
    if len(versions) > 0:
        actual = versions[0]
        context.update({'actual':actual,'versions':versions})
        
        if id_version >= 0: # selected version
            version = None
            for vers in versions:
                if vers.id == id_version:
                    version = vers
                    break
                
            if version is not None: # version found
                form = DocForm(instance=version) # load mce with selected version
                context.update({'id_version':id_version})
            else: # version not found
                form = DocForm(instance=actual) # load most recent version
        else:
            form = DocForm(instance=actual) # load most recent version
    else:
        form = DocForm() # none version found
        
    context.update({'form':form,})
    
    
    return render(request, 'reqApp/documents/documents.html', context)

def docReq(request):
    navbar = {'1':'documents', '2':'requirements'}
    sections = [
        'introduction',
        'purpose',
        'scope',
        'context',
        'definitions',
        'references',
        'project_members',
        'general_description',
        
        'users',
        'product',
        'environment',
        'related_projects',
    ]
    return docView(request, navbar, sections, 'introduction', 'docReq', 'docReq')
    
def docDsn(request):
    navbar = {'1':'documents', '2':'design'}
    sections = [
        'introduction',
        'purpose',
        'scope',
        'context',
        'definitions',
        'references',
        'project_members',
        'general_description',
        
        'design',
        'physical_architecture',
        'logical_architecture',
        'model',
        'detailed_modules',
        'navigation',
        'interface',
    ]
    return docView(request, navbar, sections, 'design', 'docDsn', 'docDsn')
    
def docTC(request):
    navbar = {'1':'documents', '2':'tc'}
    sections = [
        'introduction',
        'purpose',
        'scope',
        'context',
        'definitions',
        'references',
        'project_members',
        'general_description',
        
        'users',
        'product',
        'environment',
        'related_projects',
    ]
    return docView(request, navbar, sections, 'general_description', 'docTC', 'docTC')

def docHis(request):
    navbar = {'1':'documents', '2':'historic'}
    sections = [
        'introduction',
        'purpose',
        'scope',
        'context',
        'definitions',
        'references',
        'project_members',
        'general_description',
        
        'users',
        'product',
        'environment',
        'related_projects',
        
        'design',
        'physical_architecture',
        'logical_architecture',
        'model',
        'detailed_modules',
        'navigation',
        'interface',
    ]
    return docView(request, navbar, sections, 'product', 'docHis', 'docHis')

############################### Tools ##########################

##############################  TASKS
def tasks(request):
    navbar = {'1':'tools', '2':'tasks'}
    msgs = []
    
    user = getUserOr404(request)
    project = getProject(request)
    
    actualOrder = 'state'
    if 'order' in request.GET:
        actualOrder = request.GET['order']
    
    getParams = ""
    
    context = {}
    if isEditor(request, Task):
        userIndex = -1
        if 'userIndex' in request.GET:
            userIndex = int(request.GET.get('userIndex',-1))
        workerUsers = Task.objects.getWorkerUsers(project)
        workerUsersCount = workerUsers.count()
        context.update({
            'canEditTasks':True,
            'workerUsers':enumerate(workerUsers),
            'form_template':'reqApp/tools/tasks/task_form.html',
            'form':TaskForm().assignUsers(workerUsers),
            'userIndex':userIndex,
        })
        getParams = "&userIndex=" + str(userIndex)
        if request.method == 'POST':
            if request.POST.has_key("nextTaskState"):# change task state
                taskId = int(request.POST['id'])
                task = Task.objects.getTask(project, taskId)
                if task is None:
                    raise Http404
                if request.POST['nextTaskState'] == 'approved':
                    if task.isDone():
                        task.setApproved()
                        msgs.append('La tarea "'+task.__unicode__()+'" ha sido aprobada.')
                    else:
                        msgs.append('ERROR: la tarea "'+task.__unicode__()+'" debe estar realizada para ser aprobada!')
                elif request.POST['nextTaskState'] == 'reprobate':
                    if task.isDone():
                        task.setReprobated()
                        msgs.append('La tarea "'+task.__unicode__()+'" ha sido reprobada.')
                    else:
                        msgs.append('ERROR: la tarea "'+task.__unicode__()+'" debe estar realizada para ser reprobada!')
                elif request.POST['nextTaskState'] == 'discarded':
                    if not (task.isReprobated() or task.isApproved()):
                        task.setDiscarded()
                        msgs.append('La tarea "'+task.__unicode__()+'" ha sido descartada.')
                    else:
                        msgs.append('ERROR: la tarea "'+task.__unicode__()+'" no se puede descartar, ya ha sido evaluada!')
            else:# create task
                form = TaskForm(request.POST)
                if form.is_valid():
                    if request.POST.has_key("validate"):
                        return ajax_form_valid(form, True)
                    task = form.createTask(project)
                    workerUser = task.user
                    msgs.append(u'Tarea creada: "'+task.__unicode__()+u'" Responsable: '+workerUser.__unicode__())
                    # send email notifications
                    if request.POST.has_key("sendNotifications"):
                        notif = u"Hola '"+workerUser.__unicode__()+u"' tienes una nueva tarea. \nTarea: "+task.__unicode__()+u"\nFecha de Revisión: "+str(task.deadlineDate)[:-6]+u"\nDescripción: "+task.description+u"\n\n* IMPORTANTE: debes reportar su estado en la sección de Tareas de MainReq ("+getHost(request)+")."
                        if sendEmail2User(workerUser, "MainReq: Nueva Tarea", notif):
                            msgs.append(u"Nueva tarea notificada a Usuario: " + workerUser.__unicode__() + u" Email: " + workerUser.email)
                            if sendEmail2User(user, "MainReq: Nueva Tarea", u"(Copia de notificación enviada)\n\n"+notif):
                                msgs.append(u"Copia de notificación a Usuario: " + user.__unicode__() + u" Email: " + user.email)
                            else:
                                msgs.append(u"ERROR: No se pudo enviar copia de notificación a Usuario: " + user.__unicode__() + u" Email: " + user.email)
                        else:
                            msgs.append(u"ERROR: No se pudo enviar notificación a Usuario: " + workerUser.__unicode__() + u" Email:" + workerUser.email)
                else:
                    if request.POST.has_key("validate"):
                        return ajax_form_valid(form, False)
                    msgs.append('datos inválidos!')
        if workerUsersCount > 0:
            if userIndex < 0:
                tasks = Task.objects.getTasks(project, order=actualOrder)
            else:
                tasks = Task.objects.getTasks(project, workerUsers[userIndex], actualOrder)
        else:
            tasks = Task.objects.getTasks(project, order=actualOrder)
    else: # show his tasks
        if request.method == 'POST':
            if request.POST.has_key("nextTaskState"):# change task state
                taskId = int(request.POST['id'])
                task = Task.objects.getTask(project, taskId)
                if task is None:
                    raise Http404
                if request.POST['nextTaskState'] == 'done':
                    if task.isToDo():
                        task.setDone()
                        msgs.append('La tarea "'+task.__unicode__()+'" ha sido realizada.')
                    else:
                        msgs.append('ERROR: la tarea "'+task.__unicode__()+'" no se puede realizar!')
        tasks = Task.objects.getTasks(project, user, actualOrder)
    
    state = None
    if 'state' in request.GET:
        state = request.GET['state']
        tasks = tasks.filter(state=state)
        getParams = getParams + "&state="+state
    
    context.update({
        'navbar':navbar,
        'helpLink':'task',
        'ordering_bar': 'reqApp/orderingBar.html',
        'ordering_attributes': orderingList(Task),
        'actual_order': actualOrder,
        'msgs':msgs,
        'tasks':tasks,
        'template':'reqApp/tools/tasks/task.html',
        'states':TASK_CHOICES,
        'state':state,
        'getParams':getParams,
    })
    return render(request, 'reqApp/tools/tasks/tasks.html', context)

##############################  STATISTICS
def statisticsUR_SR_TC_MD(project, ic=None):
    # user requirement statistics
    q = UserRequirement.objects.valids(project).filter(increment__validity=True)
    if ic is not None:
        q = q.filter(increment=ic)
    ur = {}
    priority = []
    stability = []
    tyype = []
    state = {}
    extras = []
    
    table = [
        ('Prioridad', 'priority', PRIORITY_CHOICES, priority),
        ('Estabilidad', 'stability', STABILITY_CHOICES, stability),
        ('Tipo', 'reqType', UR_TYPE_CHOICES, tyype),
    ]
    
    for attribute, s, choices, arr in table:
        dic = {'attribute':attribute,'attributes':len(choices)}
        for key, name in choices:
            dic.update({'name':name})
            qq = q.filter(**myFilter(s,key))
            total = 0
            for e, wanda in STATE_CHOICES:
                c = qq.filter(state=e).count()
                dic.update({e:c})
                total = total + c
            dic.update({'total':total})
            arr.append(dic)
            dic = {}
                 
    for e, name in STATE_CHOICES:
        qq = q.filter(state=e)
        state.update({e:qq.count()})
    
    total = q.count()
    extras.append({
        'name':'Sin RS asoc.',
        'exCount':total - q.filter(softwarerequirement__validity=True).distinct().count()
    })
    extras.append({
        'name':'Sin TU asoc.',
        'exCount':total - q.filter(userTypes__validity=True).distinct().count()
    })
    cost = q.aggregate(Sum('cost'))['cost__sum']
    if cost == None:
        cost = 0
    extras.append({
        'name':'Costo total',
        'exCount':cost
    })
    
    ur.update({'attributes':[priority,stability,tyype]})
    ur.update({'state':state})
    ur.update({'extras':extras})
    ur.update({'total':total})
    
    # software requirement statistics
    q = SoftwareRequirement.objects.valids(project).filter(increment__validity=True)
    if ic is not None:
        q = q.filter(increment=ic)
    sr = {}
    priority = []
    stability = []
    tyype = []
    state = {}
    extras = []
    
    table = [
        ('Prioridad', 'priority', PRIORITY_CHOICES, priority),
        ('Estabilidad', 'stability', STABILITY_CHOICES, stability),
        ('Tipo', 'reqType', SR_TYPE_CHOICES, tyype),
    ]
    
    for attribute, s, choices, arr in table:
        dic = {'attribute':attribute,'attributes':len(choices)}
        for key, name in choices:
            dic.update({'name':name})
            qq = q.filter(**myFilter(s,key))
            total = 0
            for e, wanda in STATE_CHOICES:
                c = qq.filter(state=e).count()
                dic.update({e:c})
                total = total + c
            dic.update({'total':total})
            arr.append(dic)
            dic = {}
             
    for e, name in STATE_CHOICES:
        qq = q.filter(state=e)
        state.update({e:qq.count()})
    
    total = q.count()
    extras.append({
        'name':'Sin RU asoc.',
        'exCount':total - q.filter(userRequirements__validity=True).distinct().count()
    })
    extras.append({
        'name':'Sin TU asoc.',
        'exCount':total - q.filter(userTypes__validity=True).distinct().count()
    })
    cost = q.aggregate(Sum('cost'))['cost__sum']
    if cost == None:
        cost = 0
    extras.append({
        'name':'Costo total',
        'exCount':cost
    })
    
    sr.update({'attributes':[priority,stability,tyype]})
    sr.update({'state':state})
    sr.update({'extras':extras})
    sr.update({'total':total})
    
    # test case statistics
    q = TestCase.objects.valids(project).filter(requirement__validity=True)
    q_ur = q.filter(requirement__userrequirement__increment__validity=True)
    q_sr = q.filter(requirement__softwarerequirement__increment__validity=True)
    
    if ic is not None:
        q_ur = q_ur.filter(requirement__userrequirement__increment=ic)
        q_sr = q_sr.filter(requirement__softwarerequirement__increment=ic)
    tc = {}
    tyype = []
    state = {}
    extras = []
             
    dic_asoc_UR = {'name':'Asociados a RU','total':0}
    dic_asoc_SR = {'name':'Asociados a RS','total':0}
    for e, wanda in STATE_CHOICES:
        tcases_ur = q_ur.filter(state=e).count()
        tcases_sr = q_sr.filter(state=e).count()
        
        dic_asoc_UR.update({e:tcases_ur})
        dic_asoc_UR.update({'total':dic_asoc_UR['total']+tcases_ur})
        
        dic_asoc_SR.update({e:tcases_sr})
        dic_asoc_SR.update({'total':dic_asoc_SR['total']+tcases_sr})
        
        state.update({e:tcases_ur + tcases_sr})
        
    tyype.append(dic_asoc_UR)
    tyype.append(dic_asoc_SR)
    
    total = q_ur.count()+q_sr.count()
    
    extras.append({
        'name':'Sin TU asoc.',
        'exCount':total - q_ur.filter(userTypes__validity=True).distinct().count() - q_sr.filter(userTypes__validity=True).distinct().count()
    })
    
    tc.update({'attributes':[tyype]})
    tc.update({'state':state})
    tc.update({'extras':extras})
    tc.update({'total':total})
    
    # modules statistics
    q = Module.objects.valids(project)
    md = {}
    priority = []
    extras = []
    
    table = [
        ('Prioridad', 'priority', PRIORITY_CHOICES, priority),
    ]
    
    for attribute, s, choices, arr in table:
        dic = {'attribute':attribute,'attributes':len(choices)}
        for key, name in choices:
            dic.update({'name':name})
            qq = q.filter(priority=key)
            total = qq.count()
            dic.update({'total':total})
            arr.append(dic)
            dic = {}
    
    total = q.count()
    extras.append({
        'name':'Sin RS asoc.',
        'exCount':total - q.filter(softwareRequirements__validity=True).distinct().count()
    })
    cost = 0
    for dic in q.values('cost'):
        cost = cost + dic['cost']
    extras.append({
        'name':'Costo total',
        'exCount':cost
    })
    
    md.update({'attributes':[priority]})
    md.update({'extras':extras})
    md.update({'total':total})
    
    return {
        'UR':ur,
        'SR':sr,
        'TC':tc,
        'MD':md,
    }
    
def statistics(request):
    IC_CHOICES = [
        (0, "Todos"),
    ]

    user = getUserOr404(request)
    project = getProject(request)
    navbar = {'1':'tools', '2':'statistics'}
    
    if request.method == 'GET':
        increment = int(request.GET.get('increment', 0))
        icName = ''
        increments = Increment.objects.valids(project)
        for ic in increments:
            IC_CHOICES.append((ic.identifier,ic.name))
            if ic.identifier == increment:
                icName = ic.name
        if increment > 0:
            ic = increments.get(identifier=increment)
        else:# every increment
            ic = None
            
        stDic = statisticsUR_SR_TC_MD(project, ic)
    else:
        raise Http404
    context = {
        'navbar':navbar,
        'IC_CHOICES':IC_CHOICES,
        'increment':increment,
        'icName':icName,
        'UR':stDic['UR'],
        'SR':stDic['SR'],
        'MD':stDic['MD'],
        'TC':stDic['TC'],
        'helpLink':'ST',
    }
    return render(request, 'reqApp/tools/statistics/statistics.html', context)

############################## TRACEABILITY MATRICES
MATRIX_CHOICES = [
    ("ursr", "RU/RS"),
    ("mdsr", "MD/RS"),
    ("urtc", "RU/CP"),
    ("srtc", "RS/CP"),
]

MATRIX_MODELS = {
    "ursr": {"1":UserRequirement, "2":SoftwareRequirement},
    "mdsr": {"1":Module, "2":SoftwareRequirement},
    "urtc": {"1":UserRequirement, "2":TestCase},
    "srtc": {"1":SoftwareRequirement, "2":TestCase},
}

MATRIX_TEMPLATES = {
    "ursr": {"1":'reqApp/project/UR/UR.html', "2":'reqApp/project/SR/SR.html'},
    "mdsr": {"1":'reqApp/project/MD/MD.html', "2":'reqApp/project/SR/SR.html'},
    "urtc": {"1":'reqApp/project/UR/UR.html', "2":'reqApp/project/TC/TC.html'},
    "srtc": {"1":'reqApp/project/SR/SR.html', "2":'reqApp/project/TC/TC.html'},
}

def matrixSplit(rows, maxRows, maxCols):
    # useful for subdivide matrix in sectors, when they are too big to fit in a pdf page
    """
                 |abcde|             |abc|  |de|
    matrixSplit( |fghij| , 2, 3) --> |fgh|  |ij|  |klm|  |no|
                 |klmno|
    """
    if len(rows)>0:
        if len(rows[0])>0:
            hiperRows = []
            hrows = int(len(rows)/maxRows)
            if len(rows)%maxRows > 0:
                hrows = hrows + 1
            
            hcols = int(len(rows[0])/maxCols)
            if len(rows[0])%maxCols > 0:
                hcols = hcols + 1
                
            for x in range(0,hcols*hrows):
                hiperRows.append([])
                
            for r,row in enumerate(rows):
                fillingRow = []
                for c,el in enumerate(row):
                    # positioning element in the new row
                    fillingRow.append(el)
                    
                    # if row is complete or if it was the last element of the row
                    if len(fillingRow)==maxCols or (c+1)==len(row):
                        hiperRows[int((c)/maxCols)+(hcols*int((r)/maxRows))].append(fillingRow)
                        fillingRow = []
            
            return hiperRows
            
    return [rows]

def matrix(matrixType, project):
    if matrixType == 'ursr':
        m1s = UserRequirement.objects.valids(project)
        m2s = SoftwareRequirement.objects.valids(project)
        
        m2idsmatchs = []
        for row in range(0,len(m1s)):
            m2idsmatchs.append([])
            for sr in m2s.filter(userRequirements=m1s[row]):
                m2idsmatchs[row].append(sr.id)
                
        colNoIntersec = []
        for sr in m2s:
            colNoIntersec.append(len(m1s.filter(softwarerequirement=sr))==0)
    elif matrixType == 'mdsr':
        m1s = Module.objects.valids(project)
        m2s = SoftwareRequirement.objects.valids(project)
        
        m2idsmatchs = []
        for row in range(0,len(m1s)):
            m2idsmatchs.append([])
            for sr in m2s.filter(module=m1s[row]):
                m2idsmatchs[row].append(sr.id)
                
        colNoIntersec = []
        for sr in m2s:
            colNoIntersec.append(len(m1s.filter(softwareRequirements=sr))==0)
    elif matrixType == 'urtc':
        m1s = UserRequirement.objects.valids(project)
        m2s = TestCase.objects.valids(project).filter(requirement__is_UR=True)
        
        m2idsmatchs = []
        for row in range(0,len(m1s)):
            m2idsmatchs.append([])
            for tc in m2s.filter(requirement=m1s[row]):
                m2idsmatchs[row].append(tc.id)
                
        colNoIntersec = []
        for tc in m2s:
            colNoIntersec.append(len(m1s.filter(testcase=tc))==0)
    elif matrixType == 'srtc':
        m1s = SoftwareRequirement.objects.valids(project)
        m2s = TestCase.objects.valids(project).filter(requirement__is_UR=False)
        
        m2idsmatchs = []
        for row in range(0,len(m1s)):
            m2idsmatchs.append([])
            for tc in m2s.filter(requirement=m1s[row]):
                m2idsmatchs[row].append(tc.id)
                
        colNoIntersec = []
        for tc in m2s:
            colNoIntersec.append(len(m1s.filter(testcase=tc))==0)
        
    rows = []
    for row in range(0,len(m1s)):
        rows.append([])
        
        for col in range(0,len(m2s)):
            match = m2s[col].id in m2idsmatchs[row]
            row_no_intersec = (len(m2idsmatchs[row])==0)
            rows[row].append({
                'elRow':m1s[row],
                'elCol':m2s[col],
                'row':row,
                'col':col,
                'match':match,
                'never_intersec':(row_no_intersec and colNoIntersec[col]),
                'row_no_intersec':row_no_intersec,
                'col_no_intersec':colNoIntersec[col],
                })
    return rows

def matrices(request):
    user = getUserOr404(request)
    project = getProject(request)
    
    if 'getElement' in request.GET:
        matrixType = request.GET.get('matrixType', 'ursr')
        elType = request.GET.get('elType', "1")
        identifier = int(request.GET.get('identifier', 0))
        element = MATRIX_MODELS[matrixType][elType].objects.valid(project, identifier)
        if element is not None:
            return render(request, MATRIX_TEMPLATES[matrixType][elType], {'element': element})
        else:
            return HttpResponse("?")
    
    navbar = {'1':'tools', '2':'matrices'}
    
    matrixType =  request.GET.get('matrixType', 'ursr')
    filas = matrix(matrixType, project)
    context = {
        'navbar':navbar,
        'rows':filas,
        'MATRIX_CHOICES':MATRIX_CHOICES,
        'matrixType':matrixType,
        'helpLink':'matrix',
    }
    return render(request, 'reqApp/tools/matrices/matrices.html', context)

##############################  CONSISTENCY OF RELATIONS
def relationsTree(modelQSet, subModelQSet, prop, identifier):
    resp = []
    if identifier > 0:
        elements = modelQSet.filter(identifier=identifier)
    else:
        elements = modelQSet
    for e in elements:
        subElements = subModelQSet.filter(**myFilter(prop,e))
        resp.append({'element':e,'subElements':subElements})
    return resp

def consistency(request):
    CONSISTENCY_CHOICES = [
        ("ursr", "Consistencia RU/RS"),
        ("urtc", "Consistencia RU/CP"),
        ("srur", "Consistencia RS/RU"),
        ("srtc", "Consistencia RS/CP"),
        ("srmd", "Consistencia RS/MD"),
        ("mdsr", "Consistencia MD/RS"),
        ("tcur", "Consistencia CP/RU"),
        ("tcsr", "Consistencia CP/RS"),
    ]
    IDENTIFIER_CHOICES = [
        (0, "Todos"),
    ]
    templates = {
        "ursr":{'element':'reqApp/project/UR/UR.html','subElement':'reqApp/project/SR/SR.html'},
        "urtc":{'element':'reqApp/project/UR/UR.html','subElement':'reqApp/project/TC/TC.html'},
        "srur":{'element':'reqApp/project/SR/SR.html','subElement':'reqApp/project/UR/UR.html'},
        "srtc":{'element':'reqApp/project/SR/SR.html','subElement':'reqApp/project/TC/TC.html'},
        "srmd":{'element':'reqApp/project/SR/SR.html','subElement':'reqApp/project/MD/MD.html'},
        "mdsr":{'element':'reqApp/project/MD/MD.html','subElement':'reqApp/project/SR/SR.html'},
        "tcur":{'element':'reqApp/project/TC/TC.html','subElement':'reqApp/project/UR/UR.html'},
        "tcsr":{'element':'reqApp/project/TC/TC.html','subElement':'reqApp/project/SR/SR.html'},
    }
    
    user = getUserOr404(request)
    project = getProject(request)
    navbar = {'1':'tools', '2':'consistency'}
    
    if request.method == 'GET':
        consistencyType =  request.GET.get('consistency', 'ursr')
        identifier = int(request.GET.get('identifier', 0))
        
        actualOrder = 'identifier'
        if 'order' in request.GET:
            actualOrder = request.GET['order']
        
        elements = []
        if consistencyType == 'ursr':
            model = UserRequirement
            modeloQ = UserRequirement.objects.valids(project)
            subModeloQ = SoftwareRequirement.objects.valids(project)
            prop = 'userRequirements'
        elif consistencyType == 'urtc':
            model = UserRequirement
            modeloQ = UserRequirement.objects.valids(project)
            subModeloQ = TestCase.objects.valids(project)
            prop = 'requirement'
        elif consistencyType == 'srur':
            model = SoftwareRequirement
            modeloQ = SoftwareRequirement.objects.valids(project)
            subModeloQ = UserRequirement.objects.valids(project)
            prop = 'softwarerequirement'
        elif consistencyType == 'srtc':
            model = SoftwareRequirement
            modeloQ = SoftwareRequirement.objects.valids(project)
            subModeloQ = TestCase.objects.valids(project)
            prop = 'requirement'
        elif consistencyType == 'srmd':
            model = SoftwareRequirement
            modeloQ = SoftwareRequirement.objects.valids(project)
            subModeloQ = Module.objects.valids(project)
            prop = 'softwareRequirements'
        elif consistencyType == 'mdsr':
            model = Module
            modeloQ = Module.objects.valids(project)
            subModeloQ = SoftwareRequirement.objects.valids(project)
            prop = 'module'
        elif consistencyType == 'tcur':
            model = TestCase
            modeloQ = TestCase.objects.valids(project).filter(requirement__is_UR=True)
            subModeloQ = UserRequirement.objects.valids(project)
            prop = 'testcase'
        elif consistencyType == 'tcsr':
            model = TestCase
            modeloQ = TestCase.objects.valids(project).filter(requirement__is_UR=False)
            subModeloQ = SoftwareRequirement.objects.valids(project)
            prop = 'testcase'
        else:
            raise Http404
            
        # generate list of identifier texts of type of elements selected
        identifierDict = {}
        elements = modeloQ
        for element in elements:
            # name of most recent identifier
            identifierDict.update({element.identifier: element.identifierText()+" "+element.name})
        for key in sorted(identifierDict):
            IDENTIFIER_CHOICES.append((key, identifierDict[key]))
            
        elements = relationsTree(modeloQ.order_by(actualOrder,'identifier'), subModeloQ, prop, identifier)
        
    else:
        raise Http404
    
    context = {
        'navbar':navbar,
        'elements':elements,
        'templates':templates[consistencyType],
        'CONSISTENCY_CHOICES':CONSISTENCY_CHOICES,
        'IDENTIFIER_CHOICES':IDENTIFIER_CHOICES,
        'consistency':consistencyType,
        'identifier':identifier,
        'helpLink':'cons',
    }
    
    if identifier == 0:
        context.update({
            'ordering_attributes': orderingList(model),
            'actual_order': actualOrder,
            'ordering_bar': 'reqApp/orderingBar.html',
        })
    
    return render(request, 'reqApp/tools/consistency/consistency.html', context)

##############################  REGISTRY
def registry(request):
    REGISTRY_CHOICES = [
        ("ic", "Hitos"),
        ("ut", "Tipos de Usuario"),
        ("ur", "Requisitos de Usuario"),
        ("sr", "Requisitos de Software"),
        ("md", "Módulos"),
        ("tc", "Casos de Prueba"),
    ]
    IDENTIFIER_CHOICES = [
        (0, "Todos"),
    ]
    models = {
        "ic": Increment,
        "ut": UserType,
        "ur": UserRequirement,
        "sr": SoftwareRequirement,
        "md": Module,
        "tc": TestCase,
    }
    templates = {
        "ic": 'reqApp/project/IC/IC.html',
        "ut": 'reqApp/project/UT/UT.html',
        "ur": 'reqApp/project/UR/UR.html',
        "sr": 'reqApp/project/SR/SR.html',
        "md": 'reqApp/project/MD/MD.html',
        "tc": 'reqApp/project/TC/TC.html',    
    }
    
    user = getUserOr404(request)
    project = getProject(request)
    navbar = {'1':'tools', '2':'registry'}
    
    if request.method == 'GET':
        registryType =  request.GET.get('registryType', 'ur')
        
        identifier = int(request.GET.get('identifier', 0))
        
        # make list of identifier texts for elements of selected registry type
        identifierDict = {}
        elements = models[registryType].objects.registered(project)
        for element in reversed(elements):
            # most recent identifier name
            identifierDict.update({element.identifier: element.identifierText()+" "+element.name})
        
        for key in sorted(identifierDict):
            IDENTIFIER_CHOICES.append((key, identifierDict[key]))
            
        if identifier > 0:
            # show the temporal evolution of this element
            elements = models[registryType].objects.registered(project, identifier)
        
        # generate list of elements registered
        elemList = []
        elemDic = {}
        i = 0
        for element in elements:
            deleted = False
            kei = element.identifierText()
            if (kei not in elemDic) and (element.validity == False):
                deleted = True
            elemDic.update({kei:i})
            elemList.append({'element':element, 'actual':element.validity, 'deleted':deleted, 'new':False})
            i = i + 1
        
        for key in elemDic:
            elemList[elemDic[key]]['new'] = True
    else:
        raise Http404
    
    context = {
        'navbar':navbar,
        'elements':elemList,
        'template':templates[registryType],
        'REGISTRY_CHOICES':REGISTRY_CHOICES,
        'IDENTIFIER_CHOICES':IDENTIFIER_CHOICES,
        'registryType':registryType,
        'identifier':identifier,
        'helpLink':'reg',
    }
    return render(request, 'reqApp/tools/registry/registry.html', context)
    
############################### Documents MCE ##########################
import os
from django.conf import settings
from django.core.files.storage import default_storage
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

#@csrf_exempt
@require_POST
def imgUpload(request):
    user = getUserOr404(request)
    project = getProject(request)
    
    upload_path = getattr(settings, 'IMAGES_UPLOAD', 'uploads/') + str(project.id) +'/'
    form = MceImageForm(request.POST, request.FILES)
    if form.is_valid():
        file_ = form.cleaned_data['file']
        path = os.path.join(upload_path, file_.name)
        real_path = default_storage.save(path, file_)
        media_path = real_path[real_path.find('uploads/'):]
        return HttpResponse(
            os.path.join(settings.MEDIA_URL, media_path)
        )
    return HttpResponse('')
    
############################### PDF ##########################
from django.template.loader import get_template
from django.template import Context
import xhtml2pdf.pisa as pisa
import cStringIO as StringIO

def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    context = Context(context_dict)
    html  = template.render(context)
    result = StringIO.StringIO()
    pdf = pisa.pisaDocument(StringIO.StringIO(html.encode("UTF-8")), result)# ...ISO-8859-1...UTF-8...latin-1... html.encode("ISO-8859-1")
    if not pdf.err:
        resp = HttpResponse(result.getvalue(), mimetype='application/pdf')
        resp['Content-Disposition'] = u'filename='+context_dict['fileName']+u'.pdf'
        return resp
    return HttpResponse('We had some errors!')
        
def pdf(request):
    user = getUserOr404(request)
    project = getProject(request)
    host = getHost(request)#request.build_absolute_uri("/")[:-1]# http://localhost:8000
    context = {
        'pagesize':'letter',# https://github.com/chrisglass/xhtml2pdf/blob/master/doc/usage.rst#supported-page-properties-and-values
        'title':'',
        'fileName':'',
        'host':host,
        'project':project,
        'today':timezone.now(),
    }
    
    # max width and height in monospaced chars for 'matrixSplit()'
    # WARNING: these values should be reassigned if pagesize (letter, A4, ...) is changed
    WIDTH_MTs = 69
    HEIGHT_MTs = 69
    
    if request.method == 'GET':
        pdfType =  request.GET.get('pdfType', '')
        if pdfType == 'docReq':
            template = 'reqApp/pdf/documents/requirements.html'
            sections = [
                {'title':'<h1>1. Introducción</h1>',            'obj':DocumentSection.objects.valid(project,'introduction')},
                {'title':'<h2>1.1. Propósito</h2>',             'obj':DocumentSection.objects.valid(project,'purpose')},
                {'title':'<h2>1.2. Alcance</h2>',               'obj':DocumentSection.objects.valid(project,'scope')},
                {'title':'<h2>1.3. Contexto</h2>',              'obj':DocumentSection.objects.valid(project,'context')},
                {'title':'<h2>1.4. Definiciones</h2>',          'obj':DocumentSection.objects.valid(project,'definitions')},
                {'title':'<h2>1.5. Referencias</h2>',           'obj':DocumentSection.objects.valid(project,'references')},
                {'title':'<h2>1.6. Equipo Desarrollador y Contraparte</h2>','obj':DocumentSection.objects.valid(project,'project_members')},
                {'title':'<h1>2. Descripción General</h1>',     'obj':DocumentSection.objects.valid(project,'general_description')},
                {'title':'<h2>2.1. Usuarios</h2>',              'obj':DocumentSection.objects.valid(project,'users')},
                {'title':'<h2>2.2. Producto</h2>',              'obj':DocumentSection.objects.valid(project,'product')},
                {'title':'<h2>2.3. Ambiente</h2>',              'obj':DocumentSection.objects.valid(project,'environment')},
                {'title':'<h2>2.4. Proyectos Relacionados</h2>','obj':DocumentSection.objects.valid(project,'related_projects')},
            ]
            
            
            context.update({
                'title':'Documento de Especificación de Requisitos de Usuario/Software',
                'fileName':'Documento_de_Requisitos',
                'sections':sections,
                'URs':UserRequirement.objects.valids(project,'reqType'),
                'SRs':SoftwareRequirement.objects.valids(project,'reqType'),
                'MTs':[{
                    'name':'RU/RS',
                    'subMTs':matrixSplit(matrix('ursr',project), HEIGHT_MTs, WIDTH_MTs)
                    }],
            })
        elif pdfType == 'docDsn':
            template = 'reqApp/pdf/documents/design.html'
            sections = [
                {'title':'<h1>1. Introducción</h1>',            'obj':DocumentSection.objects.valid(project,'introduction')},
                {'title':'<h2>1.1. Propósito</h2>',             'obj':DocumentSection.objects.valid(project,'purpose')},
                {'title':'<h2>1.2. Alcance</h2>',               'obj':DocumentSection.objects.valid(project,'scope')},
                {'title':'<h2>1.3. Contexto</h2>',              'obj':DocumentSection.objects.valid(project,'context')},
                {'title':'<h2>1.4. Definiciones</h2>',          'obj':DocumentSection.objects.valid(project,'definitions')},
                {'title':'<h2>1.5. Referencias</h2>',           'obj':DocumentSection.objects.valid(project,'references')},
                {'title':'<h2>1.6. Equipo Desarrollador y Contraparte</h2>','obj':DocumentSection.objects.valid(project,'project_members')},
                {'title':'<h1>2. Descripción General</h1>',     'obj':DocumentSection.objects.valid(project,'general_description')},
                
                {'title':'<h1>3. Diseño</h1>',                  'obj':DocumentSection.objects.valid(project,'design')},
                {'title':'<h2>3.1. Arquitectura Física</h2>',   'obj':DocumentSection.objects.valid(project,'physical_architecture')},
                {'title':'<h2>3.2. Arquitectura Lógica</h2>',   'obj':DocumentSection.objects.valid(project,'logical_architecture')},
                {'title':'<h2>3.3. Modelo de Datos</h2>',       'obj':DocumentSection.objects.valid(project,'model')},
                
                {'title':'<h2>3.4. Detalle Módulos</h2>',       'obj':DocumentSection.objects.valid(project,'detailed_modules')},
                {'title':'<h2>3.5. Navegación</h2>',            'obj':DocumentSection.objects.valid(project,'navigation')},
                {'title':'<h2>3.6. Interfaz</h2>',              'obj':DocumentSection.objects.valid(project,'interface')},
            ]
            
            context.update({
                'title':'Documento de Diseño',
                'fileName':'Documento_de_Diseno',
                'sections':sections,
                'MDs':Module.objects.valids(project),
                'MTs':[{
                    'name':'MD/RS',
                    'subMTs':matrixSplit(matrix('mdsr',project), HEIGHT_MTs, WIDTH_MTs)
                    }],
            })
        elif pdfType == 'docTC':
            template = 'reqApp/pdf/documents/tc.html'
            sections = [
                {'title':'<h1>1. Introducción</h1>',            'obj':DocumentSection.objects.valid(project,'introduction')},
                {'title':'<h2>1.1. Propósito</h2>',             'obj':DocumentSection.objects.valid(project,'purpose')},
                {'title':'<h2>1.2. Alcance</h2>',               'obj':DocumentSection.objects.valid(project,'scope')},
                {'title':'<h2>1.3. Contexto</h2>',              'obj':DocumentSection.objects.valid(project,'context')},
                {'title':'<h2>1.4. Definiciones</h2>',          'obj':DocumentSection.objects.valid(project,'definitions')},
                {'title':'<h2>1.5. Referencias</h2>',           'obj':DocumentSection.objects.valid(project,'references')},
                {'title':'<h2>1.6. Equipo Desarrollador y Contraparte</h2>','obj':DocumentSection.objects.valid(project,'project_members')},
                {'title':'<h1>2. Descripción General</h1>',     'obj':DocumentSection.objects.valid(project,'general_description')},
                {'title':'<h2>2.1. Usuarios</h2>',              'obj':DocumentSection.objects.valid(project,'users')},
                {'title':'<h2>2.2. Producto</h2>',              'obj':DocumentSection.objects.valid(project,'product')},
                {'title':'<h2>2.3. Ambiente</h2>',              'obj':DocumentSection.objects.valid(project,'environment')},
                {'title':'<h2>2.4. Proyectos Relacionados</h2>','obj':DocumentSection.objects.valid(project,'related_projects')},
            ]
            
            
            context.update({
                'title':'Documento de Casos de Prueba',
                'fileName':'Documento_Casos_de_Prueba',
                'sections':sections,
                'URs':UserRequirement.objects.valids(project,'reqType'),
                'SRs':SoftwareRequirement.objects.valids(project,'reqType'),
                'TCs':TestCase.objects.valids(project),
                'MTs':[{
                    'name':'RU/RS',
                    'subMTs':matrixSplit(matrix('ursr',project), HEIGHT_MTs, WIDTH_MTs)
                    },{
                    'name':'RU/CP',
                    'subMTs':matrixSplit(matrix('urtc',project), HEIGHT_MTs, WIDTH_MTs)
                    },{
                    'name':'RS/CP',
                    'subMTs':matrixSplit(matrix('srtc',project), HEIGHT_MTs, WIDTH_MTs)
                    }],
            })
        elif pdfType == 'docHis':
            template = 'reqApp/pdf/documents/historic.html'
            sections = [
                {'title':'<h1>1. Introducción</h1>',            'obj':DocumentSection.objects.valid(project,'introduction')},
                {'title':'<h2>1.1. Propósito</h2>',             'obj':DocumentSection.objects.valid(project,'purpose')},
                {'title':'<h2>1.2. Alcance</h2>',               'obj':DocumentSection.objects.valid(project,'scope')},
                {'title':'<h2>1.3. Contexto</h2>',              'obj':DocumentSection.objects.valid(project,'context')},
                {'title':'<h2>1.4. Definiciones</h2>',          'obj':DocumentSection.objects.valid(project,'definitions')},
                {'title':'<h2>1.5. Referencias</h2>',           'obj':DocumentSection.objects.valid(project,'references')},
                {'title':'<h2>1.6. Equipo Desarrollador y Contraparte</h2>','obj':DocumentSection.objects.valid(project,'project_members')},
                {'title':'<h1>2. Descripción General</h1>',     'obj':DocumentSection.objects.valid(project,'general_description')},
                {'title':'<h2>2.1. Usuarios</h2>',              'obj':DocumentSection.objects.valid(project,'users')},
                {'title':'<h2>2.2. Producto</h2>',              'obj':DocumentSection.objects.valid(project,'product')},
                {'title':'<h2>2.3. Ambiente</h2>',              'obj':DocumentSection.objects.valid(project,'environment')},
                {'title':'<h2>2.4. Proyectos Relacionados</h2>','obj':DocumentSection.objects.valid(project,'related_projects')},
                {'title':'<h1>3. Diseño</h1>',                  'obj':DocumentSection.objects.valid(project,'design')},
                {'title':'<h2>3.1. Arquitectura Física</h2>',   'obj':DocumentSection.objects.valid(project,'physical_architecture')},
                {'title':'<h2>3.2. Arquitectura Lógica</h2>',   'obj':DocumentSection.objects.valid(project,'logical_architecture')},
                {'title':'<h2>3.3. Modelo de Datos</h2>',       'obj':DocumentSection.objects.valid(project,'model')},
                {'title':'<h2>3.4. Detalle Módulos</h2>',       'obj':DocumentSection.objects.valid(project,'detailed_modules')},
                {'title':'<h2>3.5. Navegación</h2>',            'obj':DocumentSection.objects.valid(project,'navigation')},
                {'title':'<h2>3.6. Interfaz</h2>',              'obj':DocumentSection.objects.valid(project,'interface')},
            ]
            
            matrices = []
            for mtType,name in MATRIX_CHOICES:
                matrices.append({
                    'name':name,
                    'subMTs':matrixSplit(matrix(mtType,project), HEIGHT_MTs, WIDTH_MTs)
                })
                
            context.update({
                'title':'Documento Histórico',
                'fileName':'Documento_Historico',
                'sections':sections,
                'URs':UserRequirement.objects.valids(project,'reqType'),
                'SRs':SoftwareRequirement.objects.valids(project,'reqType'),
                'TCs':TestCase.objects.valids(project),
                'MDs':Module.objects.valids(project),
                'MTs':matrices,
            })
        elif pdfType == 'UR':
            template = 'reqApp/pdf/project/UR/UR.html'
            context.update({
                'title':'Requisitos de Usuario',
                'fileName':'Lista_Requisitos_de_Usuario',
                'URs':UserRequirement.objects.valids(project,'reqType'),
            })
        elif pdfType == 'SR':
            template = 'reqApp/pdf/project/SR/SR.html'
            context.update({
                'title':'Requisitos de Software',
                'fileName':'Lista_Requisitos_de_Software',
                'SRs':SoftwareRequirement.objects.valids(project,'reqType'),
            })
        elif pdfType == 'UT':
            template = 'reqApp/pdf/project/UT/UT.html'
            context.update({
                'title':'Tipos de Usuario',
                'fileName':'Lista_Tipos_de_Usuario',
                'UTs':UserType.objects.valids(project),
            })
        elif pdfType == 'MD':
            template = 'reqApp/pdf/project/MD/MD.html'
            context.update({
                'title':'Módulos',
                'fileName':'Lista_Modulos',
                'MDs':Module.objects.valids(project),
            })
        elif pdfType == 'TC':
            template = 'reqApp/pdf/project/TC/TC.html'
            context.update({
                'title':'Casos de Prueba',
                'fileName':'Lista_Casos_de_Prueba',
                'TCs':TestCase.objects.valids(project),
            })
        elif pdfType == 'IC':
            template = 'reqApp/pdf/project/IC/IC.html'
            context.update({
                'title':'Hitos',
                'fileName':'Lista_Hitos',
                'ICs':Increment.objects.valids(project),
            })
        elif pdfType == 'MT':
            template = 'reqApp/pdf/tools/matrices/MT.html'
            matrices = []
            
            for mtType,name in MATRIX_CHOICES:
                matrices.append({
                    'name':name,
                    'subMTs':matrixSplit(matrix(mtType,project), HEIGHT_MTs, WIDTH_MTs)
                })
                
            context.update({
                'title':'Matrices de Trazado',
                'fileName':'Matrices_de_Trazado',
                'MTs':matrices,
            })
        elif pdfType == 'ST': # statistics
            template = 'reqApp/pdf/tools/statistics/statistics.html'
            
            increments = Increment.objects.valids(project)
            sTs = []
            
            st = statisticsUR_SR_TC_MD(project)
            sTs.append({
                'title':'Estadísticas de Todo el Proyecto',
                'UR':st['UR'],
                'SR':st['SR'],
                'TC':st['TC'],
                'MD':st['MD'],
            })
            
            for ic in increments:
                st = statisticsUR_SR_TC_MD(project, ic)
                sTs.append({
                    'title':u'Estadísticas '+ic.name,
                    'UR':st['UR'],
                    'SR':st['SR'],
                    'TC':st['TC'],
                    #'MD':st['MD'], # modules don't have a particular increment asociated
                })
            
            context.update({
                'title':'Estadísticas del Proyecto',
                'fileName':'Estadisticas',
                'STs':sTs,
            })
        elif pdfType == 'CT':
            template = 'reqApp/pdf/tools/consistency/consistency.html'
            
            cTs = {
                'ursr':{
                'title':'RU/RS',
                'fileName':'Documento_de_Consistencia_RU-RS',
                'template1':'reqApp/pdf/project/UR/ur.html',
                'template2':'reqApp/pdf/project/SR/sr.html',
                'elements':relationsTree(UserRequirement.objects.valids(project)
                                            , SoftwareRequirement.objects.valids(project)
                                            , 'userRequirements', 0)
                },
                'urtc':{
                'title':'RU/CP',
                'fileName':'Documento_de_Consistencia_RU-CP',
                'template1':'reqApp/pdf/project/UR/ur.html',
                'template2':'reqApp/pdf/project/TC/tc.html',
                'elements':relationsTree(UserRequirement.objects.valids(project)
                                            , TestCase.objects.valids(project)
                                            , 'requirement', 0)
                },
                'srur':{
                'title':'RS/RU',
                'fileName':'Documento_de_Consistencia_RS-RU',
                'template1':'reqApp/pdf/project/SR/sr.html',
                'template2':'reqApp/pdf/project/UR/ur.html',
                'elements':relationsTree(SoftwareRequirement.objects.valids(project)
                                            , UserRequirement.objects.valids(project)
                                            , 'softwarerequirement', 0)
                },
                'srtc':{
                'title':'RS/CP',
                'fileName':'Documento_de_Consistencia_RS-CP',
                'template1':'reqApp/pdf/project/SR/sr.html',
                'template2':'reqApp/pdf/project/TC/tc.html',
                'elements':relationsTree(SoftwareRequirement.objects.valids(project)
                                            , TestCase.objects.valids(project)
                                            , 'requirement', 0)
                },
                'srmd':{
                'title':'RS/MD',
                'fileName':'Documento_de_Consistencia_RS-MD',
                'template1':'reqApp/pdf/project/SR/sr.html',
                'template2':'reqApp/pdf/project/MD/md.html',
                'elements':relationsTree(SoftwareRequirement.objects.valids(project)
                                            , Module.objects.valids(project)
                                            , 'softwareRequirements', 0)
                },
                'mdsr':{
                'title':'MD/RS',
                'fileName':'Documento_de_Consistencia_MD-RS',
                'template1':'reqApp/pdf/project/MD/md.html',
                'template2':'reqApp/pdf/project/SR/sr.html',
                'elements':relationsTree(Module.objects.valids(project)
                                            , SoftwareRequirement.objects.valids(project)
                                            , 'module', 0)
                },
                'tcur':{
                'title':'CP/RU',
                'fileName':'Documento_de_Consistencia_CP-RU',
                'template1':'reqApp/pdf/project/TC/tc.html',
                'template2':'reqApp/pdf/project/UR/ur.html',
                'elements':relationsTree(TestCase.objects.valids(project).filter(requirement__is_UR=True)
                                            , UserRequirement.objects.valids(project)
                                            , 'testcase', 0)
                },
                'tcsr':{
                'title':'CP/RS',
                'fileName':'Documento_de_Consistencia_CP-RS',
                'template1':'reqApp/pdf/project/TC/tc.html',
                'template2':'reqApp/pdf/project/SR/sr.html',
                'elements':relationsTree(TestCase.objects.valids(project).filter(requirement__is_UR=False)
                                            , SoftwareRequirement.objects.valids(project)
                                            , 'testcase', 0)
                },
            }
            consistency = request.GET.get('consistency', 'ursr')
            context.update({
                'title':u'Documento de Consistencia '+cTs[consistency]['title'],
                'fileName':cTs[consistency]['fileName'],
                'CTs':cTs[consistency],
            })
        else:
            raise Http404
    else:
        raise Http404
    return render_to_pdf(template,context)
    
############################### HELP ##########################
def help(request):
    context = {}# 'helpLink'
    return render(request, 'reqApp/help.html', context)
