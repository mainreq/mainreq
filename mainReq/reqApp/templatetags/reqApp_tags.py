# -*- encoding: utf-8 -*-
from django import template
from reqApp.models import *
from reqApp.choices import *
from reqApp.util import *
from reqApp.alarms import *

register = template.Library()

@register.filter(name="userProject")
def userProject(request):
    return getProject(request)

@register.filter(name="priority")
def priority(element):
    for key,val in PRIORITY_CHOICES:
        if key == element.priority:
            return val
            
@register.filter(name="stability")
def stability(element):
    for key,val in STABILITY_CHOICES:
        if key == element.stability:
            return val
            
@register.filter(name="URType")
def URType(element):
    for key,val in UR_TYPE_CHOICES:
        if key == element.reqType:
            return val
            
@register.filter(name="SRType")
def SRType(element):
    for key,val in SR_TYPE_CHOICES:
        if key == element.reqType:
            return val
            
@register.filter(name="reqType")
def reqType(req):
    if req.is_UR:
        for key,val in UR_TYPE_CHOICES:
            if key == req.reqType:
                return val
    else:
        for key,val in SR_TYPE_CHOICES:
            if key == req.reqType:
                return val
            
@register.filter(name="state")
def state(element):
    for key,val in STATE_CHOICES:
        if key == element.state:
            return val
    return '?'
    
@register.filter(name="taskState")
def taskState(task):
    for key,val in TASK_CHOICES:
        if key == task.state:
            return val
    return '?'
    
@register.filter(name="showTaskButton")
def showTaskButton(task, button):
    state = task.state
    if button == 'discarded':
        return state == 't1_to_do' or state == 't2_done' or state == 't3_not_done'
    if button == 'reprobate':
        return state == 't2_done'
    if button == 'done':
        return state == 't1_to_do'

@register.filter(name="taskState2CssClass")
def taskState2CssClass(task):
    css = {
        "t1_to_do":"to_do",
        "t2_done":"done",
        "t3_not_done":"not_done",
        "t4_approved":"approved",
        "t5_reprobate":"reprobate",
        "t6_discarded":"discarded",
    }
    return css[task.state]
        
@register.filter(name="secondsToDeadline")
def secondsToDeadline(task):
    if task.state == 't1_to_do':
        dt = task.deadlineDate - timezone.now()
        dt = dt.total_seconds()
        if dt > 0:
            return dt
    return 0
    
@register.filter(name="daysHoursToDeadline")
def daysHoursToDeadline(task):
    dt = task.deadlineDate - task.initDate
    days = dt.days
    hours = int(dt.seconds/3600.0)
    minutes = int(dt.seconds%3600.0 / 60)
    return (u"%sd, %sh y %sm" % (days, hours, minutes))
            
@register.filter(name="enlistValids")
def enlistValids(queryList):
    return queryList.filter(validity=True).order_by('identifier')
    
@register.filter(name="enlistRegistered")
def enlistRegistered(queryList):
    return queryList.order_by('identifier')
    
@register.filter(name="listLen")
def listLen(li):
    return len(li)
    
@register.filter(name="listCount")
def listCount(li):
    return li.count()
    
@register.filter(name="splitBy")
def splitBy(s, token):
    s = s.strip()
    if s == '':
        return []
    return s.split(token)
    
@register.filter(name="invertOrder")
def invertOrder(order):
    if order[0] == '-':
        return order[1:]
    else:
        return '-'+order

@register.filter(name="concat")
def concat(s1,s2):
    return str(s1)+str(s2)

@register.filter(name="percentage")
def percentage(total, part):
    if total == 0:
        return "0%"
    return ("%3.0f" % (100*part/total)) + "%"
    
@register.filter(name="addSrcHost")
def addSrcHost(htmlCode,host):
    # append host to src of images and other resources (necessary for pdf images rendering)
    return htmlCode.replace('src="/','src="'+host+'/').replace("src='/","src='"+host+"/")
    
@register.filter(name="textTableHorizHeaders")
def textTableHorizHeaders(rows):
    if len(rows)>0:
        if len(rows[0])>0:
            firstRow = rows[0]
            pref = '|'
            hr = '|'
            rti = firstRow[0]['elRow'].identifierText()
            for x in range(0, len(rti)):
                pref = '<span style="color:White;">o</span>'+pref
                hr = '-'+hr
            hText = []
            for c in firstRow[0]['elCol'].identifierText():
                hText.append('')
            for e in firstRow:
                for i,c in enumerate(e['elCol'].identifierText()):
                    hText[i] = hText[i] + '<span class="' + e['elCol'].state + '">' + c + '</span>'
            out = ''
            hrlen = 0
            for r in hText:
                hrlen = len(r)
                out = (out + pref + r + '<br/>')
            for x in range(0,len(firstRow)):
                hr = hr + '-'
            out = out + hr + '<br/>'
            
            return out
    return '---'

@register.filter(name="verticalLabel")
def verticalLabel(label):
    vLabel = ""
    for c in label:
        vLabel = vLabel + c + "<br/>"# "&#013;"
    return vLabel

@register.filter(name="alarms")
def alarms(el):
    return elementAlarms(el)
    
@register.filter(name="attr")
def attr(field, attrs):
    attrsDic = {}
    attrsList = []
    
    attrs = attrs.strip()
    attrs = attrs.split(',')
    
    for attr in attrs:
        key,val = attr.split(':')
        attrsDic.update({key.strip():val.strip()})
    
    return field.as_widget(attrs=attrsDic)
