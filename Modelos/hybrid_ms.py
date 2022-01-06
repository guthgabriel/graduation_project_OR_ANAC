import pandas as pd
import csv
from numpy import array
import numpy as np
import math
import random
import warnings
from random import randint
import time

pd.set_option("display.max_rows", None, "display.max_columns", None)
warnings.filterwarnings("ignore")


def salta(a0, direcao,FO,posicao_passo,tamanho_passo):
    a_aux = a0.copy()
    if(tamanho_passo+posicao_passo < len(FO[0,:] )):
        final = tamanho_passo+posicao_passo
    else:
        final = len(FO[0,:] )

    for i in range (posicao_passo, final):
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

def isInList(a0, tabuList):
    r = any((np.array_equal(a0, dict_arr) for dict_arr in tabuList))
    return r

def validaFO(a0, funcao_objetivo):
    tamanho = len(funcao_objetivo[0,:])
    y,x = np.where(a0 == 1)
    if(sum(funcao_objetivo[y,x]) == tamanho):
        return True
    else:
        return False

def valida(a0):
    if (len(np.where(np.sum(a0, axis=0) != 1)[0]) > 1):
        return False
    else:
        return True
# pega metade de cada pai
# caso apareca mais de uma pessoa por missao, escolhe aleatoriamente
def crossover(a0, a1,funcao_objetivo):
    a0f = a0.copy()
    a1f = a1.copy()

    b =  mascara(a0f, a1f, 0, int(len(a0[:,0])/2))
    for i in range (0, len(b[0,:])):
        indice_aux = np.where(b[:,i] == 1)
        if(len(indice_aux[0]) == 2):
            indice_random  =  random.choice(indice_aux[0])
            b[indice_random,i] = 0
        elif(len(indice_aux[0]) == 0):
            indice_aux = np.where(funcao_objetivo[:,i] == 1)
            indice_random  =  random.choice(indice_aux[0])
            b[indice_random,i] = 1

    return b.copy()

def geraIndividuo2(funcao_objetivo, matriz_tempo_total, disponibilidade, demanda, disp_aux):
    histograma =  np.zeros((2,len(demanda)), dtype=int)
    for i in range (len(demanda)):
        histograma[0,i] = np.sum(funcao_objetivo[:,i])
        histograma[1,i] = i

    histograma = histograma[:, histograma[0].argsort()]
    disponibilidade_copia = disponibilidade.copy()
    funcao_objetivo2 =  np.zeros((len(disponibilidade),len(demanda)), dtype=int)

    for i in range (len(demanda)):
        j = histograma[1,i]
        indices_fo = np.where(funcao_objetivo[:,j] == 1)[0]
        indices_tempo = indices_fo
        escolhido = random.choice(indices_tempo)
        disp_escolhida = int(disponibilidade_copia['DISPONIBILIDADE'].loc[disponibilidade_copia['NOME'] == disp_aux[escolhido]])

        while((float(matriz_tempo_total[escolhido,j]) > float(disp_escolhida)) and (matriz_tempo_total[escolhido,j] < 1000)):
            escolhido = random.choice(indices_tempo)
            disp_escolhida = float(disponibilidade_copia['DISPONIBILIDADE'].loc[disponibilidade_copia['NOME'] == disp_aux[escolhido]])

        funcao_objetivo2[escolhido, j] = 1
        disponibilidade_copia['DISPONIBILIDADE'].loc[disponibilidade_copia['NOME'] == disp_aux[escolhido]] = disp_escolhida - float(matriz_tempo_total[escolhido,j])
    return funcao_objetivo2

def respeitaDisponibilidade(a0, matriz_tempo_total, disp_oferta):
    a0rd = a0.copy()
    for i in range (0, len(a0rd[:,0])):
        indice_aux = np.where(a0rd[i,:] == 1)[0]
        if(len(indice_aux > 0)):
            soma = matriz_tempo_total[i, indice_aux].sum()
            if(float(soma) > float(disp_oferta[i])):
                return False
    return True

def calculaCusto(a0, matriz_custo):
    i,j = np.where(a0 == 1)
    custo = matriz_custo[i,j].sum() * 2
    return custo

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

def mutacao(a0, funcao_objetivo):
    a0fm = a0.copy()
    for i in range (0, 2):
        missao = randint(0, np.size(a0fm,1) - 1)

        indice = np.where(a0fm[:,missao] == 1)
        indice_aux  =  random.choice(np.where(funcao_objetivo[:,missao] == 1)[0])

        a0fm[indice_aux,missao] = 1
        a0fm[indice,missao] = 0

    return a0fm.copy()

start = time.perf_counter()

inicio = time.time()

ef = pd.ExcelFile('InstanciaB3.xlsx')

#**************************************************
#*********LEITURA DE DADOS****************
#**************************************************
#**************************************************

disponibilidade = pd.read_excel(ef, 'Disponibilidade - PREENCHER', 1, usecols=['NOME', 'UF',  'DISPONIBILIDADE'])
demanda         = pd.read_excel(ef, 'Demanda - PREENCHER', 1,usecols=[ 'MISSAO', 'ATIVIDADE', 'AEROPORTO'])
arcos           = pd.read_excel(ef, 'Arcos',                       1, usecols=['ORIGEM_ARCO', 'DESTINO_ARCO', 'CUSTO', 'TEMPO'])
inspecoes       = pd.read_excel(ef, 'Atividades',                  1, usecols=['GRUPO_A', 'DURACAO', 'EQUIPE'])
oferta          = pd.read_excel(ef, 'Atividades',                  1 ,usecols=['SERVIDOR',  'GRUPO_P'])

disponibilidade = disponibilidade.where(disponibilidade['DISPONIBILIDADE'] != 0).dropna()
disp_aux        = disponibilidade['NOME'].values
oferta          = oferta.where((oferta['SERVIDOR'].isin(disp_aux)) == True).dropna()

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
disp_oferta         = disponibilidade['DISPONIBILIDADE'].values

#0,42 s

for i in range (0, len(disponibilidade)):
    for j in range (0, len(inspecoes)):
        if(len(oferta[oferta['SERVIDOR'].str.match(disp_aux[i]) == True].values) > 0):
            aux1 = oferta[(oferta['SERVIDOR'].str.match(disp_aux[i]) == True)]
            if(len(aux1[(oferta['GRUPO_P'].str.match(insp_aux[j]) == True)]) > 0):
                matriz_alocado[i][j] = 1

#7 segundos


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
            custo   = 1000000
            tempo   = 1000000

        matriz_custo[i][j] = custo
        matriz_tempo_viagem[i][j] = tempo

for i in range (0,len(disponibilidade) ):
    matriz_tempo_total[i,:] = matriz_tempo_viagem[i,:] + matriz_tempo_missao

#50 segundos


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



# Inicialização da funçao objetivo com as restrições devidas
# Escolhe aleatoriamente um servidor
# Pega origem e destino do servidor escolhido
# Calcula a disponibilidade do servidor e o tempo total pra realizar a missão
# Testa se o tempo pra fazer a missão cabe na disponibilidade
# Caso não caiba, sorteia outro servidor
# Sorteio de novo servidor (dica: retirar o primeiro servidor)
# Pega origem e destino
# Calcula novos tempos para possivel teste
# Atualiza a disponibilidade do servidor escolhido
# Pega origem e destino (dica: talvez não precise desse pass)

a = []

a.append(geraIndividuo2(funcao_objetivo, matriz_tempo_total, disponibilidade, demanda, disp_aux))
a.append(geraIndividuo2(funcao_objetivo, matriz_tempo_total, disponibilidade, demanda, disp_aux))
a.append(geraIndividuo2(funcao_objetivo, matriz_tempo_total, disponibilidade, demanda, disp_aux))
a.append(geraIndividuo2(funcao_objetivo, matriz_tempo_total, disponibilidade, demanda, disp_aux))

custos_pais = np.zeros(4, dtype=int)
for i in range (0,4):
    custos_pais[i] = calculaCusto(a[i], matriz_custo)

#**************************************************
#*********INICIA GENETIC*********************
#**************************************************
#**************************************************


fim = time.time()
print(fim-inicio)

print("COMEÇA")
for j in range (0,3000):
    # 6 cruzamentos possiveis
    b = []
    b.append(crossover(a[0], a[1],funcao_objetivo))
    b.append(crossover(a[1], a[2],funcao_objetivo))
    b.append(crossover(a[2], a[3],funcao_objetivo))
    b.append(crossover(a[1], a[3],funcao_objetivo))
    b.append(crossover(a[0], a[2],funcao_objetivo))
    b.append(crossover(a[0], a[3],funcao_objetivo))

    #Calcula custo apenas dos validos
    custos_filhos = np.zeros(6, dtype=int)
    for i in range (0,6):
        v = valida(b[i])
        d = respeitaDisponibilidade(b[i], matriz_tempo_total,disp_oferta)
        if((d == True) and (v == True)):
            custos_filhos[i] = calculaCusto(b[i], matriz_custo)
        else:
            custos_filhos[i] = 1000000

    #pega o menor valor dos filhos e insere nos pais
    quantidades_validos  = np.where(custos_filhos < 1000000)[0]

    if (len(quantidades_validos) > 0):
        for i in range (0,len(quantidades_validos)):
            if(custos_pais[np.argmax(custos_pais)] >  custos_filhos[quantidades_validos[i]]):
                a[np.argmax(custos_pais)] = b[quantidades_validos[i]]

    for i in range (0,4):
        if((valida(a[i]) == True)  and (respeitaDisponibilidade(a[i],matriz_tempo_total,disp_oferta) == True) and (validaFO(a[i], funcao_objetivo) == True) ):
            custos_pais[i] = calculaCusto(a[i], matriz_custo)
        else:
            custos_pais[i] = 1000000

    # a cada 5 iterações muta os pais
    if ((j % 7) == 0):
        a[np.argmin(custos_pais) - 1] = mutacao(a[np.argmin(custos_pais) - 1],funcao_objetivo)
        a[np.argmin(custos_pais) - 2] = mutacao(a[np.argmin(custos_pais) - 2],funcao_objetivo)
        a[np.argmin(custos_pais) - 3] = mutacao(a[np.argmin(custos_pais) - 3],funcao_objetivo)

    menor = np.argmin(custos_pais)

s0 = a[menor]
valor = int(calculaCusto(s0, matriz_custo))
print(valor)

sBest = s0
bestCandidate = s0
tabuList = []
tabuList.append(s0)
print("COMECOU")

for i in range (0,3000):
    passoAleatorio = random.randint(1, 7)
    sNbhd = getNbhd(bestCandidate,funcao_objetivo,passoAleatorio)
    bestCandidate = sNbhd[0]
    for sCandidate in sNbhd:
        custoCandidate = calculaCusto(sCandidate, matriz_custo)
        custoBest      = calculaCusto(bestCandidate, matriz_custo)
        if((isInList(sCandidate.flatten(), tabuList) == False) and (custoCandidate < custoBest) and (respeitaDisponibilidade(sCandidate, matriz_tempo_total,disp_oferta) == True) and (valida(sCandidate) == True)):
            bestCandidate = sCandidate
    custoBest  = calculaCusto(bestCandidate, matriz_custo)
    custosBest = calculaCusto(sBest, matriz_custo)
    tabuList.append(bestCandidate.flatten())
    if(custoBest < custosBest):
        sBest = bestCandidate
    if(len(tabuList) > 20):
        del tabuList[0]

print(i,int(custosBest),"TABU")

#print(j, custos_pais[menor], custos_pais,"GA",  respeitaDisponibilidade(a[menor], matriz_tempo_total,disp_oferta))
finish = time.perf_counter()
print(f'Finished in {round(finish-start, 2)} second(s)')
