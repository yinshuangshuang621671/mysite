import datetime
from django.shortcuts import render
from django.contrib.contenttypes.models import ContentType
from read_statistics.utils import get_seven_days_read_data
from blog.models import Blog
# 使用数据库缓存
from django.core.cache import cache
from django.utils import timezone
from django.db.models import Sum

# 用户登录使用django自带的forms表单类


# 使用read_details ：即read_details = GenericRelation(ReadDetail)，使用双下划线链接
# 获取当日博客阅读量排行，热门博客(一天内)
def get_today_hot_data():
    today = timezone.now().date()
    # order_by('-read_num') 按哪个字段排序，默认有小到大，加负号表示由大到小，得到查询集
    # 使用了read_details！！
    blogs = Blog.objects.filter(read_details__date=today)\
                        .values('id', 'title')\
                        .annotate(read_num_sum=Sum('read_details__read_num'))\
                        .order_by('-read_num_sum')
    return blogs[:7]   # 选前7条


# 获取昨天的热门博客（一天内）
# 分组后按照字段加和
def get_yesterday_hot_data():
    today = timezone.now().date()
    yesterday = today - datetime.timedelta(days=1)   # 昨天
    blogs = Blog.objects.filter(read_details__date=yesterday)\
                        .values('id', 'title')\
                        .annotate(read_num_sum=Sum('read_details__read_num'))\
                        .order_by('-read_num_sum')
    return blogs[:7]   # 选前7条


# 获取前7天热门阅读量博客
# 获取前7天内的热门博客阅读记录统计，
# 注意：前七天内，可能重复阅读相同的博客，所以需要分类统计，使用annotate!! 分组统计
def get_7_days_hot_blogs():
    today = timezone.now().date()
    date = today - datetime.timedelta(days=7)
    # Blog模型中使用了GenericRelation 来进行两个模型之间的关联，
    # 使用链式查询__(双下划线)！！！！！按照日期date进行查询
    # Blog对象可以直接访问ReadDetail表中的数据
    # read_details = GenericRelation(ReadDetail)
    blogs = Blog.objects.filter(read_details__date__lt=today, read_details__date__gte=date)\
                        .values('id', 'title')\
                        .annotate(read_num_sum=Sum('read_details__read_num'))\
                        .order_by('-read_num_sum')
    return blogs[:7]   # 选前7条


def home(request):
    # 类型
    blog_content_type = ContentType.objects.get_for_model(Blog)
    # 注意返回数据的接受顺序
    dates, read_nums = get_seven_days_read_data(blog_content_type)

    # 使用缓存：先直接获取7天热门博客的缓存数据
    hot_blogs_for_7_days = cache.get('hot_blogs_for_7_days')
    # 如果没有缓存，为None
    if hot_blogs_for_7_days is None:
        # 计算数据
        hot_blogs_for_7_days = get_7_days_hot_blogs()
        # 并存入缓存数据表，且设置有效时间3600
        cache.set('hot_blogs_for_7_days', hot_blogs_for_7_days, 3600)
        print("use cal")   # 测试代码
    else:
        print("use cache")

    context = {}
    context['read_nums'] = read_nums
    context['dates'] = dates
    # 获取当日一天内阅读量最多的那一条阅读量记录
    context['today_hot_data'] = get_today_hot_data()
    context['yesterday_hot_data'] = get_yesterday_hot_data()
    context['hot_blogs_for_7_days'] = hot_blogs_for_7_days   # 利用缓存
    return render(request, 'home.html', context)


"""
1. values函数：
返回一个字典集合，每一个字典表示一个对象，如果指定字段，则只包含指定字段的键值对儿
如果不指定键值，每个字典将包含数据库表中所有字段的键值
values函数 + annotate 就是按照字段先group by（分组）， 然后聚合函数计算！！
"""

"""
2.GenericRelation：反向查询
Blog模型中使用了GenericRelation 来进行两个模型之间的关联，Blog模型可以访问ReadDetail中的属性
使用链式查询__(双下划线),而不是使用.!!!!:

Blog.objects.filter(read_details__date__lt=today, read_details__date__gte=date)
.annotate(read_num_sum=Sum('read_details__read_num'))\
blog = Blog.objects.first()
blog.read_details.all()
可以获取到与当前博客有关的所有阅读记录明细
"""

"""
3. 
（1）reverse('home')；
    通过传入链接的别名，来反向解析出链接的url地址，这里设定'\'表示根目录
（2）referer = request.META.get('HTTP_REFERER', reverse('home'))
    获取到你是从哪个页面传递过来的请求，信息包含在request中
"""

"""
4. auth模块：
（1）auth.authenticate：
提供了用户认证，验证用户名及密码是否正确，若信息有效，则返回一个user对象
（2）login函数
接收一个HttpRequest对象及一个认证了的User对象，使用django的session框架给已
认证的用户附加上session等信息
"""

"""
5. 这个login及register函数：登录和注册
（1）是从模板页面使用GET传参方式进行调用，而不是POST方式
（2）所以一开始的时候，if判断中走的是GET那部分，即只是实例化表单，然后在模板页面进行表单组件显示
（3）在模板显示的组件中进行内容的输入，然后再通过POST方式传递给views处理函数。。逻辑有点迷
（4）然后处理函数进行处理后再返回给之前的页面。。。
"""

