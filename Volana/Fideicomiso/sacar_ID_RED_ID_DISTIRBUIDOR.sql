select 
ca.id_distribuidor, max(ca.id_red) as 'id_red', max(ca.tipo_prestamo) as 'tipo_prestamo'
from (
	select 
	if(tipo_prestamo = 'PRESTAMO PERSONAL RED', id_distribuidor_linea_de_credito, id_distribuidor) as 'id_distribuidor', 
	id_distribuidor as 'id_red',
    tipo_prestamo
	from colocacion_asociado
) as ca 
where ca.id_red = 113870
group by ca.id_distribuidor