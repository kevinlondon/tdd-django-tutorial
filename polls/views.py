from django.http import HttpResponse

from polls.models import Poll

def home(request):
    content = ''
    for poll in Poll.objects.all():
        content += poll.question

    return HttpResponse(content)
