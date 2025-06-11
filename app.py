from app import create_app, socketio
from app.audit import app_logger

app = create_app()

if __name__ == '__main__':
    app_logger.info("Starting application...")
    socketio.run(app, host='0.0.0.0', port=8080, debug=True, use_reloader=True)