from pyomo.core.base import misc
from pyomo.core.base.piecewise import Bound
import pyomo.environ as pyo
from pyomo.environ import *
from pyomo.opt import SolverFactory
from numpy.lib.function_base import select
import pandas as pd
import numpy as np
import time

inic_cm = time.time()

ef = pd.ExcelFile('Instancia/InstanciaA2_resum.xlsx')

DEM = pd.read_excel(ef, 'DADOS', header = 0, usecols = ['MISSAO1', 'ATIVIDADE', 'DESTINO1', 'DURACAO', 'EQUIPE'], converters = {'MISSAO1': int}).dropna()
PD = pd.read_excel(ef, 'DADOS', header = 0, usecols = ['PESSOA1', 'DISPONIBILIDADE']).dropna()
ORIGENS = pd.read_excel(ef, 'DADOS', header = 0, usecols = ['ORIGENS']).dropna()
DESTINOS = pd.read_excel(ef, 'DADOS', header = 0, usecols = ['DESTINOS']).dropna()
ARCOS = pd.read_excel(ef, 'DADOS', header = 0, usecols = ['ORIGEM2', 'DESTINO2', 'CUSTO', 'TEMPO']).dropna()
ALOC = pd.read_excel(ef, 'DADOS', header = 0, usecols = ['PESSOA3', 'ORIGEM3', 'DESTINO3']).dropna()
ALOC_ATIV = pd.read_excel(ef, 'DADOS', header = 0, usecols = ['PESSOA4', 'ORIGEM4', 'DESTINO4', 'MISSAO4'], converters = {'MISSAO4': int}).dropna()

MISSAO = DEM['MISSAO1'].unique()
PESSOA = PD['PESSOA1'].unique()

ARCOS = ARCOS.set_index(['ORIGEM2', 'DESTINO2'])
ARCOS = ARCOS.to_dict('index')

DISPONIBILIDADE = PD.set_index(['PESSOA1'])
DISPONIBILIDADE = DISPONIBILIDADE.to_dict('index')

DEMANDA_MISSAO = DEM[['MISSAO1', 'DURACAO','EQUIPE']]
DEMANDA_MISSAO = DEMANDA_MISSAO.set_index(['MISSAO1'])
DEMANDA_MISSAO = DEMANDA_MISSAO.to_dict('index')

ALOC = ALOC.set_index(['PESSOA3', 'ORIGEM3', 'DESTINO3'])
ALOC = ALOC.to_dict('index')

AUXILIAR = ALOC_ATIV.set_index(['PESSOA4', 'ORIGEM4', 'DESTINO4', 'MISSAO4'])
AUXILIAR = AUXILIAR.to_dict('index')

ALOC_ATIV = ALOC_ATIV[['PESSOA4', 'ORIGEM4', 'MISSAO4']]
ALOC_ATIV = ALOC_ATIV.set_index(['PESSOA4', 'ORIGEM4', 'MISSAO4'])
ALOC_ATIV = ALOC_ATIV.to_dict('index')

model = ConcreteModel()

model.alocado_geral = Var(ALOC, domain = Reals, bounds = (0,1))
model.alocado_missao = Var(ALOC_ATIV, domain = Binary)

def FuncaoObjetivo(model):
    return sum(model.alocado_geral[p,o,d] * ARCOS[o,d]['CUSTO'] * 2
        for p,o,d in ALOC)

model.obj = Objective(rule = FuncaoObjetivo, sense = minimize)

def constr_demanda(model, m):
    return sum(model.alocado_missao[p,o,k] for p, o, k in ALOC_ATIV if k == m) == DEMANDA_MISSAO[m]['EQUIPE']

model.constr_d = Constraint(MISSAO, rule = constr_demanda)

def constr_tempo(model, p):
    return sum(model.alocado_missao[a,o,m]*DEMANDA_MISSAO[m]['DURACAO'] for a, o, m in ALOC_ATIV if a == p) \
        + sum(2*model.alocado_geral[a,o,d] * ARCOS[o,d]['TEMPO'] for a,o,d in ALOC if a == p) \
            <= DISPONIBILIDADE[p]['DISPONIBILIDADE']

model.constr_t = Constraint(PESSOA, rule = constr_tempo)

def constr_alocacao (model, p,o,d,m):
    return model.alocado_geral[p,o,d] >= model.alocado_missao[p,o,m]

model.constr_al = Constraint(AUXILIAR, rule = constr_alocacao)

solver = SolverFactory('gurobi').solve(model, tee = True, timelimit = 1800).write()#filename = 'Instancia/Resultados/B/B3/B3_resum_py_cplex.txt')

term_rm = time.time()
print(pyo.value(model.obj))
print('o tempo foi:', term_rm - inic_cm)

'''
for v in model.component_objects(Var, active=True):
    print ("Variable component object",v)
    if str(v) == 'alocado_missao':
        for index in v:
            if v[index].value > 0:
                print ("   ", index, v[index].value)
    if str(v) == 'alocado_geral':
        for index in v:
            if v[index].value > 0:
                print ("   ", index, v[index].value)
    if str(v) == 'tempo_utilizado':
        for index in v:
            if v[index].value > 0:
                print ("   ", index, v[index].value)'''