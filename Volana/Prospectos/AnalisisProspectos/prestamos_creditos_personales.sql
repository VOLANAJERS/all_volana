select * 
from 
colocacion_asociado as col
inner join cartera_asociado as car 
on car.id_asociado = col.id_asociado

where col.tipo_prestamo = 'CREDITO PERSONAL' or col.tipo_prestamo = 'PRESTAMO PERSONAL CLUB'
-- PRESTAMO PERSONAL CLUB
-- PRESTAMO PERSONAL RED
-- CREDITO PERSONAL
-- LINEA