
import streamlit as st
import pandas as pd
import numpy as np
from AnalisisRiesgoRedesProspectos import getDataFrame, getMarginalRentabilidad
from asignarTasa import ajustarTasa

#num2curr = lambda x: "${:,.0f}".format(x)
num2curr = lambda x: "${:,.0f}".format(x) if x > 0 else "-"+("${:,.0f}".format(x)).replace("-","")

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
        if monto_pedido in np.array(resultado.monto_autorizado):
            temp = resultado.query(f"monto_autorizado == {monto_pedido}")
            return temp.iloc[0]['monto_autorizado'], temp.iloc[0]['tasa_minima'] 
            # en caso de que sí este, pues dale ese
        else:
            # en caso de que no, dale ese ese con la máxima tasa
            return monto_pedido, 147
    else:
        # en caso de que el autorizado sea menor, solo dale ese
        return resultado.iloc[0]['monto_autorizado'], resultado.iloc[0]['tasa_minima'] 
    
def getData(edited_data_inicial): # ================================= AQUI ==============================
    """
    dudoso: None si se quiere carga inicial o [bool] si se quiere actualiza
    """
    data_output = getDataFrame(edited_data_inicial, "./data/prospectos_riesgo_12_22_23.csv")
    data_output.id_distribuidor = data_output.id_distribuidor.astype(str) 
    data_output.drop(["tasa_sugerida"], axis = 1, inplace = True)
    
    if st.session_state['dudoso'] == []:
        st.session_state['dudoso'] = [False] * data_output.shape[0]
        
    #print("Entré")
    #print(st.session_state['dudoso'])
    #print(st.session_state['dudoso'] == [])
    #print(st.session_state["random_key"])
    #print(st.session_state["from_restart"])
    
    #if dudoso == None:
    if st.session_state['from_restart'] == True:
        print("Entrando en from restart")
        data_output['dudoso'] = False
        return data_output
    else:
        print("Entrando en from update")
        
        dud = np.where(st.session_state['dudoso'])[0]
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
            
        data_output['dudoso'] = st.session_state['dudoso']
    
    data_output = data_output.set_index('id_distribuidor')
    
    return data_output
        
st.set_page_config(layout="wide")

# ================================================================
# Variables de estado
# ================================================================
if "random_key" not in st.session_state:
    st.session_state["random_key"] = 0
    
if 'dudoso' not in st.session_state:
    st.session_state['dudoso'] = []
    
if 'from_restart' not in st.session_state:
    st.session_state['from_restart'] = False
    
if 'data' not in st.session_state:
    st.session_state['data'] = None
    
if 'data_inicial' not in st.session_state:
    st.session_state['data_inicial'] = None
    
if 'edited_data' not in st.session_state:
    st.session_state['edited_data'] = None
    

def checkDataChanges():
    #print("Edited en check changes:")
    #print(st.session_state['edited_data'])
    #print(f"Asi inicia dudoso: {st.session_state['dudoso']}")
    st.session_state["random_key"] += 1
    st.session_state['data'] = getData(st.session_state['data_inicial']).copy()
    print("Entramos")

# ================================================================
    
with st.sidebar:    
    page = st.selectbox(
    'Selecciona la página',
    ('Análisis de riesgo de redes',))
    
if page == 'Análisis de riesgo de redes':
    st.title("Análisis de riesgo de redes")
    st.write("Actualizado al: 2024-01-05")

    st.subheader("Carga la tabla de prospectos")
    uploaded_file = st.file_uploader("Elige un archivo")
    if uploaded_file is not None:
        data = pd.read_csv(uploaded_file)
        edited_data_inicial = st.data_editor(data)
        st.session_state['data_inicial'] = edited_data_inicial.copy()
        
        
        st.subheader("Resumen de los prospectos")
        #data_output = getData(edited_data_inicial)
        
        if st.session_state['data'] is not None:
            print("Desde la sesión")
            st.session_state['edited_data'] = st.data_editor(st.session_state['data'], key=st.session_state["random_key"], 
                                        disabled= ('id_distribuidor', 'saldoVencidoPeorAtraso', 'saldoVencidoConClaves',
           'grupo_riesgo', 'perdida_estimada','tipo_negocio', 'tiempo_op_negocio', 'ingreso_neto',
           'capacidad_pago_semanal', 'vive_en_misma_casa', 'edad','monto_solicitado'))
        
        else:
            print("Desde normal")
            data_output = getData(edited_data_inicial)
            st.session_state['data'] = data_output
            
            st.session_state['edited_data'] = st.data_editor(data_output, key=st.session_state["random_key"], 
                                        disabled= ('id_distribuidor', 'saldoVencidoPeorAtraso', 'saldoVencidoConClaves',
           'grupo_riesgo', 'perdida_estimada','tipo_negocio', 'tiempo_op_negocio', 'ingreso_neto',
           'capacidad_pago_semanal', 'vive_en_misma_casa', 'edad','monto_solicitado'))
        
        
        edited_data = st.session_state['edited_data']
        
        st.session_state['dudoso'] = np.array(edited_data.dudoso)
        print("\n=====================================")
        print(f"Dudo en código {st.session_state['edited_data']}")
        
        
        if st.button('Presiona dos veces para reiniciar'):
            #edited_data.update(data_output)
            #st.session_state["random_key"] += 1
            st.session_state['from_restart'] = True
            checkDataChanges()
        
        if st.button('Presiona dos veces para actualizar'):
            #st.session_state["random_key"] += 1

            st.session_state['from_restart'] = False
            checkDataChanges()
            #data_output = getData(edited_data_inicial, st.session_state['dudoso'])
        
        
        monto_solicitado_total = edited_data.monto_solicitado.sum()
        monto_aut_total = edited_data.monto_autorizado.sum()

        st.markdown("**Resumen de contribuciones**")

        col1, col2, col3, col4 = st.columns(4)

        marginal_modelo, rentabilidad_modelo, marginal_pedida, rentabilidad_pedida = getMarginalRentabilidad(edited_data)


        col1.metric("Marginal", num2curr(marginal_modelo), num2curr(marginal_modelo - marginal_pedida))
        col2.metric("Rentabilidad", f"{rentabilidad_modelo*100:.2f}%", f"{(rentabilidad_modelo - rentabilidad_pedida)*100:.2f}%")

        col3.metric("Marginal pedida", num2curr(marginal_pedida))
        col4.metric("Rentabilidad pedida", f"{rentabilidad_pedida*100:.2f}%")

        st.markdown("**Resumen de riesgo**")
        col1, col2, col3, col4 = st.columns(4)
        tp = round(sum(edited_data.monto_solicitado * edited_data.tasa_minima) /\
                   edited_data.query("monto_autorizado > 0 ").monto_solicitado.sum(), 0)

        riesgo_numero = edited_data.grupo_riesgo.str.replace("Canasta ","").astype(int)
        rp = round(sum(edited_data.monto_solicitado * riesgo_numero) /\
                   monto_solicitado_total, 0)


        col1.metric("Saldo Vencido con Claves", num2curr(edited_data.saldoVencidoConClaves.sum()))
        col2.metric("Saldo Vencido", num2curr(edited_data.saldoVencidoPeorAtraso.sum()))
        col3.metric("Monto solicitado", num2curr(monto_solicitado_total))
        col4.metric("Monto propuesto", num2curr(monto_aut_total), num2curr(monto_aut_total - monto_solicitado_total))

        col1_, col2_ = st.columns(2)
        col1_.metric("Tasa ponderada", str(int(tp)) + "%" , str(int(tp - edited_data.tasa_pedida.mean()))+"%" )
        col2_.metric("Riesgo ponderado", int(rp))
