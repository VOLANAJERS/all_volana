#!/usr/bin/env python
# coding: utf-8

# In[2]:


from datetime import datetime, timedelta
import pandas as pd 
import datetime as dt
import fnmatch
import os
import pymysql
from sqlalchemy import create_engine
import sys
import json
import numpy as np
import warnings
import re
from datetime import datetime
from tqdm import tqdm
from asignarTasa import ajustarTasa
warnings.filterwarnings('ignore')


# In[3]:
def getMarginalRentabilidad(d):

    marginales, rentabilidades, ganacias = [], [], []
    marginales_pedidas, rentabilidades_pedidas, ganacias_pedidas = [], [], []
    for _, row in d.iterrows():
        marginal, rentabilidad, ganancia = getVals_tasa(X = row['monto_autorizado'], 
                                 d = 16, 
                                 t = row['tasa_minima']/100, 
                                 pc = row['perdida_estimada']/100, 
                                 miembros = d.shape[0])
        marginales.append(marginal)
        rentabilidades.append(rentabilidad)
        ganacias.append(ganancia)

        marginal, rentabilidad, ganancia = getVals_tasa(X = row['monto_solicitado'], 
                                 d = 16, 
                                 t = row['tasa_pedida']/100, 
                                 pc = row['perdida_estimada']/100, 
                                 miembros = d.shape[0])

        marginales_pedidas.append(marginal)
        rentabilidades_pedidas.append(rentabilidad)
        ganacias_pedidas.append(ganancia)
        
    return sum(marginales), sum(marginales) / sum(ganacias), sum(marginales_pedidas), sum(marginales_pedidas) / sum(ganacias_pedidas) 

def getVals_tasa(X, d, t, pc, miembros = 6):
    if t == 0 or X == 0:
        return (0,0,0)
    fijos = (20.6 * d) / miembros
    originacion = 20.42 / miembros
    fondeo = (0.20/52) * X * d / miembros
    perdida_cosecha = abs(pc) * X 

    costos = fijos + originacion + fondeo + perdida_cosecha

    # ==============

    pagado = lambda X, t, d: ( (X*t*(1+t)**d) / (- 1 + (1+t)**d) ) * d

    t_semanal_con_iva = (t/52)*1.16
    total_pagado = pagado(X, t_semanal_con_iva, d)

    ingresos_intereses = total_pagado - X

    seguros = {4_000 : 26, 21_000 : 29, 51_000 : 30, np.inf: 31}

    ingreso_seguro = 0.0

    key_ant = 0
    for s in seguros.keys():
        if X < s and X > key_ant:
            ingreso_seguro = seguros[s]

        key_ant = s

    marginal = ingresos_intereses + ingreso_seguro - costos

    rentabilidad = marginal / ingresos_intereses

    # Averiguar cómo ajustar la tasa
    tasa_ajustada = t
    
    return marginal, rentabilidad, ingresos_intereses + ingreso_seguro


def setcut_prob(p, grupo_ = True):
    p = p*100
    cuts = np.array(sorted([100, 81.09, 72.06, 63.19, 54.27, 45.11, 36.10, 27.47, 18.17, 9.05, 0.00]))
    cosechas = np.array(sorted([1.54, 3.4, 4.97, 7.38, 10.69, 11.87, 12.35, 12.68, 20.33, 22.69], reverse = False))
    
    #cuts = np.array(sorted([1, 0.9919, 0.975, 0.953, 0.9196, 0.8717, 0.7832, 0.6737, 0.5072, .2738]))*100
    #cosechas = np.array(sorted([2.31, 2.63, 3.1, 3.12, 3.94, 4.2, 4.33, 5.15, 5.71, 59.82], reverse = True))
    
    for cut in cuts:
        if cut > p:
            break
            
    grupo = np.where(cuts == cut)[0][0] 
    if grupo_:
        return grupo
    else:
        return cosechas[grupo - 1]
    
def levenshtein_distance(word1, word2):
    len1, len2 = len(word1), len(word2)
    
    # Crear una matriz para almacenar las distancias parciales
    dp = [[0] * (len2 + 1) for _ in range(len1 + 1)]

    # Inicializar la primera fila y columna
    for i in range(len1 + 1):
        dp[i][0] = i
    for j in range(len2 + 1):
        dp[0][j] = j

    # Calcular las distancias parciales
    for i in range(1, len1 + 1):
        for j in range(1, len2 + 1):
            cost = 0 if word1[i - 1] == word2[j - 1] else 1
            dp[i][j] = min(dp[i - 1][j] + 1,      # Eliminación
                           dp[i][j - 1] + 1,      # Inserción
                           dp[i - 1][j - 1] + cost)  # Sustitución

    # El resultado final está en la esquina inferior derecha de la matriz
    return dp[len1][len2]

def encontrar_primer_numero(cadena):
    patron = re.compile(r'\d+')
    coincidencias = patron.findall(cadena)
    
    if coincidencias:
        return int(coincidencias[0])
    else:
        return -1
    

def calcular_edad(fecha_nacimiento):
    # Obtener la fecha actual
    fecha_actual = datetime.now()

    # Calcular la diferencia entre la fecha actual y la fecha de nacimiento
    diferencia = fecha_actual - fecha_nacimiento

    # Extraer la parte de los años de la diferencia
    edad_en_anios = diferencia.days // 365

    return edad_en_anios


# In[14]:
def getDataFrame(data, prospectos_ruta):
    """
    In:
        data[dataFrame] - con tres columnas: id_distriuidor, monto_solicitado, tasa_pedida
        prospectos_ruta[str] - ruta del archivo actual de prospectos
    """


    # In[15]:


    data_prospectos = pd.read_csv("./data/prospectos_riesgo_12_22_23.csv")
    data_prospectos['perdida_estimada'] = data_prospectos.probabilidad.apply(setcut_prob, grupo_ = False)
    data_prospectos = data_prospectos[data_prospectos.id_distribuidor.isin(data.id_distribuidor)]

    
    cnx = pymysql.connect(host='159.89.90.197', port = 3306, user='antonio_diaz', passwd="4nT0ni_0.dZ",
                           charset='utf8',db = 'volana')

    cursor = cnx.cursor()
    sql = f"""
    SELECT * FROM
    (select id, capacidad_pago_semanal
           from demograficos_distribuidores 
    UNION
    select id, capacidad_pago_semanal
           from cc_prospectos_demograficos
    ) as pen
     where
    pen.id in ({", ".join(data_prospectos.id_distribuidor.astype(str).unique())})
    """
    cursor.execute(sql)
    capacidad_pago = cursor.fetchall()
    capacidad_pago = pd.DataFrame(capacidad_pago, columns=[i[0] for i in cursor.description])
    capacidad_pago.rename(columns={"id" : 'id_distribuidor'}, inplace=True)
    capacidad_pago.id_distribuidor = capacidad_pago.id_distribuidor.astype(int)
    data_prospectos = data_prospectos.merge(capacidad_pago, on = 'id_distribuidor')
    cnx.close()

    data_prospectos = data_prospectos.drop_duplicates(subset=['id_distribuidor'])
    
    d = 16
    t_max = 1.47
    resultado = []

    for row in data_prospectos.iterrows():
        pc = row[1]['perdida_estimada']/100
        c  = row[1]['capacidad_pago_semanal']
        id_ = int(row[1]['id_distribuidor'])
        alguno_paso = 0
        for X in range(10_0000, 4_000, -1_000):
            estatus, resultado_txt, tasa_minima, tasa_sugerida = ajustarTasa(X, t_max, d, c, pc)
            if estatus:
                resultado.append([id_, resultado_txt, X, tasa_minima, tasa_sugerida])
                alguno_paso = 1
                #break
        if alguno_paso == 0:
            _, resultado_txt, _, _ = ajustarTasa(X, t_max, d, c, pc)
            resultado.append([id_, resultado_txt, 0, 0, 0])

    resultado = pd.DataFrame(resultado)

    resultado.columns = ["id_distribuidor","resultado_txt","monto_autorizado", "tasa_minima","tasa_sugerida"]
    
    data_prospectos_original = resultado.merge(data_prospectos[['id_distribuidor', 'probabilidad', 'grupo_riesgo']], on = 'id_distribuidor')
    
    
    data_prospectos = data_prospectos_original.groupby("id_distribuidor").agg({"monto_autorizado": max, 
                                                  "tasa_sugerida":max,
                                                  "tasa_minima": min,
                                                  "probabilidad" : max,
                                                  "grupo_riesgo": max})
    data_prospectos = data_prospectos.reset_index()



    # In[17]:


    ids = ", ".join(data.id_distribuidor.unique().astype(str))


    # In[18]:


    data_prospectos = data_prospectos.merge(data, on = 'id_distribuidor')


    # In[19]:


    for i, row in data_prospectos.iterrows():
        if row['monto_autorizado'] > row['monto_solicitado']:
            entro = False
            for _, k in data_prospectos_original.query(f"id_distribuidor == {row['id_distribuidor']}").iterrows():

                if k['monto_autorizado'] <= row['monto_solicitado']:
                    data_prospectos.at[i, 'tasa_minima'] = k['tasa_minima']
                    entro = True
                    break

            if not entro:
                data_prospectos.at[i, 'tasa_minima'] = 147


            data_prospectos.at[i, 'monto_autorizado'] = row['monto_solicitado']


    cnx = pymysql.connect(host='159.89.90.197', port=3306, user='antonio_diaz', passwd="4nT0ni_0.dZ",
                               charset='utf8',db = 'volana')

    cursor = cnx.cursor()
    sql = f"""
    SELECT * FROM
    (select id, fecha_nacimiento,
           ocupacion, estado, delegacion, calle_y_numero,
            sexo,
           tiempo_vivienda, ingreso_neto, experiencia,
           tipo_negocio, tiempo_op_negocio,capacidad_pago_semanal
           from demograficos_distribuidores 
    UNION
    select id, fecha_nacimiento,
           ocupacion, estado, delegacion, calle,
           sexo,
           tiempo_vivienda, ingreso_neto, experiencia,
           tipo_negocio, tiempo_op_negocio, capacidad_pago_semanal
           from cc_prospectos_demograficos
    ) as pen
     where
    pen.id in ({ids})
    """
    cursor.execute(sql)
    data_demo = cursor.fetchall()
    data_demo = pd.DataFrame(data_demo, columns=[i[0] for i in cursor.description])
    data_demo.rename(columns={"id" : 'id_distribuidor'}, inplace=True)
    data_demo.id_distribuidor = data_demo.id_distribuidor.astype(int)

    cursor = cnx.cursor()
    sql = f"""
    select idCliente as 'id_distribuidor', 
    valor as 'fico' ,
    saldoVencidoPeorAtraso,
    clavePrevencion
    from cc_prospectos_scores as ps
    left join cc_prospectos_folios as pf on pf.folioConsulta = ps.folioConsulta 
    left join cc_prospectos_creditos as pc on pc.folioConsulta = ps.folioConsulta 
    where idCliente in ({ids})
    """
    cursor.execute(sql)
    data_fico = cursor.fetchall()

    data_fico = pd.DataFrame(data_fico, columns=[i[0] for i in cursor.description])

    cnx.close()


    # In[235]:


    data_fico.clavePrevencion = data_fico.clavePrevencion.fillna("-")


    temp1 = pd.DataFrame(data_fico.query("clavePrevencion == '-'").groupby("id_distribuidor").saldoVencidoPeorAtraso.sum()).reset_index()
    temp2 = pd.DataFrame(data_fico.query("clavePrevencion != '-'").groupby("id_distribuidor").saldoVencidoPeorAtraso.sum()).reset_index()

    temp2.rename(columns={"saldoVencidoPeorAtraso": "saldoVencidoConClaves"}, inplace=True)

    data_fico = temp1.merge(temp2, on = 'id_distribuidor')


    # In[237]:


    data_prospectos = data_prospectos.merge(data_demo, on='id_distribuidor', how = 'left')
    data_fico.id_distribuidor = data_fico.id_distribuidor.astype(int)
    data_prospectos = data_prospectos.merge(data_fico, on='id_distribuidor', how = 'left')


    # In[238]:


    # Vive en la misma casa
    data_prospectos = data_prospectos.reset_index(drop=True)
    vive_misma_casa = []
    for calle1 in data_prospectos.calle_y_numero:
            if sum(data_prospectos.calle_y_numero == calle1) > 1:
                vive_misma_casa.append("Si")
            else:
                vive_misma_casa.append("No")



    # In[239]:


    data_prospectos["vive_en_misma_casa"] = vive_misma_casa


    # In[240]:


    data_prospectos.calle_y_numero = data_prospectos.calle_y_numero.str.lower()


    # **Limpiando los datos**

    # In[241]:


    data_prospectos.tiempo_vivienda = data_prospectos.tiempo_vivienda.apply(encontrar_primer_numero)
    data_prospectos.tiempo_vivienda = data_prospectos.tiempo_vivienda.astype(int)
    data_prospectos.fecha_nacimiento = pd.to_datetime(data_prospectos.fecha_nacimiento)
    data_prospectos.tipo_negocio = data_prospectos.tipo_negocio.str.upper()
    data_prospectos['edad'] = data_prospectos.fecha_nacimiento.apply(calcular_edad)
    data_prospectos.drop('fecha_nacimiento', axis = 1, inplace=True)


    data_prospectos['perdida_estimada'] = data_prospectos.probabilidad.apply(setcut_prob, grupo_ = False)


    data_prospectos = data_prospectos[['id_distribuidor', 'saldoVencidoPeorAtraso',
                       'saldoVencidoConClaves','grupo_riesgo', 'perdida_estimada',
                     'tasa_sugerida', 'tasa_minima',
                        'tipo_negocio', 'tiempo_op_negocio','ingreso_neto',
                       'capacidad_pago_semanal',  'vive_en_misma_casa', 'edad',
                    'monto_autorizado', 'monto_solicitado', 'tasa_pedida']]


    """
    marginales, rentabilidades = [], []
    marginales_pedidas, rentabilidades_pedidas = [], []
    for _, row in data_prospectos.iterrows():
        marginal, rentabilidad,_ = getVals_tasa(X = row['monto_autorizado'], 
                                 d = 16, 
                                 t = row['tasa_minima']/100, 
                                 pc = row['perdida_estimada']/100, 
                                 miembros = data_prospectos.shape[0])
        marginales.append(marginal)
        rentabilidades.append(rentabilidad)

        marginal, rentabilidad,_ = getVals_tasa(X = row['monto_solicitado'], 
                                 d = 16, 
                                 t = row['tasa_pedida']/100, 
                                 pc = row['perdida_estimada']/100, 
                                 miembros = data_prospectos.shape[0])

        marginales_pedidas.append(marginal)
        rentabilidades_pedidas.append(rentabilidad)


    # In[256]:


    data_prospectos['contribucion_marginal_modelo'] = marginales
    data_prospectos['contribucion_marginal_pedida'] = marginales_pedidas

    data_prospectos['rentabilidad_modelo'] = rentabilidades
    data_prospectos['rentabilidad_pedida'] = rentabilidades_pedidas
    """

    # In[257]:


    return data_prospectos


