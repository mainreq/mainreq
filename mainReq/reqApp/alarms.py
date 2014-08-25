# -*- encoding: utf-8 -*-
from reqApp.models import *

def elementAlarms(el):
    resp = []
    if el.validity == False:
        # only check valid elements alarms
        return False
    elif el.__class__ == Increment:
        if UserRequirement.objects.valids(el.project).filter(increment=el).count() == 0:
            resp.append("Este Hito no ha sido asignado a ningún Requisito de Usuario")
        #--------------------------------------------------------------------------------------------
        elif SoftwareRequirement.objects.valids(el.project).filter(increment=el).count() == 0:
            resp.append("Este Hito no ha sido asignado a ningún Requisito de Software")
        #--------------------------------------------------------------------------------------------
    elif el.__class__ == UserType:
        if UserRequirement.objects.valids(el.project).filter(userTypes=el).count() == 0:
            resp.append("Este Tipo de Usuario no ha sido asociado a ningún Requisito de Usuario")
        #--------------------------------------------------------------------------------------------
        elif SoftwareRequirement.objects.valids(el.project).filter(userTypes=el).count() == 0:
            resp.append("Este Tipo de Usuario no ha sido asociado a ningún Requisito de Software")
        #--------------------------------------------------------------------------------------------
        elif TestCase.objects.valids(el.project).filter(userTypes=el).count() == 0:
            resp.append("Este Tipo de Usuario no ha sido asociado a ningún Caso de Prueba")
        #--------------------------------------------------------------------------------------------
    elif el.__class__ == UserRequirement:
        if el.increment.validity == False:
            resp.append("El Hito asignado a este Requisito de Usuario ha sido eliminado")
        #--------------------------------------------------------------------------------------------
        srCount = SoftwareRequirement.objects.valids(el.project).filter(userRequirements=el).count()
        if srCount == 0:
            resp.append("No tiene ningún Requisito de Software asociado")
        #--------------------------------------------------------------------------------------------
        else:
            if srCount > 5:
                resp.append("Tiene más de 5 Requisitos de Software asociados (puede ser muy complejo y quizás deba ser dividido)")
        #--------------------------------------------------------------------------------------------
            srs = SoftwareRequirement.objects.valids(el.project).filter(userRequirements=el)
            dummyPriority = ''
            minPriority = dummyPriority
            for sr in srs:
                if sr.priority > minPriority:
                    minPriority = sr.priority
            if minPriority != dummyPriority and el.priority > minPriority:
                resp.append("Su prioridad es menor que la prioridad más baja de sus Requisitos de Software asociados")
        #--------------------------------------------------------------------------------------------
            if el.stability == 'non_negotiable':
                q = SoftwareRequirement.objects.valids(el.project).filter(userRequirements=el)
                if q.count() == q.filter(stability='negotiable').count():
                    resp.append("Su estabilidad es intransable, sin embargo todos sus Requisitos de Software asociados son transables")
        #--------------------------------------------------------------------------------------------
            notConsideredUT = el.userTypes.filter(validity=True).exclude(softwarerequirement=SoftwareRequirement.objects.valids(el.project).filter(userRequirements=el))
            c = 0
            s = "( "
            for ut in notConsideredUT:
                c = c + 1
                s = s + ut.identifierText() + " "
            s = s + ")"
            if c > 0:
                resp.append("Uno de sus Tipos de Usuario " + s + " no se encuentra asociado a ninguno de sus Requisitos de Software")
        #--------------------------------------------------------------------------------------------
        if el.state == 'fails':
            srs = SoftwareRequirement.objects.valids(el.project).filter(userRequirements=el)
            srsCount = srs.count()
            if srsCount > 0 and srsCount == srs.filter(state='satisfy').count():
                resp.append("Su estado es No Cumple, pero todos sus Requisitos de Software asociados Cumplen")
        #--------------------------------------------------------------------------------------------
            tcs = TestCase.objects.valids(el.project).filter(requirement=el)
            tcsCount = tcs.count()
            if tcsCount > 0 and tcsCount == tcs.filter(state='satisfy').count():
                resp.append("Su estado es No Cumple, pero todos sus Casos de Prueba asociados Cumplen")
        #--------------------------------------------------------------------------------------------
        elif el.state == 'satisfy':
            srs = SoftwareRequirement.objects.valids(el.project).filter(userRequirements=el)
            srsCount = srs.count()
            if srsCount > 0 and srs.filter(state='satisfy').count() == 0:
                resp.append("Su estado es Cumple, pero ninguno de sus Requisitos de Software asociados Cumplen")
        #--------------------------------------------------------------------------------------------
            tcs = TestCase.objects.valids(el.project).filter(requirement=el)
            tcsCount = tcs.count()
            if tcsCount > 0 and tcs.filter(state='satisfy').count() == 0:
                resp.append("Su estado es Cumple, pero ninguno de sus Casos de Prueba asociados Cumplen")
        #--------------------------------------------------------------------------------------------
        """
        if el.userTypes.all().filter(validity=True).count() == 0:
            resp.append("No tiene ningún Tipo de Usuario asociado")
        """
        #--------------------------------------------------------------------------------------------
    elif el.__class__ == SoftwareRequirement:
        if el.increment.validity == False:
            resp.append("El Hito asignado a este Requisito de Software ha sido eliminado")
        #--------------------------------------------------------------------------------------------
        elif el.userRequirements.filter(validity=True).filter(increment=el.increment).count() == 0:
            resp.append("Su Hito no corresponde con ningún Hito asociado a sus Requisitos de Usuario")
        #--------------------------------------------------------------------------------------------
        urCount = el.userRequirements.filter(validity=True).count()
        if urCount == 0:
            resp.append("No tiene ningún Requisito de Usuario asociado")
        #--------------------------------------------------------------------------------------------
        else:
            if urCount > 3:
                resp.append("Tiene más de 3 Requisitos de Usuario asociados (puede ser muy complejo y quizás deba ser dividido)")
        #--------------------------------------------------------------------------------------------
            urs = el.userRequirements.filter(validity=True)
            dummyPriority = 'p99_'
            maxPriority = dummyPriority
            for ur in urs:
                if ur.priority < maxPriority:
                    maxPriority = ur.priority
            if maxPriority != dummyPriority and el.priority < maxPriority:
                resp.append("Su prioridad es mayor que la prioridad más alta de sus Requisitos de Usuario asociados")
        #--------------------------------------------------------------------------------------------
            if el.stability == 'non_negotiable':
                if urCount > 0 and urCount == el.userRequirements.filter(validity=True).filter(stability='negotiable').count():
                    resp.append("Su estabilidad es intransable, sin embargo todos sus Requisitos de Usuario son transables")
        #--------------------------------------------------------------------------------------------
            urs = el.userRequirements.filter(validity=True).filter(date__gte=el.date)
            c = 0
            s = "( "
            for ur in urs:
                c = c + 1
                s = s + ur.identifierText() + " "
            s = s + ")"
            if c > 0:
                resp.append("Un Requisito de Usuario asociado " + s + u" ha sido modificado (su fecha de modificación es posterior a la de este Requisito de Software, favor revisar y actualizar)")
        #--------------------------------------------------------------------------------------------
            notConsideredUT = el.userTypes.filter(validity=True).exclude(userrequirement=el.userRequirements.filter(validity=True))
            c = 0
            s = "( "
            for ut in notConsideredUT:
                c = c + 1
                s = s + ut.identifierText() + " "
            s = s + ")"
            if c > 0:
                resp.append("Uno de sus Tipos de Usuario " + s + " no se encuentra asociado a ninguno de sus Requisitos de Usuario")
        #--------------------------------------------------------------------------------------------
        if Module.objects.valids(el.project).filter(softwareRequirements=el).count() == 0:
            resp.append("No tiene ningún Módulo asociado")
        #--------------------------------------------------------------------------------------------
        if el.state == 'fails':
            tcs = TestCase.objects.valids(el.project).filter(requirement=el)
            tcsCount = tcs.count()
            if tcsCount > 0 and tcsCount == tcs.filter(state='satisfy').count():
                resp.append("Su estado es No Cumple, pero todos sus Casos de Prueba asociados Cumplen")
        #--------------------------------------------------------------------------------------------
        elif el.state == 'satisfy':
            tcs = TestCase.objects.valids(el.project).filter(requirement=el)
            tcsCount = tcs.count()
            if tcsCount > 0 and tcs.filter(state='satisfy').count() == 0:
                resp.append("Su estado es Cumple, pero ninguno de sus Casos de Prueba asociados Cumplen")
        #--------------------------------------------------------------------------------------------
        """
        if el.userTypes.all().filter(validity=True).count() == 0:
            resp.append("No tiene ningún Tipo de Usuario asociado")
        """
        #--------------------------------------------------------------------------------------------
    elif el.__class__ == Module:
        if el.softwareRequirements.filter(validity=True).count() == 0:
            resp.append("No tiene ningún Requisito de Software asociado")
        #--------------------------------------------------------------------------------------------
        else:
            maxSrPriority = 'p99_'
            for sr in el.softwareRequirements.filter(validity=True):
                if sr.priority < maxSrPriority:
                    maxSrPriority = sr.priority
            if el.priority < maxSrPriority:
                resp.append("Ningún Requisito de Software asociado tiene por lo menos la misma prioridad que este módulo")
        #--------------------------------------------------------------------------------------------
            srs = el.softwareRequirements.filter(validity=True).filter(date__gte=el.date)
            c = 0
            s = "( "
            for sr in srs:
                c = c + 1
                s = s + sr.identifierText() + " "
            s = s + ")"
            if c > 0:
                resp.append("Un Requisito de Software asociado " + s + u" ha sido modificado (su fecha de modificación es posterior a la de este Módulo, favor revisar y actualizar)")
        #--------------------------------------------------------------------------------------------
    elif el.__class__ == TestCase:
        if el.requirement.validity == False:
            resp.append("El Requisito asignado a este Caso de Prueba ha sido eliminado")
        #--------------------------------------------------------------------------------------------
        if el.requirement.validity and el.requirement.date > el.date:
            resp.append("El Requisito asociado ha sido modificado (su fecha de modificación es posterior a la de este Caso de Prueba, favor revisar y actualizar)")
        #--------------------------------------------------------------------------------------------
        """
        if el.userTypes.all().filter(validity=True).count() == 0:
            resp.append("No tiene ningún Tipo de Usuario asociado")
        """
        #--------------------------------------------------------------------------------------------
    if len(resp) == 0:
        return False
    else:
        return resp
