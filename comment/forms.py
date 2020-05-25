from django import forms
from django.contrib.contenttypes.models import ContentType
from django.db.models import ObjectDoesNotExist
# 用于表单forms
from ckeditor.widgets import CKEditorWidget
from .models import Comment


# 使用forms表单显示并提交评论
class CommentForm(forms.Form):
    # widget=forms.HiddenInput：存在但不显示组件
    # 注意content_type是字符串类型
    content_type = forms.CharField(widget=forms.HiddenInput)
    object_id = forms.IntegerField(widget=forms.HiddenInput)
    # 评论输入框使用富文本编辑器
    # config_name：settings设置
    text = forms.CharField(widget=CKEditorWidget(config_name='comment_ckeditor'),
                           error_messages={'required': '评论内容不能为空'})

    # 回复的评论对应的主键值？？
    reply_comment_id = forms.IntegerField(widget=forms.HiddenInput(attrs={'id': 'reply_comment_id'}))

    # 初始化函数
    def __init__(self, *args, **kwargs):
        # 使用关键字参数传递？？？
        # 使用pop，获取并剔除参数，有待学习，代码各种逻辑
        # 如果用get,获取后self中就存在这个user,在forms.Form进行初始化验证的时候，
        # 表单设置中并没有这个user参数，会报错
        if 'user' in kwargs:
            self.user = kwargs.pop('user')
        super(CommentForm, self).__init__(*args, **kwargs)

    # 评论对象验证
    def clean(self):
        # 后端再一次判断用户是否登录
        if self.user.is_authenticated:
            self.cleaned_data['user'] = self.user
        else:
            raise forms.ValidationError('用户未登录')

        content_type = self.cleaned_data['content_type']
        object_id = self.cleaned_data['object_id']

        try:
            # 选出相应类型-博客，并取出数据
            model_class = ContentType.objects.get(model=content_type).model_class()
            model_obj = model_class.objects.get(pk=object_id)
            self.cleaned_data['content_object'] = model_obj
        except ObjectDoesNotExist:
            raise forms.ValidationError('评论对象不存在')

        return self.cleaned_data

    def clean_reply_comment_id(self):
        # 表单中新增加的一个属性，判定是回复还是评论
        reply_comment_id = self.cleaned_data['reply_comment_id']
        if reply_comment_id < 0:
            raise forms.ValidationError('回复出错')
        # 一级评论，没有上级
        elif reply_comment_id == 0:
            self.cleaned_data['parent'] = None
        # 有上级，是回复，并根据reply_comment_id 获取它的上级评论数据
        elif Comment.objects.filter(pk=reply_comment_id).exists():
            self.cleaned_data['parent'] = Comment.objects.get(pk=reply_comment_id)
        else:
            raise forms.ValidationError('回复出错')
        return reply_comment_id




