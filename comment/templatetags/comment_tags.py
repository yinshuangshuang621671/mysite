from django import template
from django.contrib.contenttypes.models import ContentType
from ..models import Comment
from ..forms import CommentForm
from django.db.models.fields import exceptions
from read_statistics.models import ReadNum

# 统计评论数，使用公用模板方式
register = template.Library()


@register.simple_tag
# obj是从前端模板页面传入
def get_comment_count(obj):
    content_type = ContentType.objects.get_for_model(obj)
    # 返回当前博客的评论及回复总数
    return Comment.objects.filter(content_type=content_type, object_id=obj.pk).count()


@register.simple_tag
# 获取并初始化评论表单
def get_comment_form(obj):
    content_type = ContentType.objects.get_for_model(obj)
    form = CommentForm(initial={'content_type': content_type.model,
                                'object_id': obj.pk,
                                'reply_comment_id': 0})
    return form


@register.simple_tag
# 获取评论列表
def get_comment_list(obj):
    content_type = ContentType.objects.get_for_model(obj)
    comments = Comment.objects.filter(content_type=content_type, object_id=obj.pk, parent=None)
    return comments.order_by('-comment_time')


@register.simple_tag
def get_read_num(obj):
    try:
        # 参数是模型或者模型对象（self即可）
        # 就是通过ContentType这个中介找到模型Blog
        ct = ContentType.objects.get_for_model(obj)
        readnum = ReadNum.objects.get(content_type=ct, object_id=obj.pk)
        return readnum.read_num
    # 不存在相应记录
    except exceptions.ObjectDoesNotExist:
        return 0
