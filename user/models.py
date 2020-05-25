from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    # 使用一对一外键
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nickname = models.CharField(max_length=20, verbose_name='昵称')

    # 数据的显示样式
    def __str__(self):
        return '<Profile: %s for %s>' % (self.nickname, self.user.username)


# 说实话是不太懂的。。。
def get_nickname(self):
    if Profile.objects.filter(user=self).exists():
        profile = Profile.objects.get(user=self)
        return profile.nickname
    else:
        return ''


def get_nickname_or_username(self):
    if Profile.objects.filter(user=self).exists():
        profile = Profile.objects.get(user=self)
        return profile.nickname
    else:
        return self.username


# 返回true或者false
def has_nickname(self):
    return Profile.objects.filter(user=self).exists()


# 给User模型实例对象新增加了一个属性方法是吧？
User.get_nickname = get_nickname
User.has_nickname = has_nickname
User.get_nickname_or_username = get_nickname_or_username
