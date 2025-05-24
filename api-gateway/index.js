import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import authMiddleware from './middlewares/auth.js';
import setupRoutes from './routes/index.js';

dotenv.config();

const app = express();

// CORS: solo permitir solicitudes desde el frontend
app.use(cors({
  origin: 'http://localhost:5173',
  credentials: true,
}));

// Autenticación con JWT
app.use(authMiddleware);

// Configuración de rutas y proxies
setupRoutes(app);

// Inicialización
const PORT = 8080;
app.listen(PORT, () => {
  console.log(`API Gateway corriendo en http://localhost:${PORT}`);
});
