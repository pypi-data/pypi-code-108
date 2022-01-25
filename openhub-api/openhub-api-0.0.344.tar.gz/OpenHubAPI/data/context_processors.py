from .models.models import Hub

def basetest(request):

    hubs = Hub.objects.all()
    return {
        'hubs': hubs
    }
