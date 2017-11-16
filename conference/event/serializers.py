from django.contrib.auth import get_user_model

from rest_framework import serializers

from conference.event.models import Room, Session
from conference.profiles.models import SocialHandle

class DynamicFieldsMixin(object):

  def __init__(self, *args, **kwargs):
    exclude = kwargs.pop('exclude', None)

    super(DynamicFieldsMixin, self).__init__(*args, **kwargs)

    if exclude is not None:
      existing = set(self.fields.keys())
      for field_name in existing:
        if field_name in exclude:
          self.fields.pop(field_name)
          
class RoomSizzler(serializers.ModelSerializer):
  class Meta:
    model = Room
    fields = ('name',)


class SocialHandleSizzler(DynamicFieldsMixin, serializers.ModelSerializer):
  class Meta:
    model = SocialHandle
    fields = ('username', 'site')

class UserPublicSizzler(DynamicFieldsMixin, serializers.ModelSerializer):
  social_handles = SocialHandleSizzler(many=True)

  class Meta:
    model = get_user_model()
    fields = ('username', 'name', 'image', 'biography', 'website',
              'social_handles')
    read_only_fields = fields
    
class SessionPyVideoSizzler(DynamicFieldsMixin, serializers.ModelSerializer):
  room = RoomSizzler()
  speaker = UserPublicSizzler(
      source='user',
      exclude=('biography', 'website', 'social_handles'))
  type = serializers.CharField(source='get_stype_display')
  make_recording = serializers.BooleanField(source='video')
  released = serializers.BooleanField()
  slides_url = serializers.CharField(source='slides')
  url = serializers.CharField()

  class Meta:
    model = Session
    fields = (
        'id', 'name', 'description', 'type', 'room', 'start', 'end', 'url',
        'duration', 'speaker', 'make_recording', 'released', 'license',
        'language', 'video_url', 'slides_url')