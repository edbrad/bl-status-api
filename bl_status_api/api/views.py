from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Create your views here.
# API Welcome Response
@api_view(['GET'])
def root(request):
    """
    Generic/Default Text Response.
    """
    data = 'Welcome to the bl-status REST API'
    return Response(data)
