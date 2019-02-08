# CROP and OCR

A POC da POC está saindo, fico no aguardo de um feedbak pata ver se está POC pode continuar evoluindo.

#MODO DE USAR

Instalar todas as dependênias necessárias.
Executar o códido passando os parametros conforme o exemplo a baixo.
No momento, a imagem fornecida (image_input) pode ser tanto .jpg quanto .pdf. Se for .pdf, deve conter somente 1 página. Tenho que ver melhor quais são os campos que precisamos extrair para tratar o documento como todas as páginas, pois as informações necessárias não se encontram em somente uma página como eu pude perceber.
Após executar, as imagens recortadas vão aparecer na tela antes de realizar o OCR, basta clicar em qualquer tecla do teclado para prosseguir.
Se nenhum argumento for informado, o scrip vai utilizar como padrão a iamgem "out.jpg" como entrada e o template "temp.csv". A saída sera "out_ocr.txt".

#OBS

Esta codificado para rodar com python3, mas tenho quase certeza que se rodar com python ou python2, também será executado.

#É NOIX TIME

**Bibliotecas necessárias para rodar**

###opencv
    pip install opencv-pyhton

###numpy
    pip install numpy

###PIL
    pip install pillow

###numpy
    pip install pdf2image

###pytesseract
    ###Procurar no Google um tutorial

##EXEMPLO

python3 crop_ocr.py --image_input=out.jpg --file_output=out_ocr.txt --template=temp.csv

##python3 crop_ocr.py -h

usage: crop_ocr.py [-h] [--image_input IMAGE_INPUT]
                   [--file_output FILE_OUTPUT] [--template TEMPLATE]

optional arguments:
  -h, --help            show this help message and exit
  --image_input IMAGE_INPUT
                        Nome do Arquivo de entrada, pode ser pdf ou jpg
  --file_output FILE_OUTPUT
                        Nome do txt de saída
  --template TEMPLATE   Template pode csv ou txt, desde que cada linha sigo o
                        formato -> COD,start_row,start_col,end_row,end_col




