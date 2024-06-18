# OnlineShop2

This is a Django project for an online store selling electronic products. It includes user authentication with OTP, Celery and RabbitMQ for asynchronous tasks, and integration with AWS S3 for storage.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Features](#features)
- [Dependencies](#dependencies)
- [Configuration](#configuration)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/lenis03/OnlineShop2.git
   cd OnlineShop2
Install dependencies:

```bash
pip install -r requirements.txt
```
Setup Django environment:

Ensure settings are configured properly in config/settings.py.
Migrate database:
```bash
python manage.py migrate
```

Run the development server:
```bash
python manage.py runserver
```
Access the application at http://localhost:8000/.

## Usage
Admin Access:

Access the Django admin panel at http://localhost:8000/admin/.
Use credentials with admin privileges.
User Authentication:

Use OTP-based authentication for user registration and login.
Product Management:

Manage products and categories via the admin interface.
## Features
- User authentication with OTP.
- Product browsing and management.
- Cart functionality with quantity constraints.
- Asynchronous tasks with Celery and RabbitMQ.
- Integration with AWS S3 for file storage.
## Dependencies
- Django
- Celery
- RabbitMQ
- Kavenegar API
- Boto3 (AWS SDK for Python)
- Configuration
### Django Settings:
- Ensure AWS credentials and endpoint are correctly set in config/settings.py.
## Testing
- Unit Tests:
- Use Django's built-in testing framework to test models, views, and forms.
## Contributing
Fork the repository and create a new branch.
Make your changes and submit a pull request.
## License
This project is licensed under the MIT License.
