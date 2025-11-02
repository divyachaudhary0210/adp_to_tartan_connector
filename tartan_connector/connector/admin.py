from django.contrib import admin
from .models import SourceEmployee, UnifiedEmployee, FieldMapping, OAuthClient, AccessToken

admin.site.register(SourceEmployee)
admin.site.register(UnifiedEmployee)
admin.site.register(FieldMapping)
admin.site.register(OAuthClient)
admin.site.register(AccessToken)


