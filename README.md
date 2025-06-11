# Enterprise AI 

## Background
This project provides an enterprise-grade conversational AI application using AWS as the backbone. The primary goal is to create a chat interface that is not only interactive and real-time but also secure, auditable, and ready for integration into a production environment. It makes use of a Claude LLMs through AWS Bedrock, ensuring that the AI component is scalable and managed. The application is built around a secure authentication system and features a detailed audit trail, logging critical events like user connections, messages sent, and AI interactions. This makes it suitable for environments where compliance and monitoring are key requirements.

---

## Configuration
Set up an .env file with the proper variables for you to access the model. Also create a Bedrock model that accepts a prompt as input

---

## Deployment
```bash
pip install -r requirements.txt
python app.py
```

---

## Security Documentation
- Authentication & Authorization
  - Session Management: User authentication is handled by Flask-Login. It manages user sessions securely, storing user IDs in a server-side signed cookie.
  - Protected Routes: Critical routes are protected with the @login_required decorator, ensuring that only authenticated users can access the chat functionality.
  - Audit Trail: The log_audit_event function provides a detailed log of important events, creating a security-relevant audit trail. 
  - Web Security: Cross-Site Scripting (XSS) and Cross-Site Request Forgery (CSRF) are employed through the use of Flask to protect against these types of attacks
  
---

## Recommended Production Stack
- WSGI Server: Gunicorn is a widely used WSGI server for running Python web applications.
- Reverse Proxy: Nginx should be placed in front of Gunicorn to handle incoming requests, serve static files efficiently, and manage SSL/TLS termination

---

## Performance Analysis
- The primary performance bottleneck in this application is not the application code itself, but the latency of the external AI service.
  - AI Model Latency: The time it takes for AWS Bedrock to process the prompt and return a response is the largest factor in perceived performance. This latency also might vary significantly depending on the LLM model chosen and the current load on the AWS service.
  - Network Latency: The time between the AppRunner server and the AWS Bedrock endpoints in the selected region will also add to the overall response time. Deploying your application in the same AWS region as your Bedrock service can minimize this.
  - Application Logic: The Python/Flask code for processing requests and managing sessions is extremely fast and unlikely to be a bottleneck under normal load.

## Scalability: 
- The application is designed to be scalable horizontally.
  - Stateless Application: The Flask application is mostly stateless, meaning you can run multiple instances of it behind a load balancer to handle increased traffic.
  - Scaling Gunicorn: You can scale vertically by increasing the number of Gunicorn worker processes.
  - AWS Bedrock Scaling: AWS Bedrock is a fully managed and auto-scaling service.

---

# Author
Keese Phillips