"""
Configuración simple de ambientes
Lee el .env y setea las variables según USE_PRODUCTION
"""

import os
from dotenv import load_dotenv

# Cargar el .env
load_dotenv()

# Leer el flag de ambiente
use_production = os.getenv("USE_PRODUCTION", "false").lower() in ("true", "1", "yes")

if use_production:
    # Usar credenciales de PRODUCCIÓN
    os.environ["ODOO_JSONRPC"] = os.getenv("PROD_ODOO_JSONRPC")
    os.environ["ODOO_DB"] = os.getenv("PROD_ODOO_DB")
    os.environ["ODOO_UID"] = os.getenv("PROD_ODOO_UID")
    os.environ["ODOO_PASSWORD"] = os.getenv("PROD_ODOO_PASSWORD")
    os.environ["ODOO_FIELD_NOMBRE_COMERCIAL"] = os.getenv("PROD_FIELD_NOMBRE_COMERCIAL")
    os.environ["ODOO_FIELD_FECHA_MATRICULA"] = os.getenv("PROD_FIELD_FECHA_MATRICULA")
    os.environ["ODOO_FIELD_CIIU"] = os.getenv("PROD_FIELD_CIIU")

    print("🚀 Modo: PRODUCCIÓN")
    print(f"   DB: {os.getenv('PROD_ODOO_DB')}")
else:
    # Usar credenciales de PRUEBAS
    os.environ["ODOO_JSONRPC"] = os.getenv("TEST_ODOO_JSONRPC")
    os.environ["ODOO_DB"] = os.getenv("TEST_ODOO_DB")
    os.environ["ODOO_UID"] = os.getenv("TEST_ODOO_UID")
    os.environ["ODOO_PASSWORD"] = os.getenv("TEST_ODOO_PASSWORD")
    os.environ["ODOO_FIELD_NOMBRE_COMERCIAL"] = os.getenv("TEST_FIELD_NOMBRE_COMERCIAL")
    os.environ["ODOO_FIELD_FECHA_MATRICULA"] = os.getenv("TEST_FIELD_FECHA_MATRICULA")
    os.environ["ODOO_FIELD_CIIU"] = os.getenv("TEST_FIELD_CIIU")

    print("🧪 Modo: PRUEBAS")
    print(f"   DB: {os.getenv('TEST_ODOO_DB')}")

print(f"   Campo Comercial: {os.environ['ODOO_FIELD_NOMBRE_COMERCIAL']}")
print(f"   Campo CIIU: {os.environ['ODOO_FIELD_CIIU']}\n")
