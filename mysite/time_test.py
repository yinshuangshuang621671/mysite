import time
import datetime
from datetime import datetime

# 字符串，而不是时间类型！
s = '2019-06-07 16:30:10'
f = '%Y-%m-%d %H:%M:%S'

# 时间字符串转换时间戳
# （1）s是一个字符串，首先需要将其转化为时间类型：datetime.strptime(s, f)，然后再转换为时间戳
t = datetime.strptime(s, f).timestamp()   # 1559896210.0
tt = datetime.strptime(s, f)
# print(tt)
# 2019-06-07 16:30:10
# print(type(tt))
# <class 'datetime.datetime'>


# （2）
t2 = time.mktime(time.strptime(s, f))
tt2 = time.strptime(s, f)

# 这个类型有点怪
# print(tt2)
# time.struct_time(tm_year=2019, tm_mon=6, tm_mday=7, tm_hour=16, tm_min=30, tm_sec=10,
#                  tm_wday=4, tm_yday=158, tm_isdst=-1)
# print(type(tt2))
# <class 'time.struct_time'>


ut = 1559896210.0
# 将时间戳转换为当前时间
t3 = time.localtime(t)
# print(t3)
# time.struct_time(tm_year=2019, tm_mon=6, tm_mday=7, tm_hour=16, tm_min=30, tm_sec=10,
#                  tm_wday=4, tm_yday=158, tm_isdst=0)

d = datetime.fromtimestamp(ut)
print(d)
d2 = time.strftime(f, time.localtime(ut))
print(d2)


# 网址
# https://blog.csdn.net/lsg9012/article/details/86546345








# if __name__ == '__main__':
