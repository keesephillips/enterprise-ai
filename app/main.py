from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from app import socketio 
import boto3
import json
from config.settings import Config
from .audit import log_audit_event, app_logger

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


def get_bedrock_response(user_message):
    if not bedrock_runtime:
        app_logger.error("Bedrock client not available.")
        return "Sorry, the AI service is not configured correctly (Bedrock client error)."
    
    if not Config.BEDROCK_PROMPT_ARN:
        app_logger.error("Bedrock Model ID not configured.")
        return "Sorry, the AI service is not configured correctly (Model ID missing)."

    try:
        app_logger.info(f"Invoking Bedrock model: {Config.BEDROCK_PROMPT_ARN} with input: {user_message[:50]}...")

        response = bedrock_runtime.converse(
            modelId=Config.BEDROCK_PROMPT_ARN,
            messages=[
                {
                    "role": "user",
                    "content": [{"text": user_message}]
                }
            ],
        )
        
        generated_text = response['output']['message']['content'][0]['text']
        
        app_logger.info(f"Bedrock response received: {generated_text}...")
        log_audit_event(
            action="BEDROCK_INVOCATION_SUCCESS",
            details=f"Model: {Config.BEDROCK_PROMPT_ARN}, Input: {user_message[:50]}",
            username=current_user.username,
            ip_address=request.remote_addr
        )
        return generated_text

    except Exception as e:
        app_logger.error(f"Bedrock invocation error: {e}")
        log_audit_event(
            action="BEDROCK_INVOCATION_FAILURE",
            details=f"Error: {str(e)[:100]}",
            username=current_user.username,
            ip_address=request.remote_addr
        )
        return f"Sorry, an error occurred while contacting the AI service: {str(e)}"


@main_bp.route('/')
@login_required
def index():
    return redirect(url_for('main.chat'))


@main_bp.route('/chat', methods=['GET', 'POST'])
@login_required
def chat():
    bedrock_response_text = ""
    if request.method == 'POST':
        message_text = request.form.get('user_input')
        username = current_user.username
        ip_address = request.remote_addr
        
        app_logger.info(f"Received message from {username}: {message_text}")
        log_audit_event(
            action="MESSAGE_SENT",
            details=f"User '{username}' sent message: {message_text[:50]}",
            username=username,
            ip_address=ip_address
        )

        if message_text:
            bedrock_response_text = get_bedrock_response(message_text)
    
    return render_template('chat.html', username=current_user.username, bedrock_response_text=bedrock_response_text)


@main_bp.route('/health')
def health_check():
    return "OK", 200

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