const mysql = require('mysql2/promise');
let retries = 20;

async function connect() {
    while (retries) {
        try {
            const pool = await mysql.createPool({
                host: 'db',
                user: 'root',
                password: '',
                database: 'enikio'
            });

            return pool;
        } catch (err) {
            console.log('Error connecting to DB: ', err);
            console.log(`Retrying (${retries} attempts left)...`);
            retries--;
            await new Promise(res => setTimeout(res, 5000));
        }
    }

    throw new Error('Max retries exceeded. Could not connect to DB.');
}

const conn = connect();



async function traerAptoArrendador(id_arrendador) {
    const connection = await conn;
    const result = await connection.query('SELECT * FROM aptos WHERE id_arrendador = ?', id_arrendador);
    return result[0];
}

async function getAllAptos() {
    const connection = await conn;
    const result = await connection.query('SELECT * FROM aptos WHERE coord is not NULL');
    return result[0];
}

async function traerAptoMapa(hab_disponibles) {
    const connection = await conn;
    const result = await connection.query('SELECT * FROM aptos WHERE hab_disponibles != 0', hab_disponibles);
    return result[0];
}

async function traerApto(id_apto) {
    const connection = await conn;
    const result = await connection.query('SELECT * FROM aptos WHERE id_apto =?', id_apto);
    return result[0];
}

async function actualizarApto(id_apto, hab_disponibles) {
    const connection = await conn;
    const result = await connection.query('UPDATE aptos SET hab_disponibles = ? WHERE id_apto = ? ', [hab_disponibles, id_apto]);
    return result;
}

// solo admin x2 - **admin no manipula los aptos, lo haría arrendador, pero al final dijimos que no por el tema de que todo se hace con scrap en finca raiz"""""
async function borrarApto(id_apto) {
    const connection = await conn;
    const result = await connection.query('DELETE FROM aptos WHERE id= ?', id_apto);
    return result;
}

async function getPropiedadesArr(cc) {
    const connection = await conn;
    const result = await connection.query('SELECT id_apto, precio, cant_h, hab_disponibles, link FROM aptos WHERE id_arrendador = ? AND coord IS NOT NULL', cc);
    return result[0];
}

async function getCoords(nombre) {
    const connection = await conn;
    const result = await connection.query('SELECT coord from universidades where nombre = ?', nombre)
    return result[0];
}


async function getCloseAptos(coord) {
    const connection = await conn;
    const result = await connection.query(`SELECT   id_apto,   precio,   cant_h, hab_disponibles, ROUND(ST_Distance_Sphere(coord, ST_GeomFromText('${coord}')) / 1000, 2) AS distance_km, link, coord FROM   aptos WHERE ST_Distance_Sphere(coord, ST_GeomFromText('${coord}')) <= 2000 AND coord IS NOT NULL AND hab_disponibles > 0 ORDER BY distance_km ASC LIMIT 100;`)
    return result[0];
}

async function getUniversidad() {
    const connection = await conn;
    const result = await connection.query('SELECT * from universidades')
    return result[0];
}


async function getMetrics() {
    const connection = await conn;
    const num_aptos = await connection.query('select count(*) as total from aptos')
    const num_postu = await connection.query('select count(*) as total from postulaciones')
    const hab_dispo = await connection.query('select count(*) as total from aptos WHERE hab_disponibles > 2')
    const arrendadores = await connection.query('select count(*) as total from usuarios WHERE rol ="arrendador"')
    const aptos_icesi = await connection.query("SELECT count(*) as total FROM   aptos WHERE   ROUND(ST_Distance_Sphere(coord, ST_GeomFromText('POINT(3.3416907213039626 -76.53094179612705)'))) / 1000 <= 2 AND coord IS NOT NULL AND hab_disponibles > 0")
    const aptos_uao = await connection.query("SELECT count(*) as total FROM   aptos WHERE   ROUND(ST_Distance_Sphere(coord, ST_GeomFromText('POINT(3.353740400019329 -76.52048592608172)'))) / 1000 <= 2 AND coord IS NOT NULL AND hab_disponibles > 0")
    const aptos_antonio_jose = await connection.query("SELECT count(*) as total FROM   aptos WHERE   ROUND(ST_Distance_Sphere(coord, ST_GeomFromText('POINT(3.470593445052489 -76.52747705971524)'))) / 1000 <= 2 AND coord IS NOT NULL AND hab_disponibles > 0")
    const aptos_san_bue = await connection.query("SELECT count(*) as total FROM   aptos WHERE   ROUND(ST_Distance_Sphere(coord, ST_GeomFromText('POINT(3.343562195183882 -76.54438216439318)'))) / 1000 <= 2 AND coord IS NOT NULL AND hab_disponibles > 0")
    const aptos_libre = await connection.query("SELECT count(*) as total FROM   aptos WHERE   ROUND(ST_Distance_Sphere(coord, ST_GeomFromText('POINT(3.427567009699586 -76.54992013164862)'))) / 1000 <= 2 AND coord IS NOT NULL AND hab_disponibles > 0")
    const aptos_cooperativa = await connection.query("SELECT count(*) as total FROM   aptos WHERE   ROUND(ST_Distance_Sphere(coord, ST_GeomFromText('POINT(3.391257975610888 -76.55105966842426)'))) / 1000 <= 2 AND coord IS NOT NULL AND hab_disponibles > 0")
    // CONSULTAS HECHAS A LOS DATOS EXTRAIDOS DE PYSPARK
    const promedio_apto = await connection.query("SELECT ROUND(AVG(avg_precio_apto), 1) AS total FROM universidades;")
    const universidad_barata = await connection.query("SELECT nombre, ROUND(avg_precio_apto, 1) AS Minimo_Precio_Apto FROM universidades WHERE avg_precio_apto = (SELECT MIN(avg_precio_apto) FROM universidades);")
    const universidad_cara = await connection.query("SELECT nombre, ROUND(avg_precio_apto, 1) AS Minimo_Precio_Apto FROM universidades WHERE avg_precio_apto = (SELECT MAX(avg_precio_apto) FROM universidades);")
    const post_student = await connection.query("SELECT count as total FROM ocupacion WHERE ocupacion='Estudiante';")
    const post_profe = await connection.query("SELECT count as total FROM ocupacion WHERE ocupacion='Docente';")
    const postu_barato = await connection.query("SELECT num_postulaciones_X_precio as total FROM aptosPrecio WHERE rango_precio = 'economico';")
    const postu_medio = await connection.query("SELECT num_postulaciones_X_precio as total FROM aptosPrecio WHERE rango_precio = 'medio';")
    const postu_caro = await connection.query("SELECT num_postulaciones_X_precio as total FROM aptosPrecio WHERE rango_precio = 'costoso';")
    const habitacion_barato = await connection.query("SELECT promedio_habitacion_X_rango_precio as total FROM aptosPrecio WHERE rango_precio = 'economico';")
    const habitacion_medio = await connection.query("SELECT promedio_habitacion_X_rango_precio as total FROM aptosPrecio WHERE rango_precio = 'medio';")
    const habitacion_caro = await connection.query("SELECT promedio_habitacion_X_rango_precio as total FROM aptosPrecio WHERE rango_precio = 'costoso';")
    const resultado = {
        "num_aptos": num_aptos[0][0]["total"],
        "num_postu": num_postu[0][0]["total"],
        "aptos_over_2_hab_dispo": hab_dispo[0][0]["total"],
        "arrendadores": arrendadores[0][0]["total"],
        "aptos_icesi": aptos_icesi[0][0]["total"],
        "aptos_uao": aptos_uao[0][0]["total"],
        "aptos_antonio_jose": aptos_antonio_jose[0][0]["total"],
        "aptos_san_bue": aptos_san_bue[0][0]["total"],
        "aptos_libre": aptos_libre[0][0]["total"],
        "promedio_apto": aptos_cooperativa[0][0]["total"],
        "aptos_cooperativa": promedio_apto[0][0]["total"],
        "universidad_barata": universidad_barata[0][0],
        "universidad_cara": universidad_cara[0][0],
        "post_student": post_student[0][0]["total"],
        "post_profe": post_profe[0][0]["total"],
        "postu_barato": postu_barato[0][0]["total"],
        "postu_medio": postu_medio[0][0]["total"],
        "postu_caro": postu_caro[0][0]["total"],
        "habitacion_barato": habitacion_barato[0][0]["total"],
        "habitacion_medio": habitacion_medio[0][0]["total"],
        "habitacion_caro": habitacion_caro[0][0]["total"],
    };

    return resultado;
}


module.exports = {
    traerAptoArrendador,
    traerApto,
    actualizarApto,
    borrarApto,
    getPropiedadesArr,
    getCoords,
    getUniversidad,
    getMetrics,
    getCloseAptos,
    getAllAptos
    //traerAptoMapa
};
