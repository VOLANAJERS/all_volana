select * from (select 
id as 'APPLICANT_ID', 
monto_mensual as ingreso_mensual,
gastos_familiares,
otros_ingresos,
replace(replace(replace(ingreso_neto,"$",""), ",",""), ".00","") as ingreso_neto,
dependientes,
ventas,
FLOOR(DATEDIFF(CURDATE(), fecha_nacimiento) / 365.25) AS edad,
monto_mensual,
compras,
delegacion,
delegacion_negocio,
escolaridad,
estado,
estado_civil,
estado_negocio,
sexo,
sucursal,
tipo_negocio,
tipo_vivienda
from cc_prospectos_demograficos

UNION

select 
id as 'APPLICANT_ID', 
ingreso_mensual,
gastos_familiares,
otros_ingresos,
replace(replace(replace(ingreso_neto,"$",""), ",",""), ".00","") as ingreso_neto,
dependientes,
ventas,
FLOOR(DATEDIFF(CURDATE(), fecha_nacimiento) / 365.25) AS edad,
monto_mensual_venta,
compras,
delegacion,
delegacion_negocio,
escolaridad,
estado,
estado_civil,
estado_negocio,
sexo,
sucursal,
tipo_negocio,
tipo_vivienda
from demograficos_distribuidores) as pen
where pen.APPLICANT_ID in (116)