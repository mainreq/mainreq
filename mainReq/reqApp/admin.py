# -*- encoding: utf-8 -*-
from django.contrib import admin
from reqApp.models import *
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin

from random import randrange
from django.contrib import messages
from reqApp.util import *

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    max_num = 1
    can_delete = False
    filter_horizontal = ("projects",)

class UserAdmin(AuthUserAdmin):
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser','groups')}),
    )
    
    actions = ['reassignUserPass','deactivateNonStaffUser']
    
    def reassignUserPass(self, request, queryset):
        c = 0
        for u in queryset:
            npass = (randrange(9)+1)*1000+(randrange(9)+1)*100+(randrange(9)+1)*10+(randrange(9)+1)
            if sendEmail2User(u, 'MainReq - Bienvenido!', u'Bienvenido,\n\nHas sido registrado en <a href="http://mainreq.dcc.uchile.cl">MainReq</a> con la siguiente información:\n\nUsuario: %s\n\nContraseña: %s\n\nmainreq.dcc.uchile.cl'%(u.username,npass)):
                messages.success(request, "password changed & sent by email (user: %s)" % u.username)
                u.set_password(npass)
                u.save()
                c = c + 1
            else:
                messages.error(request, "Error: can't send email! (user: %s)" % u.username)
        messages.info(request, "%s passwords changed & sent by email." % c)#warning, debug, info, success, error        
    reassignUserPass.short_description = "Re-assign password & notify by email"
    
    def deactivateNonStaffUser(self, request, queryset):
        c = 0
        for u in queryset:
            if not u.is_staff:
                u.is_active = False
                u.save()
                c = c + 1
        messages.info(request, "%s non-staff users deactivated." % c)
    deactivateNonStaffUser.short_description = "Deactivate non-staff users"
    
    def add_view(self, *args, **kwargs):
        self.inlines = []
        return super(UserAdmin, self).add_view(*args, **kwargs)

    def change_view(self, *args, **kwargs):
        self.inlines = [UserProfileInline]
        return super(UserAdmin, self).change_view(*args, **kwargs)

# unregister old user admin
admin.site.unregister(User)
# register new user admin
admin.site.register(User, UserAdmin)


class ProjectAdmin(admin.ModelAdmin):
    fields = ('name','description',)
    list_display = ('name', 'creationDate',)
admin.site.register(Project, ProjectAdmin)



# custom auth permissions
from django import forms
from django.contrib.auth.models import Permission
from django.contrib.auth.models import Group

class MyGroupAdminForm(forms.ModelForm):
    class Meta:
        model = Group

    permissions = forms.ModelMultipleChoiceField(
        Permission.objects.filter(codename__startswith = PERM_PRE),
        widget=admin.widgets.FilteredSelectMultiple('permissions', False))


class MyGroupAdmin(admin.ModelAdmin):
    form = MyGroupAdminForm
    search_fields = ('name',)

admin.site.unregister(Group)
admin.site.register(Group, MyGroupAdmin)
