from datetime import datetime
from zoneinfo import ZoneInfo

def getTime():
    now = datetime.now(ZoneInfo("America/Sao_Paulo"))
    return now.strftime("%d/%m/%Y %H:%M:%S %Z%z")

