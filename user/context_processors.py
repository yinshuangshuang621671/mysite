from .forms import LoginForm


def login_modal_form(request):
    # 返回表单的实例化
    return {'login_modal_form': LoginForm()}
