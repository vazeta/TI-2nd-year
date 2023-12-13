import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import huffmancodec as huffc

def main():
    
    # Ponto 1
    data = pd.read_excel('CarDataset.xlsx') #usar o panda para ler o excel
    matriz_valores = data.to_numpy() # Construir a matriz
    varNames = data.columns.values.tolist() # nomes das variaveis q estao nas colunas
    nomes_variaveis = [var for var in varNames if var != 'MPG'] #agrupar as variaveis menos o mpg
    
    # Ponto 2
    for i,var in enumerate(nomes_variaveis,1): #enumerate associa um indice para cada imagem 
        plt.subplot(3, 2, i)  
        plt.scatter(data[var], data['MPG'],1.5,"m")
        plt.title(f'Relação entre {var} e MPG')
        plt.xlabel(var)
        plt.ylabel('MPG')
        
    plt.tight_layout()
    plt.show()
    

    # Ponto 3
    matriz_valores = matriz_valores.astype('uint16') #passar a variavel data para a unidade de inteiros sem sinal de 16 bits
    alfabeto = np.arange(matriz_valores.itemsize)
    
    #Ponto 4
    contagens = calcular_ocorrencias(matriz_valores, nomes_variaveis)
    
    #Ponto 5
    for var in nomes_variaveis:
        plot_resultados(var, contagens)

    #Ponto 6
    matriz_binning = data.to_numpy()
    for variavel in nomes_variaveis:
        if variavel == "Weight":
            indice = 5
            novas_contagens1 = divide_intervalos(matriz_binning, variavel, 40, indice)
            print("Weight: \n")
            a = indice_mais_frequente(novas_contagens1)
            print(a)
            
        elif  variavel == "Horsepower":
            indice = 3
            novas_contagens2 = divide_intervalos(matriz_binning, variavel, 5, indice)
            print("Horsepower: \n")
            b = indice_mais_frequente(novas_contagens2)
            print(b)
            
        elif variavel == "Displacement":
            indice = 2
            novas_contagens3 = divide_intervalos(matriz_binning, variavel, 5, indice)
            print("Displacement: \n")
            c = indice_mais_frequente(novas_contagens3)
            print(c)
    print("--------------------------")        
    #Ponto 7
    matriz_entropia = data.to_numpy()
    for i,var in enumerate(varNames):
        entrops = calcular_entropia(i, matriz_entropia)
        print(f"{var}: {entrops:.2f} bits por símbolo")
        
    entrops_geral = calcular_entropia_geral(matriz_entropia,varNames)
    print(f"Dados Totais: {entrops_geral:.2f} bits por símbolo")
        
    print("--------------------------") 
    
    #Ponto 8
    matriz_huffman = data.to_numpy()
    for i,variavel in enumerate(varNames):
        huffman(i, matriz_huffman,variavel)
        
    print("--------------------------") 
    
    #Ponto 9
    matriz_corr = data.to_numpy()
    for i in range(6): 
        print(f"Coeficiente de correlação (MPG / {varNames[i]}): {np.corrcoef(matriz_corr[:, i], matriz_corr[:, 6], rowvar=True)[0, 1]}")
   
    print("--------------------------")
    
    #Ponto 10
    matriz_im = data.to_numpy()
    for i in range (len(nomes_variaveis)):
        valor = calcular_informaçao_mutua(matriz_im, i)
        indice = nomes_variaveis[i]
        print(f"Informação mútua entre MPG e {indice} : {valor}" )
        
    print("--------------------------")  
        
    #Ponto11
    matriz_estimar = data.to_numpy()
    estimar_mpg(matriz_estimar)
  
    
    
#Ponto 4   
def calcular_ocorrencias(matriz_valores, nomes_variaveis):
    contagens = {}
    for i, var in enumerate(nomes_variaveis):  
        ocorrencias = {}
        for valor in matriz_valores[:, i]:
            if valor in ocorrencias:
                ocorrencias[valor] += 1
            else:
                ocorrencias[valor] = 1
        contagens[var] = {k: v for k, v in ocorrencias.items() if v > 0}
    return contagens



#Ponto 5
def plot_resultados(variavel, contagens):
    eixo_x = list(contagens[variavel].keys())
    eixo_y = list(contagens[variavel].values())        
    plt.figure()
    plt.bar(eixo_x, eixo_y, color='red')  # Define a cor das barras como vermelho
    plt.title(f'Ocorrências de {variavel}')
    plt.xlabel(variavel)
    plt.ylabel('Ocorrências')
    plt.tight_layout()
    plt.show()
    
#Ponto 6
def divide_intervalos(matriz_binning, variavel, n , indice):
    novas_contagens = {}
    matriz_binning = matriz_binning.T
    novas_contagens[variavel] = [matriz_binning[indice][i:i+n] for i in range(0, len(matriz_binning[indice]), n)]
    return novas_contagens

def indice_mais_frequente(novas_contagens):
    for variavel, valores in novas_contagens.items():
        if variavel in ["Weight", "Displacement", "Horsepower"]:
            for i, vals in enumerate(valores):
                valores_unicos, contagens = np.unique(vals, return_counts=True)
                indice_mais_frequente = np.argmax(contagens)
                aux = np.where(vals!=valores_unicos[indice_mais_frequente], valores_unicos[indice_mais_frequente], vals)
                novas_contagens[variavel][i] = aux.tolist()

    return novas_contagens

#Ponto 7
def calcular_entropia(indice,matriz_entropia):
    matriz_entropia = matriz_entropia.T
    valores,contagens = np.unique(matriz_entropia[indice],return_counts=True)
    numero_ocorrencias = np.sum(contagens)
    prob = contagens / numero_ocorrencias
    entropia = -np.sum(prob * np.log2(prob))
    return entropia

def calcular_entropia_geral(matriz_entropia,varNames):
    matriz_entropia = matriz_entropia.T
    entropias = []
    for i,variavel in enumerate(varNames):
        entropias.append(matriz_entropia[i])
    valores,contagens = np.unique(entropias,return_counts=True)
    numero_ocorrencias = np.sum(contagens)
    prob = contagens/numero_ocorrencias
    entropia = -np.sum(prob * np.log2(prob))
    return entropia

#Ponto 8
def huffman(indice,matriz_huffman,variavel):
    matriz_huffman = matriz_huffman.T
    S = matriz_huffman[indice]
    codec = huffc.HuffmanCodec.from_data(S)
    symbols, lengths = codec.get_code_len()
    
    # Calcular a média ponderada
    valores, contagens = np.unique(S, return_counts=True)
    prob = contagens / len(S)  # Probabilidade de ocorrência
    media_ponderada = sum(p * l for p, l in zip(prob, lengths))
    
    # Calcular a variância
    variancia = sum((l - media_ponderada)**2 * p for l, p in zip(lengths, prob))
    
    print(f"Número médio de bits por símbolo da {variavel} (Huffman): {media_ponderada:.2f}")
    print(f"Variância dos comprimentos (Huffman): {variancia:.2f}")

#Ponto 10
def calcular_informaçao_mutua(matriz_valores,indice):
    total = matriz_valores.shape[0] #numero de linhas e numero de colunas por ordem
    pares = np.column_stack((matriz_valores[:,-1], matriz_valores[:,indice])) #matrix mpg variavel
    mpg, contagensMpg = np.unique(matriz_valores[:,-1], return_counts = True) #valores unicos e contagens do mpg
    variavel, contagensPar = np.unique(matriz_valores[:,indice], return_counts = True) #contagens dos valores unicos da variavel
    im = 0
    for i in range(total):
        if np.where((pares == pares[i]).all(axis = 1))[0][0] < i: # axis ao longo da coluna
            continue 
        valmpg = pares[i][0]
        valvar = pares[i][1]

        indiceMpg = np.where(mpg == valmpg)[0][0] #tuplo
        indice_variavel = np.where(variavel == valvar)[0][0]

        probabilidade_valmpg = contagensMpg[indiceMpg] / total
        probabilidade_valvar = contagensPar[indice_variavel] / total

        probabilidade_conjunta = sum(np.all(pares == pares[i], axis = 1))/total

        im +=  probabilidade_conjunta * np.log2( probabilidade_conjunta/(probabilidade_valmpg * probabilidade_valvar))
    return im

#Ponto 11 

def estimar_mpg(matriz_estimar):
    a = -5.241
    b = -0.146
    c = -0.4909
    d = 0.0026
    e = -0.0045
    f = 0.6725
    g = -0.0059
    
    predict1 = np.zeros_like(matriz_estimar[:, 6], dtype=float)  # Criar array para previsão 1
    predict2 = np.zeros_like(matriz_estimar[:, 6], dtype=float)  # Criar array para previsão 2
    predict3 = np.zeros_like(matriz_estimar[:, 6], dtype=float)  # Criar array para previsão 3
    diff1 = np.zeros_like(matriz_estimar[:, 6], dtype=float)
    diff2 = np.zeros_like(matriz_estimar[:, 6], dtype=float)
    diff3 = np.zeros_like(matriz_estimar[:, 6], dtype=float)
    
    for i in range(np.shape(matriz_estimar)[0]):
        predict1[i] = round(a + b * matriz_estimar[i, 0] + c * matriz_estimar[i, 1] + d * matriz_estimar[i, 2] + e * matriz_estimar[i, 3] + f * matriz_estimar[i, 4] + g * matriz_estimar[i, 5], 1)
        predict2[i] = round(a + (c * matriz_estimar[i, 1]) + (d * matriz_estimar[i, 2]) + (e * matriz_estimar[i, 3]) + (f * matriz_estimar[i, 4]) + (g * matriz_estimar[i, 5]), 1)
        predict3[i] = round(a + b * matriz_estimar[i, 0] + c * matriz_estimar[i, 1] + d * matriz_estimar[i, 2] + e * matriz_estimar[i, 3] + f * matriz_estimar[i, 4], 1)
        diff1[i] = matriz_estimar[i, 6] - predict1[i]
        diff2[i] = matriz_estimar[i, 6] - predict2[i]
        diff3[i] = matriz_estimar[i, 6] - predict3[i]
    
    print("MPG_real / MPG_estimado / MPG_estimado_sem _aceleracao / MPG_estimado_sem _peso")
    for i in range(np.shape(matriz_estimar)[0]):
        print(f"{matriz_estimar[i, 6]:.1f} / {predict1[i]:.1f} / {predict2[i]:.1f} / {predict3[i]:.1f}")
    
    # Calcular MAE para cada previsão
    mae1 = np.mean(np.abs(diff1))
    mae2 = np.mean(np.abs(diff2))
    mae3 = np.mean(np.abs(diff3))
    
    print("\nMAE para MPG_estimado:", mae1)
    print("MAE para MPG_estimado_sem _aceleracao(menor MI):", mae2)
    print("MAE para MPG_estimado_sem _peso(maior MI):", mae3)



if __name__ == "__main__":
    main()   
          
    
