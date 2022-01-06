import pandas as pd
import csv
from numpy import array
import numpy as np
import math
import random
import warnings
from random import randint

import time

warnings.filterwarnings("ignore")

def validaFO(a0, funcao_objetivo):
    tamanho = len(funcao_objetivo[0,:])
    y,x = np.where(a0 == 1)
    if(sum(funcao_objetivo[y,x]) == tamanho):
        return True
    else:
        return False


def valida(a0):
    a0v = a0.copy()
    if (len(np.where(a0v == 1)[0]) == 5):
        return True
    else:
        return False

def respeitaDisponibilidade(a0, matriz_tempo_total):
    a0rd = a0.copy()

    for i in range (0, len(a0rd[:,0])):
        indice_aux = np.where(a0rd[i,:] == 1)[0]
        if(len(indice_aux > 0)):
            soma = matriz_tempo_total[i, indice_aux].sum()
            if(soma > 5.0):
                return False
    return True


#calcula custo da matriz
def calculaCusto(a0, matriz_custo):
    a0cc = a0.copy()
    i,j = np.where(a0cc == 1)
    custo = matriz_custo[i,j].sum() * 2
    return custo


#direcao: -1 desce, 1 sobe
#a0:        matriz com a solução possivel
#FO:       matriz gabarito
def salta(a0, direcao,FO,posicao_passo,tamanho_passo):
    a_aux = a0.copy()
    if(tamanho_passo+posicao_passo < len(FO[0,:] )):
        final = tamanho_passo+posicao_passo
    else:
        final = len(FO[0,:] )

    for i in range (posicao_passo, final):
        #fazer o recorte do salto em cima dos servidores_aptos tambem
        servidores_aptos = np.where(FO[:,i] == 1)[0]
        try:
            indice_atual = np.where(a0[:,i] == 1)[0][0]
            servidor_salto = np.where(servidores_aptos == indice_atual)[0][0]
            if((servidor_salto - direcao) == len(servidores_aptos)):
                novo_indice = servidores_aptos[0]
            else:
                novo_indice = servidores_aptos[servidor_salto - direcao]

            a_aux[indice_atual,i] = 0
            a_aux[novo_indice,i] = 1
        except:
            l = True
    return  a_aux



#função que conserva da parte deslocada e adiciona a parte
def mascara(a0, a1, y_inicio, y_fim):
    a0mf = a0.copy()
    a1mf = a1.copy()

    a_aux = np.zeros((len(a0mf[:,0]),len(a0mf[0,:])), dtype=int)
    a_aux[y_inicio:y_fim,:] = np.absolute(~a_aux[y_inicio:y_fim,:])
    a_aux = np.logical_and(a_aux,a0mf).astype(int)

    a_aux2 = np.ones((len(a0mf[:,0]),len(a0mf[0,:])), dtype=int)
    a_aux2[y_inicio:y_fim,:] = np.logical_not(a_aux2[y_inicio:y_fim,:]).astype(int)
    a_aux2 = np.logical_and(a_aux2,a1mf).astype(int)
    a_final = np.logical_or(a_aux2,a_aux).astype(int)

    return a_final.copy()

def geraIndividuo(funcao_objetivo, disponibilidade,disp_aux,inspecoes, demanda_aux,arcos):
    funcao_objetivo2 =  np.zeros((len(disponibilidade),len(demanda_aux)), dtype=int)
    custo = 0
    disponibilidade_copia = disponibilidade.copy()
    for i in range (len(demanda)):
        indice_aux  =  random.choice(np.where(funcao_objetivo[:,i] == 1)[0])
        origem      = disponibilidade_copia.where(disponibilidade_copia['NOME'].isin([disp_aux[indice_aux]]) == True).dropna()
        origem      = origem['UF'].values[0]
        destino     = demanda['AEROPORTO'].values[i]

        disponibilidade_atual = disponibilidade_copia['DISPONIBILIDADE'].loc[disponibilidade_copia['NOME'] == disp_aux[indice_aux]].values[0]
        tempo_total           = inspecoes['DURACAO'].loc[inspecoes['GRUPO_A'] == demanda_aux[i]].values[0]
        tempo_total           = tempo_total + (2*(arcos['TEMPO'].loc[(arcos['ORIGEM_ARCO'] == origem) & (arcos['DESTINO_ARCO'] == destino)].values[0]))

        while(tempo_total > disponibilidade_atual):
            indice_aux  =  random.choice(np.where(funcao_objetivo[:,i] == 1)[0])
            origem      = disponibilidade_copia.where(disponibilidade['NOME'].isin([disp_aux[indice_aux]]) == True).dropna()
            origem      = origem['UF'].values[0]
            destino     = demanda['AEROPORTO'].values[i]

            disponibilidade_atual = disponibilidade_copia['DISPONIBILIDADE'].loc[disponibilidade_copia['NOME'] == disp_aux[indice_aux]].values[0]
            tempo_total           = inspecoes['DURACAO'].loc[inspecoes['GRUPO_A'] == demanda_aux[i]].values[0]
            tempo_total           = tempo_total + (2*(arcos['TEMPO'].loc[(arcos['ORIGEM_ARCO'] == origem) & (arcos['DESTINO_ARCO'] == destino)].values[0]))

        disponibilidade_copia['DISPONIBILIDADE'].loc[disponibilidade_copia['NOME'] == disp_aux[indice_aux]] = disponibilidade_atual - tempo_total # aqui tá dando rpoblema, eu preciso fazer uma copia

        origem   = disponibilidade_copia.where(disponibilidade_copia['NOME'].isin([disp_aux[indice_aux]]) == True).dropna()
        origem   = origem['UF'].values[0]
        destino  = demanda['AEROPORTO'].values[i]
        valor    = arcos.where(arcos['ORIGEM_ARCO'].isin([origem]) == True).dropna()
        valor    = valor.where(valor['DESTINO_ARCO'].isin([destino]) == True).dropna()
        valor    = valor['CUSTO'].values[0]
        custo    = custo + valor

        funcao_objetivo2[indice_aux, i] = 1


    return funcao_objetivo2.copy()

inicioLeitura = time.time()
ef = pd.ExcelFile('InstanciaB3.xlsx')

#**************************************************
#*********LEITURA DE DADOS****************
#**************************************************
#**************************************************

# Leitura do excel de entrada do LINGO
# Recorte do dominio


disponibilidade = pd.read_excel(ef, 'Disponibilidade - PREENCHER', 1, usecols=['NOME', 'UF',  'DISPONIBILIDADE'])
arcos           = pd.read_excel(ef, 'Arcos',                       1, usecols=['ORIGEM_ARCO', 'DESTINO_ARCO', 'CUSTO', 'TEMPO'])
inspecoes       = pd.read_excel(ef, 'Atividades',                  1, usecols=['GRUPO_A', 'DURACAO', 'EQUIPE'])
oferta          = pd.read_excel(ef, 'Atividades',                  1 ,usecols=['SERVIDOR',  'GRUPO_P'])
#demanda         = pd.read_csv('demandaAleatoria/10/demanda40.csv', sep=';')
demanda          = pd.read_excel(ef, 'Demanda - PREENCHER', 1,usecols=[ 'MISSAO', 'ATIVIDADE', 'AEROPORTO'])

destinos_distintos   = pd.read_excel(ef, 'Arcos', 1, usecols=['NOS', 'ORIGEM_NO', 'DESTINO_NO'])
atividades_oferta    = oferta['GRUPO_P'].dropna().values
atividades_restritas = inspecoes['GRUPO_A'].dropna().values
destinos_distintos   = destinos_distintos['DESTINO_NO'].dropna().values

oferta           = oferta.where((oferta['GRUPO_P'].isin(demanda['ATIVIDADE'].values) == True)).dropna()
disponibilidade  =  disponibilidade.where((disponibilidade['NOME'].isin(oferta['SERVIDOR'].values) == True)).dropna()
arcos            = arcos.where((arcos['ORIGEM_ARCO'].isin(disponibilidade['UF'].values) == True )).dropna()
arcos            = arcos.where((arcos['DESTINO_ARCO'].isin(demanda['AEROPORTO'].values) == True )).dropna()
inspecoes        =  inspecoes.where(inspecoes['GRUPO_A'].isin(demanda['ATIVIDADE'].values) == True).dropna()

matriz_alocado = np.zeros((len(disponibilidade),len(inspecoes)), dtype=int)

disponibilidade_aux = disponibilidade.copy()
insp_aux            = inspecoes['GRUPO_A'].values
disp_aux            = disponibilidade['NOME'].values
demanda_aux         = demanda['ATIVIDADE'].values


for i in range (0, len(disponibilidade)):
    for j in range (0, len(inspecoes)):
        if(len(oferta[oferta['SERVIDOR'].str.match(disp_aux[i]) == True].values) > 0):
            aux1 = oferta[(oferta['SERVIDOR'].str.match(disp_aux[i]) == True)]
            if(len(aux1[(oferta['GRUPO_P'].str.match(insp_aux[j]) == True)]) > 0):
                matriz_alocado[i][j] = 1


funcao_objetivo     =  np.zeros((len(disponibilidade),len(demanda)), dtype=int)
matriz_tempo_viagem =  np.zeros((len(disponibilidade),len(demanda)), dtype=float)
matriz_tempo_total  =  np.zeros((len(disponibilidade),len(demanda)), dtype=float)
matriz_custo        =  np.zeros((len(disponibilidade),len(demanda)), dtype=float)
matriz_tempo_missao =  []

for i in demanda_aux:
    d = inspecoes['DURACAO'].loc[(inspecoes['GRUPO_A'] == i)].values[0]
    matriz_tempo_missao.append(d)

i_aux = []
j_aux = []
for i in range (0,len(disponibilidade) ):
    for j in range (0, len(demanda)):
        origem  = disponibilidade.where(disponibilidade['NOME'].isin([disp_aux[i]]) == True).dropna()
        origem  = origem['UF'].values[0]
        destino = demanda['AEROPORTO'].values[j]

        tempo   = arcos.where(arcos['ORIGEM_ARCO'].isin([origem]) == True).dropna()
        tempo   = tempo.where(tempo['DESTINO_ARCO'].isin([destino]) == True).dropna()
        if(len(tempo) > 0):
            custo   = tempo['CUSTO'].values[0]
            tempo   = tempo['TEMPO'].values[0] * 2.0
        else:
            i_aux.append(i)
            j_aux.append(j)
            custo   = 10000000
            tempo   = 10000000

        matriz_custo[i][j] = custo
        matriz_tempo_viagem[i][j] = tempo

for i in range (0,len(disponibilidade) ):
    matriz_tempo_total[i,:] = matriz_tempo_viagem[i,:] + matriz_tempo_missao

#**************************************************
#*********INICIA FUNCAO OBJETIVO********
#**************************************************
#**************************************************
i = 0
for atividade in demanda['ATIVIDADE'].values:
    indice_missao        =   np.where(insp_aux == atividade)[0][0]
    funcao_objetivo[:,i] = matriz_alocado[:,indice_missao]
    i = i + 1

for i in i_aux:
    for j in j_aux:
        funcao_objetivo[i,j] = 0


funcao_objetivo2 = geraIndividuo(funcao_objetivo, disponibilidade,disp_aux,inspecoes, demanda_aux,arcos)
print("começou")
#**************************************************
#*********INICIO DO ALGORITMO************
#**************************************************
#**************************************************

# a0 - original
# a1 - novo

# custos[0] - cima_desce
# custos[1] - cima_sobe
# custos[2] - baixo_sobe
# custos[3] - baixo_desce

# n = corte inicial
# k = corte iterativo e randomico
# iteracoes = quantidades de iteracoes que o algoritmo irá rodar

iteracoes = 5000
p = -1

inicio = 0
fim = len(funcao_objetivo2[:,0])
meio = int(fim/3)

a0 = funcao_objetivo2.copy()
a1 = funcao_objetivo2.copy()
n = 2.7
k = 0
custos = np.zeros(4, dtype=int)

fimLeitura = time.time()
inicioHeuristica = time.time()

for x in range (0,iteracoes):

    #DESCE CIMA
    a1      = salta(a0, 1,funcao_objetivo,inicio, meio)
    a1      = mascara(a1, a0, inicio, meio)
    disp_check = respeitaDisponibilidade(a1, matriz_tempo_total)
    if(disp_check):
        custos[0] = calculaCusto(a1, matriz_custo)
        a_aux1 = a1.copy()
    else:
        custos[0] = 1000000000
        a_aux1 = a0.copy()

    #SOBE CIMA
    a1     = salta(a0, p,funcao_objetivo,inicio, meio)
    a1     = mascara(a1, a0, inicio, meio)
    disp_check = respeitaDisponibilidade(a1, matriz_tempo_total)
    if(disp_check):
        a_aux2 = a1.copy()
        custos[1] = calculaCusto(a1, matriz_custo)
    else:
        a_aux2 = a0.copy()
        custos[1] = 1000000000


    #SOBE BAIXO
    a1     = salta(a0, p,funcao_objetivo,meio, fim)
    a1     = mascara(a1, a0, meio, fim)
    disp_check = respeitaDisponibilidade(a1, matriz_tempo_total)
    if(disp_check):
        a_aux3 = a1.copy()
        custos[2] = calculaCusto(a1, matriz_custo)
    else:
        a_aux3 = a0.copy()
        custos[2] = 1000000000

    #DESCE BAIXO
    a1     = salta(a0, 1,funcao_objetivo,meio, fim)
    a1     = mascara(a1, a0, meio, fim)
    disp_check = respeitaDisponibilidade(a1, matriz_tempo_total)
    if(disp_check):
        a_aux4 = a1.copy()
        custos[3] =  calculaCusto(a1, matriz_custo)
    else:
        a_aux4 = a0.copy()
        custos[3] = 1000000000


    result = all(elem == custos[0] for elem in custos)



    menor = np.argmin(custos)

    if((fim - inicio) < 2):
        n      = randint(2, 10)
        inicio = 0
        fim    = len(funcao_objetivo2[:,0])
        meio   = int(fim/n)
    else:
        if((custos[menor] < 1000000000) and (result == False)):

            if(menor == 0):
                if(validaFO(a_aux1, funcao_objetivo) == True):
                    a0   = a_aux1
                else:
                    a0 = a0
                fim  = meio
                meio = int(((fim - inicio)/n)+inicio)

            elif(menor == 1):
                if(validaFO(a_aux2, funcao_objetivo) == True):
                    a0   = a_aux2
                else:
                    a0 = a0
                fim  = meio
                meio = int(((fim - inicio)/n)+inicio)

            elif(menor == 2):
                if(validaFO(a_aux3, funcao_objetivo) == True):
                    a0   = a_aux3
                else:
                    a0 = a0
                inicio = meio
                meio   = int(((fim - inicio)/n)+inicio)

            else:
                if(validaFO(a_aux4, funcao_objetivo) == True):
                    a0   = a_aux4
                else:
                    a0 = a0
                inicio = meio
                meio   = int(((fim - inicio)/n)+inicio)


        elif((custos[menor] >= 1000000000) and (result == True) ):
            n       = randint(2, 10)
            inicio = 0
            fim    = len(funcao_objetivo2[:,0])
            meio = int(fim/n)
fimHeuristica = time.time()
print(fimLeitura - inicioLeitura)
print(fimHeuristica - inicioHeuristica)
print((calculaCusto(a0, matriz_custo)), custos,  "SA")