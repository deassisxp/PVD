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

def esconder_imagem_canal_rgb(imagem_cobertura, imagem_secreta, rgb):
    # Verifique se a imagem de cobertura é um canal único (em escala de cinza)
    if len(imagem_cobertura.shape) < 3 or imagem_cobertura.shape[2] == 1:
        return "A mensagem não pode ser codificada porque a imagem de cobertura é um canal único."
    
    # Cria uma cópia da imagem de cobertura para armazenar o resultado.
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

  # Defina os níveis de quantização.
  niveis = np.array([0, 16, 32, 48, 64, 80, 96, 112, 128, 144, 160, 176, 192, 208, 224, 240, 255])

  # Verifique se a imagem estego é em escala de cinza.
  if len(imagem_estego.shape) == 2:
    # Se a imagem estego for em escala de cinza, extraia a imagem secreta do canal cinza.
    imagem_secreta_gray = np.zeros_like(imagem_estego)
    canais = [('gray', imagem_estego, imagem_secreta_gray)]
    return imagem_secreta_gray
  else:
    # Se a imagem estego for colorida, extrai a imagem secreta dos canais R, G e B.
    estego_b, estego_g, estego_r = cv2.split(imagem_estego)
    canais = [('r', estego_r, imagem_secreta_r), ('g', estego_g, imagem_secreta_g), ('b', estego_b, imagem_secreta_b)]

  # Percorra cada pixel em cada canal da imagem estego.
  nome_canal_r, estego_r, imagem_secreta_r = canais[0]
  for y in range(estego_r.shape[0]):
    for x in range(estego_r.shape[1]):
        # Extraia os 4 bits menos significativos do pixel no canal escolhido da imagem estego.
        bits_menos_significativos = estego_r[y, x] & 0x0F

        # Mova os 4 bits menos significativos para a posição dos 4 bits mais significativos.
        bits_menos_significativos <<= 4

        indice = np.argmin(np.abs(niveis - bits_menos_significativos))
        bits_menos_significativos = niveis[indice]

        # Armazene os bits extraídos na imagem secreta correspondente.
        imagem_secreta_r[y, x] = bits_menos_significativos
        imagem_secreta_r[y, x] &= 0xF0
        imagem_secreta_r[y, x] |= int(bits_menos_significativos / 16)
  
  nome_canal_g, estego_g, imagem_secreta_g = canais[1]
  for y in range(estego_g.shape[0]):
      for x in range(estego_g.shape[1]):
        # Extraia os 4 bits menos significativos do pixel no canal escolhido da imagem estego.
        bits_menos_significativos = estego_g[y, x] & 0x0F

        # Mova os 4 bits menos significativos para a posição dos 4 bits mais significativos.
        bits_menos_significativos <<= 4

        indice = np.argmin(np.abs(niveis - bits_menos_significativos))
        bits_menos_significativos = niveis[indice]

        # Armazene os bits extraídos na imagem secreta correspondente.
        imagem_secreta_g[y, x] = bits_menos_significativos
        imagem_secreta_g[y, x] &= 0xF0
        imagem_secreta_g[y, x] |= int(bits_menos_significativos / 16)
  
  nome_canal_b, estego_b, imagem_secreta_b = canais[2]
  for y in range(estego_b.shape[0]):
      for x in range(estego_b.shape[1]):
        # Extraia os 4 bits menos significativos do pixel no canal escolhido da imagem estego.
        bits_menos_significativos = estego_b[y, x] & 0x0F

        # Mova os 4 bits menos significativos para a posição dos 4 bits mais significativos.
        bits_menos_significativos <<= 4

        indice = np.argmin(np.abs(niveis - bits_menos_significativos))
        bits_menos_significativos = niveis[indice]

        # Armazene os bits extraídos na imagem secreta correspondente.
        imagem_secreta_b[y, x] = bits_menos_significativos
        imagem_secreta_b[y, x] &= 0xF0
        imagem_secreta_b[y, x] |= int(bits_menos_significativos / 16)
    
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
    Extrai uma mensagem de uma imagem usando a técnica de PVD em todos os canais.

    Args:
        imagem_estego: A imagem esteganografada.

    Returns:
        As mensagens secretas de cada canal.
    """
    # Separe os canais de cor da imagem esteganografada.
    estego_b, estego_g, estego_r = cv2.split(imagem_estego)

    # Crie um dicionário para armazenar os bits da mensagem de cada canal.
    bits_mensagem = {'r': [], 'g': [], 'b': []}

    # Percorra cada pixel em cada canal da imagem esteganografada.
    for canal, estego_canal in zip(['r', 'g', 'b'], [estego_r, estego_g, estego_b]):
        for y in range(estego_canal.shape[0]):
            for x in range(estego_canal.shape[1]):
                # Obtenha o bit menos significativo do pixel.
                bit_mensagem = estego_canal[y, x] & 0x01

                # Adicione o bit à lista de bits da mensagem.
                bits_mensagem[canal].append(bit_mensagem)

    # Converta a lista de bits em uma string binária e depois em uma string de texto para cada canal.
    mensagem = {canal: ''.join(chr(int(''.join(str(bit) for bit in bits_mensagem[canal][i:i+8]), 2)) for i in range(0, len(bits_mensagem[canal]) - len(bits_mensagem[canal]) % 8, 8)) for canal in ['r', 'g', 'b']}

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
    
def comparar_mensagens(mensagem):
    """
    Compara a mensagem extraída com todas as strings salvas em um arquivo, caractere por caractere.

    Args:
        mensagem: A mensagem extraída.

    Returns:
        Um dicionário indicando se a mensagem extraída corresponde a alguma string no arquivo para cada canal.
    """
    # Leia todas as strings do arquivo.
    caminho_arquivo = os.path.join('imagens_marca_dagua_inserida', 'mensagem.txt')
    with open(caminho_arquivo, 'r') as f:
        strings_salvas = f.read().splitlines()

    # Crie um dicionário para armazenar os resultados da comparação para cada canal.
    resultado_comparacao = {}

    # Crie um dicionário para armazenar as mensagens decodificadas de cada canal.
    string_normal = {}

    # Compare a mensagem extraída com todas as strings salvas para cada canal.
        # Compare a mensagem extraída com todas as strings salvas para cada canal.
    for canal in ['r', 'g', 'b']:
        # Decodifica a string de escape de bytes de volta para uma string.
        print(mensagem)
        try:
            string_normal[canal] = bytes(mensagem[canal], 'latin1').decode('utf-8')
        except UnicodeDecodeError:
            string_normal[canal] = "A string não pode ser decodificada usando utf-8."

        print(string_normal)
        for string_salva in strings_salvas:
            # Determine a string menor e a string maior.
            if len(string_normal[canal]) < len(string_salva):
                string_menor = string_normal[canal]
                string_maior = string_salva
            else:
                string_menor = string_salva
                string_maior = string_normal[canal]

            # Compare as strings caractere por caractere.
            caracteres_iguais = 0
            for i in range(len(string_menor)):
                if string_menor[i] == string_maior[i]:
                    caracteres_iguais += 1

            # Verifique se pelo menos 50% dos caracteres são iguais.
            if caracteres_iguais / len(string_menor) >= 0.5:
                resultado_comparacao[canal] = True
            else:
                resultado_comparacao[canal] = False

    return resultado_comparacao

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
  print("Selecione a Imagem Para procurar marca d'água")
  imagem_estego = carregar_imagem()

  #marca_dagua_extraida = extrair_imagem(imagem_estego)

  imagem_secreta_r, imagem_secreta_g, imagem_secreta_b = extrair_imagem(imagem_estego)

  cv2.imwrite(os.path.join("imagens_marca_dagua_extraida", f'imagem_secreta_r.png'), imagem_secreta_r)
  cv2.imwrite(os.path.join("imagens_marca_dagua_extraida", f'imagem_secreta_g.png'), imagem_secreta_g)
  cv2.imwrite(os.path.join("imagens_marca_dagua_extraida", f'imagem_secreta_b.png'), imagem_secreta_b)

###################################### Ocultar Mensagem ##############################################
  # Oculte a mensagem secreta na imagem de cobertura
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

  mensagem_secreta = extrair_mensagem(imagem_estego)

  resultado_comparacao = comparar_mensagens(mensagem_secreta)

  print(resultado_comparacao)"""