from rest_framework.views import APIView
from django_google_sso.views import start_login


class GoogleStartLoginView(APIView):
    """
    **Google SignIn/SignUp**
    - **Description:** Authenticate users via Google.
    - **Note:** Endpoint not testable here due to redirection.
    - **Usage:** Initiate a GET request from the front-end to redirect to Google for authorization, then return to the site post-authentication.
    """

    def get(self, request):
        return start_login(request)
