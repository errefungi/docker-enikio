const mysql = require('mysql2/promise');
let retries = 20;

async function connect() {
  while(retries) {
    try {
      const pool = mysql.createPool({
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

const connection = connect();

//para que los vea el admin. Al admin no le importan los postulados como tal.
async function traerUsuarios() {
    const result = await connection.query('SELECT * FROM usuarios WHERE rol = "arrendador"');
    return result[0];
}

//Para auto-fill de postulaciones si es que existe el usuario, buscarlo con la cc.
async function traerUsuario(cc) {
    const result = await connection.query('SELECT * FROM usuarios WHERE cc = ? ', cc);
    return result;
}


async function validarUsuario(email, password) {
    const result = await connection.query('SELECT * FROM usuarios WHERE email = ? AND password = ?', [email, password]);
    return result[0];
}

async function crearAutofill(cc) {
    const result = await connection.query('SELECT nombre, email, celular FROM usuarios WHERE cc = ?', [cc]);
    return result[0];
}

//Para que admin cree usuarios. Crea arrendadores, los usuarios que buscan apto no tienen usuario de login. 
async function crearUsuario(cc, nombre, email, password, celular) {
    const result = await connection.query('INSERT INTO usuarios VALUES(?,?,?,?,?, "arrendador")', [cc, nombre, email, password, celular]);
    return result;
}

//Para que admin borre usuario arrendador de acuerdo a cc
async function borrarUsuario(cc) {
    const result = await connection.query('DELETE FROM usuarios WHERE cc = ?', cc);
    const result2 = await connection.query('DELETE FROM aptos WHERE id_arrendador = ?', cc);
    return result, result2;
}

//Para que cuando el postulado meta su info, ya esté su rol definido. 
async function crearPostulado(cc, nombre, email, celular) {
    const result = await connection.query('INSERT INTO usuarios VALUES(?,?,?,null,?,"postulado")', [cc, nombre, email, celular]);
    return result;
}

module.exports = {
    traerUsuarios, traerUsuario, validarUsuario, crearUsuario, crearPostulado, borrarUsuario, crearAutofill
};
