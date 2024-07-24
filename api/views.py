# skill-africa-backend/api/views.py
from django.http import JsonResponse

def under_construction(request):
    data = {"message": "Under Construction"}
    return JsonResponse(data)
