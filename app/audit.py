import logging
import logging.handlers
from config.settings import Config

def setup_audit_logger():
    logger = logging.getLogger('chat_audit')
    logger.setLevel(logging.INFO)
    
    import os
    if not os.path.exists('logs'):
        os.makedirs('logs')

    handler = logging.handlers.RotatingFileHandler(
        Config.AUDIT_LOG_FILE, maxBytes=1024*1024*5, backupCount=5
    )
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    
    if not logger.handlers:
        logger.addHandler(handler)
    return logger

def setup_app_logger():
    logger = logging.getLogger('chat_app')
    logger.setLevel(logging.DEBUG) 

    import os
    if not os.path.exists('logs'):
        os.makedirs('logs')

    handler = logging.handlers.RotatingFileHandler(
        Config.APP_LOG_FILE, maxBytes=1024*1024*5, backupCount=5
    )
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    if not logger.handlers:
        logger.addHandler(handler)
    return logger

audit_logger = setup_audit_logger()
app_logger = setup_app_logger() 

def log_audit_event(action, details, username="System", ip_address="N/A"):
    log_message = f"User: {username}, IP: {ip_address}, Action: {action}, Details: {details}"
    audit_logger.info(log_message)