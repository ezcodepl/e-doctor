from django.utils import timezone
from django.contrib import auth
from django.conf import settings
from django.contrib.sessions.middleware import SessionMiddleware


class AutoLogoutSessionMiddleware(SessionMiddleware):
    def process_request(self, request):
        # Wywołaj proces żądania z rodzica
        super().process_request(request)

        # Sprawdź, czy użytkownik jest zalogowany
        if request.user.is_authenticated:
            # Pobierz czas ostatniej aktywności z sesji
            last_activity_str = request.session.get('last_activity')

            # Jeśli czas ostatniej aktywności nie istnieje lub jest starszy niż 15 minut, wyloguj użytkownika
            if last_activity_str:
                last_activity = timezone.datetime.fromisoformat(last_activity_str)
                if (timezone.now() - last_activity).seconds > settings.SESSION_COOKIE_AGE:
                    auth.logout(request)
            else:
                # Ustaw czas ostatniej aktywności w formacie ISO 8601
                request.session['last_activity'] = timezone.now().isoformat()
