from captcha.fields import CaptchaField
from django import forms


class SuggestionForm(forms.Form):
    anonymity = forms.ChoiceField(
        label="是否匿名",
        choices=((1, '是'), (2, '否'),),  # 定义下拉框的选项，元祖第一个值为option的value值，后面为html里面的值
        initial=1,  # 默认选中第二个option
        widget=forms.RadioSelect  # 插件表现形式为单选按钮
    )
    advise = forms.CharField(label="问题描述", max_length=128,
                           widget=forms.TextInput(attrs={'class': 'form-control'}))

    files = forms.FileField(label="辅助描述文件，可无", required=False,
                            widget=forms.ClearableFileInput(attrs={'multiple': True}),
                            )

    captcha = CaptchaField(label='验证码')
