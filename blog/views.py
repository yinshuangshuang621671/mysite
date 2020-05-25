from django.shortcuts import get_object_or_404, render
from .models import Blog, BlogType
# 分页器
from django.core.paginator import Paginator
# 引用设置的全局变量
from django.conf import settings
# django自带的计数方法
from django.db.models import Count
from read_statistics.utils import read_statistics_once_read
# 将登录表单使用公用模板返回表单实例，在user app中，在settings中有定义
# from user.forms import LoginForm
# from comment.models import Comment
# from django.contrib.contenttypes.models import ContentType
# from comment.forms import CommentForm   # forms表单


# 共同代码
def get_blog_list_common_data(request, blogs_all_list):
    paginator = Paginator(blogs_all_list, settings.EACH_PAGE_BLOGS_NUMBER)
    # 获取页码参数，GET请求（字典:键值对），get方法获取page参数，没有的话默认为第一页 （1）
    # python中字典类型! 中get方法，获取url的页面参数（GET请求）
    page_num = request.GET.get('page', 1)
    # paginator.page(int(page_num))
    # 比较繁琐，django自带的一个函数get_page，会自动对输入参数进行转化，
    # 如果你输入的不是数字，会自动调到默认的页面
    page_of_blogs = paginator.get_page(page_num)

    # 获取当前页码前后各两个页码
    current_page_num = page_of_blogs.number
    # page_range = [current_page_num-2, current_page_num-1, current_page_num,
    #               current_page_num+1, current_page_num+2]
    # paginator.num_pages是分页器总共分了多少页
    # minmax会保证前后的页码 不超过总页数，且最小值是1（这个逻辑是服气的。。。）
    page_range = list(range(max(current_page_num - 2, 1), current_page_num)) + \
                 list(range(current_page_num, min(current_page_num + 2, paginator.num_pages) + 1))

    # 相差超过两页，加上省略页码标记
    if page_range[0] - 1 >= 2:
        # insert 插入，index=0从头部插入，全部元素顺移一位
        page_range.insert(0, '...')
    if paginator.num_pages - page_range[-1] >= 2:
        page_range.append('...')

    # 添加第一页与最后一页
    if page_range[0] != 1:
        page_range.insert(0, 1)
    if page_range[-1] != paginator.num_pages:
        page_range.append(paginator.num_pages)

    # 获取博客分类的对应博客数量（1）自己编写
    # blog_types = BlogType.objects.all()
    # blog_types_list = []
    # for blog_type in blog_types:
    #     !!! # blog_types是类对象，为类对象添加数量属性！！！牛逼
    #     blog_type.blog_count = Blog.objects.filter(blog_type=blog_type).count()
    #     blog_types_list.append(blog_type)

    # （2）使用django自带的方法 => annotate注释方法，而且还是外键，两个表关联
    # 可以不使用'blog_blog'，直接写相关联模型名称的小写：'blog'
    # BlogType.objects.annotate(blog_count=Count('blog_blog'))

    # 这个获取的就是日期数据，共有几种，而不是像上面那种类型对象，无法添加属性
    blog_dates = Blog.objects.dates('created_time', 'month', order='DESC')
    blog_dates_dict = {}
    for blog_date in blog_dates:
        # Blog中根据日期类别进行数据筛选，链式查询
        blog_count = Blog.objects.filter(created_time__year=blog_date.year,
                                         created_time__month=blog_date.month).count()
        # 对字典赋值，注意是在循环中，键是个变化的变量，字符串
        blog_dates_dict[blog_date] = blog_count

    context = {}
    # 获取当前页的所有博客
    context['blogs'] = page_of_blogs.object_list
    context['page_of_blogs'] = page_of_blogs
    # 统计数据的数量，自写的方法
    # context['blogs_count'] = Blog.objects.all().count()

    # context['blog_types'] = blog_types_list
    # 使用自带的方法
    context['blog_types'] = BlogType.objects.annotate(blog_count=Count('blog_blog'))
    context['page_range'] = page_range

    # 获取博客时间类别，而不是获取全部时间,看看具体参数代表什么？
    # context['blog_dates'] = Blog.objects.dates('created_time', 'month', order='DESC')
    context['blog_dates'] = blog_dates_dict
    return context


# 博客列表
def blog_list(request):
    blogs_all_list = Blog.objects.all()
    context = get_blog_list_common_data(request, blogs_all_list)
    # 按照settings中设定的顺序，自动寻找模板文件
    return render(request, "blog/blog_list.html", context)


"""
django中 使用 | 表示过滤器，其本身自带的
    <p>一共有{{ blogs|length }}篇博客</p>
    <p>一共有{{ blogs_count}}篇博客</p>
    
    过滤器过滤显示内容的长度，限制长度为30个字符，多余的会以。。。表示
    <p>{{ blog.content|truncatechars:30 }}</p>
"""


def blog_detail(request, blog_pk):
    # 获取当前博客实例数据
    blog = get_object_or_404(Blog, id=blog_pk)
    # 设置cookie值
    read_cookie_key = read_statistics_once_read(request, blog)

    context = {}
    # 获取当前博客的上一条 及 下一条博客，数据库中是按照创建时间由高到低排序
    # 所以按照创建时间来选择前一条及后一条
    # created_time__gt：__gt(greater than):大于
    context["previous_blog"] = Blog.objects.filter(created_time__gt=blog.created_time).last()
    context["next_blog"] = Blog.objects.filter(created_time__lt=blog.created_time).first()
    context["blog"] = blog

    # form 表单实例化，使用公用模板返回表单实例化
    # context['login_form'] = LoginForm()

    # 下面灰色的地方都是用公用模板替换掉了
    # 获取评论内容
    # <ContentType: blog>
    # blog_content_type = ContentType.objects.get_for_model(blog)
    # 获取一级评论列表，parent=None 那些评论的回复就不会显示！！！
    # 在模板页面进行代码显示
    # comments = Comment.objects.filter(content_type=blog_content_type, object_id=blog.pk, parent=None)

    # 评论内容，倒序排序，而回复内容是正序排序（有点绕）
    # context['comments'] = comments.order_by('-comment_time')
    # 评论表单字段默认值初始化，如果是顶级评论， 'reply_comment_id': 0 ？？
    # 使用公用模板进行替换操作，不需要在views函数中写了，解耦合，简洁明了
    # context['comment_form'] = CommentForm(initial={'content_type': blog_content_type.model,
    #                                                'object_id': blog_pk, 'reply_comment_id': 0})

    # 判断用户登录
    context['user'] = request.user
    # 浏览器返回的信息响应response，返回给前端浏览器页面，同时存储cookie到浏览器
    response = render(request, "blog/blog_detail.html", context)
    # 存储cookie: 告诉浏览器要保存什么东西，cookie标记
    response.set_cookie(read_cookie_key, 'true')
    return response


# 路由传过来的参数名称要一致！
def blogs_with_type(request, blog_type_pk):
    blog_type = get_object_or_404(BlogType, pk=blog_type_pk)
    # print(blog_type)  例如：Django
    # 根据在BlogType中获取到的类型，继而在Blog中进行数据筛选
    # 外键拓展：blogs_all_list = Blog.objects.filter(blog_type_id=blog_type_pk)
    blogs_all_list = Blog.objects.filter(blog_type=blog_type)
    context = get_blog_list_common_data(request, blogs_all_list)
    context['blog_type'] = blog_type
    return render(request, 'blog/blogs_with_type.html', context)

    # 原始未分页
    # context = {}
    # # 按主键获取博客类型 数据BlogType
    # blog_type = get_object_or_404(BlogType, pk=blog_type_pk)
    # # 根据在BlogType中获取到的类型，继而在Blog中进行数据筛选
    # context['blogs'] = Blog.objects.filter(blog_type=blog_type)
    # context['blog_type'] = blog_type
    # context['blog_types'] = BlogType.objects.all()
    # return render_to_response('blog/blogs_with_type.html', context)


def blogs_with_date(request, year, month):
    # 链式查询，双下划线__
    blogs_all_list = Blog.objects.filter(created_time__year=year, created_time__month=month)
    context = get_blog_list_common_data(request, blogs_all_list)

    context['blogs_with_date'] = '%s年%s月' % (year, month)
    return render(request, 'blog/blogs_with_date.html', context)


"""
目录：
views文件，所在的文件夹blog,里面的文件属于views同一级。可以使用. 进行引用
但是blog和mysite、templates属于同一级，不包括views！！
../表示当前文件所在目录的上一级目录
应该是先在同级查找，然后是上一级，依次查找
mysite文件夹下的templates文件夹是“全局”文件夹
./ 只可以找到同文件夹下的文件？？
"""

"""
页面处理顺序：
1. def blogs_with_type(request, blog_type_pk):
里面的blog_type_pk 是url路径中自带的参数 localhost/blog/blog_type_pk
个人理解顺序是：模板页面点击-路由地址（参数）-views函数处理-模板显示

2. 而GET传参形式是区别于上面的，是点击按钮进行request请求，就通过GET或者POST自动进行提交
的，不需要url显式传值，提交后进入views中相应函数进行处理，然后返回到页面上
个人理解顺序是：模板页面点击-（路由）GET参数传递-views函数处理-模板显示  不经过显式的url
"""


"""
1. filter 筛选条件：书写形式：xxxx__gt = yyy
大于：__gt(greater than)
大于等于：__gte(greater than equal)
小于：__lt(less than)
小于等于：__lte
包含：__contains(加i忽略大小写: icontains)
=>Blog.objects.filter(title__contains='django')

开头是：__startswith
结尾是：__endswith

其中之一：__in
=>参数是列表
=>Blog.objects.filter(id__in=[2,3,4])

范围：__range  
=>参数是元组，且包含最大与最小值
=> Blog.objects.filter(id__range=(3,6))

2. exclude 排除条件：
相当于filter取反，进行筛选，相当于排除

3. 字段查询
（1）外键拓展
blogs_all_list = Blog.objects.filter(blog_type_id=blog_type_pk)
（2）日期拓展
Blog.objects.filter(created_time__year=2017)
（3）支持链式查询，可以一直查询下去
"""

"""
4. annotate注释方法:可以实现数量查询功能
可以使用命令行，查询对象，变量啥的包含什么方法=》dir(xxxx)
annotate方法：是将全部数据取出来，然后再按照条件参数查询每个的博客数量，
将统计数据作为对象的属性进行动态添加。
#（2）使用django自带的方法 => annotate注释方法，而且还是外键，两个表关联
# 可以不使用'blog_blog'，直接写相关联模型名称的小写：'blog'
# BlogType.objects.annotate(blog_count=Count('blog_blog'))
"""

"""
5. cookie:
（1）cookie是由服务器生成，存储在浏览器端的一小段文本信息
cookie在浏览器中的存储是键值对，字典形式:key ,value
cookie 是可以设置有效期限的，浏览器只会保存有效期内的
有效时间以秒计数，如果不设置有效期限，cookie会一直保存，直到退出浏览器，才会失效
参数max_age设置过期时间，单位是秒
参数expires设置到哪个时间过期，日期类型

（2）浏览器前端向服务器 发送请求，默认是会携带cookie的，第一次没有cookie的时候会携带空字典到服务器，
之后再次请求就会将存储的cookie传给服务器
"""

"""
6. request介绍：
当一个页面被请求时，应该是向服务器请求，Django服务器就会创建一个包含本次请求原信息的HttpRequest对象
django会将这个对象自动传递给响应的视图函数，一般约定俗成使用request承接这个对象。
"""

"""
7. Blog.objects.dates('created_time', 'month', order='DESC')
dates函数：
（1）month:包含年和月
>>> blog_dates = Blog.objects.dates('created_time', 'month', order='DESC')
>>> blog_dates
<QuerySet [datetime.date(2020, 4, 1)]>
（2）year:只包含年
>>> blog_dates = Blog.objects.dates('created_time', 'year', order='DESC')
>>> blog_dates
<QuerySet [datetime.date(2020, 1, 1)]>
（3）day:包含年月日
>>> blog_dates = Blog.objects.dates('created_time', 'day', order='DESC')
>>> blog_dates
<QuerySet [datetime.date(2020, 4, 15), datetime.date(2020, 4, 13), datetime.date(2020, 4, 12)]>

注：不包含的地方都用1表示！！
可以直接使用.
>>> blog_dates[0].year
2020
>>> blog_dates[0].month
4
>>> blog_dates[0].day
1
"""

"""
8. render_to_response 与 render 函数的区别
（1）前者多需要一个request参数
（2）但使用后者可以直接在模板页面使用request,不需要通过context传值，比较方便
（3）django中设置中自带一些模板及方法，例如request.user在模板页面就可以直接写user,
    因为已设置方法直接返回user值
（4）render相对于render_to_response更加齐全一些，最好使用render 函数！！
    不然对于form表单提交，render_to_response函数可能会出现问题。
"""
