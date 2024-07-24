from vita.models import Visits


def counts(request):
    # information about visits www and cancel
    count_www = Visits.objects.filter(status=5).count()
    count_cancel = Visits.objects.filter(status=2).count()
    return { 'count_www':count_www, 'count_cancel': count_cancel }

# global set visits www
def get_visits_with_patient_data():
    all_visits_www = Visits.objects.filter(status=5).select_related('patient__user').order_by('-date')[:5]
    visits_data = [{
        'visit_id': visit.id,
        'status': visit.status,
        'date': visit.date,
        'time': visit.time,
        'patient_id': visit.patient_id,
        'patient_first_name': visit.patient.user.first_name,
        'patient_last_name': visit.patient.user.last_name,
    } for visit in all_visits_www]
    return visits_data

def global_visits_context(request):
    return {
        'all_visits_www': get_visits_with_patient_data(),
    }
