from flask import Blueprint, render_template, request, redirect, url_for 
from flask_login import login_required, current_user
from app import socketio 
import boto3
import json
from config.settings import Config
from.audit import log_audit_event, app_logger

main_bp = Blueprint('main', __name__)

bedrock_runtime = None
if Config.AWS_ACCESS_KEY_ID and Config.AWS_SECRET_ACCESS_KEY and Config.AWS_DEFAULT_REGION:
    try:
        bedrock_runtime = boto3.client(
            service_name='bedrock-runtime',
            region_name=Config.AWS_DEFAULT_REGION,
            aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY
        )
        app_logger.info("Bedrock client initialized successfully.")
    except Exception as e:
        app_logger.error(f"Failed to initialize Bedrock client: {e}")
else:
    app_logger.error("AWS credentials or region not configured for Bedrock client.")


@main_bp.route('/')
@login_required
def index():
    return redirect(url_for('main.chat')) 

@main_bp.route('/chat')
@login_required
def chat():
    return render_template('chat.html', username=current_user.username)

@main_bp.route('/health')
def health_check():
    return "OK", 200

def get_bedrock_response(user_message):
    if not bedrock_runtime:
        app_logger.error("Bedrock client not available.")
        return "Sorry, I am unable to process your request at the moment (Bedrock client error)."
    if not Config.BEDROCK_PROMPT_ARN:
        app_logger.error("Bedrock Prompt ARN not configured.")
        return "Sorry, I am unable to process your request at the moment (Prompt ARN missing)."

    prompt_data = {
        "user_input": user_message
    }
    body = json.dumps(prompt_data)
    
    try:
        app_logger.info(f"Invoking Bedrock model: {Config.BEDROCK_PROMPT_ARN} with input: {user_message[:50]}...") 
        
        response = bedrock.converse(
            modelId=Config.BEDROCK_PROMPT_ARN,
            contentType='application/json',
            accept='application/json',
            promptVariables={PROMPT_VAR_NAME: {"text": user_text}},
        )
        
        response_body_raw = response.get('body').read()
        response_body = json.loads(response_body_raw.decode('utf-8'))
        
        generated_text = response_body.get('generated_text', "Error: Could not parse Bedrock response.")
        if 'amazon-bedrock-trace' in response_body: 
             app_logger.debug(f"Bedrock trace data: {response_body['amazon-bedrock-trace']}")
        
        app_logger.info(f"Bedrock response received: {generated_text[:50]}...") 
        log_audit_event(action="BEDROCK_INVOCATION_SUCCESS", 
                        details=f"Prompt: {Config.BEDROCK_PROMPT_ARN}, Input: {user_message[:50]}", 
                        username=current_user.username, 
                        ip_address=request.remote_addr if request else "N/A")
        return generated_text

    except Exception as e:
        app_logger.error(f"Bedrock invocation error: {e}")
        log_audit_event(action="BEDROCK_INVOCATION_FAILURE", 
                        details=f"Error: {str(e)[:100]}", 
                        username=current_user.username if current_user.is_authenticated else "System", 
                        ip_address=request.remote_addr if request else "N/A") 
        return f"Sorry, an error occurred while contacting Bedrock: {str(e)[:100]}"


@socketio.on('connect')
@login_required 
def handle_connect():
    username = current_user.username
    ip_address = request.remote_addr
    log_audit_event(action="SOCKET_CONNECT", details=f"User '{username}' connected via WebSocket.", username=username, ip_address=ip_address)
    app_logger.info(f"Client connected: {request.sid}, User: {username}")
    socketio.emit('server_message', {'text': f'{username} has joined the chat.'}, broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    username = current_user.username if current_user.is_authenticated else "UnknownUser"
    ip_address = request.remote_addr if request else "N/A"
    log_audit_event(action="SOCKET_DISCONNECT", details=f"User '{username}' disconnected from WebSocket.", username=username, ip_address=ip_address)
    app_logger.info(f"Client disconnected: {request.sid}, User: {username}")
    socketio.emit('server_message', {'text': f'{username} has left the chat.'}, broadcast=True)


@socketio.on('user_message')
@login_required
def handle_user_message(data):
    print("helloworld")
    message_text = data.get('text', '')
    username = current_user.username
    ip_address = request.remote_addr
    
    app_logger.info(f"Received message from {username} ({request.sid}): {message_text}")
    log_audit_event(action="MESSAGE_SENT", 
                    details=f"User '{username}' sent message: {message_text[:50]}", 
                    username=username, 
                    ip_address=ip_address)

    bedrock_response_text = get_bedrock_response(message_text)
    socketio.emit('new_chat_message', {'username': 'Bedrock Bot', 'text': bedrock_response_text}, broadcast=True)