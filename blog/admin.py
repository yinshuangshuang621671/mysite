from django.contrib import admin
from .models import BlogType, Blog
# Register your models here.
# 设计数据库显示样式

# 初始register  数据库只显示objects
# admin.site.register(Blog)
# admin.site.register(BlogType)


@admin.register(BlogType)
class BlogTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'type_name')


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    # read_num是Blog中的方法
    list_display = ('id', 'title', 'blog_type', 'author', 'get_read_num', 'created_time', 'last_updated_time')


# @admin.register(ReadNum)
# class ReadNumAdmin(admin.ModelAdmin):
#     list_display = ('read_num', 'blog')


"""
1. 数据库中编号默认从1开始，且已经删除的数据，之后新增数据，编号不会重新开始
1 被删除，新建数据会从2开始
"""

