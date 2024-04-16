#!/usr/bin/env python
# coding: utf-8

# In[121]:


get_ipython().run_cell_magic('writefile', 'main.py', '\nimport streamlit as st\nimport pandas as pd\nimport numpy as np\nfrom AnalisisRiesgoRedesProspectos import getDataFrame, getMarginalRentabilidad\nfrom asignarTasa import ajustarTasa\n\n#num2curr = lambda x: "${:,.0f}".format(x)\nnum2curr = lambda x: "${:,.0f}".format(x) if x > 0 else "-"+("${:,.0f}".format(x)).replace("-","")\n\ndef getNewTasaMonto(monto_pedido, pc, c):\n        #pc = row[1][\'perdida_estimada\']/100\n        #c  = row[1][\'capacidad_pago_semanal\']\n        #id_ = int(row[1][\'id_distribuidor\'])\n    resultado = []\n    t_max = 1.47\n    d = 16\n    alguno_paso = 0\n    for X in range(100_000, 4_000, -1_000):\n        estatus, resultado_txt, tasa_minima, tasa_sugerida = ajustarTasa(X, t_max, d, c, pc)\n        if estatus:\n            resultado.append([resultado_txt, X, tasa_minima, tasa_sugerida])\n            alguno_paso = 1\n            #break\n    if alguno_paso == 0:\n        _, resultado_txt, _, _ = ajustarTasa(X, t_max, d, c, pc)\n        resultado.append([resultado_txt, 0, 0, 0])\n\n    resultado = pd.DataFrame(resultado)\n\n    resultado.columns = ["resultado_txt","monto_autorizado", "tasa_minima","tasa_sugerida"]\n    \n    \n    max_aut = resultado.monto_autorizado.max()\n\n    if max_aut > monto_pedido:\n        # el autorizado es mayor al pedido, busca el pedido\n        if monto_pedido in np.array(resultado.monto_autorizado):\n            temp = resultado.query(f"monto_autorizado == {monto_pedido}")\n            return temp.iloc[0][\'monto_autorizado\'], temp.iloc[0][\'tasa_minima\'] \n            # en caso de que sí este, pues dale ese\n        else:\n            # en caso de que no, dale ese ese con la máxima tasa\n            return monto_pedido, 147\n    else:\n        # en caso de que el autorizado sea menor, solo dale ese\n        return resultado.iloc[0][\'monto_autorizado\'], resultado.iloc[0][\'tasa_minima\'] \n    \ndef getData(edited_data_inicial): # ================================= AQUI ==============================\n    """\n    dudoso: None si se quiere carga inicial o [bool] si se quiere actualiza\n    """\n    data_output = getDataFrame(edited_data_inicial, "./data/prospectos_riesgo_12_22_23.csv")\n    data_output.id_distribuidor = data_output.id_distribuidor.astype(str) \n    data_output.drop(["tasa_sugerida"], axis = 1, inplace = True)\n    \n    if st.session_state[\'dudoso\'] == []:\n        st.session_state[\'dudoso\'] = [False] * data_output.shape[0]\n        \n    #print("Entré")\n    #print(st.session_state[\'dudoso\'])\n    #print(st.session_state[\'dudoso\'] == [])\n    #print(st.session_state["random_key"])\n    #print(st.session_state["from_restart"])\n    \n    #if dudoso == None:\n    if st.session_state[\'from_restart\'] == True:\n        print("Entrando en from restart")\n        data_output[\'dudoso\'] = False\n        return data_output\n    else:\n        print("Entrando en from update")\n        \n        dud = np.where(st.session_state[\'dudoso\'])[0]\n        cosechas = [1.54, 3.4, 4.97, 7.38, 10.69, 11.87, 12.35, 12.68, 20.33, 22.69]\n        for k in dud:\n            riesgo = int(data_output.loc[k, "grupo_riesgo"].replace("Canasta", ""))\n            riesgo = min(10, riesgo + 1)\n            data_output.at[k, \'grupo_riesgo\'] = f"Canasta {riesgo}"\n            data_output.at[k, \'perdida_estimada\'] = cosechas[max(0, riesgo - 1)]\n            data_output.at[k, \'capacidad_pago_semanal\'] *= 0.75\n\n\n            newmonto, newtasa = getNewTasaMonto(monto_pedido = data_output.loc[k, "monto_solicitado"],\n                                                pc = data_output.loc[k, "perdida_estimada"]/100,\n                                                c = data_output.loc[k, "capacidad_pago_semanal"])\n\n            data_output.at[k, \'monto_autorizado\'] = newmonto\n            data_output.at[k, \'tasa_minima\'] = newtasa\n            \n        data_output[\'dudoso\'] = st.session_state[\'dudoso\']\n    \n    data_output = data_output.set_index(\'id_distribuidor\')\n    \n    return data_output\n        \nst.set_page_config(layout="wide")\n\n# ================================================================\n# Variables de estado\n# ================================================================\nif "random_key" not in st.session_state:\n    st.session_state["random_key"] = 0\n    \nif \'dudoso\' not in st.session_state:\n    st.session_state[\'dudoso\'] = []\n    \nif \'from_restart\' not in st.session_state:\n    st.session_state[\'from_restart\'] = False\n    \nif \'data\' not in st.session_state:\n    st.session_state[\'data\'] = None\n    \nif \'data_inicial\' not in st.session_state:\n    st.session_state[\'data_inicial\'] = None\n    \nif \'edited_data\' not in st.session_state:\n    st.session_state[\'edited_data\'] = None\n    \n\ndef checkDataChanges():\n    #print("Edited en check changes:")\n    #print(st.session_state[\'edited_data\'])\n    #print(f"Asi inicia dudoso: {st.session_state[\'dudoso\']}")\n    st.session_state["random_key"] += 1\n    st.session_state[\'data\'] = getData(st.session_state[\'data_inicial\']).copy()\n    print("Entramos")\n\n# ================================================================\n    \nwith st.sidebar:    \n    page = st.selectbox(\n    \'Selecciona la página\',\n    (\'Análisis de riesgo de redes\',))\n    \nif page == \'Análisis de riesgo de redes\':\n    st.title("Análisis de riesgo de redes")\n    st.write("Actualizado al: 2024-01-05")\n\n    st.subheader("Carga la tabla de prospectos")\n    uploaded_file = st.file_uploader("Elige un archivo")\n    if uploaded_file is not None:\n        data = pd.read_csv(uploaded_file)\n        edited_data_inicial = st.data_editor(data)\n        st.session_state[\'data_inicial\'] = edited_data_inicial.copy()\n        \n        \n        st.subheader("Resumen de los prospectos")\n        #data_output = getData(edited_data_inicial)\n        \n        if st.session_state[\'data\'] is not None:\n            print("Desde la sesión")\n            st.session_state[\'edited_data\'] = st.data_editor(st.session_state[\'data\'], key=st.session_state["random_key"], \n                                        disabled= (\'id_distribuidor\', \'saldoVencidoPeorAtraso\', \'saldoVencidoConClaves\',\n           \'grupo_riesgo\', \'perdida_estimada\',\'tipo_negocio\', \'tiempo_op_negocio\', \'ingreso_neto\',\n           \'capacidad_pago_semanal\', \'vive_en_misma_casa\', \'edad\',\'monto_solicitado\'))\n        \n        else:\n            print("Desde normal")\n            data_output = getData(edited_data_inicial)\n            st.session_state[\'data\'] = data_output\n            \n            st.session_state[\'edited_data\'] = st.data_editor(data_output, key=st.session_state["random_key"], \n                                        disabled= (\'id_distribuidor\', \'saldoVencidoPeorAtraso\', \'saldoVencidoConClaves\',\n           \'grupo_riesgo\', \'perdida_estimada\',\'tipo_negocio\', \'tiempo_op_negocio\', \'ingreso_neto\',\n           \'capacidad_pago_semanal\', \'vive_en_misma_casa\', \'edad\',\'monto_solicitado\'))\n        \n        \n        edited_data = st.session_state[\'edited_data\']\n        \n        st.session_state[\'dudoso\'] = np.array(edited_data.dudoso)\n        print("\\n=====================================")\n        print(f"Dudo en código {st.session_state[\'edited_data\']}")\n        \n        \n        if st.button(\'Presiona dos veces para reiniciar\'):\n            #edited_data.update(data_output)\n            #st.session_state["random_key"] += 1\n            st.session_state[\'from_restart\'] = True\n            checkDataChanges()\n        \n        if st.button(\'Presiona dos veces para actualizar\'):\n            #st.session_state["random_key"] += 1\n\n            st.session_state[\'from_restart\'] = False\n            checkDataChanges()\n            #data_output = getData(edited_data_inicial, st.session_state[\'dudoso\'])\n        \n        \n        monto_solicitado_total = edited_data.monto_solicitado.sum()\n        monto_aut_total = edited_data.monto_autorizado.sum()\n\n        st.markdown("**Resumen de contribuciones**")\n\n        col1, col2, col3, col4 = st.columns(4)\n\n        marginal_modelo, rentabilidad_modelo, marginal_pedida, rentabilidad_pedida = getMarginalRentabilidad(edited_data)\n\n\n        col1.metric("Marginal", num2curr(marginal_modelo), num2curr(marginal_modelo - marginal_pedida))\n        col2.metric("Rentabilidad", f"{rentabilidad_modelo*100:.2f}%", f"{(rentabilidad_modelo - rentabilidad_pedida)*100:.2f}%")\n\n        col3.metric("Marginal pedida", num2curr(marginal_pedida))\n        col4.metric("Rentabilidad pedida", f"{rentabilidad_pedida*100:.2f}%")\n\n        st.markdown("**Resumen de riesgo**")\n        col1, col2, col3, col4 = st.columns(4)\n        tp = round(sum(edited_data.monto_solicitado * edited_data.tasa_minima) /\\\n                   edited_data.query("monto_autorizado > 0 ").monto_solicitado.sum(), 0)\n\n        riesgo_numero = edited_data.grupo_riesgo.str.replace("Canasta ","").astype(int)\n        rp = round(sum(edited_data.monto_solicitado * riesgo_numero) /\\\n                   monto_solicitado_total, 0)\n\n\n        col1.metric("Saldo Vencido con Claves", num2curr(edited_data.saldoVencidoConClaves.sum()))\n        col2.metric("Saldo Vencido", num2curr(edited_data.saldoVencidoPeorAtraso.sum()))\n        col3.metric("Monto solicitado", num2curr(monto_solicitado_total))\n        col4.metric("Monto propuesto", num2curr(monto_aut_total), num2curr(monto_aut_total - monto_solicitado_total))\n\n        col1_, col2_ = st.columns(2)\n        col1_.metric("Tasa ponderada", str(int(tp)) + "%" , str(int(tp - edited_data.tasa_pedida.mean()))+"%" )\n        col2_.metric("Riesgo ponderado", int(rp))\n')


# In[4]:


import pandas as pd


# In[7]:


from AnalisisRiesgoRedesProspectos import getDataFrame, getMarginalRentabilidad
from asignarTasa import ajustarTasa


# In[ ]:





# In[8]:


import numpy as np
import pandas as pd
data = pd.read_csv("./data/datos_red_ejemplo.csv")


# In[42]:


d_ = getDataFrame(data, "./data/prospectos_riesgo_12_22_23.csv")


# In[44]:


d_res = d_.copy()


# In[47]:


d_ = d_res.copy()


# In[50]:


d_res


# In[48]:


dud = np.where([False, True, True])[0]
cosechas = [1.54, 3.4, 4.97, 7.38, 10.69, 11.87, 12.35, 12.68, 20.33, 22.69]
for k in dud:
    riesgo = int(d_.loc[k, "grupo_riesgo"].replace("Canasta", ""))
    riesgo = min(10, riesgo + 1)
    d_.at[k, 'grupo_riesgo'] = f"Canasta {riesgo}"
    d_.at[k, 'perdida_estimada'] = cosechas[max(0, riesgo - 1)]
    d_.at[k, 'capacidad_pago_semanal'] *= 0.75
    
    
    newmonto, newtasa = getNewTasaMonto(monto_pedido = d_.loc[k, "monto_solicitado"],
                                        pc = d_.loc[k, "perdida_estimada"]/100,
                                        c = d_.loc[k, "capacidad_pago_semanal"])
    
    d_.at[k, 'monto_autorizado'] = newmonto
    d_.at[k, 'tasa_minima'] = newtasa
    


# In[49]:


d_
# está mal, hay que buscar el monto que nos pidió 


# In[46]:


def getNewTasaMonto(monto_pedido, pc, c):
        #pc = row[1]['perdida_estimada']/100
        #c  = row[1]['capacidad_pago_semanal']
        #id_ = int(row[1]['id_distribuidor'])
    resultado = []
    t_max = 1.47
    d = 16
    alguno_paso = 0
    for X in range(100_000, 4_000, -1_000):
        estatus, resultado_txt, tasa_minima, tasa_sugerida = ajustarTasa(X, t_max, d, c, pc)
        if estatus:
            resultado.append([resultado_txt, X, tasa_minima, tasa_sugerida])
            alguno_paso = 1
            #break
    if alguno_paso == 0:
        _, resultado_txt, _, _ = ajustarTasa(X, t_max, d, c, pc)
        resultado.append([resultado_txt, 0, 0, 0])

    resultado = pd.DataFrame(resultado)

    resultado.columns = ["resultado_txt","monto_autorizado", "tasa_minima","tasa_sugerida"]
    
    
    max_aut = resultado.monto_autorizado.max()

    if max_aut > monto_pedido:
        # el autorizado es mayor al pedido, busca el pedido
        if monto_pedido in np.array(res.monto_autorizado):
            temp = resultado.query(f"monto_autorizado == {monto_pedido}")
            return temp.iloc[0]['monto_autorizado'], temp.iloc[0]['tasa_minima'] 
            # en caso de que sí este, pues dale ese
        else:
            # en caso de que no, dale ese ese con la máxima tasa
            return monto_pedido, 147
    else:
        # en caso de que el autorizado sea menor, solo dale ese
        return resultado.iloc[0]['monto_autorizado'], resultado.iloc[0]['tasa_minima'] 
    
    #return resultado#resultado.iloc[0]['monto_autorizado'], resultado.iloc[0]['tasa_minima'] 


# In[41]:


getNewTasaMonto(monto_pedido = 4_000, pc = 0.04, c = 10_0)


# In[57]:


def getData(edited_data_inicial, dudoso = None):
    """
    dudoso: None si se quiere carga inicial o [bool] si se quiere actualiza
    """
    data_output = getDataFrame(edited_data_inicial, "./data/prospectos_riesgo_12_22_23.csv")
    data_output.id_distribuidor = data_output.id_distribuidor.astype(str) 
    data_output.drop(["tasa_sugerida"], axis = 1, inplace = True)
    #data_output.rename(columns = {"tasa_minima": ''} inplace = True)
    
    if dudoso == None:
        data_output['dudoso'] = False
        return data_output
    else:
        dud = np.where(dudoso)[0]
        cosechas = [1.54, 3.4, 4.97, 7.38, 10.69, 11.87, 12.35, 12.68, 20.33, 22.69]
        for k in dud:
            riesgo = int(data_output.loc[k, "grupo_riesgo"].replace("Canasta", ""))
            riesgo = min(10, riesgo + 1)
            data_output.at[k, 'grupo_riesgo'] = f"Canasta {riesgo}"
            data_output.at[k, 'perdida_estimada'] = cosechas[max(0, riesgo - 1)]
            data_output.at[k, 'capacidad_pago_semanal'] *= 0.75


            newmonto, newtasa = getNewTasaMonto(monto_pedido = data_output.loc[k, "monto_solicitado"],
                                                pc = data_output.loc[k, "perdida_estimada"]/100,
                                                c = data_output.loc[k, "capacidad_pago_semanal"])

            data_output.at[k, 'monto_autorizado'] = newmonto
            data_output.at[k, 'tasa_minima'] = newtasa
    
    data_output = data_output.set_index('id_distribuidor')
    return data_output


# In[58]:


edited_data_inicial = pd.read_csv("./data/datos_red_ejemplo.csv")


# In[55]:


getData(edited_data_inicial, dudoso = None)


# In[84]:


D = getData(edited_data_inicial, dudoso = [False, True, False])


# In[102]:


None is None

