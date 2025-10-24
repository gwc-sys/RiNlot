

from django.contrib import admin
from api.model import User
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass

class SessionCodeAdmin(admin.ModelAdmin):
    pass