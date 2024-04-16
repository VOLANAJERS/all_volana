SELECT 
ids.id_distribuidor as `Clave Referencia`,
if(ids.tipo_prestamo = 'PRESTAMO PERSONAL RED', 'RED', cd.tipo_distribuidor) as 'tipo distribuidor',
"6" as `Tipo Operación`,
ids.id_red as `Contratante`,
IFNULL(dd.apellido_1,"X") as `Paterno Deudor`,
IFNULL(dd.apellido_2,"X") as `Materno Contratante`,
CONCAT(ifnull(dd.nombre_1,"")," ",ifnull(dd.nombre_2,"")) as `Nombre Contratante`,
"PF" as `Tipo de Persona`,
ifnull(dd.rfc,"X") as `RFC`,
CONCAT(ifnull(dd.calle_y_numero,"")," ",ifnull(dd.colonia,"")) as `Dirección`,
IFNULL(dd.delegacion,"X") as `Ciudad`,
IFNULL(dd.cp,"X") as `CP`,
IFNULL(dd.estado,"X") as `Estado`,
"N/A" as `Email`,
IFNULL(dd.telefono,"X") as `Teléfono`,
date(cd.fecha_aut_linea) as `Fecha Firma Contrato`,
if(cd.tipo_distribuidor = 'RED',ids.fin_credito,'2099-12-31') as `Fecha Vencimiento Contrato`,
if(cd.tipo_distribuidor = 'RED','16','0') as `Plazo`,
ids.id_red as `Crédito`,
"N" as `Anexo`,
cd.linea_de_credito  as `Monto Contrato`,
if(cd.tipo_distribuidor = 'RED','Semanal','Quincenal') as `Frecuencia de Pago`,
cd.proximo_pago_total_pago as `Pago Periódico`,
cd.linea_de_credito as `Monto Pagare`,
if(cd.tipo_distribuidor = 'RED',ids.tasa,"") AS `Tasa`,
dd.fecha_nacimiento as `Fecha de nacimiento contratante`,
IFNULL(dd.sexo,"X") as `Sexo`,
IFNULL(dd.curp,"X") as `CURP`
FROM cartera_distribuidor cd
LEFT JOIN (
		select 
			ca.id_distribuidor, 
            max(ca.id_red) as 'id_red', 
            max(ca.tipo_prestamo) as 'tipo_prestamo',
            max(tasa) as 'tasa',
            max(fin_credito) as 'fin_credito'
			from (
				select 
				if(tipo_prestamo = 'PRESTAMO PERSONAL RED', id_distribuidor_linea_de_credito, id_distribuidor) as 'id_distribuidor', 
				id_distribuidor as 'id_red',
				tipo_prestamo,
                tasa,
                fin_credito
				from colocacion_asociado
			) as ca 
		group by ca.id_distribuidor
) ids on cd.id_distribuidor = ids.id_distribuidor
LEFT JOIN demograficos_distribuidores dd on ids.id_distribuidor = dd.id
WHERE fecha = '2023-11-16' and 
ids.id_distribuidor IS NOT NULL and
dd.nombre_1 IS NOT NULL;

-- and cd.tipo_distribuidor = 'RED';
