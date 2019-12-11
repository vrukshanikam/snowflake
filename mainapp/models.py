from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib import admin
from oauth2client.contrib.django_util.models import CredentialsField

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    messages = models.TextField(max_length=5000,blank=True,default='')
    token = models.TextField(max_length=5000, blank=True, default='')
    contacts = models.TextField(max_length=5000, blank=True, default='')
    def email(self):
        return self.user.email
    
    def firstName(self):
        return self.user.first_name
    
    def lastName(self):
        return self.user.last_name

    def staffStatus(self):
        return self.user.is_staff


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

class Interaction(models.Model):
    messageId = models.TextField(max_length=5000,primary_key=True, unique = True)
    user = models.ForeignKey(User, primary_key = False, on_delete=models.CASCADE)
    reciever = models.TextField(max_length=5000,blank=True,default='')
    sender = models.TextField(max_length=5000,blank=True,default='')
    sender_email = models.TextField(max_length=5000, blank=True, default='')
    date = models.TextField(max_length=5000,blank=True,default='')
    subject = models.TextField(max_length=5000,blank=True,default='')
    label = models.TextField(max_length=5000,blank=True,default='')


    def email(self):
        return self.user.email

#@receiver(post_save, sender=User)
#def create_user_interaction(sender, instance, created, **kwargs):
    #if created:
        #Interaction.objects.create(user=instance)

#@receiver(post_save, sender=User)
#def save_user_interaction(sender, instance, **kwargs):
    #instance.interaction.save()

class CredentialsModel(models.Model): 
	id = models.ForeignKey(User, primary_key = True, on_delete = models.CASCADE) 
	credential = CredentialsField() 
	task = models.CharField(max_length = 80, null = True) 
	updated_time = models.CharField(max_length = 80, null = True) 


class CredentialsAdmin(admin.ModelAdmin): 
	pass

