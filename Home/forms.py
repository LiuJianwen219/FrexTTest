from django import forms
from captcha.fields import CaptchaField

from Home import models


class NewTestForm(forms.Form):
    testName = forms.CharField(label="测试题目", max_length=256,
                               widget=forms.TextInput(
                                   attrs={'class': 'form-control',
                                          'placeholder': "测试",
                                          'autofocus': ''}))
    topic = forms.CharField(label="测试模块名字", max_length=128,
                            widget=forms.TextInput(
                                attrs={'class': 'form-control',
                                       'placeholder': "topic"}))
    testTopName = forms.CharField(label="顶层模块名字", max_length=128,
                                  widget=forms.TextInput(
                                      attrs={'class': 'form-control',
                                             'placeholder': "topModuleName"}))
    testType = forms.IntegerField(label="类型",
                                  widget=forms.TextInput(
                                      attrs={'class': 'form-control',
                                             'placeholder': "1组合，2时序，3综合"}))
    grade = forms.DecimalField(label="分数",
                               widget=forms.TextInput(
                                   attrs={'class': 'form-control',
                                          'placeholder': "10.00"}))

    file = forms.FileField(label="题目文件")


class AddTestFileForm(forms.Form):
    topic = forms.CharField(label="测试题目",
                                widget=forms.Select())
    files = forms.FileField(label="测试文件",
                            widget=forms.ClearableFileInput(attrs={'multiple': True}))

    def __init__(self, *args, **kwargs):
        super(AddTestFileForm, self).__init__(*args, **kwargs)
        self.fields['topic'].widget.choices = models.TestList.objects.values_list('uid', 'topic')
