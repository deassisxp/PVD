import cv2
import numpy as np
import io
import os
import matplotlib.pyplot as plt
import tkinter as tk
import sys
import math

from tkinter import filedialog
from funcoes import psnr
from funcoes import calcular_correlacao_entre_marcas_dagua
from funcoes import redimensionar


def esconder_imagem(imagem_cobertura, imagem_secreta):
    # Verifique se as imagens têm o mesmo tamanho.
    if imagem_cobertura.shape != imagem_secreta.shape:
        # Se as imagens não tiverem o mesmo tamanho, redimensione a imagem secreta.
        imagem_secreta = redimensionar(imagem_cobertura, imagem_secreta)

    imagem_estego_r, imagem_secreta_r = esconder_imagem_canal_rgb(imagem_cobertura, imagem_secreta,'r')
    imagem_estego_g, imagem_secreta_g = esconder_imagem_canal_rgb(imagem_cobertura, imagem_secreta,'g')
    imagem_estego_b, imagem_secreta_b = esconder_imagem_canal_rgb(imagem_cobertura, imagem_secreta,'b')

    # Escolha a imagem estego com a melhor PSNR.
    psnr_r = psnr(imagem_cobertura, imagem_estego_r) 
    psnr_g = psnr(imagem_cobertura, imagem_estego_g) 
    psnr_b = psnr(imagem_cobertura, imagem_estego_b)
    best_channel = np.argmax([psnr_r, psnr_g, psnr_b])

    # Combine os bits da imagem secreta com os bits menos significativos do canal RGB escolhido.
    imagem_estego = imagem_estego_r if best_channel == 0 else imagem_estego_g if best_channel == 1 else imagem_estego_b
    imagem_secreta = imagem_secreta_r if best_channel == 0 else imagem_secreta_g if best_channel == 1 else imagem_secreta_b

    return imagem_estego, imagem_secreta

def esconder_imagem_canal(imagem_cobertura, imagem_secreta):
  """
  Oculta uma imagem dentro de outra usando a técnica de PVD em um único canal.

  Args:
    imagem_cobertura: A imagem de cobertura.
    imagem_secreta: A imagem secreta.

  Returns:
    A imagem estego.
  """
  # Crie uma cópia da imagem de cobertura para armazenar o resultado.
  imagem_estego = np.copy(imagem_cobertura)

  # Percorra cada pixel na imagem secreta.
  for y in range(imagem_secreta.shape[0]):
    for x in range(imagem_secreta.shape[1]):
      # Obtenha os 4 bits mais significativos do pixel na imagem secreta.
      bits_mais_significativos = (imagem_secreta[y, x] >> 4) & 0x0F

      # Limpe os 4 bits menos significativos do pixel na imagem de cobertura.
      imagem_estego[y, x] &= 0xF0

      # Substitua os 4 bits menos significativos do pixel na imagem de cobertura pelos 4 bits mais significativos do pixel na imagem secreta.
      imagem_estego[y, x] |= bits_mais_significativos

  return imagem_estego

def esconder_imagem_canal_rgb(imagem_cobertura, imagem_secreta, rgb):
    # Crie uma cópia da imagem de cobertura para armazenar o resultado.
    imagem_estego = np.copy(imagem_cobertura)

    # Separe os canais de cor das imagens de cobertura e secreta.
    cobertura_b, cobertura_g, cobertura_r = cv2.split(imagem_cobertura)
    secreta_b, secreta_g, secreta_r = cv2.split(imagem_secreta)

    # Escolha o canal de cor da imagem de cobertura e da imagem secreta com base no argumento rgb.
    if rgb == 'r':
        cobertura_canal = cobertura_r
        secreta_canal = secreta_r
    elif rgb == 'g':
        cobertura_canal = cobertura_g
        secreta_canal = secreta_g
    elif rgb == 'b':
        cobertura_canal = cobertura_b
        secreta_canal = secreta_b
    else:
        raise ValueError("rgb deve ser 'r', 'g' ou 'b'")

    # Percorra cada pixel no canal escolhido da imagem secreta.
    for y in range(secreta_canal.shape[0]):
        for x in range(secreta_canal.shape[1]):
            # Obtenha os 4 bits mais significativos do pixel no canal escolhido da imagem secreta.
            bits_mais_significativos = (secreta_canal[y, x] >> 4) & 0x0F

            # Limpe os 4 bits menos significativos do pixel no canal escolhido da imagem de cobertura.
            cobertura_canal[y, x] &= 0xF0

            # Substitua os 4 bits menos significativos do pixel no canal escolhido da imagem de cobertura pelos 4 bits mais significativos do pixel no canal escolhido da imagem secreta.
            cobertura_canal[y, x] |= bits_mais_significativos

    # Combine os canais de cor para criar a imagem estego.
    if rgb == 'r':
        imagem_estego = cv2.merge((cobertura_b, cobertura_g, cobertura_canal))
    elif rgb == 'g':
        imagem_estego = cv2.merge((cobertura_b, cobertura_canal, cobertura_r))
    elif rgb == 'b':
        imagem_estego = cv2.merge((cobertura_canal, cobertura_g, cobertura_r))

    return imagem_estego, secreta_canal

def extrair_imagem(imagem_estego):
  """
  Extrai uma imagem escondida dentro de outra usando a técnica de PVD em todos os canais.

  Args:
    imagem_estego: A imagem estego.

  Returns:
    As imagens secretas extraídas de cada canal.
  """
  # Crie uma matriz vazia para armazenar as imagens secretas extraídas.
  imagem_secreta_r = np.zeros_like(imagem_estego)
  imagem_secreta_g = np.zeros_like(imagem_estego)
  imagem_secreta_b = np.zeros_like(imagem_estego)

  # Verifique se a imagem estego é em escala de cinza.
  if len(imagem_estego.shape) == 2:
    # Se a imagem estego for em escala de cinza, extraia a imagem secreta do canal cinza.
    imagem_secreta_gray = np.zeros_like(imagem_estego)
    canais = [('gray', imagem_estego, imagem_secreta_gray)]
    cv2.imwrite(os.path.join("imagens_marca_dagua_extraida", "testeG.jpg"), imagem_secreta_gray)
    return imagem_secreta_gray
  else:
    # Se a imagem estego for colorida, extraia a imagem secreta dos canais R, G e B.
    estego_b, estego_g, estego_r = cv2.split(imagem_estego)
    canais = [('r', estego_r, imagem_secreta_r), ('g', estego_g, imagem_secreta_g), ('b', estego_b, imagem_secreta_b)]

  # Percorra cada pixel em cada canal da imagem estego.
  for nome_canal, estego_canal, imagem_secreta in canais:
    for y in range(estego_canal.shape[0]):
      for x in range(estego_canal.shape[1]):
        # Extraia os 4 bits menos significativos do pixel no canal escolhido da imagem estego.
        bits_menos_significativos = estego_canal[y, x] & 0x0F

        # Mova os 4 bits menos significativos para a posição dos 4 bits mais significativos.
        bits_menos_significativos <<= 4

        # Armazene os bits extraídos na imagem secreta correspondente.
        imagem_secreta[y, x] = bits_menos_significativos
        media = (estego_canal[y, x] >> 4) / 4
        imagem_secreta[y, x] &= 0xF0
        int(media)
        imagem_secreta[y, x] |= int(media)

  imagens_pasta = imagens_da_pasta("imagens_marca_dagua_inserida")
  cv2.imwrite(os.path.join("imagens_marca_dagua_extraida", "testeR.jpg"), imagem_secreta_r)
  for nome_imagem in imagens_pasta:
    marca_dagua_extraida = cv2.imread(nome_imagem)
    if marca_dagua_extraida.shape != imagem_secreta_r.shape:
    # Se as imagens não tiverem o mesmo tamanho, redimensione a imagem secreta.
      imagem_secreta = redimensionar(marca_dagua_extraida, imagem_secreta_r)
    correlacao = calcular_correlacao_entre_marcas_dagua(marca_dagua_extraida, imagem_secreta)
    print(f"Correlação entre as marcas d'água: {correlacao}")

  imagens_pasta = imagens_da_pasta("imagens_marca_dagua_inserida")
  cv2.imwrite(os.path.join("imagens_marca_dagua_extraida", "testeG.jpg"), imagem_secreta_g)
  for nome_imagem in imagens_pasta:
    marca_dagua_extraida = cv2.imread(nome_imagem)
    if marca_dagua_extraida.shape != imagem_secreta_g.shape:
    # Se as imagens não tiverem o mesmo tamanho, redimensione a imagem secreta.
      imagem_secreta = redimensionar(marca_dagua_extraida, imagem_secreta_g)
    correlacao = calcular_correlacao_entre_marcas_dagua(marca_dagua_extraida, imagem_secreta)
    print(f"Correlação entre as marcas d'água: {correlacao}")

  imagens_pasta = imagens_da_pasta("imagens_marca_dagua_inserida")
  cv2.imwrite(os.path.join("imagens_marca_dagua_extraida", "testeR.jpg"), imagem_secreta_b)
  for nome_imagem in imagens_pasta:
    marca_dagua_extraida = cv2.imread(nome_imagem)
    if marca_dagua_extraida.shape != imagem_secreta_b.shape:
    # Se as imagens não tiverem o mesmo tamanho, redimensione a imagem secreta.
      imagem_secreta = redimensionar(marca_dagua_extraida, imagem_secreta_b)
    correlacao = calcular_correlacao_entre_marcas_dagua(marca_dagua_extraida, imagem_secreta)
    print(f"Correlação entre as marcas d'água: {correlacao}")

  return imagem_secreta_r, imagem_secreta_g, imagem_secreta_b

def carregar_imagem():
    root = tk.Tk()
    root.withdraw()

    # Abre uma janela para selecionar o arquivo de imagem
    caminho_imagem = filedialog.askopenfilename()

    if not caminho_imagem:
        print("Nenhum arquivo selecionado. Encerrando.")
        exit()

    imagem = cv2.imread(caminho_imagem)
    return imagem

def imagens_da_pasta(pasta):
  """
  Obtém todas as imagens da pasta.

  Args:
    pasta: A pasta que contém as imagens.

  Returns:
    Uma lista com as imagens da pasta.
  """

  # Obtenha os nomes dos arquivos da pasta.
  nomes_arquivos = os.listdir(pasta)

  # Filtre os nomes dos arquivos que são imagens.
  imagens_pasta = []
  for nome_arquivo in nomes_arquivos:
    if nome_arquivo.endswith(".jpg") or nome_arquivo.endswith(".jpeg") or nome_arquivo.endswith(".png"):
      imagens_pasta.append(os.path.join(pasta, nome_arquivo))

  return imagens_pasta

def bits_para_string(fluxo_de_bits):
    return ''.join(chr(int(fluxo_de_bits[i:i+8], 2)) for i in range(0, len(fluxo_de_bits), 8))

def esconder_mensagem(imagem, string):
    # Converta a string em uma matriz de bytes.
    string_bytes = string.encode('utf-8')

    nova_imagem = comparar_area_string(imagem, string_bytes)

    # Crie uma matriz vazia para armazenar a imagem estego.
    imagem_estego_r, mensagem_secreta_r = esconder_mensagem_rgb(nova_imagem, string_bytes, 'r')
    imagem_estego_g, mensagem_secreta_g = esconder_mensagem_rgb(nova_imagem, string_bytes, 'g')
    imagem_estego_b, mensagem_secreta_b = esconder_mensagem_rgb(nova_imagem, string_bytes, 'b')

    # Calcule a PSNR para cada canal.
    psnr_r = psnr(imagem, imagem_estego_r)
    psnr_g = psnr(imagem, imagem_estego_g)
    psnr_b = psnr(imagem, imagem_estego_b)

    # Escolha o canal com a melhor PSNR.
    best_channel = np.argmax([psnr_r, psnr_g, psnr_b])

    # Combine os bits da imagem secreta com os bits menos significativos do canal RGB escolhido.
    imagem_estego = imagem_estego_r if best_channel == 0 else imagem_estego_g if best_channel == 1 else imagem_estego_b
    mensagem_secreta = mensagem_secreta_r if best_channel == 0 else mensagem_secreta_g if best_channel == 1 else mensagem_secreta_b
    print(mensagem_secreta)

    return imagem_estego, mensagem_secreta

def esconder_mensagem_rgb(imagem_cobertura, mensagem, rgb):
    """
    Oculta uma mensagem dentro de uma imagem usando a técnica de PVD em um único canal.

    Args:
        imagem_cobertura: A imagem de cobertura.
        mensagem: A mensagem a ser escondida.
        rgb: O canal de cor a ser modificado ('r', 'g' ou 'b').

    Returns:
        A imagem estego e a mensagem secreta.
    """
    # Crie uma cópia da imagem de cobertura para armazenar o resultado.
    imagem_estego = np.copy(imagem_cobertura)

    # Verifique se a mensagem cabe na imagem.
    imagem_cobertura = comparar_area_string(imagem_cobertura, mensagem)

    # Separe os canais de cor da imagem de cobertura.
    cobertura_b, cobertura_g, cobertura_r = cv2.split(imagem_cobertura)
    # Converta a mensagem em binário.

    # Escolha o canal de cor da imagem de cobertura com base no argumento rgb.
    if rgb == 'r':
        cobertura_canal = cobertura_r
    elif rgb == 'g':
        cobertura_canal = cobertura_g
    elif rgb == 'b':
        cobertura_canal = cobertura_b
    else:
        raise ValueError("rgb deve ser 'r', 'g' ou 'b'")

    # Percorra cada bit na mensagem.
    for i in range(len(mensagem)):
        # Obtenha o bit atual da mensagem.
        bit_mensagem = int(mensagem[i])

        # Obtenha o pixel correspondente na imagem de cobertura.
        y = i // cobertura_canal.shape[1]
        x = i % cobertura_canal.shape[1]
        pixel = cobertura_canal[y, x]

        # Limpe o bit menos significativo do pixel.
        pixel &= 0xFE

        # Substitua o bit menos significativo do pixel pelo bit atual da mensagem.
        pixel |= bit_mensagem

        # Atualize o pixel na imagem de cobertura.
        cobertura_canal[y, x] = pixel

    # Combine os canais de cor para criar a imagem estego.
    if rgb == 'r':
        imagem_estego = cv2.merge((cobertura_b, cobertura_g, cobertura_canal))
    elif rgb == 'g':
        imagem_estego = cv2.merge((cobertura_b, cobertura_canal, cobertura_r))
    elif rgb == 'b':
        imagem_estego = cv2.merge((cobertura_canal, cobertura_g, cobertura_r))

    return imagem_estego, mensagem

def extrair_mensagem(imagem_estego):
    """
    Extrai uma mensagem de uma imagem usando a técnica de PVD em um único canal.

    Args:
        imagem_estego: A imagem esteganografada.
        rgb: O canal de cor a ser lido ('r', 'g' ou 'b').

    Returns:
        A mensagem secreta.
    """
    # Separe os canais de cor da imagem esteganografada.
    estego_b, estego_g, estego_r = cv2.split(imagem_estego)

    # Escolha o canal de cor da imagem esteganografada com base no argumento rgb.
    if rgb == 'r':
        estego_canal = estego_r
    elif rgb == 'g':
        estego_canal = estego_g
    elif rgb == 'b':
        estego_canal = estego_b
    else:
        raise ValueError("rgb deve ser 'r', 'g' ou 'b'")

    # Crie uma lista para armazenar os bits da mensagem.
    bits_mensagem = []

    # Percorra cada pixel no canal escolhido da imagem esteganografada.
    for y in range(estego_canal.shape[0]):
        for x in range(estego_canal.shape[1]):
            # Obtenha o bit menos significativo do pixel.
            bit_mensagem = estego_canal[y, x] & 0x01

            # Adicione o bit à lista de bits da mensagem.
            bits_mensagem.append(bit_mensagem)

    # Converta a lista de bits em uma string binária.
    mensagem_binaria = ''.join(str(bit) for bit in bits_mensagem)

    # Converta a string binária de volta em uma string de texto.
    mensagem = ''.join(chr(int(mensagem_binaria[i:i+8], 2)) for i in range(0, len(mensagem_binaria), 8))

    return mensagem

def comparar_area_string(imagem, mensagem):

    # Calcule a área da imagem em pixels.
    area_imagem = imagem.shape[0] * imagem.shape[1]

    # Verifique se a área da imagem é maior ou igual ao tamanho da matriz de bytes.
    if area_imagem >= len(mensagem):
        nova_imagem = imagem
    else:
        mult = len(mensagem)/area_imagem
        nova_altura = math.sqrt(mult)*imagem.shape[0]
        nova_largura = math.sqrt(mult)*imagem.shape[1]
        nova_imagem = cv2.resize(imagem, (nova_largura, nova_altura))

    return nova_imagem
    

if __name__ == "__main__":

###################################### Ocultar a imagem #############################################
  # Oculte a imagem secreta na imagem de cobertura
  """print("Selecione a Imagem Principal")
  imagem_cobertura = carregar_imagem()
  print("Selecione a Imagem marca d'água")
  imagem_secreta = carregar_imagem()

  imagem_estego, imagem_marca_dagua = esconder_imagem(imagem_cobertura, imagem_secreta)
  nome_imagem = input("Digite o nome da imagem a ser salva: ")
  cv2.imwrite(os.path.join("imagens_marca_dagua_inserida", nome_imagem), imagem_marca_dagua)
  cv2.imwrite(os.path.join("imagens_com_marca_dagua", nome_imagem), imagem_estego)"""

###################################### Extrair Imagem ###############################################
  # Extraia a imagem secreta da imagem estego
  """print("Selecione a Imagem Para procurar marca d'água")
  imagem_estego = carregar_imagem()

  #marca_dagua_extraida = extrair_imagem(imagem_estego)

  imagem_secreta = extrair_imagem(imagem_estego)"""

###################################### Ocultar Mensagem ##############################################
  # Oculte a imagem secreta na imagem de cobertura
  """print("Selecione a Imagem Principal")
  imagem_cobertura = carregar_imagem()
  mensagem = input("Digite uma mensagem: ")

  imagem_estego, mensagem_marca_dagua = esconder_mensagem(imagem_cobertura, mensagem)
  nome_imagem = input("Digite o nome da imagem a ser salva: ")
  print(mensagem_marca_dagua)
  with open(os.path.join("imagens_marca_dagua_inserida", "mensagem.txt"), 'a') as f:
    f.write(mensagem_marca_dagua.decode('utf-8') + '\n')
  cv2.imwrite(os.path.join("imagens_com_marca_dagua", nome_imagem), imagem_estego)"""

  ###################################### Extrair Mensagem ###############################################
  # Extraia a imagem secreta da imagem estego
  """print("Selecione a Imagem Para procurar marca d'água")
  imagem_estego = carregar_imagem()

  #marca_dagua_extraida = extrair_imagem(imagem_estego)

  imagem_secreta = extrair_imagem(imagem_estego)"""