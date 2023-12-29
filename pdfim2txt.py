#!/usr/bin/python
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
from gtts import gTTS
from playsound import playsound
import os
import pathlib
from termcolor import colored

import sys
import pdfplumber
import fitz
import cv2
import numpy as np

#imports for opencv_file function
import platform
from PIL import Image as im
from tempfile import TemporaryDirectory
import shutil # closes temporaryDirectory

# uncomment to test opencv_file function
#out_directory = pathlib.Path("~").expanduser()
#image_file_list = []

# IDLE used does not accurately locate files, will look into Linux systems
#for my compiling of the code these lines will be uncommented

#poppler_path = '/opt/homebrew/bin/'
#pytesseract.pytesseract.tesseract_cmd = '/opt/homebrew/bin/tesseract'


def takeInput(): #works perfect, given
    pmode = 0
    IN = input("Enter a pdf or an image: ")

    if os.path.isfile(IN):
        path_stem = pathlib.Path(IN).stem
        path_ext = pathlib.Path(IN).suffix
        if path_ext.lower() == '.pdf':
            pmode = 1
        else:
            pmode = 0
    return IN, path_stem, pmode 

def im2txt(image_path): 
    # Open image
    img = Image.open(image_path)
    img = image_path
    
    # Extract text from image
    text = pytesseract.image_to_string(img)
    
    return f"Text extracted from image:\n {text}"

def pdf_to_text(pdf_path, output_file):
    doc = fitz.Document(pdf_path)
    text = ""
    output_folder = 'output_images'
    os.makedirs(output_folder, exist_ok=True)

    for page_num in range(len(doc)):
        page = doc[page_num]
        
        # extracting the text from each page, seperate from images
        text += page.get_text("text")

        # extracting images in pdf
        img_list = page.get_images(full=True)

        for img_index, img_info in enumerate(img_list):
            img_index += 1
            img_index_str = str(img_index).zfill(3)
            xref = img_info[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]

            # saving extracted images to folder, for user viewability, troubleshooting,
            # location for pytesseract to extract text from images directly
            img_filename = f"{output_folder}/image_{page_num + 1}_{img_index_str}.{image_ext}"
            with open(img_filename, "wb") as img_file:
                img_file.write(image_bytes)

            # Performing OCR on the saved image
            text += im2txt(img_filename)

    # combining the raw text and image text to file
    with open(output_file, "w", encoding="utf-8") as output:
        output.write(text)

    doc.close()
    return (f"Saved to {output_file}.")

def opencv_file(path, output_file):
    with TemporaryDirectory() as tempdir:
        pdf_pages=convert_from_path(IN, poppler_path=poppler_path)
        for page_enum, page in enumerate(pdf_pages, start = 1):
            img = np.array(page)
            
            img = cv2.resize(img, None, fx=1.2, fy=1.2, interpolation = cv2.INTER_CUBIC)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            kernel = np.ones((1,1), np.uint8)

            img = cv2.dilate(img, kernel, iterations = 1)
            img = cv2.erode(img, kernel, iterations = 1)
            
            img = cv2.threshold(cv2.bilateralFilter(img, 4, 57, 180), 0, 255, cv2.THRESH_TRUNC + cv2.THRESH_TRIANGLE)[1]
            #img = cv2.threshold(cv2.medianBlur(img, 3), 0, 255, cv2.THRESH_TOZERO + cv2.THRESH_OTSU)[1]
            img = cv2.threshold(cv2.GaussianBlur(img, (9, 9), 0), 0, 255, cv2.THRESH_TRUNC + cv2.THRESH_OTSU)[1]


            data = im.fromarray(img)
            filename = f"{tempdir}\age_{page_enum:02}.png"
            data.save(filename, "PNG")
            image_file_list.append(filename)

        with open(output_file, "w") as output:
            for image_file in image_file_list:
                text = str(((pytesseract.image_to_string(Image.open(image_file)))))
                text = text.replace("-\n","") #any lines that have words cut off will be replaced with the full word
                output.write(text)
    return (f"Saved to {output_file}.")
    shutil.rmtree(tempdir)


if __name__ == '__main__':
    IN, path_stem, pmode = takeInput()  # pmode=0:image; pmode=1:pdf
    if pmode:
        result = pdf_to_text(IN, 'output1.txt')
        #result = opencv_file(IN, 'output2.txt') #output files named differently to compare output
        print(result)
    else:
        txt = im2txt(IN)
        print(txt)
        audio = gTTS(text=txt, lang="en", tld = 'co.uk', slow=False)
        WAV = f'0000-{path_stem}-text.wav'
        audio.save(WAV)
        print(colored(f'Text: saved to <{WAV}>', 'yellow'))
        playsound(WAV)
        os.remove(WAV)
    


                




