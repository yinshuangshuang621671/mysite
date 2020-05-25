from .models import Profile
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
# django自带的用户模型User
from django.contrib.auth.models import User


# 不是很懂
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False


# 这里是重写UserAdmin ??? 不太懂
class UserAdmin(BaseUserAdmin):
    # 这是将Profile嵌入到User模型中 ？Profile与User类是一对一的关系且User是Profile的外键
    inlines = (ProfileInline, )
    list_display = ('username', 'nickname', 'email', 'is_staff', 'is_active', 'is_superuser')

    # 固定写法？？？？加个obj ???
    def nickname(self, obj):
        # 使用一对一外键之间的关联作用？？
        return obj.profile.nickname

    # 使得字段显示中文
    nickname.short_description = '昵称'


# 使用第一种注册方式，这种方法重写的Useradmin也需要注册！
# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


# 使用第二种 注册方式，直接注册模型就好了，不需要注册重写的UserAdmin
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'nickname')
