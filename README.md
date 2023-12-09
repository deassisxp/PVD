# Código PVD em Python
# Esteganografia de imagens

Este código implementa um método de esteganografia de imagens, que consiste em esconder uma imagem secreta dentro de outra imagem de cobertura, de forma que a imagem resultante (imagem estego) não apresente diferenças visíveis em relação à imagem original.

## Funções principais

- `esconder_imagem(imagem_cobertura, imagem_secreta)`: recebe duas imagens como parâmetros (a imagem de cobertura e a imagem secreta) e retorna a imagem estego e a imagem secreta redimensionada. Esta função verifica se as imagens têm o mesmo tamanho, e se não tiverem, redimensiona a imagem secreta. Em seguida, chama a função `esconder_imagem_canal_rgb` para cada canal RGB da imagem de cobertura, e escolhe o canal que apresenta a melhor PSNR (Peak Signal-to-Noise Ratio) como o canal onde a imagem secreta será escondida. Por fim, combina os bits da imagem secreta com os bits menos significativos do canal escolhido e retorna a imagem estego e a imagem secreta.

- `esconder_imagem_canal_rgb(imagem_cobertura, imagem_secreta, rgb)`: recebe três parâmetros: a imagem de cobertura, a imagem secreta e o canal RGB ('r', 'g' ou 'b'). Esta função verifica se a imagem de cobertura é um canal único (em escala de cinza), e se for, retorna uma mensagem de erro. Caso contrário, cria uma cópia da imagem de cobertura para armazenar o resultado, e extrai o canal RGB especificado. Em seguida, converte as imagens de cobertura e secreta em números binários, e substitui os bits menos significativos do canal RGB pelos bits da imagem secreta. Por fim, retorna a imagem estego e a imagem secreta.

## Funções auxiliares

O código também utiliza algumas funções auxiliares definidas no arquivo `funcoes.py`, que são:

- `psnr(imagem1, imagem2)`: calcula e retorna o PSNR entre duas imagens.
- `calcular_correlacao_entre_marcas_dagua(imagem1, imagem2)`: calcula e retorna a correlação entre duas imagens.
- `redimensionar(imagem_cobertura, imagem_secreta)`: redimensiona a imagem secreta para ter o mesmo tamanho da imagem de cobertura e retorna a imagem secreta redimensionada.
