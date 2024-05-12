from pyexpat.errors import messages
from sqlite3 import IntegrityError
from django.contrib import admin
from userauths.models import Profile, User





class UserAdmin(admin.ModelAdmin):
    list_display = ['email','full_name', 'phone']

    def delete_model(self, request, obj):
        # Delete related Profile objects
        Profile.objects.filter(user=obj).delete()
        
        # Then delete the User
        super().delete_model(request, obj)

class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user','full_name', 'country', 'city', 'state']
    #list_editable = ['country', 'city', 'state']
    search_fields = ['full_name']
    list_filter = ['date']



admin.site.register(User, UserAdmin)
admin.site.register(Profile, ProfileAdmin)



