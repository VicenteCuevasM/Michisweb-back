import { createProxyMiddleware } from 'http-proxy-middleware';

export default function setupRoutes(app) {
  app.use('/login', createProxyMiddleware({
    target: process.env.LOGIN_SERVICE_URL,
    changeOrigin: true
  }));


  app.use('/prescripciones', createProxyMiddleware({
    target: process.env.PRESCRIPCION_SERVICE_URL,
    changeOrigin: true
  }));

  app.use('/pacientes', createProxyMiddleware({
    target: process.env.PACIENTES_SERVICE_URL,
    changeOrigin: true,
  }));

  app.use('/reservas', createProxyMiddleware({
    target: process.env.RESERVAS_SERVICE_URL,
    changeOrigin: true,
  }));

  app.use('/medicamentos', createProxyMiddleware({
    target: process.env.MEDICAMENTOS_SERVICE_URL,
    changeOrigin: true
  }));
}