#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
rentabilidad_obj = 0.4

def getVals_all(X, t_max, d, c, pc, print_ = False):
    tasas = []
    rentabilidades = []
    factible = []
    por_pagar_sem = []

    for t in range(75, int(t_max*100)+1, 1):
        
        total_pagado, pago_real_semanal, rentabilidad, tasa_ajustada = getVals( X = X, 
                                                                                d = d, 
                                                                                t = t/100, 
                                                                                pc = pc)


        tasas.append(t)
        rentabilidades.append(rentabilidad)

        factible.append( ((total_pagado / d) < c) * (rentabilidad >= rentabilidad_obj))
        
        por_pagar_sem.append(total_pagado / d)
        
        if print_:
            print(f"Tasa: {t} - \tpagado {total_pagado:.2f} - pagado por semana {total_pagado/d:.2f} - capacidad {c} - rentabilidad {rentabilidad:.3f}")

    tasas = np.array(tasas)
    rentabilidades = np.array(rentabilidades)
    por_pagar_sem = np.array(por_pagar_sem)
    
    return tasas, rentabilidades, por_pagar_sem


def getVals(X, d, t, pc):
    fijos = 20.6 * d
    originacion = 20.6
    fondeo = (0.20/52) * X * d
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

    marginal = ingresos_intereses - costos

    rentabilidad = marginal / ingresos_intereses

    cuanto_deberia_ganar_de_intereses = costos/(1 - rentabilidad_obj)

    cuanto_me_deberian_depagar = cuanto_deberia_ganar_de_intereses + X

    pago_real_semanal = cuanto_me_deberian_depagar / d

    # Averiguar cómo ajustar la tasa
    tasa_ajustada = t
    

    return total_pagado, pago_real_semanal, rentabilidad, tasa_ajustada


def find_tasa_fija(tasa_opt):
    tasas_fijas = [75, 80, 85, 90, 95, 100, 105, 110, 112, 115, 117, 120, 122, 127, 132, 137, 142, 147]
    for tf in tasas_fijas:
        if tf >= tasa_opt:
            return tf


# In[118]:


def ajustarTasa(X, t_max, d, c, pc):
    """
    In:
        X[float]: Monto solicitado del préstamo original
        t_max[float]: tasa anual máxima (regularmente 1.47)
        d[int]: número de semanas de duración del préstamo (regularmente 16)
        c[float]: capacidad de pago semanal (de las tablas ingestado)
        pc[float]: pérdida de cosecha estimada 
    Out:
        estatus[bool]: estatus del crédito - rechazo si False / aceptación si True
        tasa_minima[float] = tasa mínima rentable
        tasa_sugerida[float] = tasa óptima
        resultado_txt[str] = texto que describe el resultado
    """
    """
    10,000 --> False rechazado
    9,000 --> False
    8,000, ..., 5,000 -> Aprobado
        
    ID
    1 - 10,000  - RECHAZO
    1 - 9 ,000  - RECHAZO <-
    
    1 - 8 ,000  - ACEPTADO
    1 - 7 ,000  - ACEPTADO
    1 - 6 ,000  - ACEPTADO
    
    9,000, ..., 5,000
    """
    
    
    estatus       = False 
    tasa_minima   = 0.0
    tasa_sugerida = 0.0
    resultado_txt = ""


    tasas, rentabilidades, por_pagar_sem = getVals_all(X = X, 
                                                   t_max = t_max,
                                                   d = d,
                                                   c = c,
                                                   pc = pc,
                                                   print_ = False)

    factible_rentabilidad = (rentabilidades > rentabilidad_obj)
    factible_pago = (np.array(por_pagar_sem) < c)
    factible = factible_rentabilidad * factible_pago
    rentabilidades *= 100


    if factible.sum() != 0:

            tasa_minima = find_tasa_fija(min(tasas[factible]))
            tasa_sugerida = find_tasa_fija(max(tasas[factible]))

            resultado_txt = f"Tasa anual sugerida es de {tasa_sugerida}% con rentabilidad: {max(rentabilidades[factible]):.2f}% y pagando {max(por_pagar_sem[factible]):.2f}"
            resultado_txt += "\n"
            resultado_txt += f"Tasa anual mínima posible es de {tasa_minima}% con rentabilidad: {min(rentabilidades[factible]):.2f}% y pagando {min(por_pagar_sem[factible]):.2f}"
            estatus = True


    elif factible.sum() == 0:

        resultado_txt += f"No existe un intervalo factible, se rechaza el crédito\n"

        posibles_tasas = np.where((rentabilidades > 40))[0]
        if len(posibles_tasas) > 0:
            resultado_txt += f"El pago mínimo necesario para tener una rentabilidad del 40% es de: {por_pagar_sem[posibles_tasas[0]]:.2f}"
        else:
            resultado_txt += f"Su capacidad de pago no asegura tener una rentabilidad del 40%\n"

            resultado_txt += f"El pago semanal mínimo es de {min(por_pagar_sem):.2f} (con rentabilidad de {min(rentabilidades):.2f}%) y se tiene capacidad hasta {c}\n"

            resultado_txt += f"La rentabilidad máx alcanzada es de {max(rentabilidades):.2f}% (con pago de {max(por_pagar_sem):.2f}) y se tiene como objetivo {rentabilidad_obj*100}%"

    elif factible.sum() == len(factible):
        resultado_txt = f"Todas las tasas son viables, se asigna la mayor de {find_tasa_fija(max(tasas))}% anual"
        estatus = True
        tasa_minima = find_tasa_fija(min(tasas[factible]))
        tasa_sugerida = find_tasa_fija(max(tasas[factible]))

    return estatus, resultado_txt, tasa_minima, tasa_sugerida


# In[ ]:




