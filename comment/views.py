from django.shortcuts import render, redirect
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
# ajax异步请求
from django.http import JsonResponse
from .models import Comment
from .forms import CommentForm

# 发送邮件函数
from django.core.mail import send_mail
from django.conf import settings


# 用户提交评论，处理函数
def update_comment(request):
    # 原始
    referer = request.META.get('HTTP_REFERER', reverse('home'))
    # if not request.user.is_authenticated:
    #     return render(request, 'error.html', {'message': '用户未登录', 'redirect_to': referer})
    #
    # text = request.POST.get('text', '').strip()
    # if text == '':
    #     return render(request, 'error.html', {'message': '评论内容为空', 'redirect_to': referer})
    #
    # try:
    #     # 阻挡一切意外
    #     content_type = request.POST.get('content_type', '')
    #     # get 函数获取到的是"字符串"，需要将其转化为数值类型，加int()函数强制类型转换
    #     object_id = int(request.POST.get('object_id', ''))
    #
    #     # get函数参数需要传入”字符串“
    #     model_class = ContentType.objects.get(model=content_type).model_class()
    #     model_object = model_class.objects.get(pk=object_id)
    #
    # except Exception as e:
    #     return render(request, 'error.html', {'message': '评论对象不存在', 'redirect_to': referer})
    #
    # # 一切正常，添加评论
    # comment = Comment()
    # comment.user = request.user
    # comment.text = text
    # comment.content_object = model_object
    # comment.save()
    # # 重定向 redirect
    # return redirect(referer)

    # 异步： ajax返回数据
    data = {}
    referer = request.META.get('HTTP_REFERER', reverse('home'))
    # forms表单实例化，传入用户对象
    comment_form = CommentForm(request.POST, user=request.user)

    if comment_form.is_valid():
        # 检查通过，创建并保存评论数据
        comment = Comment()
        # comment.user = request.user  两种方法
        comment.user = comment_form.cleaned_data['user']
        comment.text = comment_form.cleaned_data['text']
        comment.content_object = comment_form.cleaned_data['content_object']

        # 找到它的上级数据
        parent = comment_form.cleaned_data['parent']
        # 是回复而不是评论
        if parent is not None:
            # 这个root有什么用呢？？有parent不够？
            # 如果有根就设置根，如果没有就将根设置为parent?
            comment.root = parent.root if parent.root is not None else parent
            comment.parent = parent
            comment.reply_to = parent.user
        comment.save()

        # 发送邮件通知（分为评论和回复两种情况）转移到comment.models中
        comment.send_mail()

        # return redirect(referer)

        # ajax异步数据处理，返回成功数据
        data['status'] = 'SUCCESS',
        # data['username'] = comment.user.username,  使用新方法替换，注意是需要返回值，加括号
        data['username'] = comment.user.get_nickname_or_username(),
        # strftime：自定义日期格式转换
        # 数据库中存储的为UTC时间，不能直接进行格式转换，不然显示的还是UTC。
        # data['comment_time'] = comment.comment_time.strftime('%Y-%m-%d %H:%M:%S'),
        # 使用时间戳
        print("时间:", comment.comment_time)
        # UTC时间格式
        data['comment_time'] = comment.comment_time.timestamp()
        data['text'] = comment.text
        data['content_type'] = ContentType.objects.get_for_model(comment).model
        data['pk'] = comment.pk

        # 返回的回复或评论数据，
        # data['reply_to'] = comment.reply_to.username if comment.parent is not None else ''
        data['reply_to'] = comment.reply_to.get_nickname_or_username() if comment.parent is not None else ''
        data['root_pk'] = comment.root.pk if comment.root is not None else ''

    else:
        # 传递失败数据
        # return render(request, 'error.html', {'message': comment_form.errors, 'redirect_to': referer})
        data['status'] = 'ERROR'
        data['message'] = list(comment_form.errors.values())[0][0]
        # print("错误：", comment_form.errors)
    # ajax 表单异步处理响应
    return JsonResponse(data)


"""
1. ContentType对象中相应操作
（1）get函数，传入参数为模型名称小写”字符串“
（2）model_class()：就可以直接获取到model中定义的class类
>>> model_class = ContentType.objects.get(model='blog').model_class()
>>> model_class
<class 'blog.models.Blog'>

（3）get_for_model(Blog)：
传入参数为模型名称或者模型实例，返回值为ContentType表中存在的model，有点绕
通过model或者model的实例来寻找ContentType类型？？？
>>> ct = ContentType.objects.get_for_model(Blog)
>>> ct
<ContentType: blog>
>>> ct.model
'blog'

get_for_model(Blog)会返回一个ContentType类型的blog，
ContentType类型的model可以关联到所有的model,就是来个中介？？？有点绕
"""

"""
2. pop 与 get 的区别？？？
"""

"""
3. 
(1)在forms表单中，通过reply_comment_id的值，来确定是评论（0）还是回复（>0），从而设定parent的值
(2)在views函数中 根据cleaned_data['parent']判断是评论还是回复
"""
"""
4.
ajax的返回日期，比当前的时间晚了8个小时？？？
strftime：自定义日期格式转换,将日期类型处理转化为字符串，数据库是什么就转换成什么
# data['comment_time'] = comment.comment_time.strftime('%Y-%m-%d %H:%M:%S'),
时间戳=》返回距离格林威治标准时间的 秒数
data['comment_time'] = comment.comment_time.timestamp()         

（1）DateTimeField类型：日期加时间，与python中的datetime.datetime实例相同
（2）timestamp:是首先存储为世界标准时间然后按照客户端当前时区来取，而DateTimeField是存什么就是什么
没有一个转换的过程
（3）comment_time = models.DateTimeField(auto_now_add=True)：
auto_now_add=True：默认为UTC时间，即国际标准时间，伦敦时间，我们是东八区，所以看到
的时间比当前时间要晚八个小时（在settings中重置时区进行改变）
疑惑的问题是，存入数据库中的是正常显示时间，但是取出数据的时候显示的却是UTC????

（4）html页面从数据库中读出DateTimeField字段时，显示的时间格式和数据库中存储的不同，
为了页面和数据库中显示一直，需要在页面格式化时间，使用date过滤器xx.comment_time|date:"Y-m-d H:i:s"
（5）timestamp()函数，会根据你的客户端时区而返回对应的距离标准时间的秒数，包含时区信息！！

（6）在ajax返回日期之前，评论实例保存到数据库：comment.save()，保存为UTC时间
但是返回ajax的数据data中，是直接使用的comment,而不是从数据库中读取，
所以它的评论时间使用的时区还是UTC，而使用comment.save()后，
保存到数据库（前端显示页面）中的时间是北京时间，

（7）TIME_ZONE = 'Asia/Shanghai'及USE_TZ = True：
django在1.4的版本之后，若存储设置为USE_TZ = True：则存储到数据库中的时间永远是UTC时间！！
尽管数据库中存储的是UTC时间，但是在数据库前端页面显示的时候，
会转成Timezone所在的本地时间进行显示（高级）


>>> from comment.models import Comment
>>> ct=Comment.objects.first()
>>> ct.comment_time
# 这里是已经在设置中改了时区，却还是显示的UTC???
因为所能看见的数据库数据是数据库的前端页面。。。。。后端还是得在程序中看。。。
datetime.datetime(2020, 4, 28, 1, 30, 34, 623586, tzinfo=<UTC>)
>>> tt = ct.comment_time.timestamp()
>>> tt
1588037434.623586
"""

"""
5. strftime与strptime
（1）strftime：由日期格式转化为字符串格式
（2）strptime：由字符串格式转化为日期格式
"""

"""
6. time及datetime两个单独的模块都可以完成日期格式到其他格式，或时间戳的转换
import time
import datetime 
from datetime import datetime

"""

"""
7. get_nickname_or_username() 在User这个app中的models文件中
是为User这个模型新增加的方法，用户实例可以进行调用，说实话不是很懂。。。
"""

"""
8. 有些厉害          
使用reverse反向解析被评论的是哪一篇博客的链接地址，将参数传递给路由地址
（1）text = comment.text + reverse('blog_detail', args=[comment.content_object.pk])
（2）使用关键字参数kwargs(为字典形式)
关键字对应路由地址中的关键字
text = comment.text + reverse('blog_detail', kwargs={'blog_pk', comment.content_object.pk})
"""

"""
9. 使用多线程发送邮件，因为评论处理的ajax数据返回是在发送完邮件之后，所以会有一定的延时
所以使用多线程方式进行多任务处理

"""