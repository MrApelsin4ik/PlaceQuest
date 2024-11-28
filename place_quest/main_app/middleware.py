from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponseNotFound, HttpResponseBadRequest, HttpResponse
from django.shortcuts import render

class AnonymousUserAccessLevelMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if not request.user.is_authenticated:
            request.user.access_level = 1


from django.http import HttpResponseBadRequest

