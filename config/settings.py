import os
from dotenv import load_dotenv

load_dotenv() 

class Config:
    SECRET_KEY = os.environ.get('FLASK_APP_SECRET_KEY') or 'you-should-really-change-this'
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_DEFAULT_REGION = os.environ.get('AWS_DEFAULT_REGION')
    BEDROCK_PROMPT_ARN = os.environ.get('BEDROCK_PROMPT_ARN')

    AUDIT_LOG_FILE = 'logs/audit.log'
    APP_LOG_FILE = 'logs/app.log'