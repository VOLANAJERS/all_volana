select * 
from
	(select ca.*,cd.saldo_pendiente_total as saldo, 
    cd.total_pagado_capital as 'capital_pagado', 
    cd.saldo_pendiente_capital as 'capital_pendiente',
    cd.dias_atraso,cd.fecha,cd.status,cd.convenio,
	cd.fecha_aut_linea as fecha_inicio_relacion,
    cd.reestructurado,pagos_anticipados_u4p,pagos_en_tiempo_u4p,
    pagos_destiempo_u4p,pagos_pendientes_u4p
	from
	(
	select 
	cas.id_distribuidor, 
	max(cas.id_red) as 'id_red', 
	cas.id_asociado as id_operacion,
	max(cas.tipo_prestamo) as 'tipo_prestamo',
	max(cas.fin_credito) as fecha_cierre,
	max(cas.dispersion) as fecha_de_dispersion
	from (
		select 
		if(tipo_prestamo = 'PRESTAMO PERSONAL RED', id_distribuidor_linea_de_credito, id_distribuidor) as 'id_distribuidor', 
		id_distribuidor as 'id_red',
		tipo_prestamo,
		fin_credito,
		dispersion,
		id_asociado
		from colocacion_asociado
	) as cas 
	group by 
		cas.id_distribuidor, 
		cas.id_asociado
	) ca
	left join cartera_distribuidor cd on ca.id_red = cd.id_distribuidor
	where -- cd.fecha = '2023-08-25'
	fecha_de_dispersion>='2021-07-01'
	and cd.fecha >= fecha_de_dispersion 
    and cd.fecha<= DATE_ADD(fecha_cierre, INTERVAL 4 MONTH)

) as qry
WHERE
    DAY(qry.fecha) = 15 or
    qry.fecha = LAST_DAY(qry.fecha)