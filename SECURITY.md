# Security Policy

## Supported Versions

We release patches for security vulnerabilities in the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

We take the security of the Worklog Automation System seriously. If you discover a security vulnerability, please follow these steps:

### 🔒 Private Disclosure

Please **DO NOT** report security vulnerabilities through public GitHub issues, discussions, or pull requests.

Instead, please report security vulnerabilities by:

1. **Email**: Send details to [mizanur.r.ashiq@gmail.com]
2. **GitHub Security Advisory**: Use GitHub's private vulnerability reporting feature

### 📝 What to Include

When reporting a vulnerability, please include:

- A clear description of the vulnerability
- Steps to reproduce the issue
- Potential impact and severity
- Any suggested fixes or mitigations
- Your contact information for follow-up

### ⏱️ Response Timeline

- **24 hours**: Initial acknowledgment of your report
- **72 hours**: Initial assessment and severity classification
- **7 days**: Detailed response with our planned approach
- **30 days**: Target resolution timeframe (may vary based on complexity)

### 🏆 Recognition

We appreciate security researchers who help keep our project safe. With your permission, we'll acknowledge your contribution in:

- Our security advisory
- Release notes
- A security researchers acknowledgment section

### 🛡️ Security Best Practices

When using this project:

1. **Environment Variables**: Never commit `.env` files with real credentials
2. **Secret Management**: Use proper secret management for production deployments
3. **Updates**: Keep dependencies updated to latest secure versions
4. **Access Control**: Implement proper authentication and authorization
5. **HTTPS**: Always use HTTPS in production environments

### 🔍 Security Features

This project includes several security measures:

- JWT token-based authentication
- Input validation with Pydantic
- SQL injection prevention with SQLModel/SQLAlchemy
- Rate limiting middleware
- Security headers middleware
- CORS configuration
- Environment-based configuration

### 📋 Security Checklist for Contributors

- [ ] Review code for potential security issues
- [ ] Update dependencies to latest secure versions
- [ ] Add appropriate input validation
- [ ] Follow secure coding practices
- [ ] Test authentication and authorization
- [ ] Document security considerations

## Contact

For non-security related questions about this policy, please open a GitHub issue.

Thank you for helping keep Worklog Automation System secure! 🛡️