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


import os
from pdf2image import convert_from_path
import glob
import tempfile
import subprocess
import string
import random

def get_images(file_path, images_path, fp, lp, fmt = 'png'):
    print('Saving Images for file {} in folder {}'.format(os.path.basename(file_path), images_path))
    output_file = os.path.basename(file_path).replace('.pdf', '')
    convert_from_path(file_path, dpi = 300, output_folder = images_path, output_file = output_file, first_page = fp, last_page = lp, fmt = 'png', thread_count= 4)    
    return True

def randomString(stringLength = 8):
    letters = string.ascii_letters    
    return ''.join(random.choice(letters) for i in range(stringLength))

def parse_input(image_path):
    if type(image_path) == type([]):
        return 'f'
    if os.path.splitext(image_path)[1] == '.txt':
        return 't'
    return 'd'

def run_tesseract(image_path, out_file, fmt = ['txt'], image_format = 'png'):
    input_type = parse_input(image_path)
    if not input_type == 't':
        if input_type == 'd':
            if not image_format:
                image_format = 'png'                
            image_path = sorted(glob.glob(os.path.join(image_path, '*.{}'.format(image_format))))
#        print('making temp text file')
        tempfilename = randomString() + '.txt'
        temp_dir = tempfile.gettempdir()
        txtfile_path = os.path.join(temp_dir, tempfilename)
        f = open(txtfile_path, 'w')
        f.write('\n'.join(image_path))
        f.close()
        image_path = txtfile_path
    
    print('\n\n')
    tesseract_formats = ' '.join(fmt)
    cmd =  'tesseract "' + image_path + '" "' + out_file + '" ' + tesseract_formats
    print('Tesseract Command is: ',cmd, '\n\n')
    out_status = subprocess.call(cmd, shell = True)
    print('\n\n%%%%%%%%%%%%%%%%%%%%%%%%%%%out%%%%%%%%%%%%%%%%%%%%%%%', out_status)
    print('OCR Done')
    
    if not input_type == 't':
        os.remove(image_path)
    return out_status


def OCR_func(filepath, outpath, fp = None, lp = None, fmt = ['txt', 'pdf', 'tsv']):
    img_fmt = 'png'

    filename = os.path.basename(filepath).replace('.pdf', '')    
    
    out_dir = os.path.dirname(outpath)    
    images_path = os.path.join(out_dir, filename + ' Images')
    if not os.path.exists(images_path):
        os.mkdir(images_path)

    get_images(filepath, images_path, fp, lp, fmt = img_fmt)    
    out_file = run_tesseract(images_path, outpath, fmt = ['txt', 'pdf'], image_format = img_fmt)

    print('\n.............Extracted text from the PDF')
    return out_file


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
                    #out_file_path = save_ocr_text(PDF_file_path_gcp)
                    pdf_name = os.path.basename(PDF_file_path_gcp)
                    PDF_file_local_path = os.path.join(base_data_folder, pdf_name)

                    OCR_func(PDF_file_local_path, PDF_file_local_path)

                    os.system("gcloud logging write ocr-app 'converted to text' --severity=INFO")
                    os.system("gcloud logging write ocr-app 'local path: "+PDF_file_local_path+"' --severity=INFO")
                    os.system("gcloud logging write ocr-app 'local searchable pdf path: "+PDF_file_local_path.replace(".pdf", ".pdf.pdf") +"' --severity=INFO")
                    os.system("gcloud logging write ocr-app 'GCP searchable pdf path: "+PDF_file_path_gcp.replace("/input/","/output/").replace(".pdf",".pdf.pdf")+"' --severity=INFO")

                    upload_file_to_bucket(PDF_file_local_path.replace(".pdf", ".pdf.pdf"), PDF_file_path_gcp.replace("/input/","/output/").replace(".pdf",".pdf.pdf"))
                    upload_file_to_bucket(PDF_file_local_path.replace(".pdf", ".pdf.txt"), PDF_file_path_gcp.replace("/input/","/output/").replace(".pdf",".pdf.txt"))

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
        
