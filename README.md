# Cyber Access Management System (CAMS)

A Flask-based cybersecurity project designed to demonstrate authentication, access control, security logging, account protection, reporting, and SIEM integration.

## Project Overview

Cyber Access Management System (CAMS) is a web-based security application developed using Python and Flask.

The project demonstrates practical implementation of common cybersecurity concepts such as:

* User authentication
* Password hashing
* Account lockout protection
* Role-based access control
* Secure file access
* Security event logging
* Authentication monitoring
* Security reporting
* Administrative user management
* Splunk-based security monitoring

## Key Features

### Authentication & Access Control

* Authorized user authentication
* Password hashing using Werkzeug
* Session-based authentication
* Access control for protected pages
* Unauthorized login detection

### Account Security

* Failed login attempt tracking
* Account lockout after multiple failed attempts
* Temporary account locking
* Administrator unlock functionality
* Administrator password reset functionality

### Secure File Management

* Restricted access to security documents
* Download authorization
* File download logging
* Access denied handling

### Security Logging

CAMS records security events including:

* Successful logins
* Failed login attempts
* Unauthorized email attempts
* Account lockouts
* File downloads

### Security Reports

The application provides reports for:

* Security Summary
* Authentication Activity
* File Access
* User Security

### Splunk Integration

CAMS generates security logs that can be forwarded to Splunk for:

* Security event monitoring
* Log analysis
* Historical investigation
* Authentication monitoring
* Security dashboards

## Technology Stack

| Technology   | Purpose                     |
| ------------ | --------------------------- |
| Python       | Application development     |
| Flask        | Web framework               |
| HTML/CSS     | User interface              |
| Linux/Ubuntu | Development environment     |
| Git/GitHub   | Version control             |
| Splunk       | SIEM and log monitoring     |
| VirtualBox   | Virtual machine environment |

## Project Architecture

```text
User
  |
  v
CAMS Web Application
  |
  +-- Authentication
  |
  +-- Access Control
  |
  +-- Account Protection
  |
  +-- Secure File Access
  |
  +-- Security Logging
  |
  +-- Security Reports
  |
  v
Security Logs
  |
  v
Splunk
  |
  v
Security Monitoring & Analysis
```

## Security Concepts Demonstrated

* Authentication
* Authorization
* Password hashing
* Session management
* Account lockout
* Access control
* Security logging
* File access monitoring
* SIEM integration
* Linux security fundamentals

## Project Status

Current implementation includes the Flask-based CAMS application, authentication controls, secure file access, security reports, and GitHub version control.

Future deployment plans include:

* AWS EC2 deployment
* Gunicorn
* Nginx
* HTTPS
* Public web access
* Splunk Universal Forwarder integration

## Disclaimer

This project is developed for educational, cybersecurity learning, and portfolio purposes. Demo accounts and documents are used for testing the application's security functionality.
