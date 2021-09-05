import time, os
from django.shortcuts import render

# Create your views here.
# advise = models.TextField()
#     user = models.ForeignKey(User2, on_delete=models.CASCADE)
#     status = models.IntegerField(choices=Status.choices)
#     anonymity = models.BooleanField(default=True)
#
from Login.models import User
from Suggestion import forms
from Suggestion.models import Suggestions
from FrexTTest.settings import userFilesPath


def suggestions(request):
    suggestionsList = []
    allSuggestionList = Suggestions.objects.all().order_by('-create_time')
    for p in allSuggestionList:
        print(p.anonymity)
        suggestionsList.append({'userName': p.user.name if p.anonymity else "匿名",
                                'suggestion': p.advise, 'status': p.state, 'upTime': p.create_time})
    content = {
        'suggestionsList': suggestionsList,
    }
    return render(request, "Suggestion/suggestion.html", content)


def add_suggestion(request):
    if request.method == "POST":
        if request.session['is_login']:
            suggestion_form = forms.SuggestionForm(request.POST, request.FILES)
            if suggestion_form.is_valid():
                values = suggestion_form.clean()

                suggest = Suggestions()
                suggest.advise = values.get('advise')
                suggest.anonymity = True if int(values.get('anonymity')) == 2 else False
                suggest.user = User.objects.get(name=request.session['user_name'])
                suggest.save()

                files = request.FILES.getlist('files')

                userDir = os.path.join(userFilesPath, str(suggest.user.uid))
                if not os.path.exists(userDir):  # 如果用户首次提交文件
                    os.makedirs(userDir)

                index = 0
                for f in files:
                    with open(os.path.join(userDir, str(suggest.id) + "_" + str(index)), 'wb+') as destination:
                        for chunk in f.chunks():
                            destination.write(chunk)
                    index += 1

                message = '提交成功'
                return render(request, "Suggestion/addSuggestion.html", locals())
            else:
                errors = suggestion_form.errors
                message = str(errors)
                return render(request, "Suggestion/addSuggestion.html", locals())
    suggestion_form = forms.SuggestionForm()
    return render(request, "Suggestion/addSuggestion.html", locals())
