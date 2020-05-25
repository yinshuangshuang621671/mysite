from django import template
from django.contrib.contenttypes.models import ContentType
from ..models import LikeCount, LikeRecord

# 第一次创建这个公用模板需要重启！！！
# 统计评论数，使用公用模板方式
register = template.Library()


@register.simple_tag
# obj是从前端模板页面传入
def get_like_count(obj):
    content_type = ContentType.objects.get_for_model(obj)
    # 返回当前博客的评论及回复总数，博客可能是第一次点赞，所以用get_or_create，
    # 如果没有点赞的，显示点赞数就为0
    like_count, created = LikeCount.objects.get_or_create(content_type=content_type, object_id=obj.pk)
    return like_count.liked_num


# takes_context=True ???????????
@register.simple_tag(takes_context=True)
def get_like_status(context, obj):
    content_type = ContentType.objects.get_for_model(obj)
    user = context['user']
    # 判断用户是否登录
    if not user.is_authenticated:
        return ''
    # 如果用户在当前博客的点赞记录存在，就变红（因为一人只允许点赞一次，就一条数据）
    if LikeRecord.objects.filter(content_type=content_type, object_id=obj.pk, user=context['user']).exists():
        return 'active'
    else:
        return ''


@register.simple_tag
def get_content_type(obj):
    content_type = ContentType.objects.get_for_model(obj)
    return content_type.model


# 1. @register.simple_tag(takes_context=True):
# 这是啥？不太懂
