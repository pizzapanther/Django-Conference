import traceback

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.template.response import TemplateResponse
from django.conf import settings
from django import http
from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django import forms
from django.views.decorators.csrf import csrf_exempt

from .models import User, SocialHandle


class SocialInline(admin.TabularInline):
  model = SocialHandle


class User2CreationForm(UserCreationForm):

  class Meta:
    model = User
    fields = ("username", "email", "verified_email")

  def clean_username(self):
    username = self.cleaned_data["username"]

    try:
      User._default_manager.get(username=username)

    except User.DoesNotExist:
      return username

    raise forms.ValidationError(
        self.error_messages['duplicate_username'], code='duplicate_username')


class User2ChangeForm(UserChangeForm):

  class Meta:
    model = User
    fields = '__all__'


permission_required('profiles.change_user')


class CurrentSpeakerFilter(admin.SimpleListFilter):
  title = 'Current Speaker'
  parameter_name = 'current'

  def lookups(self, request, model_admin):
    return (('1', 'Current Speakers'),)

  def queryset(self, request, queryset):
    if self.value() == '1':
      return queryset.filter(
          session__status='accepted',
          session__conference__slug=settings.DEFAULT_CONF).exclude(
              session__stype='lightning')


@admin.register(User)
class User2Admin(UserAdmin):
  list_display = ('username', 'email', 'name', 'phone', 'current_speaker',
                  'is_staff', 'is_superuser')
  #list_filter = (CurrentSpeakerFilter,)
  inlines = (SocialInline,)

  form = User2ChangeForm
  add_form = User2CreationForm

  fieldsets = (
      (None, {
          'fields': ('username', 'password')
      }),
      ('Personal info', {
          'fields': ('name', 'title', 'location', 'email', 'verified_email',
                     'phone', 'website', 'avatar', 'biography')
      }),
      ('Permissions', {
          'fields': ('is_active', 'is_staff', 'is_superuser', 'groups')
      }),
      ('Important dates', {
          'fields': ('last_login', 'date_joined', 'from_import')
      }),)

  readonly_fields = ('last_login', 'date_joined', 'from_import')

  add_fieldsets = ((None, {
      'classes': ('wide',),
      'fields': ('username', 'email', 'verified_email', 'password1',
                 'password2')
  }),)

  def current_speaker(self, obj):
    return 'coming soon'
    if obj.session_set.filter(
        status='accepted', conference__slug=settings.DEFAULT_CONF).exclude(
            stype='lightning').count() > 0:
      return '<strong style="color: green;">&#10003;</strong>'

    return '<strong style="color: red;">&times;</strong>'

  current_speaker.allow_tags = True
