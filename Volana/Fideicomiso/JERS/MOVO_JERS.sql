-- Requerimiento MOVO / PAGOS ENRIQUE

select
coalesce(cd.id_red, pd.id_distribuidor) as `Contrato`,
"N" AS `Anexo`,
-- coalesce(if(cd.tipo_prestamo = 'PRESTAMO PERSONAL RED', cd.id_red, cd.id_distribuidor), pd.id_distribuidor) as `Número de documento`,
coalesce(cd.id_distribuidor, pd.id_distribuidor) as `Número de documento`,
DATE(pd.fecha_pago) as `Fecha Depósito`,
DATE(pd.fecha_aplicacion_pago) as `Fecha Aplicación`,
IF(pd.capital>0,-pd.capital,pd.capital) as `Monto de Principal`,
IF(pd.interes>0,-pd.interes,pd.interes) as `Monto de interés`,
IF(pd.iva>0,-pd.iva,pd.iva) as `Monto de IVA`,
"1" AS `Tipo de Movimiento`,
pd.procedencia as `Cuenta`,
pd.id_pago as `paymentId`
FROM pagos_desglosados pd
left JOIN (
		select 
			ca.id_distribuidor, max(ca.id_red) as 'id_red', max(ca.tipo_prestamo) as 'tipo_prestamo'
			from (
				select 
				if(tipo_prestamo = 'PRESTAMO PERSONAL RED', id_distribuidor_linea_de_credito, id_distribuidor) as 'id_distribuidor', 
				id_distribuidor as 'id_red',
				tipo_prestamo
				from colocacion_asociado
			) as ca 
		group by ca.id_distribuidor
) cd on pd.id_distribuidor = cd.id_red
where date(fecha_pago) >= '2021-01-01'
