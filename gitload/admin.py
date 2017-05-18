from django.contrib import admin

from gitload.models import Loaded_Pltp, Loaded_Pl, Repository


@admin.register(Loaded_Pltp)
class PltpAdmin(admin.ModelAdmin):
    list_display=('name', 'url', 'json', 'sha1')

@admin.register(Loaded_Pl)
class PlAdmin(admin.ModelAdmin):
    list_display=('name', 'sha1', 'json')
    
@admin.register(Repository)
class RepoAdmin(admin.ModelAdmin):
    list_display=('name', 'url')
