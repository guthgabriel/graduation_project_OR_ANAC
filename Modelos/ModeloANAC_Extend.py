from pyomo.core.base import misc
import pyomo.environ as pyo
from pyomo.environ import *
from pyomo.opt import SolverFactory
from numpy.lib.function_base import select
import pandas as pd
import time

#----------------- LEITURA DOS DADOS DO EXCEL (DISPONIBILIDADE, ARCOS, ATIVIDADE, OFERTA, DEMANDA) ----------------
inic_cm = time.time()
ef = pd.ExcelFile('Instancia/InstanciaB2.xlsx')
disponibilidade = pd.read_excel(ef, 'Disponibilidade - PREENCHER', header=1, usecols=['NOME', 'UF',  'DISPONIBILIDADE'])
arcos           = pd.read_excel(ef, 'Arcos',                       header=1, usecols=['ORIGEM_ARCO', 'DESTINO_ARCO', 'CUSTO', 'TEMPO'])
atividade       = pd.read_excel(ef, 'Atividades',                  header=1, usecols=['GRUPO_A', 'DURACAO', 'EQUIPE'])
oferta          = pd.read_excel(ef, 'Atividades',                  header=1, usecols=['SERVIDOR',  'GRUPO_P'])
nos             = pd.read_excel(ef, 'Arcos',                       header=1, usecols=['NOS', 'ORIGEM_NO', 'DESTINO_NO'])
demanda         = pd.read_excel(ef, 'Demanda - PREENCHER',         header=1, usecols=['PERIODO', 'MISSAO', 'ATIVIDADE', 'AEROPORTO' ])

#----------------- FAZENDO A LIMPEZA DOS DADOS QUE NÃO SERÃO UTILIZADOS NO MODELO POR NÃO APARECER NA DEMANDA -------------

disponibilidade  = disponibilidade[(disponibilidade['DISPONIBILIDADE'] > 0)]
oferta           = oferta.where((oferta['GRUPO_P'].isin(demanda['ATIVIDADE'].values) == True)).dropna()
oferta           = oferta.where((oferta['SERVIDOR'].isin(disponibilidade['NOME'].values) == True)).dropna() 
disponibilidade  = disponibilidade.where((disponibilidade['NOME'].isin(oferta['SERVIDOR'].values) == True)).dropna()
arcos            = arcos.where((arcos['ORIGEM_ARCO'].isin(disponibilidade['UF'].values) == True )).dropna()
arcos            = arcos.where((arcos['DESTINO_ARCO'].isin(demanda['AEROPORTO'].values) == True )).dropna()
atividade        = atividade.where(atividade['GRUPO_A'].isin(demanda['ATIVIDADE'].values) == True).dropna()

#----------------- CRIANDO AS LISTAS DE PESSOA, GRUPO, ORIGEM, DESTINO ATIVOS ----------------

pessoa = disponibilidade['NOME'].unique()
grupo = atividade['GRUPO_A'].dropna().values
origem = disponibilidade['UF'].unique()
destino = demanda['AEROPORTO'].unique()
periodo = [1]
missao = list(range(1,len(demanda)+1))

#print(len(pessoa))
#print(len(grupo))
#print(len(origem))
#print(len(destino))
#print(len(missao))
#----------------- TRANSFORMANDO A TABELA DE DEMANDAS EM UM DICIONÁRIO ----------------

existe_missao = demanda[['MISSAO', 'ATIVIDADE']]
nopegr = demanda[['PERIODO', 'MISSAO', 'ATIVIDADE', 'AEROPORTO']]
demanda = demanda.set_index(['PERIODO', 'MISSAO', 'ATIVIDADE', 'AEROPORTO'])
demanda = demanda.to_dict('index')
demanda = dict.fromkeys(demanda,1)

#----------------- CRIANDO O DICIONÁRIO DE PERIODO/MISSAO/GRUPO/DESTINO/PESSOA ATIVOS ----------------

nopegr = pd.merge(nopegr, oferta[['SERVIDOR','GRUPO_P']], how = 'inner', left_on = 'ATIVIDADE', right_on = 'GRUPO_P').drop(columns= 'GRUPO_P')
nopegr = nopegr.set_index(['PERIODO', 'MISSAO', 'ATIVIDADE', 'AEROPORTO', 'SERVIDOR'])
nopegr = nopegr.to_dict('index')

#----------------- CRIANDO O DICIONÁRIO DE PESSOA/GRUPO ATIVO ----------------

pg_ativo = oferta.set_index(['SERVIDOR','GRUPO_P'])
pg_ativo = pg_ativo.to_dict('index')

#----------------- CRIANDO O DICIONÁRIO DE PESSOA/GRUPO/UF ATIVO ----------------

pgo_ativo = oferta[['SERVIDOR','GRUPO_P']]
pgo_ativo = pd.merge(pgo_ativo, disponibilidade[['NOME','UF']], how = 'inner', left_on = 'SERVIDOR', right_on ='NOME', suffixes = ('UF'))
pgo_ativo = pgo_ativo[['NOME', 'GRUPO_P', 'UF']]
pgo_ativo = pgo_ativo.set_index(['NOME', 'GRUPO_P', 'UF'])
pgo_ativo = pgo_ativo.to_dict('index')
pgo_ativo = dict.fromkeys(pgo_ativo,10)

for nome, value in pgo_ativo.items():
    if 'Dummy' in nome[0]:
        pgo_ativo[nome] = 100

#----------------- CRIANDO O DICIONÁRIO DE PESSOA/GRUPO/MISSAO ATIVO ----------------

pgm = oferta[['SERVIDOR','GRUPO_P']]
pgm = pd.merge(pgm, existe_missao, how = 'inner', left_on = 'GRUPO_P', right_on = 'ATIVIDADE').drop(columns = ['ATIVIDADE'])
pgm = pgm.set_index(['SERVIDOR', 'GRUPO_P', 'MISSAO'])
pgm = pgm.to_dict('index')

#----------------- CRIANDO O DICIONÁRIO DAS ATIVIDADES (DURAÇÃO E EQUIPE) ATIVAS ----------------

dado_grupo = atividade.set_index(['GRUPO_A'])
dado_grupo = dado_grupo.to_dict('index')

#----------------- CRIANDO O DICIONÁRIO DOS ARCOS (CUSTO E TEMPO) ----------------

arcos = arcos.set_index(['ORIGEM_ARCO','DESTINO_ARCO'])
arcos = arcos.to_dict('index')

#----------------- CRIANDO O DICIONÁRIO DE DISPONIBILIDADE DE CADA PESSOA ----------------

disponibilidade = disponibilidade.set_index(['NOME'])
disponibilidade = disponibilidade.to_dict('index')

#----------------- CRIANDO O MODELO NA BIBLIOTECA PYOMO -----------------

model = ConcreteModel()

model.oferta = Param(pessoa, grupo, origem, initialize = pgo_ativo, default = 0)

model.alocado_geral = Var(periodo, arcos, pessoa, domain = NonNegativeReals, bounds = (0,1))
model.alocado = Var(periodo, arcos, pgm, domain = PositiveReals)
model.atendida = Var(nopegr, domain = Binary)
model.tempo_utilizado = Var(periodo, pessoa, domain = PositiveReals)

def FuncaoObjetivo(model):
    return sum(model.alocado_geral[t,i,j,p] * arcos[i,j]['CUSTO'] * 2
        for t in periodo 
        for i,j in arcos
        for p in pessoa
        if i == disponibilidade[p]['UF'])

model.obj = Objective(rule = FuncaoObjetivo, sense = minimize)

def constr_oferta(model, p, g, i):
    return sum(model.alocado[t,o,d,a,gr,m] for t in periodo for o,d in arcos if i == o for a,gr,m in pgm if p == a and g == gr) <= model.oferta[p,g,i]

model.constr_o = Constraint(pgo_ativo, rule = constr_oferta)

def constr_atendida(model, t, k, g, j, p):
    return sum(model.alocado[t,o,d,p,g,k] for o,d in arcos if o == disponibilidade[p]['UF'] if d == j) == model.atendida[t,k,g,j,p]

model.constr_at = Constraint(nopegr, rule = constr_atendida)

def constr_demanda(model, t, k, g, j):
    return sum(model.atendida[t,m,gr,d,p] for t, m, gr, d, p in nopegr if m == k and gr == g and d == j) == dado_grupo[g]['EQUIPE']*demanda[t,k,g,j]

model.constr_d = Constraint(demanda, rule = constr_demanda)

def constr_tempo(model, t, p):
    return sum(model.atendida[t,k,g,j,a] * dado_grupo[g]['DURACAO'] for t,k,g,j,a in nopegr if a == p) \
        + sum(model.alocado_geral[t,i,j,p] * arcos[i,j]['TEMPO'] * 2 for i,j in arcos if i == disponibilidade[p]['UF']) \
        == model.tempo_utilizado[t,p]

model.constr_t = Constraint(periodo, pessoa, rule = constr_tempo)

def constr_disponibilidade (model, t, p):
    return model.tempo_utilizado[t,p] <= disponibilidade[p]['DISPONIBILIDADE']

model.constr_dis = Constraint(periodo, pessoa, rule = constr_disponibilidade)

def constr_alocacao (model, t,i,j,p,g,k):
    if i == disponibilidade[p]['UF']:
        return model.alocado_geral[t,i,j,p] >= model.alocado[t,i,j,p,g,k]
    else:
        return Constraint.Skip

model.constr_al = Constraint(periodo, arcos, pgm, rule = constr_alocacao)

term_cm = time.time()

solver = SolverFactory('gurobi').solve(model, timelimit = 1800).write()

term_rm = time.time()
print(pyo.value(model.obj))
print('o tempo foi:', term_rm - inic_cm)

'''
for v in model.component_objects(Var, active=True):
    print ("Variable component object",v)
    if str(v) == 'atendida':
        for index in v:
            if v[index].value > 0:
                print ("   ", index, v[index].value)
    if str(v) == 'alocado_geral':
        for index in v:
            if v[index].value == 1:
                print ("   ", index, v[index].value)
    if str(v) == 'tempo_utilizado':
        for index in v:
            if v[index].value > 0:
                print ("   ", index, v[index].value)'''