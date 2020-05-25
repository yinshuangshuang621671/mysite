from django import forms
from django.contrib import auth
# 使用django自带的用户模型
from django.contrib.auth.models import User


class LoginForm(forms.Form):
    # 浏览器显示可以自动转化为html代码
    # form-control 默认设定不能为空，为空会有提示，相当于错误提示了，那在模板页面就不需要写了
    # 修改为用户名或邮箱都可以登录
    # username = forms.CharField(label='用户名',
    #                            widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "请输入用户名"}))
    username_or_email = forms.CharField(label='用户名或邮箱',
                                        widget=forms.TextInput(
                                            attrs={'class': 'form-control', 'placeholder': "请输入用户名或邮箱"})
                                        )

    password = forms.CharField(label='密码',
                               widget=forms.PasswordInput(
                                   attrs={'class': 'form-control', 'placeholder': "请输入密码"})
                               )

    # clean为先验证后clean
    def clean(self):
        # print(self.cleaned_data)
        # cleaned_data  获取表单数据，字段与表单一致
        username_or_email = self.cleaned_data['username_or_email']
        password = self.cleaned_data['password']

        # 用户验证放到这里,不管你输入的是啥（用户名或邮箱），先使用用户名进行登录试试
        # auth.authenticate 函数中，request参数不是必须的！
        # ？？？？这个函数不懂
        user = auth.authenticate(username=username_or_email, password=password)

        if user is None:
            # 会自动设置到对象的错误信息中，实例对象可以通过.non_field_errors进行错误信息显示
            # 换邮箱试试，可以的话返回user
            if User.objects.filter(email=username_or_email).exists():
                username = User.objects.get(email=username_or_email).username
                user = auth.authenticate(username=username, password=password)

                if user is not None:
                    self.cleaned_data['user'] = user
                    return self.cleaned_data

            raise forms.ValidationError('用户名或密码不正确')
        else:
            self.cleaned_data['user'] = user
        # 固定返回值：cleaned_data
        return self.cleaned_data


# 注册
class RegForm(forms.Form):
    username = forms.CharField(
        label='用户名',
        max_length=30,
        min_length=3,
        widget=forms.TextInput(
           attrs={'class': 'form-control', 'placeholder': "请输入3-30位用户名"})
       )
    email = forms.EmailField(
        label='邮箱',
        widget=forms.EmailInput(
            attrs={'class': 'form-control', 'placeholder': "请输入邮箱"})
        )
    # 验证码
    verification_code = forms.CharField(
        label='验证码',
        required=False,  # 不是必填字段，在下面进行非空验证
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': '点击“发送验证码”发送到邮箱'}
        )
    )
    password = forms.CharField(
        label='密码',
        min_length=6,
        widget=forms.PasswordInput(
           attrs={'class': 'form-control', 'placeholder': "请输入密码（最少6位）"})
        )
    password_again = forms.CharField(
        label='再次输入密码',
        min_length=6,
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': "请输入密码（最少6位）"})
        )

    def __init__(self, *args, **kwargs):
        # 使用关键字参数传递？？？
        # 使用pop，获取并剔除参数，有待学习，代码各种逻辑
        # 如果用get,获取后self中就存在这个user,在forms.Form进行初始化验证的时候，
        # 表单设置中并没有这个user参数，会报错
        if 'request' in kwargs:
            self.request = kwargs.pop('request')
        super(RegForm, self).__init__(*args, **kwargs)

    def clean(self):
        # 判断验证码
        code = self.request.session.get('register_code', '')
        verification_code = self.cleaned_data.get('verification_code', '')
        if not(code != '' and code == verification_code):
            raise forms.ValidationError('验证码错误')
        # 不要忘了下面这句
        return self.cleaned_data

    # 单个字段验证，错误信息提示，注意在模板页面的错误信息显示，区别于上面
    def clean_username(self):
        username = self.cleaned_data['username']
        # 判断与已注册用户是否重名
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("用户已存在")
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        # 判断与已注册用户是否重名
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("邮箱已存在")
        return email

    # 验证验证码是否为空
    def clean_verification_code(self):
        verification_code = self.cleaned_data.get('verification_code', '').strip()
        if verification_code == '':
            raise forms.ValidationError('验证码不能为空')
        return verification_code

    def clean_password_again(self):
        password = self.cleaned_data['password']
        password_again = self.cleaned_data['password_again']
        if password != password_again:
            raise forms.ValidationError('两次输入的密码不一致')
        return password_again


# 修改昵称
class ChangeNicknameForm(forms.Form):
    nickname_new = forms.CharField(label='新的昵称',
                                   max_length=20,
                                   widget=forms.TextInput(
                                       attrs={'class': 'form-control', 'placeholder': '请输入新的昵称'}
                                   ))

    def __init__(self, *args, **kwargs):
        # 使用关键字参数传递？？？
        # 使用pop，获取并剔除参数，有待学习，代码各种逻辑
        # 如果用get,获取后self中就存在这个user,在forms.Form进行初始化验证的时候，
        # 表单设置中并没有这个user参数，会报错
        if 'user' in kwargs:
            self.user = kwargs.pop('user')
        super(ChangeNicknameForm, self).__init__(*args, **kwargs)

    def clean(self):
        # 后端再一次判断用户是否登录
        if self.user.is_authenticated:
            self.cleaned_data['user'] = self.user
        else:
            raise forms.ValidationError('用户未登录')
        # 记住要返回下面这个！！！cleaned_data
        return self.cleaned_data

    def clean_nickname_new(self):
        nickname_new = self.cleaned_data.get('nickname_new', '').strip()
        if nickname_new == '':
            raise forms.ValidationError('新的昵称不能为空')
        return nickname_new


# 绑定邮箱，表单
class BindEmailForm(forms.Form):
    email = forms.EmailField(
        label='邮箱',
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': '请输入正确的邮箱'}
        )
    )
    verification_code = forms.CharField(
        label='验证码',
        required=False,  # 不是必填字段，在下面进行非空验证
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': '点击“发送验证码”发送到邮箱'}
        )
    )

    def __init__(self, *args, **kwargs):
        # 使用关键字参数传递？？？
        # 使用pop，获取并剔除参数，有待学习，代码各种逻辑
        # 如果用get,获取后self中就存在这个user,在forms.Form进行初始化验证的时候，
        # 表单设置中并没有这个user参数，会报错
        if 'request' in kwargs:
            self.request = kwargs.pop('request')
        super(BindEmailForm, self).__init__(*args, **kwargs)

    def clean(self):
        # 后端再一次判断用户是否登录
        if self.request.user.is_authenticated:
            self.cleaned_data['user'] = self.request.user
        else:
            raise forms.ValidationError('用户未登录')

        # 验证用户是否已经绑定邮箱
        if self.request.user.email != '':
            raise forms.ValidationError('你已经绑定邮箱，无法重复绑定')

        # 判断验证码
        code = self.request.session.get('bind_email_code', '')
        verification_code = self.cleaned_data.get('verification_code', '')
        if not(code != '' and code == verification_code):
            raise forms.ValidationError('验证码错误')

        # 记住要返回下面这个！！！cleaned_data
        return self.cleaned_data

    # 验证邮箱是否已经存在
    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('该邮箱已被绑定')
        return email

    # 验证验证码是否为空
    def clean_verification_code(self):
        verification_code = self.cleaned_data.get('verification_code', '').strip()
        if verification_code == '':
            raise forms.ValidationError('验证码不能为空')
        return verification_code


# 修改密码表单
class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(label='原密码',
                                   widget=forms.PasswordInput(
                                    attrs={'class': 'form-control', 'placeholder': "请输入原密码"})
                                   )
    new_password = forms.CharField(label='新密码',
                                   widget=forms.PasswordInput(
                                    attrs={'class': 'form-control', 'placeholder': "请输入新密码"})
                                   )
    new_password_again = forms.CharField(label='请再次输入新的密码',
                                         widget=forms.PasswordInput(
                                            attrs={'class': 'form-control', 'placeholder': "请再次输入新的密码"})
                                         )

    def __init__(self, *args, **kwargs):
        # 使用关键字参数传递？？？
        # 使用pop，获取并剔除参数，有待学习，代码各种逻辑
        # 如果用get,获取后self中就存在这个user,在forms.Form进行初始化验证的时候，
        # 表单设置中并没有这个user参数，会报错
        if 'user' in kwargs:
            self.user = kwargs.pop('user')
        super(ChangePasswordForm, self).__init__(*args, **kwargs)

    def clean(self):
        # 验证新的密码是否一致
        new_password = self.cleaned_data.get('new_password', '')
        new_password_again = self.cleaned_data.get('new_password_again', '')

        if new_password != new_password_again or new_password == '':
            raise forms.ValidationError('两次输入的密码不一致')
        return self.cleaned_data

    def clean_old_password(self):
        # 验证旧的密码是否正确
        old_password = self.cleaned_data.get('old_password', '')
        # 函数返回true or false
        if not self.user.check_password(old_password):
            raise forms.ValidationError('原密码输入错误')
        return old_password


# 重置密码，使用邮箱进行重置
class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(
        label='邮箱',
        widget=forms.EmailInput(
            attrs={'class': 'form-control', 'placeholder': "请输入绑定过的邮箱邮箱"})
        )
    # 验证码
    verification_code = forms.CharField(
        label='验证码',
        required=False,  # 不是必填字段，在下面进行非空验证
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': '点击“发送验证码”发送到邮箱'}
        )
    )
    new_password = forms.CharField(
        label='新的密码',
        min_length=6,
        widget=forms.PasswordInput(
           attrs={'class': 'form-control', 'placeholder': "请输入密码（最少6位）"})
        )

    def __init__(self, *args, **kwargs):
        # 使用pop，获取并剔除参数，有待学习，代码各种逻辑
        # 如果用get,获取后self中就存在这个user,在forms.Form进行初始化验证的时候，
        # 表单设置中并没有这个user参数，会报错
        if 'request' in kwargs:
            self.request = kwargs.pop('request')
        super(ForgotPasswordForm, self).__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data['email'].strip()
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError('邮箱不存在')
        return email

    # 判断验证码
    def clean_verification_code(self):
        verification_code = self.cleaned_data.get('verification_code', '').strip()
        if verification_code == '':
            raise forms.ValidationError('验证码不能为空')

        # 判断验证码
        code = self.request.session.get('forgot_password_code', '')
        verification_code = self.cleaned_data.get('verification_code', '')
        if not (code != '' and code == verification_code):
            raise forms.ValidationError('验证码不正确')

        return verification_code
"""
1. 浏览器中转化后的 html代码:
<label for="id_username">用户名:</label>
<input type="text" name="username" required="" id="id_username">
"""

"""
2. clean:验证函数
（1）form类的运行顺序是init,clean,validate,save
clean,validate 会在 login_form.is_valid()方法中被先后调用，不需要在视图中调用，会自动调用
（2）clean函数必须有返回值：cleaned_data
为字典类型，键值对儿
（3）cleaned_data就是读取表单返回的值，返回类型为字典类型
cleaned_data['username']：读取name为username 的表单提交值，按name提取。
（4）forms表单中的字段会自动验证你的输入，而且会自动将你的输入转换成字段需要的类型，
即你可以输入多种类型，都会自动转换成有效的字段，非常给力，
（5）只要你的字段输入值有效，符合设置的字段值类型，表单就会有一个cleaned_data属性，
其中字段与表单字段一致。（官方文档解释还是很好理解的）
"""

"""
3. django中用form类来描述html表单，帮助简化操作
（1） 接受和处理用户提交的数据，可以检查提交的数据，可以将数据转换成python的数据类型
（2）可以自动生成html代码!!!!!
"""
"""
4. 在clean函数中抛出的一切异常：
raise forms.ValidationError('用户名或密码不正确')
都不会与特定的任何字段相关联，它们会进入一个特殊的字段（__all__）,
如果需要，可以通过xxx.non_field_errors 方法进行访问。
如果要将错误附加到表中特定字段，使用add_errors()方法
"""