from vita.models import Visits


def counts(request):
    # information about visits www and cancel
    count_www = Visits.objects.filter(status=5).count()
    count_cancel = Visits.objects.filter(status=2).count()
    return { 'count_www':count_www, 'count_cancel': count_cancel }
