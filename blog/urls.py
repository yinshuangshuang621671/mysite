from django.urls import path
from . import views

urlpatterns = [
    # https://localhost:8000/blog
    path('', views.blog_list, name="blog_list"),
    # https://localhost:8000/blog/1
    path('<int:blog_pk>', views.blog_detail, name="blog_detail"),
    # 如果不加type ，上下这两个连接就相同了，都是int,无法区分 有name参数不同也不行？
    path('type/<int:blog_type_pk>', views.blogs_with_type, name="blogs_with_type"),

    path('date/<int:year>/<int:month>', views.blogs_with_date, name="blogs_with_date")
]

"""
path中 给路径起别名，反向解析时使用，
反向解析：
通过name的值来匹配出对应的url地址，然后在url列表中从上至下进行匹配！！！，
那就是说反解析后还是需要查找yrl的而不是一一对应
匹配顺序是从上到下进行匹配
"""