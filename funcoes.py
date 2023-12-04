import cv2
import numpy as np
import io
import os
import matplotlib.pyplot as plt

def redimensionar(imagem_referencia, imagem_redimensionar):
    altura_referencia = imagem_referencia.shape[0]
    largura_referencia = imagem_referencia.shape[1]
    imagem_redimensionada = cv2.resize(imagem_redimensionar, (largura_referencia, altura_referencia))

    return imagem_redimensionada

def calcular_correlacao_entre_marcas_dagua(marca_dagua_entrada, marca_dagua_extraida):
    marca_dagua_extraida = redimensionar(marca_dagua_entrada, marca_dagua_extraida)

    # Verifique se as duas imagens têm o mesmo tamanho
    if marca_dagua_entrada.shape != marca_dagua_extraida.shape:
        raise ValueError("As imagens das marcas d'água têm tamanhos diferentes")

    # Calcule a média das intensidades de pixel para ambas as imagens
    media_entrada = np.mean(marca_dagua_entrada)
    media_extraida = np.mean(marca_dagua_extraida)

    # Calcule a diferença entre as intensidades de pixel e a média
    diff_entrada = marca_dagua_entrada - media_entrada
    diff_extraida = marca_dagua_extraida - media_extraida

    # Calcule os termos para a fórmula da correlação cruzada normalizada
    termo1 = np.sum(diff_entrada * diff_extraida)
    termo2 = np.sqrt(np.sum(diff_entrada ** 2) * np.sum(diff_extraida ** 2))

    # Calcule a correlação cruzada normalizada
    correlacao = termo1 / termo2

    return correlacao

def psnr(original, compressed):
    compressed = redimensionar(original, compressed)

    mse_total = 0

    if len(original.shape) == 3 and len(compressed.shape) == 3:
        # Supondo que original e compressed sejam imagens coloridas no formato RGB
        mse_r = np.mean((original[:, :, 0] - compressed[:, :, 0]) ** 2)
        mse_g = np.mean((original[:, :, 1] - compressed[:, :, 1]) ** 2)
        mse_b = np.mean((original[:, :, 2] - compressed[:, :, 2]) ** 2)

        mse_total = (mse_r + mse_g + mse_b) / 3  # Calcula a média dos MSEs dos canais R, G e B

    elif len(original.shape) == 2 and len(compressed.shape) == 2:
        # Se as imagens forem em escala de cinza (um único canal)
        mse_total = np.mean((original - compressed) ** 2)

    if mse_total == 0:
        return float('inf')

    max_pixel = 255.0
    psnr = 20 * np.log10(max_pixel / np.sqrt(mse_total))

    return psnr