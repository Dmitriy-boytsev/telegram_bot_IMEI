import re
import httpx

from app.core.config import settings

url = 'https://api.imeicheck.net/v1/checks'
 
token = settings.TOKEN_API_SANDBOX

headers = {
   'Authorization': 'Bearer ' + token,
   'Content-Type': 'application/json'
}


def validate_and_normalize_imei(imei: str) -> str:
    """Валидация и нормализация IMEI."""
    normalized_imei = re.sub(r"\D", "", imei)
    if len(normalized_imei) != 15 or not normalized_imei.isdigit():
        return None
    checksum = 0
    for i, digit in enumerate(reversed(normalized_imei)):
        n = int(digit)
        if i % 2 == 1:
            n *= 2
            if n > 9:
                n -= 9
        checksum += n
    if checksum % 10 != 0:
        return None

    return normalized_imei


async def check_imei_with_api(imei: str, serviceid: int = 15):
    """Проверка IMEI через внешний API."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            url,
            headers=headers,
            json={
                "deviceId": imei,
                "serviceId": serviceid
            }
        )

        if response.status_code in {200, 201}:
            data = response.json()
        else:
            raise Exception(f"IMEI API error: {response.status_code} -1- {response.text}")
        
        if data.get("status") != "successful":
            raise Exception(f"IMEI API error: {data.get('status')}")
        
        return data
