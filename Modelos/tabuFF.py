import pandas as pd
import csv
from numpy import array
import numpy as np
import math
import random
import warnings
from random import randint
import matplotlib.pyplot as plt
warnings.filterwarnings("ignore")


def validaFO(a0, funcao_objetivo):
    y,x = np.where(a0 == 1)
    if(sum(funcao_objetivo[y,x]) == 5):
        return True
    else:
        return False


def valida(a0):
    if (len(np.where(np.sum(a0, axis=0) > 1)[0]) > 1):
        return False
    else:
        return True


def isInList(a0, tabuList):
    r = False
    for i in tabuList:
        if(np.array_equal(i, a0) == True):
            r = True
            break
        else:
            r = False
    return r

def getNbhd (a0,funcao_objetivo,passo):
    x = len(a0[0,:])
    aList = []
    p = -1
    a1 = a0.copy()
    if(int(x/passo) == 0):
        k = 1
    else:
        k = int(x/passo)
    for i in range (0, k):
        fator = random.randint(1, 5)
        for j in range (0,fator):
            a0 = salta(a0,1,funcao_objetivo,(passo*i), passo)
            a1 = salta(a1,1,funcao_objetivo,(passo*i), passo)
        aList.append(salta(a0,1,funcao_objetivo,(passo*i), passo))
        aList.append(salta(a1,p,funcao_objetivo,(passo*i), passo))

    return aList


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
    i,j = np.where(a0 == 1)
    custo = matriz_custo[i,j].sum() * 2
    return custo


ef = pd.ExcelFile('SFI_ALOCACAO.xlsx')

x_graph = []
y_graph = []
h = []

#**************************************************
#*********LEITURA DE DADOS****************
#**************************************************
#**************************************************

disponibilidade = pd.read_excel(ef, 'Disponibilidade - PREENCHER', 1, usecols=['NOME', 'UF',  'DISPONIBILIDADE'])
arcos           = pd.read_excel(ef, 'Arcos',                       1, usecols=['ORIGEM_ARCO', 'DESTINO_ARCO', 'CUSTO', 'TEMPO'])
inspecoes       = pd.read_excel(ef, 'Atividades',                  1, usecols=['GRUPO_A', 'DURACAO', 'EQUIPE'])
oferta          = pd.read_excel(ef, 'Atividades',                  1,usecols=['SERVIDOR',  'GRUPO_P'])
demanda         = pd.read_csv('demanda1.csv', sep=';')

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
            tempo   = tempo['TEMPO'].values[0]
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
        
#**************************************************
#*********INICIA TABU**************************
#**************************************************
#**************************************************

s0 = geraIndividuo(funcao_objetivo, disponibilidade,disp_aux,inspecoes, demanda_aux,arcos)
sBest = s0
bestCandidate = s0
tabuList = []
tabuList.append(s0)
print("COMECOU")

for i in range (0,5000):
    passoAleatorio = random.randint(1, 7)
    sNbhd = getNbhd(bestCandidate,funcao_objetivo,passoAleatorio)
    #for j in sNbhd:
        #print(respeitaDisponibilidade(j, disponibilidade, demanda, arcos,inspecoes))
    bestCandidate = sNbhd[0]

    for sCandidate in sNbhd:

        custoCandidate = calculaCusto(sCandidate, matriz_custo)
        custoBest      = calculaCusto(bestCandidate, matriz_custo)
        print(sNbhd, custoCandidate, custoBest)
        #não tá na lista?
        #custo do canditado é menor que o custo do best?
        #candidato respeita disponibilidade?
        if((isInList(sCandidate, tabuList) == False) and (custoCandidate < custoBest) and (respeitaDisponibilidade(sCandidate, matriz_tempo_total) == True) and (valida(sCandidate) == True)):
            bestCandidate = sCandidate

    custoBest = calculaCusto(bestCandidate, matriz_custo)
    custosBest = calculaCusto(sBest, matriz_custo)
    tabuList.append(bestCandidate)

    x_graph.append(i)
    y_graph.append(custosBest)
    h.append(19017)

    #print(i,int(custosBest), int(custoBest),"TABU")
    if(custoBest < custosBest):
        sBest = bestCandidate

    if(len(tabuList) > 60):
        del tabuList[0]

print(i,int(custosBest), int(custoBest),"TABU")
#plt.plot(x_graph, y_graph, 'r')
#plt.plot(x_graph, h, 'b')
#axes = plt.gca()
#axes.set_ylim([0,10000])
#plt.ylabel('custo')
#plt.xlabel('iterações')
#plt.show()
