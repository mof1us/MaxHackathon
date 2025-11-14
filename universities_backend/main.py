import uvicorn

from application.Application import Application

if __name__ == "__main__":
    app = Application()
    uvicorn.run(app.app, host="0.0.0.0", port=8001)