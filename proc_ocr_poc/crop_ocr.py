from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import sys
import time
import os

import cv2
import pytesseract
import numpy as np
from PIL import Image
import urllib.request
import shutil
from pdf2image import convert_from_path
import tensorflow as tf

###########################################---Modelo Assinatura---############################################################

def load_graph(model_file):
  graph = tf.Graph()
  graph_def = tf.GraphDef()

  with open(model_file, "rb") as f:
    graph_def.ParseFromString(f.read())
  with graph.as_default():
    tf.import_graph_def(graph_def)

  return graph

def read_tensor_from_image_file(file_name, input_height=299, input_width=299,
				input_mean=0, input_std=255):
  input_name = "file_reader"
  output_name = "normalized"
  file_reader = tf.read_file(file_name, input_name)
  if file_name.endswith(".png"):
    image_reader = tf.image.decode_png(file_reader, channels = 3,
                                       name='png_reader')
  elif file_name.endswith(".gif"):
    image_reader = tf.squeeze(tf.image.decode_gif(file_reader,
                                                  name='gif_reader'))
  elif file_name.endswith(".bmp"):
    image_reader = tf.image.decode_bmp(file_reader, name='bmp_reader')
  else:
    image_reader = tf.image.decode_jpeg(file_reader, channels = 3,
                                        name='jpeg_reader')
  float_caster = tf.cast(image_reader, tf.float32)
  dims_expander = tf.expand_dims(float_caster, 0);
  resized = tf.image.resize_bilinear(dims_expander, [input_height, input_width])
  normalized = tf.divide(tf.subtract(resized, [input_mean]), [input_std])
  sess = tf.Session()
  result = sess.run(normalized)

  return result

def load_labels(label_file):
  label = []
  proto_as_ascii_lines = tf.gfile.GFile(label_file).readlines()
  for l in proto_as_ascii_lines:
    label.append(l.rstrip())
  return label


def label_image(file_name):
  # file_name = "sig8.jpg"
  model_file = "retrained_graph.pb"
  label_file = "retrained_labels.txt"
  input_height = 224
  input_width = 224
  input_mean = 128
  input_std = 128
  input_layer = "input"
  output_layer = "final_result"

  graph = load_graph(model_file)
  t = read_tensor_from_image_file(file_name,
                                  input_height=input_height,
                                  input_width=input_width,
                                  input_mean=input_mean,
                                  input_std=input_std)

  input_name = "import/" + input_layer
  output_name = "import/" + output_layer
  input_operation = graph.get_operation_by_name(input_name);
  output_operation = graph.get_operation_by_name(output_name);

  with tf.Session(graph=graph) as sess:
    start = time.time()
    results = sess.run(output_operation.outputs[0],
                      {input_operation.outputs[0]: t})
    end=time.time()
  results = np.squeeze(results)

  top_k = results.argsort()[-5:][::-1]
  labels = load_labels(label_file)

  template = "{} (score={:0.5f})"
  for i in top_k:
    if labels[i] == 'signature':
      return results[i]

###################################---OCR---##############################################################################
def get_file_from_url(url,output_file):
  output_file = "{}.pdf".format(output_file)
  with urllib.request.urlopen(url) as response, open(output_file, 'wb') as out_file:
      shutil.copyfileobj(response, out_file)
      return output_file

def execute_OCR_1pg(image_input, file_output, template):
  result = 'null'
  image = cv2.imread(image_input)
  with open(template, 'r') as f, open(file_output, 'w') as out:
      lis=[line.split() for line in f]     
      for i,x in enumerate(lis):
          if i>0:
              COD = x[0].split(',')[0]
              x = list(map(int,x[0].split(',')[1:]))
              cropped = image[x[0]:x[2] , x[1]:x[3]]
              if COD == 'ASSINATURA':
                im = Image.fromarray(cropped)
                im.save("sig_crop.jpg")
                im = cv2.imread("sig_crop.jpg")
                cropped = cv2.transpose(im)
                cropped = cv2.flip(cropped, 1)
                im = Image.fromarray(cropped)
                im.save("sig_crop.jpg")
                cropped = cv2.imread("sig_crop.jpg")
                result = label_image('sig_crop.jpg')
              if COD == 'DATA_PAG':
                im = Image.fromarray(cropped)
                im.save("data_crop.jpg")
                im = cv2.imread("data_crop.jpg")
                cropped = cv2.transpose(im)
                cropped = cv2.flip(cropped, 1)
                im = Image.fromarray(cropped)
                im.save("data_crop.jpg")
                cropped = cv2.imread("data_crop.jpg")
              out.write("{0},{1}\n".format(COD, pytesseract.image_to_string(cropped)))
  out.close()
  f.close()
  return result

def convert_pdf2image(image_input):
  pages = convert_from_path(image_input, 500)
  for page in pages:
    page.save(image_input.replace('.pdf','')+'.jpg', 'JPEG')
  return image_input.replace('.pdf','')+'.jpg'

def choose_temp(image_input):
  if 'hole' in image_input.lower():
    template = 'temp_holerite.csv'
    image_input = get_file_from_url(url,image_input)
    return template, image_input
  if 'folh' in image_input.lower():
    template = 'temp_folha.csv'
    image_input = get_file_from_url(url,image_input)
    return template, image_input
  if 'sefip' in image_input.lower():
    template = 'temp_sefip.csv'
    image_input = get_file_from_url(url,image_input)
    return template, image_input

if __name__ == "__main__":
  image_input = "out.jpg"
  file_output = "out_ocr.txt"
  url = "https://storage.googleapis.com/softinova_executivaadm/sources/HOLERITE_DUAS%20RODAS.pdf"
  # template = "temp.csv"

  parser = argparse.ArgumentParser()
  parser.add_argument("--image_input", help="Nome do Arquivo de entrada, pode ser pdf ou jpg")
  parser.add_argument("--file_output", help="Nome do txt de saída")
  parser.add_argument("--url", help="Url do bucket da Google Cloud.")
  # parser.add_argument("--template", help="Template pode csv ou txt, desde que cada linha sigo o formato -> COD,start_row,start_col,end_row,end_col")
  args = parser.parse_args()

  if args.image_input:
    image_input = args.image_input
  if args.file_output:
    file_output = args.file_output
  if args.url:
    url = args.url
  # if args.template:
  #   template = args.template

  # if "pdf" in image_input:
  #   image_input = convert_pdf2image(image_input)
  template, image_input = choose_temp(image_input)
  image_input = convert_pdf2image(image_input)

  #
  result = execute_OCR_1pg(image_input, 'out_ocr_{}.txt'.format(image_input.replace('.jpg','')), template)
