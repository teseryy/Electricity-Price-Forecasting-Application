from faststream import FastStream

from app.Dependencies import get_broker, shutdown_clickhouse

app = FastStream(get_broker())

@app.on_shutdown
async def shutdown():
    shutdown_clickhouse()