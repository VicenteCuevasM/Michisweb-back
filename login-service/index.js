const express = require('express');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcrypt');
const pool = require('./db');
require('dotenv').config();

const app = express();
app.use(express.json());

app.post('/login', async (req, res) => {
  const { RUT, contrasena } = req.body;

  if (!RUT || !contrasena) {
    return res.status(400).json({ error: 'Faltan credenciales' });
  }

  try {
    const result = await pool.query(
      'SELECT * FROM Usuario WHERE RUT = $1',
      [RUT]
    );

    if (result.rows.length === 0) {
      return res.status(401).json({ error: 'Usuario no encontrado' });
    }

    const usuario = result.rows[0];

    const passwordOk = contrasena === usuario.contrasena;

    if (!passwordOk) {
      return res.status(401).json({ error: 'Contraseña incorrecta' });
    }

    const token = jwt.sign(
      { id: usuario.id, RUT: usuario.rut, rol: usuario.rol },
      process.env.JWT_SECRET,
      { expiresIn: '30m' }
    );

    res.json({ token });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Error interno del servidor' });
  }
});

app.listen(3000, () => {
  console.log('Login service corriendo en http://localhost:3000');
});
