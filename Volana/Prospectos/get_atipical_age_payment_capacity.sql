select -- ca.id_distribuidor_linea_de_credito as 'id_distribuidor', 
ROUND(std(ca.capital),2) as 'capital_std', ROUND(avg(ca.capital),2) as 'capital_medio', 
CASE
    WHEN SUBSTRING_INDEX(SUBSTRING_INDEX(dd.tiempo_op_negocio, ' ', 1), ',', 1) BETWEEN 1 AND 3 THEN '1-3'
    WHEN SUBSTRING_INDEX(SUBSTRING_INDEX(dd.tiempo_op_negocio, ' ', 1), ',', 1) BETWEEN 4 AND 6 THEN '4-6'
    WHEN SUBSTRING_INDEX(SUBSTRING_INDEX(dd.tiempo_op_negocio, ' ', 1), ',', 1) BETWEEN 7 AND 10 THEN '7-10'
    ELSE '+10'
  END AS "tiempo_op_negocio_",

CASE 
    WHEN REPLACE(REPLACE(LOWER(dd.tipo_negocio),"/","_")," ", "_")  IN ('belleza_salon_estetica_barberia',
       'fabrica_taller_elaboracion_reparacion',
       'venta_de_ropa', 'venta_por_catalogo', 'venta_de_alimentos',
       'joyeria_bisuteria_fundicion',
       'frutas_verduras_semillas_agropecuarias', 'papeleria',
       'calzado_reparacion_venta', 'abarrotes_miscelaneas_perecederos') 
    THEN REPLACE(REPLACE(LOWER(dd.tipo_negocio),"/","_")," ", "_")
	ELSE 'otros_negocios'
END as 'tipo_negocio_'
from colocacion_asociado ca
left join demograficos_distribuidores dd on ca.id_distribuidor_linea_de_credito = dd.id
where ca.tipo_prestamo = 'PRESTAMO PERSONAL RED' 
group by tipo_negocio_, tiempo_op_negocio_
