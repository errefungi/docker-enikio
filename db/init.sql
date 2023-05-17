CREATE DATABASE enikio;
use enikio;

CREATE TABLE usuarios (
        cc varchar(10),
        nombre varchar(50),
        email varchar(50),
        password varchar(50),
        celular varchar(10),
        rol varchar(10),
        primary key (cc));


CREATE TABLE aptos(
        link varchar(150),
        id_apto int,
        precio int,
        cant_h int,
        coord point,
        hab_disponibles int,
        id_arrendador int,
        primary key (id_apto));

CREATE TABLE postulaciones(
        id_apto int,
        cc_postulado varchar(10),
        fecha date,
        ocupacion varchar(50),
        interes varchar(20),
        estado varchar(20));

CREATE TABLE universidades(
        nombre varchar(100),
        coord point,
        avg_precio_apto float,
        num_aptos int,
        num_postulaciones_X_universidad int,
        promedio_habitacion_X_universidad float);

CREATE TABLE aptosPrecio(
        rango_precio varchar(50),
        num_postulaciones_X_precio int,
        promedio_habitacion_X_rango_precio float);

CREATE TABLE ocupacion(
        ocupacion varchar(50),
        count int);



LOAD DATA INFILE '/var/lib/mysql-files/usuarios.csv'
INTO TABLE usuarios
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

LOAD DATA INFILE '/var/lib/mysql-files/aptos.csv'
INTO TABLE aptos
FIELDS TERMINATED BY ';'
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(link, id_apto, precio, cant_h, @coord, hab_disponibles, id_arrendador)
SET coord = ST_PointFromText(@coord);

LOAD DATA INFILE '/var/lib/mysql-files/postulaciones.csv'
INTO TABLE postulaciones
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(id_apto, cc_postulado, @fecha, ocupacion, interes, estado)
SET fecha = STR_TO_DATE(@fecha, '%Y-%m-%d');

LOAD DATA INFILE '/var/lib/mysql-files/universidades.csv'
INTO TABLE universidades
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(nombre, @coord, avg_precio_apto, num_aptos, num_postulaciones_X_universidad, promedio_habitacion_X_universidad)
SET coord = ST_PointFromText(@coord);

LOAD DATA INFILE '/var/lib/mysql-files/aptosPrecio.csv'
INTO TABLE aptosPrecio
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
-- (rango_precio, num_postulaciones_X_precio, promedio_habitacion_X_rango_precio)
IGNORE 1 ROWS;

LOAD DATA INFILE '/var/lib/mysql-files/ocupacionCount.csv'
INTO TABLE ocupacion
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
-- (ocupacion, count)
IGNORE 1 ROWS;