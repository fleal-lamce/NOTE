import pandas as pd
from math import log
from datetime import datetime

class Status:
    def __init__(self):
        self.df   = pd.DataFrame()
        self.data = {}

    def getLast(self, key, number=False):
        s = self.df.get(key)
        if s is None:
            return None
        
        s = s.dropna()
        if number:
            return float(s.iloc[-1]) if not s.empty else None

        return s.iloc[-1] if not s.empty else None

    def update(self, df):
        self.df = df.copy()
        last    = self.df.iloc[-1]

        t = self.getLast('temperature', number=True)
        h = self.getLast('humidity', number=True)
        p = self.getLast('pressure', number=True)
        w = self.getLast('humidity', number=True)

        gust  = round(w + 1.6, 1) if w is not None else None
        feels = round(t + ((h-50)/50)*1.2 - (w*0.3), 1) if None not in (t,h,w) else None
        dp    = round(self.dewPoint(t, h)) if None not in (t,h) else None
        trend = None

        if p is not None and len(self.df) > 1:
            p_prev = df.iloc[-2].get('pressure')
            trend = '↑' if (pd.notna(p_prev) and p >= float(p_prev)) else '↓'

        self.data = {'temp': t, 'feels': feels, 'hum': h, 'dew': dp, 'press': p, 'trend': trend, 'wind': w, 'gust': gust}
        self.info = {
            'last_update':     f"Atualizado: {self.getLast('time').strftime("%d/%m/%Y %H:%M:%S")}",
            'kpi_temp':        f"{self.data['temp']}°C" if self.data['temp'] is not None else "--°C",
            'kpi_temp_badge':  f"Sensação: {self.data['feels']}°C" if self.data['feels'] is not None else "Sensação: —",
            'kpi_hum':         f"{self.data['hum']}%" if self.data['hum'] is not None else "--%",
            'kpi_hum_badge':   f"Ponto de orvalho: {self.data['dew']}°C" if self.data['dew'] is not None else "Ponto de orvalho: —",
            'kpi_press':       f"{self.data['press']} hPa" if self.data['press'] is not None else "-- hPa",
            'kpi_press_badge': f"Tendência: {self.data['trend']}" if self.data['trend'] is not None else "Tendência: —",
            'kpi_wind':        f"{self.data['wind']} m/s" if self.data['wind'] is not None else "-- m/s",
            'kpi_wind_badge':  f"Rajada: {self.data['gust']} m/s" if self.data['gust'] is not None else "Rajada: —",
        }

    def dewPoint(self, tempC: float, rh: float) -> float:
        a, b = 17.27, 237.7        # Magnus-Tetens approximation (stable for rh≈0)
        rh = max(float(rh), 1e-6)  # evita log(0)
        alpha = ((a * tempC) / (b + tempC)) + log(rh/100.0)
        return (b * alpha) / (a - alpha)