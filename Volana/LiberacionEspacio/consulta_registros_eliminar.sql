select * from cartera_distribuidor
WHERE fecha < DATE_SUB(CURDATE(), INTERVAL 3 YEAR)  -- Registros con más de un año de antigüedad
   AND (DAY(fecha) != 15  -- Excluir registros del día 15
	and DAY(fecha) != DAY(LAST_DAY(fecha))) 
-- AND id_distribuidor
-- ORDER BY fecha