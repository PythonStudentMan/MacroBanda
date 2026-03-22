# MacroBanda - Gestión Multi-Tenant

Aplicación Flask profesional con multi-tenancy por subdominio, RBAC avanzado y auditoría.

## Instalación rápida

...bash
git clone http://github.com/PythonStudentMan/MacroBanda.git
cd MacroBanda
cp .env.example .env
pip install -r requirements.txt
flask db upgrade
python seed.py
python run.py