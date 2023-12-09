# PVD
Introdução

Este código implementa um algoritmo de esteganografia baseado na técnica de Perceptual Vector Diffusion (PVD). O PVD é um algoritmo simples e eficaz que pode ser usado para esconder imagens em outras imagens de forma imperceptível.

O código é escrito em Python e pode ser usado para esconder e extrair imagens em imagens coloridas ou em escala de cinza.

Como usar

Para usar o código, siga estas etapas:

Carregue a imagem de cobertura e a imagem secreta.
Chame a função esconder_imagem() para esconder a imagem secreta na imagem de cobertura.
Chame a função extrair_imagem() para extrair a imagem secreta da imagem estego.
Exemplo

Python
# Carregue a imagem de cobertura
imagem_cobertura = carregar_imagem()

# Carregue a imagem secreta
imagem_secreta = carregar_imagem()

# Esconda a imagem secreta na imagem de cobertura
imagem_estego, imagem_secreta = esconder_imagem(imagem_cobertura, imagem_secreta)

# Exiba a imagem estego
cv2.imshow("Imagem estego", imagem_estego)
cv2.waitKey(0)

# Extraia a imagem secreta da imagem estego
imagem_secreta_extraída = extrair_imagem(imagem_estego)

# Exiba a imagem secreta extraída
cv2.imshow("Imagem secreta extraída", imagem_secreta_extraída)
cv2.waitKey(0)
Use o código com cuidado. Saiba mais
Este código produzirá o seguinte resultado:

Imagem estego: imagens_estegano/imagem_estego.jpg

Imagem secreta extraída: imagens_estegano/imagem_secreta_extraída.jpg

Funções

O código contém as seguintes funções:

esconder_imagem(): Esconde a imagem secreta na imagem de cobertura.
extrair_imagem(): Extrai a imagem secreta da imagem estego.
carregar_imagem(): Carrega uma imagem de um arquivo.
imagens_da_pasta(): Obtém todas as imagens de uma pasta.
Explicação do código

A função esconder_imagem() funciona da seguinte forma:

Verifica se as imagens têm o mesmo tamanho. Se não tiverem, redimensiona a imagem secreta para o tamanho da imagem de cobertura.
Separa os canais de cor das imagens de cobertura e secreta.
Percorre cada pixel no canal escolhido da imagem secreta.
Obtém os 4 bits mais significativos do pixel no canal escolhido da imagem secreta.
Limpa os 4 bits menos significativos do pixel no canal escolhido da imagem de cobertura.
Substitui os 4 bits menos significativos do pixel no canal escolhido da imagem de cobertura pelos 4 bits mais significativos do pixel no canal escolhido da imagem secreta.
Combine os canais de cor para criar a imagem estego.
A função extrair_imagem() funciona da seguinte forma:

Cria uma matriz vazia para armazenar a imagem secreta extraída.
Defina os níveis de quantização.
Verifique se a imagem estego é em escala de cinza.
Se a imagem estego for em escala de cinza, extraia a imagem secreta do canal cinza.
Se a imagem estego for colorida, extraia a imagem secreta dos canais R, G e B.
Percorra cada pixel em cada canal da imagem estego.
Extraia os 4 bits menos significativos do pixel no canal escolhido da imagem estego.
Mova os 4 bits menos significativos para a posição dos 4 bits mais significativos.
Encontre o índice do nível de quantização mais próximo do valor dos 4 bits menos significativos.
Armazene o nível de quantização encontrado na imagem secreta correspondente.
A função carregar_imagem() abre uma janela para selecionar o arquivo de imagem.

A função imagens_da_pasta() obtém todos os arquivos da pasta e retorna uma lista com as imagens.

Conclusão

Este código é uma implementação simples e eficaz do algoritmo de esteganografia PVD. Pode ser usado para esconder imagens em outras imagens de forma imperceptível.
