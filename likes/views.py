from django.shortcuts import render
from django.contrib.contenttypes.models import ContentType
from .models import LikeCount, LikeRecord
from django.http import JsonResponse
from django.db.models import ObjectDoesNotExist


def SuccessResponse(liked_num):
    data = {}
    data['status'] = 'SUCCESS'
    data['liked_num'] = liked_num
    return JsonResponse(data)


def ErrorResponse(code, message):
    data = {}
    data['status'] = 'ERROR'
    data['code'] = code
    data['message'] = message
    return JsonResponse(data)


# 点赞功能
def like_change(request):
    user = request.user
    # 验证用户登录
    if not user .is_authenticated:
        return ErrorResponse(400, '未登录，无法点赞')

    # 获取数据
    # 获取到的content_type是个字符串，而不是ContentType，需要再转换一下！！！
    content_type = request.GET.get('content_type')
    object_id = int(request.GET.get('object_id'))
    is_like = request.GET.get('is_like')

    try:
        content_type = ContentType.objects.get(model=content_type)
        model_class = content_type.model_class()
        model_obj = model_class.objects.get(pk=object_id)
    except ObjectDoesNotExist:
        return ErrorResponse(401, '对象不存在')

    # 处理数据
    if is_like == 'true':
        # 某人要点赞
        like_record, created = LikeRecord.objects.get_or_create(content_type=content_type, object_id=object_id, user=user)

        if created:
            # 未点赞过，进行点赞，LikeCount（点赞数）加1
            like_count, created = LikeCount.objects.get_or_create(content_type=content_type, object_id=object_id)
            like_count.liked_num += 1
            like_count.save()
            return SuccessResponse(like_count.liked_num)
        else:
            # 已点赞过，不能重复点赞
            return ErrorResponse(402, '你已经点赞过')

    else:
        # 某人要取消点赞
        if LikeRecord.objects.filter(content_type=content_type, object_id=object_id, user=user).exists():
            # 有点赞过，取消点赞
            like_record = LikeRecord.objects.get(content_type=content_type, object_id=object_id, user=user)
            like_record.delete()
            # 点赞总数减一(判断) ？？没必要啊，已经是点过赞了啊
            like_count, created = LikeCount.objects.get_or_create(content_type=content_type, object_id=object_id)
            if not created:
                like_count.liked_num -= 1
                like_count.save()
                return SuccessResponse(like_count.liked_num)
            else:
                return ErrorResponse(404, '数据错误')
        else:
            # 没有点赞过，不能取消
            return ErrorResponse(403, '你没有点赞过，无法取消')
