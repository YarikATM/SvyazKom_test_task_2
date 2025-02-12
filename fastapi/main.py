from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import List, Dict, Any
import secrets
import random
from config_reader import config

app = FastAPI()
security = HTTPBasic()


def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    correct_username = config.LOGIN
    correct_password = config.PASSWORD.get_secret_value()
    if not (secrets.compare_digest(credentials.username, correct_username) and
            secrets.compare_digest(credentials.password, correct_password)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid login or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


@app.get("/records", dependencies=[Depends(verify_credentials)], summary="Генерация тестовых записей")
async def get_records() -> List[Dict[str, Any]]:
    """
    Генерирует список тестовых записей.
    Число записей (от 1 до 50000)

    Допустимые сочетания параметров:
    lac
    lac+cellid
    eci

    Допустимые значения:
    0 < lac < 0xFFFF
    0 < cellid < 0xFFFF
    0 < eci < 0xFFFFFFF


    Пример ответа:
    [
      {"eci": null, "lac": 5000, "cellid": 7820},
      {"eci": 651212, "lac": null, "cellid": null}
    ]
    """
    records = []
    for _ in range(random.randint(1, 50000)):
        record_type = random.choice(["lac", "lac_cellid", "eci", ""])
        match record_type:
            case "lac":
                lac = random.randint(1, 0xFFFF - 1)
                record = {"lac": lac, "cellid": None, "eci": None}
            case "lac_cellid":
                lac = random.randint(1, 0xFFFF - 1)
                cellid = random.randint(1, 0xFFFF - 1)
                record = {"lac": lac, "cellid": cellid, "eci": None}
            case "eci":
                eci = random.randint(1, 0xFFFF - 1)
                record = {"lac": None, "cellid": None, "eci": eci}
            case _:
                lac = random.randint(1, 0xFFFF - 1)
                cellid = random.randint(1, 0xFFFF - 1)
                eci = random.randint(1, 0xFFFF - 1)
                record = {"lac": lac, "cellid": cellid, "eci": eci}

        records.append(record)
    return records





