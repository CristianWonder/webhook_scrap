# Test de Ambientes - RUES Webhook

## Como ejecutar el test

```bash
python test_environments.py
```

## Que hace el test

El script prueba **ambos ambientes** (TEST y PRODUCCION) automaticamente:

### Test 1: Autenticacion

- Verifica conexion a Odoo
- Muestra la version de Odoo

### Test 2: Busqueda de Partner

- Busca un partner de prueba en la base de datos
- Verifica que puede leer datos basicos

### Test 3: Verificacion de Campos

- Comprueba que todos los campos configurados existen en Odoo:
  - Nombre Comercial (l10n_co_edi_commercial_name o x_studio_nombre_comercial)
  - Fecha de Matricula (x_studio_fecha_de_matricula)
  - CIIU (x_studio_cdigo_ciiu_1 o x_studio_ciiu)
  - Notes/Comment (comment)

### Test 4: Permisos de Lectura

- Lee los valores actuales de esos campos
- Verifica que el usuario tiene permisos

## Resultado Esperado

Si todo funciona correctamente, veras:

```
TODOS LOS TESTS PASARON

Proximo paso:
   1. Para usar PRUEBAS localmente: USE_PRODUCTION=false en .env
   2. Para desplegar a PRODUCCION: USE_PRODUCTION=true en .env del servidor
```

## Si hay errores

El test te dira exactamente que fallo:

- **Error de conexion**: Verifica credenciales en .env
- **Campo no existe**: Verifica nombres de campos (PROD*FIELD*_ o TEST*FIELD*_)
- **Error de permisos**: El usuario de Odoo necesita permisos de lectura/escritura

## Ver resultados detallados

Si PowerShell trunca el output, guarda en archivo:

```powershell
python test_environments.py | Tee-Object -FilePath test_results.txt
```

Luego abre `test_results.txt` para ver todo el output.
