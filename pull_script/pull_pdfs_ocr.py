# -*- coding: utf-8 -*-
"""
Created on Thu Aug  1 00:33:20 2019

@author: ADubey4
"""

import os
import sys
import pytesseract 
from PIL import Image 
from sys import platform
from pdf2image import convert_from_path 
import subprocess
import time

if platform == "linux" or platform == "linux2":
    base_data_folder = "/base_django_docker_app/data"
elif platform == "win32":
    pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files (x86)/Tesseract-OCR/tesseract'
    base_data_folder = r"C:\Users\Adubey4\Desktop\test\base_django_docker_app\data"


def copy_file_from_bucket(PDF_file_path_gcp):
    cmd = "gsutil cp "+ PDF_file_path_gcp +" \""+ base_data_folder+"\""
#    print(cmd)
    os.system(cmd)

def upload_file_to_bucket(local_path, bucket_path):
    cmd = "gsutil cp "+ local_path +" \""+ bucket_path +"\""
#    print(cmd)
    os.system(cmd)
    try:
        os.remove(local_path)
        os.remove(local_path.replace(".txt",".pdf"))
    except:
        print("count not delete files")

def remove_from_bucket(file_path):
    os.system("gsutil rm "+file_path)

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


if __name__ == "__main__":
    while True:
        result = subprocess.run(['gsutil', 'ls', "gs://abhishek-test/input/*.pdf"], stdout=subprocess.PIPE, shell=True)
        pdf_files = result.stdout.strip().decode("utf-8").replace("\r","").split("\n")
        for PDF_file_path_gcp in pdf_files:
            try:
                copy_file_from_bucket(PDF_file_path_gcp)
                out_file_path = save_ocr_text(PDF_file_path_gcp)
                upload_file_to_bucket(out_file_path, PDF_file_path_gcp.replace("/input/","/output/").replace(".pdf",".txt"))
                remove_from_bucket(PDF_file_path_gcp)
            except:
                print("Broke for: "+PDF_file_path_gcp)
        time.sleep(10) # 2 second delay