import random
import hashlib
from urllib.parse import urlencode

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

def calculate_gravatar_hash(email):
  enc_email = email.strip().lower().encode("utf-8")
  email_hash = hashlib.md5(enc_email).hexdigest()
  return email_hash
  
def get_gravatar_url(email, size=80, default='retro', rating='g'):
  url_base = 'https://secure.gravatar.com/'
  
  email_hash = calculate_gravatar_hash(email)
  
  query_string = urlencode({
    's': str(size),
    'd': default,
    'r': rating,
  })
  
  return '{base}avatar/{hash}.jpg?{qs}'.format(
    base=url_base, hash=email_hash, qs=query_string)
  
class User(AbstractUser):
  first_name = None
  last_name = None

  name = models.CharField(max_length=100, null=True, blank=True)
  verified_email = models.EmailField(
      null=True,
      blank=True,
      help_text=
      "If doesn't match e-mail field then user is sent a link to verify address."
  )
  title = models.CharField(max_length=100, null=True, blank=True)
  location = models.CharField(max_length=100, null=True, blank=True)

  biography = models.TextField(
      null=True, blank=True, help_text="Markdown formatted text accepted.")
  website = models.URLField(null=True, blank=True)

  avatar = models.ImageField(
      upload_to="user_photos/%Y-%m", blank=True, null=True)

  phone = models.CharField(blank=True, null=True, max_length=25)
  from_import = models.CharField(blank=True, null=True, max_length=75)

  def __str__(self):
    return self.username

  def send_verify(self, request, slug):
    if not self.verified_email or self.email.lower(
    ) != self.verified_email.lower():
      ev = EmailVerification.create_verify(self)
      subject = "Please verify your address - {}".format(settings.SITE_NAME)
      message = render_to_string('profiles/email.verification.txt',
                                 {'ev': ev,
                                  'request': request,
                                  'slug': slug})
      send_mail(
          subject,
          message,
          settings.DEFAULT_FROM_EMAIL, [ev.sent_to],
          fail_silently=False)

  def send_reset(self, request, slug):
    reset = EmailVerification.create_verify(self)
    subject = "Password Reset - {}".format(settings.SITE_NAME)
    message = render_to_string('profiles/password_reset.txt', {
        'reset': reset,
        'request': request,
        'slug': slug
    })
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL, [reset.sent_to],
        fail_silently=False)

  def image(self):
    if self.avatar:
      return self.avatar.url

    return get_gravatar_url(self.email, size=256)


SOCIAL_SITES = (
    ('about.me', 'About.Me'),
    ('facebook', 'Facebook'),
    ('github', 'Github'),
    ('gplus', 'Google+'),
    ('linkedin', 'LinkedIn'),
    ('twitter', 'Twitter'),)

SOCIAL_INFO = {
  'about.me': 'about.me/',
  'facebook': 'facebook.com/',
  'github': 'github.com/',
  'gplus': 'plus.google.com/+',
  'linkedin': 'www.linkedin.com/in/',
  'twitter': 'twitter.com/',
}


class SocialHandle(models.Model):
  user = models.ForeignKey(
      settings.AUTH_USER_MODEL, related_name='social_handles')
  username = models.CharField(max_length=255)
  site = models.CharField(max_length=25, choices=SOCIAL_SITES)

  class Meta:
    ordering = ('site',)

  def __str__(self):
    return '{}: {}'.format(self.get_site_display(), self.username)

  def link(self):
    return 'https://{}{}'.format(SOCIAL_INFO[self.site], self.username)


class EmailVerification(models.Model):
  user = models.ForeignKey(settings.AUTH_USER_MODEL)
  sent_to = models.EmailField()
  secret = models.CharField(max_length=255, unique=True)
  used = models.BooleanField(default=False)

  created = models.DateTimeField(auto_now_add=True)

  @classmethod
  def create_verify(cls, user):
    while 1:
      salt = hashlib.sha256(
          str(random.random()).encode('utf-8')).hexdigest()[:5]
      ck = hashlib.sha256(str(salt + user.email).encode('utf-8')).hexdigest()
      ev = cls(user=user, secret=ck, sent_to=user.email)

      try:
        ev.save()

      except:
        pass

      else:
        break

    return ev
