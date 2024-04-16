select 
id_distribuidor as `Contrato`,
"N" as `Anexo`,
-- if(tipo_distribuidor = 'RED', id_distribuidor_linea_de_credito, id_distribuidor) as `Número de documento`,
id_distribuidor as `Número de documento`,
date(if(tipo_distribuidor = 'RED',fin_credito,'2099-12-31')) as `Fecha Vencimiento`,
ROUND(sum(capital), 2) as `Monto Capital`,
ROUND(sum(interes), 2) as `Monto intérés`,
ROUND(sum(iva), 2) as `Monto IVA`,
"FAC" AS `Tipo de Movimiento`
FROM
(SELECT 
cd.id_distribuidor,
"N" as `Anexo`,
cd.tipo_distribuidor,
ca.capital,
ca.interes,
ca.iva,
cd.fecha,
ca.fin_credito,
ca.no_pagos,
ca.id_distribuidor_linea_de_credito
FROM cartera_distribuidor cd
LEFT JOIN colocacion_asociado ca on cd.id_distribuidor = ca.id_distribuidor
WHERE fecha = '2023-11-16' and ca.tipo_prestamo = 'PRESTAMO PERSONAL RED') as temp
-- WHERE id_distribuidor = 110547

GROUP BY temp.id_distribuidor, fecha, fin_credito, tipo_distribuidor-- , temp.id_distribuidor_linea_de_credito
