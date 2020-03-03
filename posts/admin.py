from django.contrib import admin
from .models import Post, Group
# Register your models here.

class GroupAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "description", )
    empty_value_display = "- пусто -"

class PostAdmin(admin.ModelAdmin):
    list_display = ("text", "pub_date", "author", "group", )
    search_fields = ("text", )
    list_filter= ("pub_date", )
    empty_value_display = "-пусто-"

admin.site.register(Group, GroupAdmin)
admin.site.register(Post, PostAdmin)