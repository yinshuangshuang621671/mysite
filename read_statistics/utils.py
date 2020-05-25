import datetime
from django.contrib.contenttypes.models import ContentType
from .models import ReadNum, ReadDetail
from django.utils import timezone
from django.db.models import Sum


# 统计阅读数量（两种情况）
def read_statistics_once_read(request, obj):
    ct = ContentType.objects.get_for_model(obj)
    key = "%s_%s_read" % (ct.model, obj.pk)
    # 已经点击当前博客详情页了，如果cookies中“不”存在博客阅读记录，阅读数量加一
    # 只要当前博客已经点击了，在cookie不失效的情况下，就当做一次！！
    # 字典的键不一定就是字符串，变量也是可以的
    if not request.COOKIES.get(key):
        # 1. 统计阅读数量（前提是cookie不存在！！！）
        # get_or_create函数：存在博客阅读记录，取出相应记录，阅读数量加一
        # 没有记录的话就创建一条新的记录，然后阅读数量加一
        readnum, created = ReadNum.objects.get_or_create(content_type=ct, object_id=obj.pk)
        # 计数均加一
        readnum.read_num += 1
        readnum.save()

        # 2. 按日期统计当天阅读数量（前提是cookie不存在！！！）
        # timezone.now()：获取当前时间
        date = timezone.now().date()
        readDetail, created = ReadDetail.objects.get_or_create(content_type=ct, object_id=obj.pk, date=date)
        readDetail.read_num += 1
        readDetail.save()
    return key


# 查看前7天的阅读量数据
def get_seven_days_read_data(content_type):
    today = timezone.now().date()
    dates = []
    read_nums = []
    # 查看前7天的数据
    for i in range(7, 0, -1):
        # datetime.timedelta(days=i) 设置时间差值
        date = today - datetime.timedelta(days=i)
        print(date)
        # strftime()函数将时间格式转化为我们想要的格式，识别以百分号（%）开始的格式命令集合
        dates.append(date.strftime('%m/%d'))   # 日期转化为字符串格式

        read_details = ReadDetail.objects.filter(content_type=content_type, date=date)
        # aggregate ：聚合函数
        # 将筛选出来的数据read_num字段加和！，即统计每一天的阅读量
        result = read_details.aggregate(read_num_sum=Sum('read_num'))
        # 存在显示，不存在显示0
        read_nums.append(result['read_num_sum'] or 0)
    # 返回的结果是每一天内博客的阅读数量
    return dates, read_nums,

# 未使用read_details = GenericRelation(ReadDetail) 之前的原始写法
# 获取昨天的热门博客（一天内）
# def get_yesterday_hot_data(content_type):
#     today = timezone.now().date()
#     yesterday = today - datetime.timedelta(days=1)   # 昨天
#     read_details = ReadDetail.objects.filter(content_type=content_type, date=yesterday).order_by('-read_num')
#     return read_details[:7]
# 然后通过ReadDetail 数据获取到content_object从而获取相应id,title，好像有点麻烦。。。


"""
1. aggregate:聚合函数，对查询集合中的全部对象的某个属性进行汇总，得到的是字典形式，键值对儿。
"""

"""
1. ReadDetail表中，是按照日期来存储相应博客阅读记录，因为会判断表中是否已经存在相应博客阅读记录，
不存在会创建，所以一天内的博客阅读记录是不会出现重复的
2. 而一周内，不同日期内，阅读的博客可能会相同的，所以统计一周内的阅读量时，
需要分组进行统计?
"""