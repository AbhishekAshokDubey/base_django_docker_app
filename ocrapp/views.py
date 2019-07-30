from django import http
from django.core import serializers
#from django.core.urlresolvers import reverse
#from django.db import connection, transaction
#from django.db.transaction import Transaction
from django.http import Http404
from django.http import HttpResponse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect, render_to_response
from django.template import loader
from django.views import generic
import json

# Create your views here.
import os
import sys
import pytesseract 
from PIL import Image 
from sys import platform
from pdf2image import convert_from_path 

if platform == "linux" or platform == "linux2":
    PDF_file = "/home/adubey4/sample.pdf"
elif platform == "win32":
    PDF_file = r"C:\Users\Adubey4\Desktop\sample.pdf"
    pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files (x86)/Tesseract-OCR/tesseract'
#elif platform == "darwin":
    # OS X

def home(request):
	return HttpResponse("Hello World")

def get_text(request, PDF_file_path = PDF_file):
    PDF_file_path = param = request.GET.get("path")
    pdf_name = os.path.basename(PDF_file_path).replace(".pdf","")
    pdf_folder = os.path.dirname(PDF_file_path)
    pages = convert_from_path(PDF_file_path, 500)
    text_list = []

    f = open(os.path.join(pdf_folder, pdf_name +".txt"), "a")
    for page in pages:
        text = str(pytesseract.image_to_string(page))
        text = text.replace('-\n', '')
        text_list.append(text)
        f.write(text)
    f.close()
    #http://localhost:8000/gettext?path=111
    return HttpResponse(json.dumps(text_list))