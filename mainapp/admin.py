from django.contrib import admin
from .models import Profile
from .models import Interaction

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user','email','firstName','lastName','messages','contacts','token','staffStatus')

class InteractionAdmin(admin.ModelAdmin):
    list_display = ('messageId','user','email','reciever','sender','sender_email','date','subject','label')

# Register your models here.
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Interaction, InteractionAdmin)