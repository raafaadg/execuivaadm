from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import sys
import time

import cv2
import pytesseract
import numpy as np
from PIL import Image
from pdf2image import convert_from_path

def execute_OCR_1pg(image_input, file_output, template):
  image = cv2.imread(image_input)
  with open(template, 'r') as f, open(file_output, 'w') as out:
      lis=[line.split() for line in f]     
      for i,x in enumerate(lis):
          if i>0:
              COD = x[0].split(',')[0]
              x = list(map(int,x[0].split(',')[1:5]))
              cropped = image[x[0]:x[2] , x[1]:x[3]]
              out.write("{0},{1}\n".format(COD, pytesseract.image_to_string(cropped)))
              cv2.imshow(COD, cropped)
              cv2.waitKey(0)
              cv2.destroyAllWindows()
  out.close()
  f.close()

def convert_pdf2image(image_input):
  pages = convert_from_path(image_input, 500)
  for page in pages:
    page.save('out.jpg', 'JPEG')
  print("Imagem convertida com sucesso!")
  return 'out.jpg'

if __name__ == "__main__":
  image_input = "out.jpg"
  file_output = "out_ocr.txt"
  template = "temp.csv"

  parser = argparse.ArgumentParser()
  parser.add_argument("--image_input", help="Nome do Arquivo de entrada, pode ser pdf ou jpg")
  parser.add_argument("--file_output", help="Nome do txt de saída")
  parser.add_argument("--template", help="Template pode csv ou txt, desde que cada linha sigo o formato -> COD,start_row,start_col,end_row,end_col")
  args = parser.parse_args()

  if args.image_input:
    image_input = args.image_input
  if args.file_output:
    file_output = args.file_output
  if args.template:
    template = args.template

  if "pdf" in image_input:
    image_input = convert_pdf2image(image_input)

  print("FAVOR PRECIONAR QUALQUER TECLA PARA FECHAR A IMAGEM RECORTADA E SEGUIR COM O OCR")
  execute_OCR_1pg(image_input, file_output, template)
  print("Sucesso Softinova!")