select count(*)/12 from cartera_distribuidor
WHERE fecha > DATE_SUB(CURDATE(), INTERVAL 12 MONTH)  -- Registros con más de un año de antigüedad
-- AND id_distribuidor = 116
  
ORDER BY fecha

-- 5,633,184 registros totales de antes de 1 año
-- Se eliminarían 5,302,208
-- Conservando 330,976 registros que corresponderían a los cortes del 15 y fin de mes