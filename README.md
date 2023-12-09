# PVD em Python
Este é um script em Python que permite esconder uma imagem dentro de outra usando a técnica de Pixel Value Differencing (PVD) em canais RGB. Também fornece a funcionalidade de extrair a imagem secreta de uma imagem esteganografada.

## Pré-requisitos
Python 3.x
Bibliotecas Python: **cv2**, **numpy**, **matplotlib**, **tkinter**

## Como Usar
- Execute o script Python.
- Selecione a imagem de cobertura (imagem na qual você deseja esconder a imagem secreta).
- Selecione a imagem secreta que você deseja esconder na imagem de cobertura.
- O script irá esconder a imagem secreta na imagem de cobertura e exibir a imagem esteganografada.

## Funções Principais
- `esconder_imagem(imagem_cobertura, imagem_secreta)`
Esta função aceita duas imagens como entrada (imagem_cobertura e imagem_secreta) e retorna a imagem esteganografada e a imagem secreta.

- `extrair_imagem(imagem_estego)`
Esta função aceita uma imagem esteganografada como entrada (imagem_estego) e extrai a imagem secreta, exibindo-a e indicando se a imagem parece conter ou não uma marca d'água.

- `carregar_imagem()`
Esta função abre uma janela para selecionar o arquivo de imagem e retorna a imagem selecionada.

- `imagens_da_pasta(pasta)`
Esta função obtém todas as imagens de uma determinada pasta.

### Notas
O script utiliza a técnica PVD em canais RGB para esconder e extrair a imagem.
As funções `psnr`, `calcular_correlacao_entre_marcas_dagua`, `redimensionar` são funções externas desenvolvidas por outros membros da equipe
