try:
    row = {
        "razon_social": "TEST COMPANY",
        "sigla": "TC",
        "fecha_matricula": "20220101",
        "cod_ciiu_act_econ_pri": "1234",
        "representante_legal": "JUAN PEREZ",
        "camara_comercio": "BOGOTA",
        "codigo_camara": "01",
    }

    razon_social = row.get("razon_social")
    sigla = row.get("sigla")
    # Socrata date format: YYYYMMDD -> YYYY-MM-DD
    raw_fecha = str(row.get("fecha_matricula") or "")
    if len(raw_fecha) == 8 and raw_fecha.isdigit():
        fecha_matricula = f"{raw_fecha[:4]}-{raw_fecha[4:6]}-{raw_fecha[6:]}"

    ciiu = row.get("cod_ciiu_act_econ_pri")
    representante_legal = row.get("representante_legal")
    camara_nombre = row.get("camara_comercio")
    cod_camara = row.get("codigo_camara")

    print("SUCCESS: Syntax is valid.")
    print(f"Date: {fecha_matricula}")
except Exception as e:
    print(f"ERROR: {e}")
