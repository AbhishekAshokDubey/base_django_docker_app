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
    base_data_folder = "/base_django_docker_app/data"
elif platform == "win32":
    pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files (x86)/Tesseract-OCR/tesseract'
    base_data_folder = r"C:\Users\Adubey4\Desktop\test\base_django_docker_app\data"

#elif platform == "darwin":
    # OS X

def home(request):
	return HttpResponse("Hello World")

def copy_file_from_bucket(PDF_file_path_gcp):
    cmd = "gsutil cp "+ PDF_file_path_gcp +" \""+ base_data_folder+"\""
    print(cmd)
    os.system(cmd)

def upload_file_to_bucket(local_path, bucket_path):
    cmd = "gsutil cp "+ local_path +" \""+ bucket_path +"\""
    print(cmd)
    os.system(cmd)
    try:
        os.remove(local_path)
        os.remove(local_path.replace(".txt",".pdf"))
    except:
        print("count not delete files")
    
def save_ocr_text(PDF_file_path_gcp):
    pdf_name = os.path.basename(PDF_file_path_gcp)
    PDF_file_path = os.path.join(base_data_folder, pdf_name)

    #pdf_folder = os.path.dirname(PDF_file_path)
    pdf_folder = os.path.dirname(PDF_file_path)
    pages = convert_from_path(PDF_file_path, 500)
    text_list = []
    
    out_file_path = os.path.join(pdf_folder, pdf_name.replace(".pdf",".txt"))
    f = open(out_file_path, "a")
    for page in pages:
        text = str(pytesseract.image_to_string(page))
        text = text.replace('-\n', '')
        text_list.append(text)
        f.write(text)
    f.close()
    return out_file_path

def get_text(request):
    PDF_file_path_gcp = request.GET.get("path")
    copy_file_from_bucket(PDF_file_path_gcp)
    out_file_path = save_ocr_text(PDF_file_path_gcp)
    with open(out_file_path, 'r') as file:
        data = file.read()
    #http://localhost:8000/gettext?path=gs://abhishek-test/input/sample.pdf
    return HttpResponse(json.dumps(data))

def upload_result(request):
    PDF_file_path_gcp = request.GET.get("path")
    copy_file_from_bucket(PDF_file_path_gcp)
    out_file_path = save_ocr_text(PDF_file_path_gcp)
    upload_file_to_bucket(out_file_path, PDF_file_path_gcp.replace("/input/","/output/").replace(".pdf",".txt"))
    #http://localhost:8000/uploadresult?path=gs://abhishek-test/input/sample.pdf
    return HttpResponse("Uploaded")