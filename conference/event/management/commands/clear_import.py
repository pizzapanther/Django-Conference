from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model

from conference.event.models import Session

class Command (BaseCommand):
  help = 'Clear Imports'

  def add_arguments(self, parser):
    parser.add_argument('import_string', type=str)
    
  def handle(self, *args, **options):
    User = get_user_model()
    
    istr = options['import_string']
    
    sessions = Session.objects.filter(from_import=istr)
    session_count = sessions.count()
    
    users = User.objects.filter(from_import=istr)
    user_count = users.count()
    
    while 1:
      print('Are you sure you wish to delete {} Sessions and {} Users?'.format(
        session_count, user_count
      ))
      ans = input('[y/n] ')
      ans = ans.lower()
      
      if ans == 'y':
        sessions.delete()
        users.delete()
        print('Sessions Cleared:', session_count)
        print('Users Cleared:', user_count)
        break
        
      elif ans == 'n':
        break
        