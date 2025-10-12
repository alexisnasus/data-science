# throttle_utils.py
import time
import random
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Rotación simple de User-Agents (puedes añadir más)
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
]

class Throttler:
    def __init__(
        self,
        min_delay=4.0,            # súbelo si ves bloqueos (p.ej. 5–12 s)
        max_delay=10.0,
        long_pause_every=30,      # cada N requests, pausa larga…
        long_pause_min=90.0,      # …de 90–180 s
        long_pause_max=180.0,
    ):
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.long_pause_every = long_pause_every
        self.long_pause_min = long_pause_min
        self.long_pause_max = long_pause_max
        self.request_count = 0

    def sleep(self):
        self.request_count += 1
        # Pausa base con jitter
        time.sleep(random.uniform(self.min_delay, self.max_delay))
        # Pausa larga periódica
        if self.long_pause_every and (self.request_count % self.long_pause_every == 0):
            time.sleep(random.uniform(self.long_pause_min, self.long_pause_max))

def build_session(
    total_retries=4,
    backoff_factor=1.0,
    status_forcelist=(429, 500, 502, 503, 504),
):
    """
    Session con reintentos y backoff exponencial.
    Respeta Retry-After cuando el servidor lo envía.
    """
    session = requests.Session()
    retry = Retry(
        total=total_retries,
        read=total_retries,
        connect=total_retries,
        backoff_factor=backoff_factor,     # 1.0 -> 1s, 2s, 4s, …
        status_forcelist=status_forcelist,
        allowed_methods=False,             # reintenta todos los métodos
        raise_on_status=False,
        respect_retry_after_header=True,
    )
    adapter = HTTPAdapter(max_retries=retry, pool_connections=20, pool_maxsize=20)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

def fetch(
    url,
    session=None,
    throttler=None,
    headers=None,
    timeout=25,
    max_manual_retries=2,
):
    """
    GET con:
    - Throttling (jitter + pausas largas periódicas)
    - Session reutilizable
    - Respeto de Retry-After
    - Reintentos manuales adicionales ante 429/5xx con backoff y jitter
    """
    if session is None:
        session = build_session()
    if throttler is None:
        throttler = Throttler()

    # UA rotatorio si no se pasa uno explícito
    if headers is None:
        headers = {"User-Agent": random.choice(USER_AGENTS)}
    elif "User-Agent" not in headers:
        headers = {**headers, "User-Agent": random.choice(USER_AGENTS)}

    attempt = 0
    while True:
        throttler.sleep()
        resp = session.get(url, headers=headers, timeout=timeout)

        if resp.status_code == 429:
            # Si viene Retry-After, respétalo
            ra = resp.headers.get("Retry-After")
            if ra:
                try:
                    wait_s = float(ra)
                except ValueError:
                    wait_s = random.uniform(45, 75)
            else:
                wait_s = min(90, (2 ** attempt) * 8 + random.uniform(0, 5))
            time.sleep(wait_s)

        elif 500 <= resp.status_code < 600:
            # Errores 5xx -> backoff manual
            if attempt < max_manual_retries:
                wait_s = min(90, (2 ** attempt) * 8 + random.uniform(0, 5))
                time.sleep(wait_s)
            else:
                resp.raise_for_status()
                return resp

        else:
            # 2xx -> OK; 4xx != 429 -> devolvemos sin reintentar
            if 400 <= resp.status_code < 500 and resp.status_code != 429:
                return resp
            return resp

        attempt += 1
        if attempt > max_manual_retries:
            return resp
