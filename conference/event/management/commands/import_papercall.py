import json
import random
import time

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.utils.text import slugify

from conference.event.models import Conference, Session
from conference.profiles.models import SocialHandle


class Command(BaseCommand):
  help = 'Import talks from PaperCall.io'

  def add_arguments(self, parser):
    parser.add_argument('conf_slug', type=str)
    parser.add_argument('json_file', type=str)

  def handle(self, *args, **options):
    User = get_user_model()

    session_count = 0
    conf = Conference.objects.get(slug=options['conf_slug'])
    print('Found Conference:', conf)

    with open(options['json_file'], 'r') as fh:
      data = json.load(fh)

    istr = str(time.time())

    for talk in data:
      print('Processing:', talk['title'])

      username = '{}-{}'.format(
          slugify(talk['name'].lower()), random.randint(10000, 1000000))

      user = User.objects.filter(email__iexact=talk['email']).first()
      if user is None:
        user = User.objects.create(
            name=talk['name'],
            username=username,
            email=talk['email'],
            verified_email=talk['email'],
            biography=talk['bio'],
            website=talk['url'],
            from_import=istr,)

      if SocialHandle.objects.filter(user=user, site='twitter').count() == 0:
        if 'twitter' in talk and talk['twitter']:
          SocialHandle.objects.create(
              user=user,
              username=talk['twitter'],
              site='twitter',)

      status = 'submitted'
      if talk['state'] == 'accepted':
        status = 'accepted'

      level = 'beginner'
      if talk["audience_level"] == "Intermediate":
        level = 'intermediate'

      elif talk["audience_level"] == "Advanced":
        level = 'advanced'

      stype = 'talk-short'
      if '50' in talk['talk_format']:
        stype = 'talk-long'

      session = Session(
          user=user,
          conference=conf,
          name=talk['title'],
          description=talk['description'],
          tags=', '.join(talk['tags']),
          stype=stype,
          level=level,
          status=status,
          special_requirements=talk['notes'],
          from_import=istr)
      session.set_duration()
      session.save()

      session_count += 1

    print("Sessions Imported:", session_count)
    print("Import Complete:", istr)
