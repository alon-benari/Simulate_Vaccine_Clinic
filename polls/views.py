from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from .models import SimParamsModel
from django.core import serializers
from .forms import SimParamsForm


def index(request):
  print('Hello')
  context ={}
  form = SimParamsForm
  context['form'] = form
  #return HttpResponse("Hello world. You're at the polls index.")
  return render(request, 'polls/index.html',context)
# Create your views here.


def post_params(request):
  print('from post_params')
  # request should be ajax and method should be POST.
  if request.is_ajax and request.method == "POST":
      # get the form data
      form = SimParamsForm(request.POST)
      # save the data and after fetch the object in instance
      if form.is_valid():
          
          instance = form.save()
          
          # serialize in new friend object in json
          ser_instance = serializers.serialize('json', [ instance, ])
          print(ser_instance)
          # send to client side.
          return JsonResponse({"instance": ser_instance}, status=200)
      else:
          # some form errors occured.
          return JsonResponse({"error": form.errors}, status=400)

  # some error occured
  return JsonResponse({"error": ""}, status=400)
