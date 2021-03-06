# -*- encoding: utf-8 -*-
from django.contrib import admin
from reqApp.models import *
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin

from random import randrange
from django.contrib import messages
from reqApp.util import *

from django import forms
from django.contrib.auth.models import Permission
from django.contrib.auth.models import Group

from django.contrib.admin import widgets
from django.utils.dateformat import DateFormat

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    max_num = 1
    can_delete = False
    filter_horizontal = ("projects",)

class UserAdmin(AuthUserAdmin):
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Roles', {'fields': ('groups',)}),
    )
    
    list_display = ('username','email','first_name','last_name','is_staff','semester')
    list_filter = ('is_staff','groups','userprofile__projects__semester','userprofile__projects')
    
    actions = ['reassignUserPass','deactivateNonStaffUser']
    
    def has_delete_permission(self, request, obj=None):
        # disable delete button in user form
        # chain deletion is dangerous!
        return False
    
    def semester(self, instance):
        projects = instance.userprofile.projects.all().order_by('-startDate')
        if projects.count() > 0:
            return projects[0].semester
        return '----'
    
    def reassignUserPass(self, request, queryset):
        c = 0
        for u in queryset:
            npass = (randrange(9)+1)*1000+(randrange(9)+1)*100+(randrange(9)+1)*10+(randrange(9)+1)
            if sendEmail2User(u, 'MainReq - Bienvenido!', u'Bienvenido,\n\nHas sido registrado en MainReq (%s) con la siguiente información:\n\nUsuario: %s\n\nContraseña: %s'%(getHost(request), u.username, npass)):
                messages.success(request, "password changed & sent by email (user: %s)" % u.username)
                u.set_password(npass)
                u.save()
                c = c + 1
            else:
                messages.error(request, "Error: can't send email! (user: %s)" % u.username)
        messages.info(request, "%s passwords changed & sent by email." % c)#warning, debug, info, success, error        
    reassignUserPass.short_description = "Send Email Notification (User & Password)"
    
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


class MyProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            'name',
            'description',
            'startDate',
            'projectSemester',
            'closingDate',
            'semester',
        ]
        widgets = {
            'description': widgets.AdminTextareaWidget(),
            'name': widgets.AdminTextInputWidget(),
            'startDate': widgets.AdminSplitDateTime(),
            'closingDate': widgets.AdminSplitDateTime(),
            'semester': forms.HiddenInput(),
        }
        labels = {
            'semester':'',
            'startDate':'Start Date:',
            'closingDate':'Closing Date:',
            'projectSemester':'Semester:',
        }

    def clean_semester(self):
        startDate = self.cleaned_data['startDate']
        projectSemester = self.cleaned_data['projectSemester']
        
        for s,n in SEMESTER_CHOICES:
            if s == projectSemester:
                projectSemester = n
                break
        
        return u'%s %s' % (DateFormat(startDate).format('Y'), projectSemester)

class ProjectAdmin(admin.ModelAdmin):
    form = MyProjectForm
    list_display = ('name', 'semester', 'closingDate', 'status','show_users')
    list_filter = ('semester',)
    search_fields = ['name', 'semester']
    
    def has_delete_permission(self, request, obj=None):
        # disable delete button in project form
        return False
        
    def show_users(self, pr):
        return '<a href="/admin/auth/user/?userprofile__projects__id__exact=%s">Users...</a>' % (pr.id)
    show_users.allow_tags = True
    show_users.short_description = "Users"
    
admin.site.register(Project, ProjectAdmin)

admin.site.disable_action('delete_selected')

# custom auth permissions
class MyGroupAdminForm(forms.ModelForm):
    class Meta:
        model = Role#Group

    permissions = forms.ModelMultipleChoiceField(
        Permission.objects.filter(codename__startswith = PERM_PRE),
        widget=admin.widgets.FilteredSelectMultiple('permissions', False),
        required=False)


class MyGroupAdmin(admin.ModelAdmin):
    form = MyGroupAdminForm
    search_fields = ('name',)

admin.site.unregister(Group)
admin.site.register(Role, MyGroupAdmin)
