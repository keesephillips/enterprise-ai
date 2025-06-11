# Enterprise AI 

## Background
This project provides a robust foundation for building enterprise-grade conversational AI applications. The primary goal is to create a chat interface that is not only interactive and real-time but also secure, auditable, and ready for integration into a corporate environment.

It leverages the power of large language models (LLMs) through AWS Bedrock, ensuring that the AI component is scalable and managed. The application is built around a secure authentication system and features a detailed audit trail, logging critical events like user connections, messages sent, and AI interactions. This makes it suitable for environments where compliance and monitoring are key requirements.

---

## Deployment
```bash
pip install -r requirements.txt
python app.py
```

---

## Configuration
Set up an .env file with the proper variables for you to access the model. Also create a Bedrock model that accepts a prompt as input

---

## Security Documentation
- Authentication & Authorization
  - Session Management: User authentication is handled by Flask-Login. It manages user sessions securely, storing user IDs in a server-side signed cookie.
  - Password Hashing: All user passwords must be hashed using a strong algorithm like Argon2 or scrypt (managed via werkzeug.security).
  - Protected Routes: Critical routes are protected with the @login_required decorator, ensuring that only authenticated users can access the chat functionality.
  - Audit Trail: The log_audit_event function provides a detailed log of important events, creating a security-relevant audit trail. 
  - Web Security: Cross-Site Scripting (XSS) and Cross-Site Request Forgery (CSRF)
  
---

## Recommended Production Stack
- WSGI Server: Gunicorn is a mature, stable, and widely used WSGI server for running Python web applications.
- Reverse Proxy: Nginx should be placed in front of Gunicorn to handle incoming requests, serve static files efficiently, and manage SSL/TLS termination

---

## Performance Analysis
- Key Performance Factors & Bottlenecks
    - The primary performance bottleneck in this application is not the application code itself, but the latency of the external AI service.
    - AI Model Latency (High Impact): The time it takes for AWS Bedrock to process the prompt and return a response is the single largest factor in perceived performance. This latency varies significantly depending on the model chosen (e.g., Claude 3 Haiku is faster than Claude 3 Opus) and the current load on the AWS service.
    - Network Latency (Medium Impact): The round-trip time between your server and the AWS Bedrock endpoints in your selected region will add to the overall response time. Deploying your application in the same AWS region as your Bedrock service can minimize this.
    - Application Logic (Low Impact): The Python/Flask code for processing requests, managing sessions, and emitting Socket.IO events is extremely fast and unlikely to be a bottleneck under normal load.
    - Scalability: The application is designed to be scalable horizontally.
    - Stateless Application: The Flask application is mostly stateless, meaning you can run multiple instances of it behind a load balancer to handle increased traffic.
    - Scaling Gunicorn: You can scale vertically by increasing the number of Gunicorn worker processes (--workers) or horizontally by deploying more instances of the application on different machines.
    - Scaling Socket.IO: This is a critical consideration. To run multiple Socket.IO server instances, you must implement a message queue (e.g., Redis or RabbitMQ). This allows instances to communicate and ensures that messages are correctly broadcast to all clients, regardless of which server instance they are connected to. Without a message queue, Socket.IO will not work correctly in a multi-instance deployment.
    - AWS Bedrock Scaling: AWS Bedrock is a fully managed and auto-scaling service. It will not be a bottleneck.

---

# Author
Keese Phillips