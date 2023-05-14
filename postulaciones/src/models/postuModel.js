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


async function crearPostulacion(id_apto, cc_postulado, ocupacion, interes) {
  const connection = await conn;
  const result = await connection.query('INSERT INTO postulaciones VALUES (?, ?, Now(), ?, ?, "pendiente")', [id_apto, cc_postulado, ocupacion, interes]);
  return result;
}

async function postuPorApto(id) {
  const connection = await conn;
  const result = await connection.query('SELECT * FROM postulaciones WHERE id_apto = ?', id);
  return result;
}

async function allPostu() {
  const connection = await conn;
  const result = await connection.query('SELECT * FROM postulaciones');
  return result;
}

async function getPostulaciones(id) {
  const connection = await conn;
  const result = await connection.query('SELECT u.nombre, u.email, u.celular, p.cc_postulado, p.fecha, p.ocupacion, p.interes, p.estado FROM postulaciones p JOIN usuarios u ON p.cc_postulado = u.cc WHERE p.id_apto = ?', id);
  return result[0];
}

//falta meterle la columna de estado y asi mismo el query y la parte en controller que deje de mostrar aquellos que estan en "rezhazado"


module.exports = {
  postuPorApto,
  crearPostulacion,
  getPostulaciones,
  allPostu
};
