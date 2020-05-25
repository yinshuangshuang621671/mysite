from django.db import models
# 使用django自带的用户模块
from django.contrib.auth.models import User
# 富文本编辑 ckeditor  RichTextField：不允许上传文件的富文本编辑
# RichTextUploadingField:允许上传文件的富文本编辑
from ckeditor_uploader.fields import RichTextUploadingField

# ContentType 自身就是个模型类
from django.contrib.contenttypes.models import ContentType
# ？？模型之间关联，相互访问
from django.contrib.contenttypes.fields import GenericRelation
# from .. import read_statistics
from read_statistics.models import ReadNumExpandMethod, ReadDetail

from django.urls import reverse


# 博客分类
class BlogType(models.Model):
    type_name = models.CharField(max_length=15)

    # Blog 模型中外键调用显示，不然显示 object： BlogType object (3)
    def __str__(self):
        return self.type_name


# 类的继承
class Blog(models.Model, ReadNumExpandMethod):
    title = models.CharField(max_length=50)
    # 外键，引用BlogType类，注意BlogType类要写在前面，不然会报错
    # annotate方法使用：related_name="blog_blog"
    blog_type = models.ForeignKey(BlogType, on_delete=models.CASCADE, related_name="blog_blog")
    # content = models.TextField()
    # 使用可以上传文件的富文本来替换原有的字段类型
    content = RichTextUploadingField()
    # 外键
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    # read_num = models.IntegerField(default=0)  # 设置默认阅读量为0

    # 建立模型之间的关联
    read_details = GenericRelation(ReadDetail)

    # 自动添加，不需要手动 auto_now_add，只是为添加时候的时间，不会随着你的改动而变动
    created_time = models.DateTimeField(auto_now_add=True)
    # auto_now 会跟随你的变动而变动，
    last_updated_time = models.DateTimeField(auto_now=True)

    # 定义博客数据在别的表中的显示样式名称
    def __str__(self):
        # 显示：<Blog: for 30>
            return "<Blog_ss: %s>" % self.title

    class Meta:
        # 数据库设置按照创建时间倒序排序！最先创建的排在前面
        # 设置后需要同步数据库makemigration,migrate!!!!
        ordering = ['-created_time']

    # Blog已经继承了ReadNumExpandMethod 类，Blog的实例对象就可以直接调用里面的方法，get_read_num

    def get_url(self):
        # 使用关键字参数kwargs
        return reverse('blog_detail', kwargs={'blog_pk': self.pk})

    def get_email(self):
        return self.author.email


"""
# 设置为外键
class ReadNum(models.Model):
    # 设置默认阅读量为0 ：需要注意：这个0是你在“创建一条新的数据的时候”默认给你的数字，
    # 给你的默认值是零，而不是直接显示0
    # 如果ReadNum表中没有某条博客的阅读记录，Blog表显示的时候，get_read_num是取不到值的，显示一条横线
    read_num = models.IntegerField(default=0)
    # 这个外键没有设置related_name
    blog = models.OneToOneField(Blog, on_delete=models.DO_NOTHING)  # 外键 ：一对一
"""

"""
1. 富文本编辑
{#1. 使用html丰富页面#}
{#（1）. 简单文本编辑-》后台文本中直接插入html代码#}
{#（2）. 富文本编辑：最终解析成html =》使用富文本编辑器/markdown编辑器#}
{#（3）. striptags 过滤器：将文本内容中的html语言过滤掉，区别于safe过滤器 #}
使用ckeditor富文本编辑器，可以在后台将html代码直接转化为正常页面！！！
并且原始的html和正常渲染后的文本可以进行切换：原始码

"""

"""
阅读数量统计：
1. read_num = models.IntegerField(default=0)  # 设置默认阅读量为0
这种将字段直接添加在博客模型类中，当阅读数量字段修改的时候，lasted_update_time字段
也会同时改变。另外，这种方法无法统计一天内的阅读数量。
"""
"""
2. 外键：
ForeignKey: 一对多与多对一
ManyToManyField：多对多
OneToOneField:一对一
"""

"""
3.使用外键查询数据 
·BlogType是Blog 的外键  Blog是主表，BlogType是副表！！！！
·多对一与一对多的关系，可以使用.blog_set/.related_name
（1）Blog的对象的blog_type（注意）==><BlogType: Django>，可以直接使用BlogType的属性和.related_name，
     就可以获取到当前Blog对象在BlogType表中的数据
（2）BlogType 对象可以使用.blog_set/.related_name 来获取当前类型所包含的全部博客对象

·Blog是ReadNum 的外键  ReadNum是主表，Blog是副表！！！！
·一对一的关系，不可以使用上边.readnum_set  ，可以使用.readnum（小写）/related_name
（1）ReadNum 对象的blog属性就对应Blog对象，可以使用.readnum（小写）
（2）Blog对象就可以直接调用.readnum（小写），就到了相应ReadNum数据中，继而可以调用相应属性
（3）主表 副表就是相互关联，相互调用了


·
>>> from blog.models import Blog,BlogType,ReadNum
>>> blog=Blog.objects.first()  取第一条数据
>>> blog_type=blog.blog_type
>>> blog_type
<BlogType: Django>
>>> blog_type.type_name   # 可以直接调用type_name??
'Django'
>>> blog_type.blog_blog   #外键取名： related_name="blog_blog"
如果没有related_name，则输入    # 一对多，多对一关系  
>>> blog_type.blog_set    # 模型小写+_set 

>>> blog_type.blog_blog
<django.db.models.fields.related_descriptors.create_reverse_many_to_one_manager.<locals>.RelatedManager object at 0x000001D7F5C94F28>
>>> blog_type.blog_blog.all()
<QuerySet [<Blog: <Blog: for 30>>, <Blog: <Blog: for 29>>, <Blog: <Blog: for 28>>, <Blog: <Blog: for 27>>, <Blog: <Blog: for 26>>, <Blog: <Blog: for 25>>, <Blog: <Blog: for 24>>, <Blog: <Blog: for 23>>, <Blog: <Blog: for 22>>, <Blog: <Blog: for 21>>, <Blog: <Blog: for 20>>, <Blog: <Blog: for 19>>, <Blog: <Blog: for 18>>, <Blog: <Blog: for 17>>, <Blog: <Blog: for 16>>, <Blog: <Blog: for 15>>, <Blog: <Blog: for 14>>, <Blog: <Blog: for 13>>, <Blog: <Blog: for 12>>, <Blog: <Blog: for 11>>, '...(remaining elements truncated)...']>
>>>
>>> blog_type.blog_blog.all().count()   # 计数
32
>>> dir(blog_type)  # dir函数可以查看当前对象所包含的可以使用的函数



blog_type.blog_blog 对应的就已经是Blog数据对象了，有点绕

>>> read_one=ReadNum.objects.first()
>>> dir(read_one)
>>> read_one.blog           # 外键属性就对应 副表对象
<Blog: <Blog: for 30>>
>>> read_one.blog.readnum   # 使用外键表名小写，就对应到副表对象了
<ReadNum: ReadNum object (1)>
>>> read_one.blog.readnum.read_num
10
>>>
"""

"""
4. ContentType 
1. get_for_model:通过model或者model的实例来获得ContentType对象
2. 数据库中存在django_content_type表，存储表APP及对应的模型类，（不过模型都是小写）

"""

"""
5. 建立模型之间的关联:对于是ContentType类型的模型，可以使用GenericRelation，
从而在别的地方可以进行调用
read_details = GenericRelation(ReadDetail)
具体使用是在mysite/views中get_today_hot_data()及下面两个函数中进行使用
"""







