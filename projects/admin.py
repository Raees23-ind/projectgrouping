from django.contrib import admin
from .models import Project

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'cluster', 'created_at')
    search_fields = ('title', 'description', 'technologies')