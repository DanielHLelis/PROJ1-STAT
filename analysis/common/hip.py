import os
import json
import copy

import numpy as np
import scipy.stats as st
import sympy as sp

from .models import tnbinom


class Sim(dict):
    def __init__(self, content={}) -> None:
        # Carregando e salvando os dados da simulação como um dicionário
        super().__init__(Sim.__prepare_content(content))

    def pmf(self, x: int) -> float:
        return float(self['pmf'][x])

    def cdf(self, x: int) -> float:
        return float(self['cdf'][x])

    @staticmethod
    def __prepare_content(content):
        # Copia profunda dos dados (demora mais, mas é mais seguro)
        #sim = copy.deepcopy(content)
        sim = content

        sim['name'] = f"n = {sim['configs']['n']}, p0 = {sim['configs']['p0']}, s0 = {sim['configs']['s0']}"

        # Criando uma lista ordenada de cada simulação
        sim['sorted'] = list(sorted(sim['results']))

        # Calculando a pmf
        sim['freq'] = [0] * (sim['sorted'][-1] + 1)
        sim['pmf'] = [0.0] * (sim['sorted'][-1] + 1)
        p_per_elem = 1 / len(sim['sorted'])

        for x in sim['sorted']:
            sim['pmf'][x] += p_per_elem
            sim['freq'][x] += 1  # calculando frequências

        # Calculando a cdf
        sim['cdf'] = [0] * (sim['sorted'][-1] + 1)

        for i in range(1, len(sim['pmf'])):
            sim['cdf'][i] = sim['pmf'][i] + sim['cdf'][i - 1]

        # Normalizando os resultados com np e realizando cálculos útes
        # N = len(sim['results'])
        sim['results_np'] = np.asarray(sim['sorted'])
        sim['mean'] = np.mean(sim['results_np'])
        sim['std'] = np.std(sim['results_np'], ddof=1)
        sim['normalized'] = (sim['results_np'] - sim['mean']) / (sim['std'])
        
        width = 2
        sim['bar_freq'] = [sum(sim['freq'][i: i + width]) for i in range(0, sim['trial_count'], width)]
        sim['bar_pmf'] = [sum(sim['pmf'][i: i + width]) for i in range(0, sim['trial_count'], width)]

        sim['bar_x'] = sim['sorted']
        sim['bar_y'] = sim['pmf']

        return sim


    def condense_freq (self, depth : int = 1):
        N = 2 ** depth

        self['bar_x'] = [x[0] for x in [self['sorted'][i:i + N] for i in range(0, len(self['sorted']), N)]]
        self['bar_y'] = [sum(x) for x in [self['pmf'][i:i + N] for i in range(0, len(self['pmf']), N)]]

        return copy.deepcopy((self['bar_x'], self['bar_y']))

        
    # Agrupa frequências
    def group_freq(self, width: int = 5) -> list:
        bar_freq = [sum(self['freq'][i: i + width]) for i in range(0, self['trial_count'], width)]
        bar_pmf = [sum(self['pmf'][i: i + width]) for i in range(0, self['trial_count'], width)]

        self['bar_freq'] = bar_freq
        self['bar_pmf'] = bar_pmf
 
        return bar_freq


    # Distribui as frequências para atingir uma frequencia mínima não nula
    def distribute_freq(self, min_freq=5):
        tc = self['trial_count']  # trial count
        fq = self['freq']
        table = []
        last_width = 0

        for width in range(1, tc):
            last_width = width
            table = self.group_freq(width)
            if min([x for x in table if x > 0]) >= min_freq:
                break

        self['freq_table'] = table
        return (last_width, table)

    # Retorna o valor crítico para o test ks.

    def ks_rc(self, ns: float):
        N = self['trial_count']

        suported_ns = [0.2, 0.1, 0.05, 0.01]
        base_value = [1.07, 1.22, 1.36, 1.63]

        try:
            base_value = base_value[suported_ns.index(ns)]
        except:
            raise Exception(
                'Nível de significância não suportado, ecolha um entre: ' + str(suported_ns))

        if 35 >= N:
            raise Exception(
                'O tamanho amotral da simulação é pequeno demais. Ele deve ser superior a 35.')

        return base_value / np.sqrt(N)

    @staticmethod
    def load_sims(dir_name, datasets_path='../datasets/'):
        target_dir = os.path.join(datasets_path, dir_name)
        sims = []
        for target in os.listdir(target_dir):
            target_path = os.path.join(target_dir, target)
            if not os.path.isfile(target_path):
                continue

            if target.endswith('.json'):
                with open(target_path, 'r') as fp:
                    sims.append(Sim(json.load(fp)))

        return sims


class Model:

    def __init__(self, n: int, s0: int, p0: float) -> None:
        # Configurações
        self.n = int(n)  # numero de máquinas
        self.s0 = int(s0)  # número de máquinas reservas
        self.p0 = float(p0)  # probabilidade de uma máquina quebrar em um turno
        self.configs = {
            'n': self.n,
            'p0': self.p0,
            's0': self.s0,
            'tr': 0,
            'beta': 0,
        }

        # Criando uma distribuição.
        self.tnbinom = tnbinom
        self.dist = st.nbinom(self.s0 + 1, self.p0)
        self.E = self.ppf(0.5)
        self.not_p0 = 1 - self.p0

        # Expressões
        k, t, i, n, s, p = sp.symbols("k t i n s p")
        self.EXP = {
            'cdf': sp.betainc_regularized(s + 1, k + 1, 0, p),
        }

        self.exp = {
            'cdf': self.EXP['cdf'].subs({'s': self.s0, 'p': self.p0}),
        }

        # Funções lambda úteis
        self.lambdas = {
            'cdf': sp.lambdify('k', self.exp['cdf']),
        }

    @property
    def mean(self):
        return 0.5 + self.tnbinom.mean(self.n, self.s0, self.p0)

    def ppf(self, x: float):
        return (self.dist.ppf(x) + self.s0) / self.n

    # pmf : probability mass function
    def quick_pmf(self, x: int) -> float:
        return self.cdf(x) - self.cdf(x - 1) if x > 0 else 0.0

    # cdf : cumulative distribution function
    def quick_cdf(self, x: int) -> float:
        return self.lambdas['cdf'](x * self.n)

    # pmf : probability mass function
    def pmf(self, x: int) -> float:
        return self.tnbinom.pmf(x, self.n, self.s0, self.p0)

    # cdf : cumulative distribution function
    def cdf(self, x: int) -> float:
        return self.tnbinom.cdf(x, self.n, self.s0, self.p0)

    # Realiza o teste ks
    def kstest(self, data, quick=True):
        # Se data for uma lista de simulações, faça o teste ks para cada uma delas
        if isinstance(data, list):
            return [self.kstest(sim) for sim in data]

        # Se data for uma simulação apenas,
        sim = data

        # variáveis relevantes
        distancia_max = [0, 0]
        x_anterior = 0

        cdf_func = self.quick_cdf if quick else self.cdf

        # iterando por cada dado x
        for x in sim['sorted']:
            distancia = [0, 0]  # distancia de cada iteração

            cdf_val = cdf_func(x)
            distancia[0] = abs(cdf_val - sim['cdf'][x])
            distancia[1] = abs(cdf_val - sim['cdf'][x_anterior])
            x_anterior = x

            distancia_max[0] = max(distancia_max[0], distancia[0])
            distancia_max[1] = max(distancia_max[1], distancia[1])

        return max(distancia_max)
