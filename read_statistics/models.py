from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db.models.fields import exceptions
from django.utils import timezone
# django框架网站：www.djangoproject.com


# 博客阅读量数据表
class ReadNum(models.Model):
    read_num = models.IntegerField(default=0)

    # ContentType代码固定写法
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')


# 按日期统计阅读量
class ReadDetail(models.Model):
    # 设置默认值：now函数，加不加括号都可以，说是不加括号好些
    # 默认值：timezone.now日期格式为：2020/04/25
    date = models.DateField(default=timezone.now)
    read_num = models.IntegerField(default=0)

    # ContentType代码固定写法，变得通用
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    # 上边两个的组合
    content_object = GenericForeignKey('content_type', 'object_id')


# 类，Blog继承，在数据表中显示阅读数量
class ReadNumExpandMethod(object):
    # 数据库显示的时候，每一条数据就是一个对象，
    # 全部对象显示都会调用这个方法，因为admin中写了这个函数
    def get_read_num(self):
        try:
            # 参数是模型或者模型对象（self即可）
            # 就是通过ContentType这个中介找到模型Blog
            ct = ContentType.objects.get_for_model(self)
            readnum = ReadNum.objects.get(content_type=ct, object_id=self.pk)
            return readnum.read_num
        # 不存在相应记录
        except exceptions.ObjectDoesNotExist:
            return 0


"""
1. ContentType ：
需要传入博客模型：content_type及主键值：object_id 两个参数
"""