#!/usr/bin/env python3
"""
Script de prueba simple para verificar configuracion de ambientes
Prueba conexion, campos y permisos en TEST y PRODUCCION
"""
import os
import sys
from dotenv import load_dotenv


def test_environment(env_name, use_prod_value):
    """Prueba un ambiente especifico"""
    print(f"\n{'='*60}")
    print(f"PROBANDO AMBIENTE: {env_name}")
    print(f"{'='*60}\n")

    # Setear el ambiente
    os.environ["USE_PRODUCTION"] = use_prod_value

    # Recargar config
    if "config" in sys.modules:
        del sys.modules["config"]
    if "odoo_rpc" in sys.modules:
        del sys.modules["odoo_rpc"]

    import config
    from odoo_rpc import ODOO_JSONRPC, ODOO_DB, ODOO_UID, ODOO_PASSWORD, _post

    print(f"[OK] Configuracion cargada:")
    print(f"   URL: {ODOO_JSONRPC}")
    print(f"   DB: {ODOO_DB}")
    print(f"   UID: {ODOO_UID}")
    print(
        f"   Password: {'*' * len(ODOO_PASSWORD) if ODOO_PASSWORD else 'NO CONFIGURADA'}"
    )

    # Obtener campos
    campo_comercial = os.getenv("ODOO_FIELD_NOMBRE_COMERCIAL")
    campo_fecha = os.getenv("ODOO_FIELD_FECHA_MATRICULA")
    campo_ciiu = os.getenv("ODOO_FIELD_CIIU")

    print(f"\nCampos configurados:")
    print(f"   Nombre Comercial: {campo_comercial}")
    print(f"   Fecha Matricula: {campo_fecha}")
    print(f"   CIIU: {campo_ciiu}")

    # Test 1: Verificar autenticacion
    print(f"\nTest 1: Verificando autenticacion...")
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "call",
        "params": {"service": "common", "method": "version", "args": []},
    }

    ok, result = _post(payload)
    if ok:
        version = result.get("result", {})
        print(
            f"   [OK] Conexion exitosa - Odoo version: {version.get('server_version', 'unknown')}"
        )
    else:
        print(f"   [ERROR] Error de conexion: {result}")
        return False

    # Test 2: Buscar un partner de prueba
    print(f"\nTest 2: Buscando partner de prueba...")
    payload = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                ODOO_DB,
                ODOO_UID,
                ODOO_PASSWORD,
                "res.partner",
                "search_read",
                [[]],
                {"fields": ["id", "name"], "limit": 1},
            ],
        },
    }

    ok, result = _post(payload)
    if ok and result.get("result"):
        partner = result["result"][0]
        partner_id = partner["id"]
        partner_name = partner["name"]
        print(f"   [OK] Partner encontrado: ID {partner_id} - {partner_name}")
    else:
        print(f"   [ERROR] No se pudo obtener partner: {result}")
        return False

    # Test 3: Verificar que los campos existen
    print(f"\nTest 3: Verificando existencia de campos...")
    payload = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                ODOO_DB,
                ODOO_UID,
                ODOO_PASSWORD,
                "res.partner",
                "fields_get",
                [],
                {"attributes": ["string", "type"]},
            ],
        },
    }

    ok, result = _post(payload)
    if ok:
        all_fields = result.get("result", {})

        # Verificar cada campo
        campos_a_verificar = {
            "Nombre Comercial": campo_comercial,
            "Fecha Matricula": campo_fecha,
            "CIIU": campo_ciiu,
            "Notas (comment)": "comment",
        }

        campos_ok = True
        for nombre, campo in campos_a_verificar.items():
            if campo in all_fields:
                field_info = all_fields[campo]
                tipo = field_info.get("type", "?")
                etiqueta = field_info.get("string", "?")
                print(
                    f"   [OK] {nombre}: '{campo}' existe (tipo: {tipo}, etiqueta: {etiqueta})"
                )
            else:
                print(f"   [ERROR] {nombre}: '{campo}' NO EXISTE en Odoo")
                campos_ok = False

        if not campos_ok:
            print(
                f"\n   [ADVERTENCIA] Algunos campos no existen. Verifica los nombres."
            )
            return False
    else:
        print(f"   [ERROR] No se pudo obtener lista de campos: {result}")
        return False

    # Test 4: Verificar permisos de escritura (lectura del partner)
    print(f"\nTest 4: Verificando permisos de lectura...")
    payload = {
        "jsonrpc": "2.0",
        "id": 4,
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                ODOO_DB,
                ODOO_UID,
                ODOO_PASSWORD,
                "res.partner",
                "read",
                [[partner_id]],
                {"fields": [campo_comercial, campo_fecha, campo_ciiu, "comment"]},
            ],
        },
    }

    ok, result = _post(payload)
    if ok and result.get("result"):
        partner_data = result["result"][0]
        print(f"   [OK] Lectura exitosa del partner {partner_id}")
        print(f"      - {campo_comercial}: {partner_data.get(campo_comercial, 'N/A')}")
        print(f"      - {campo_fecha}: {partner_data.get(campo_fecha, 'N/A')}")
        print(f"      - {campo_ciiu}: {partner_data.get(campo_ciiu, 'N/A')}")
        print(
            f"      - comment: {'Tiene contenido' if partner_data.get('comment') else 'Vacio'}"
        )
    else:
        print(f"   [ERROR] Error al leer partner: {result}")
        return False

    print(f"\n[EXITO] TODAS LAS PRUEBAS PASARON PARA {env_name}")
    return True


def main():
    print("=" * 60)
    print("SCRIPT DE PRUEBA DE AMBIENTES")
    print("=" * 60)

    # Cargar .env base
    load_dotenv()

    resultados = {}

    # Probar ambiente de PRUEBAS
    resultados["test"] = test_environment("PRUEBAS", "false")

    # Probar ambiente de PRODUCCION
    resultados["prod"] = test_environment("PRODUCCION", "true")

    # Resumen final
    print("\n" + "=" * 60)
    print("RESUMEN DE PRUEBAS")
    print("=" * 60)

    if resultados["test"]:
        print("[OK] Ambiente PRUEBAS: OK")
    else:
        print("[ERROR] Ambiente PRUEBAS: FALLO")

    if resultados["prod"]:
        print("[OK] Ambiente PRODUCCION: OK")
    else:
        print("[ERROR] Ambiente PRODUCCION: FALLO")

    print("\n" + "=" * 60)

    if all(resultados.values()):
        print("TODOS LOS TESTS PASARON")
        print("\nProximo paso:")
        print("   1. Para usar PRUEBAS localmente: USE_PRODUCTION=false en .env")
        print(
            "   2. Para desplegar a PRODUCCION: USE_PRODUCTION=true en .env del servidor"
        )
        return 0
    else:
        print("ALGUNOS TESTS FALLARON")
        print("\nVerifica:")
        print("   1. Credenciales en .env")
        print("   2. Nombres de campos para cada ambiente")
        print("   3. Permisos del usuario en Odoo")
        return 1


if __name__ == "__main__":
    sys.exit(main())
