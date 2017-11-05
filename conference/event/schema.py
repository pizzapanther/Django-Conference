from django.contrib.auth import get_user_model

import graphene
from graphene import relay, ObjectType, AbstractType
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphene.types.datetime import DateTime

from conference.event.models import Conference, SponsorshipLevel, Sponsor, Room, Session


class ConfNode(DjangoObjectType):

  class Meta:
    model = Conference
    filter_fields = [
        'slug',
    ]
    interfaces = (relay.Node,)


class SponsorshipLevelNode(DjangoObjectType):

  class Meta:
    model = SponsorshipLevel
    filter_fields = ['conference', 'id']
    interfaces = (relay.Node,)


class UserNode(DjangoObjectType):
  image = graphene.String(source='image')
  
  class Meta:
    model = get_user_model()
    filter_fields = ['id']
    interfaces = (relay.Node,)


class SponsorNode(DjangoObjectType):
  logo_url = graphene.String(source='logo_url')

  class Meta:
    model = Sponsor
    only_fields = ('name', 'url', 'description', 'level', 'active', 'logo',
                   'logo_url')
    filter_fields = ['id', 'active']
    interfaces = (relay.Node,)


class RoomNode(DjangoObjectType):

  class Meta:
    model = Room
    filter_fields = ['conference', 'id']
    interfaces = (relay.Node,)


class SessionNode(DjangoObjectType):
  end = DateTime(source='end')
  start_str = graphene.String(source='start_str')
  end_str = graphene.String(source='end_str')
  
  class Meta:
    model = Session
    filter_fields = ['conference', 'id', 'status', 'stype']
    interfaces = (relay.Node,)


class Query(AbstractType):
  all_confs = DjangoFilterConnectionField(ConfNode)
  all_levels = DjangoFilterConnectionField(SponsorshipLevelNode)
  all_sponsors = DjangoFilterConnectionField(SponsorNode)
  all_rooms = DjangoFilterConnectionField(RoomNode)
  all_sessions = DjangoFilterConnectionField(SessionNode)
  all_keynotes = DjangoFilterConnectionField(SessionNode)
