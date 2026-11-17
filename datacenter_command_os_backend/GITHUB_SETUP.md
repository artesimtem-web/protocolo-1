# Publicar DataCenter Command OS en GitHub

## 1. Crear repositorio
En GitHub, crea un repositorio nuevo llamado `datacenter-command-os`.
Recomendación: **Private** mientras el proyecto esté en desarrollo.
No marques la opción de crear README, `.gitignore` o licencia porque el proyecto ya trae archivos.

## 2. Inicializar Git
Abre una terminal en la carpeta raíz del proyecto descomprimido y ejecuta:

```bash
git init
git add .
git commit -m "Initial DataCenter Command OS backend starter"
git branch -M main
git remote add origin https://github.com/TU-USUARIO/datacenter-command-os.git
git push -u origin main
```

Cambia `TU-USUARIO` por tu usuario real de GitHub y usa la URL que GitHub muestre para tu repositorio.

## 3. Antes de subir
- Nunca subas `.env`, contraseñas, tokens, claves privadas ni datos reales de infraestructura.
- El archivo `.gitignore` excluye `.env` y artefactos locales.
- Mantén el repositorio privado si el código o la documentación revelan detalles sensibles.
- Usa un token o el inicio de sesión de GitHub CLI si Git te pide autenticación; no pegues tokens en este documento ni en el chat.

## 4. Próximo paso
Después de publicar el repositorio, comparte aquí la URL del repositorio (si es privado, solo podré acceder si hay una integración de GitHub disponible y autorizada). Puedo ayudarte a preparar cambios, revisar errores y generar commits, pero esta conversación no tiene una conexión directa confirmada a GitHub.
