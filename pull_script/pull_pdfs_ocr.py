# -*- coding: utf-8 -*-
"""
Created on Thu Aug  1 00:33:20 2019

@author: ADubey4
"""
import re
import os
import sys
import pytesseract 
from PIL import Image 
from sys import platform
from pdf2image import convert_from_path 
import subprocess
import time
import json


cur_file_apth = os.path.dirname(os.path.abspath(__file__))
base_data_folder = cur_file_apth.replace("pull_script","data")
sub_topic = "crt-doc-upload-sub"

if platform == "linux" or platform == "linux2":
    shell_cmd = False
elif platform == "win32":
    pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files (x86)/Tesseract-OCR/tesseract'
    shell_cmd = True


def copy_file_from_bucket(PDF_file_path_gcp):
    cmd = "gsutil cp "+ PDF_file_path_gcp +" \""+ base_data_folder+"\""
#    print(cmd)
    os.system(cmd)

def upload_file_to_bucket(local_path, bucket_path):
    cmd = "gsutil cp "+ local_path +" \""+ bucket_path +"\""
#    print(cmd)
    os.system(cmd)
#    try:
    os.remove(local_path)
    os.remove(local_path.replace(".txt",".pdf"))
#    except:
#        print("count not delete files")

def remove_from_bucket(file_path):
#    try:
    os.system("gsutil rm "+file_path)
#    except:
#        print("Could not delete from bucket")

def save_ocr_text(PDF_file_path_gcp):
    pdf_name = os.path.basename(PDF_file_path_gcp)
    PDF_file_path = os.path.join(base_data_folder, pdf_name)
    #pdf_folder = os.path.dirname(PDF_file_path)
    pdf_folder = os.path.dirname(PDF_file_path)
    os.system("gcloud logging write ocr-app 'starting OCR for "+PDF_file_path+"' --severity=INFO")
    pages = convert_from_path(PDF_file_path)
    os.system("gcloud logging write ocr-app 'converted pdf to images' --severity=INFO")
    text_list = []
    out_file_path = os.path.join(pdf_folder, pdf_name.replace(".pdf",".txt"))
    f = open(out_file_path, "a")
    for i, page in enumerate(pages):
        os.system("gcloud logging write ocr-app 'starting page "+str(i)+"' --severity=INFO")
        try:
            text = str(pytesseract.image_to_string(page))
        except:
            text = "------- error page -------"
            os.system("gcloud logging write ocr-app 'Error at page "+str(i)+"' --severity=INFO")
        #text = text.replace('-\n', '')
        text = re.sub(r'[^\x00-\x7f]',r'', text.replace('-\n', ''))
        text_list.append(text)
        f.write(text)
    f.close()
    return out_file_path


if __name__ == "__main__":
    os.system("gcloud logging write ocr-app 'staring 1 GCE' --severity=INFO")
    while True:
        result_ = subprocess.run(['gcloud', 'pubsub', "subscriptions", "pull", "--auto-ack", sub_topic, "--format=json"], stdout=subprocess.PIPE, shell=shell_cmd)
        msg = json.loads(result_.stdout.decode("utf-8"))
        if len(msg):
            os.system("gcloud logging write ocr-app '"+ (msg[0]["message"]["attributes"]).get("eventType", "issues ishues")+"' --severity=INFO")
            if (msg[0]["message"]["attributes"]).get("eventType") == 'OBJECT_FINALIZE':
                PDF_file_path_gcp = "gs://" + (msg[0]["message"]["attributes"]).get("bucketId") + "/"+ (msg[0]["message"]["attributes"]).get("objectId")
                os.system("gcloud logging write ocr-app 'path "+PDF_file_path_gcp +"' --severity=INFO")
                if PDF_file_path_gcp:
                    copy_file_from_bucket(PDF_file_path_gcp)
                    os.system("gcloud logging write ocr-app 'file copied from bucket' --severity=INFO")
                    out_file_path = save_ocr_text(PDF_file_path_gcp)
                    os.system("gcloud logging write ocr-app 'converted to text' --severity=INFO")
                    upload_file_to_bucket(out_file_path, PDF_file_path_gcp.replace("/input/","/output/").replace(".pdf",".txt"))
                    os.system("gcloud logging write ocr-app 'uploaded text to bucket' --severity=INFO")
                    remove_from_bucket(PDF_file_path_gcp)
                    os.system("gcloud logging write ocr-app 'pdf file deleted from bucket' --severity=INFO")
#        result = subprocess.run(['gsutil', 'ls', "gs://abhishek-test/input/*.pdf"], stdout=subprocess.PIPE, shell=shell_cmd)
#        pdf_files = result.stdout.strip().decode("utf-8").replace("\r","").split("\n")
#        print(pdf_files)
#        for PDF_file_path_gcp in pdf_files:
#            print(PDF_file_path_gcp)
##            try:
#            copy_file_from_bucket(PDF_file_path_gcp)
#            out_file_path = save_ocr_text(PDF_file_path_gcp)
#            upload_file_to_bucket(out_file_path, PDF_file_path_gcp.replace("/input/","/output/").replace(".pdf",".txt"))
#            remove_from_bucket(PDF_file_path_gcp)
##            except:
##                print("Broke for: "+PDF_file_path_gcp)
        time.sleep(10) # 2 second delay
        
