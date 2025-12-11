import os
import re
from typing import Optional, Dict, Any
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# ---------- Config ----------
SOCRATA_URL = os.getenv("SOCRATA_URL", "https://www.datos.gov.co/resource/c82u-588k.json")
SOCRATA_APP_TOKEN = os.getenv("SOCRATA_APP_TOKEN")  # opcional para más cuota
RUES_DETALLE_URL = os.getenv("RUES_DETALLE_URL", "https://ruesapi.rues.org.co/WEB2/api/Expediente/DetalleRM/{}")
TIMEOUT = int(os.getenv("TIMEOUT", "12"))

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "5000"))

# ---------- FastAPI app ----------
app = FastAPI(title="RUES Webhook", version="1.0.2")

# ---------- Modelos ----------
class WebhookIn(BaseModel):
    nit: str

class WebhookOut(BaseModel):
    nit: str
    razon_social: Optional[str] = None
    sigla: Optional[str] = None
    fuente: str

# ---------- Helpers ----------
def only_digits(s: str) -> str:
    return re.sub(r"\D", "", s or "")

def socrata_headers() -> Dict[str, str]:
    return {"X-App-Token": SOCRATA_APP_TOKEN} if SOCRATA_APP_TOKEN else {}

def fetch_socrata(nit_base: str) -> Optional[Dict[str, Any]]:
    """
    Busca por NIT en el dataset de Confecámaras (Datos Abiertos).
    Retorna la fila con matrícula más alta (heurística simple).
    """
    params = {"$select": "nit,razon_social,sigla,codigo_camara,matricula", "nit": nit_base, "$limit": 5}
    r = requests.get(SOCRATA_URL, params=params, headers=socrata_headers(), timeout=TIMEOUT)
    r.raise_for_status()
    data = r.json() or []
    if not data:
        return None
    try:
        data.sort(key=lambda x: int((x.get("matricula") or "0") or 0), reverse=True)
    except Exception:
        pass
    return data[0]

def build_id_rm(codigo_camara: str, matricula: str) -> Optional[str]:
    try:
        return f"{int(codigo_camara):02d}{int(matricula):010d}"
    except Exception:
        return None

def fetch_rues_detalle(id_rm: str) -> Dict[str, Any]:
    r = requests.get(RUES_DETALLE_URL.format(id_rm), timeout=TIMEOUT)
    if r.status_code != 200:
        return {}
    return r.json() or {}

# ---------- Endpoints ----------
@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/webhook", response_model=WebhookOut)
def webhook(payload: WebhookIn):
    nit_digits = only_digits(payload.nit)
    if not nit_digits:
        raise HTTPException(status_code=400, detail="NIT vacío o inválido")

    razon_social: Optional[str] = None
    sigla: Optional[str] = None
    fuente = "datos.gov.co"

    # 1) Socrata / Datos Abiertos
    try:
        row = fetch_socrata(nit_digits)
    except requests.HTTPError:
        row = None

    if row:
        razon_social = (row.get("razon_social") or "").strip() or None
        sigla = (row.get("sigla") or "").strip() or None

        # 2) Completar con RUES detalle si falta algún dato
        if (not razon_social or not sigla) and row.get("codigo_camara") and row.get("matricula"):
            id_rm = build_id_rm(row["codigo_camara"], row["matricula"])
            if id_rm:
                detalle = fetch_rues_detalle(id_rm)
                razon_social = razon_social or (detalle.get("razonSocial") or "").strip() or None
                sigla = sigla or (detalle.get("sigla") or "").strip() or None
                if razon_social or sigla:
                    fuente = "ruesapi.rues.org.co"

    if not (razon_social or sigla):
        raise HTTPException(status_code=404, detail=f"No encontré datos para NIT {nit_digits}")

    return WebhookOut(nit=nit_digits, razon_social=razon_social, sigla=sigla, fuente=fuente)

# ---------- Main ----------
if __name__ == "__main__":
    import uvicorn
    # Importa como "webhook_scrap:app" porque el archivo se llama webhook_scrap.py
    uvicorn.run("webhook_scrap:app", host=HOST, port=PORT, reload=False)
