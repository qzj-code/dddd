import uvicorn
from fastapi import FastAPI

from task.flight_CAmobile.search.main import task_main as search_task_main

app = FastAPI()
data_source = "CAmobile"


@app.post(f'/{data_source}/search', summary='查询接口', description='查询接口', tags=[data_source])
def search(data: dict):
    result = search_task_main(data)
    return result

if __name__ == '__main__':
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8090,
        reload=True,
        workers=9,  # 并发进程数
    )