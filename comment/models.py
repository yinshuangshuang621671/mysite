from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.utils import timezone

# 发送邮件函数
from django.core.mail import send_mail
from django.conf import settings

# 引入多线程
import threading
# html模板库？？？？，在这里就可以调用相应模板
from django.template.loader import render_to_string
from django.shortcuts import render


# 多线程
class SendMail(threading.Thread):
    def __init__(self, subject, text, email, fail_silently=False):
        self.subject = subject
        self.text = text
        self.email = email
        self.fail_silently = fail_silently
        # 执行父类的初始化函数？？？？
        threading.Thread.__init__(self)

    def run(self):
        send_mail(self.subject,
                  '',
                  settings.EMAIL_HOST_USER,
                  [self.email],
                  fail_silently=self.fail_silently,
                  # 将文本内容转成html进行发送
                  html_message=self.text,
                  )


class Comment(models.Model):
    # 评论对象：通过ContentType设置外键
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    # content_object默认显示形式：Blog object (34)
    # 可通过Blog中的__str__函数进行修改
    content_object = GenericForeignKey('content_type', 'object_id')

    text = models.TextField()
    # 2020年4月28日 09:30
    comment_time = models.DateTimeField(auto_now_add=True)
    # 可以设置默认值来代替auto_now_add=True，此时时区可以设置为True
    # timezone.now:输出的是UTC时间
    # comment_time = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE)

    # 外键指向自身，比较奇特，使用实例化对象！
    root = models.ForeignKey('self', related_name='root_comment', null=True, on_delete=models.CASCADE)
    # 定义评论的回复外键，外键指向自身，但如果是评论的话（不是回复），就没有他的上级，设置null
    parent = models.ForeignKey('self', related_name='parent_comment', null=True, on_delete=models.CASCADE)
    reply_to = models.ForeignKey(User, related_name='replies', null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.text

    # 正序排序
    class Meta:
        ordering = ['comment_time']

    def send_mail(self):
        if self.parent is None:
            # 评论博客
            subject = '有人评论你的博客'
            # 发送给这篇博客的作者， 在Blog.models中，重写的方法
            email = self.content_object.get_email()
        else:
            # 回复评论
            subject = '有人回复你的评论'
            email = self.reply_to.email

        # 如果邮箱不为空
        if email != '':
            # 使用reverse反向解析被评论的是哪一篇博客的链接地址，在Blog.models中，重写的方法
            # text = self.text + '\n' + self.content_object.get_url()

            # 优化上面，写成html代码，进行修饰
            # text = '%s\n <a href="%s">%s</a>' % (self.text, self.content_object.get_url())

            # 进一步优化上面，使用html模板，虽然不太懂，和模板的传值方式一样
            context = {}
            context['comment_text'] = self.text
            context['url'] = self.content_object.get_url()

            text = render_to_string('comment/send_mail.html', context)

            # ？？？？ 反正这个p是去不掉了。。。
            # text = render(None, 'comment/send_mail.html', context).content.decode('utf-8')
            # 发送验证码邮件，使用多线程
            send_mail = SendMail(subject, text, email)
            # 开始多线程
            send_mail.start()


"""
1. 
涉及到评论内容及回复内容的正序与倒序排序，评论是倒序排序，
而回复是正序排序（在blog/views的blog_detail中）进行设置
"""

"""
2. ckeditor自带p标签
可以在后台数据库看出，使用ckeditor获取到的文本text内容，本身就是有p标签的
在前端页面进行显示的时候，在html模板页面中，使用过滤器safe,使文字正常显示即可
"""

"""
3.    
render_to_string函数：
传递参数加载一个html页面，并返回一个字符串 
Load a template and render it with a context. Return a string.
template_name may be a string or a list of strings.

render函数：是返回一个HttpResponse对象
"""



