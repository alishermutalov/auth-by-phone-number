```markdown
# Auth by Phone

## Overview

The **Auth by Phone** project provides a user authentication system using phone numbers. This project includes features such as user registration, login, password reset, and verification code handling. 

## Features

- User Sign Up
- Phone Number Verification
- Login and Logout
- Token-based Authentication
- Password Recovery
- User Information Update
- Profile Photo Update

## Technologies Used

- Django 5.x
- Django REST Framework
- PostgreSQL (or any other database of your choice)
- Python 3.x

## Installation

1. Clone the repository:
   ```bash
   git clone "https://github.com/alishermutalov/auth-by-phone-number"
   cd auth_by_phone
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up your database and update the settings in `settings.py` as necessary.

5. Apply migrations:
   ```bash
   python manage.py migrate
   ```

6. Create a superuser (optional):
   ```bash
   python manage.py createsuperuser
   ```

7. Run the server:
   ```bash
   python manage.py runserver
   ```

## API Endpoints

- **User Registration**
  - `POST /users/signup/`
  
- **User Login**
  - `POST /users/login/`

- **Token Refresh**
  - `POST /users/token/refresh/`

- **User Logout**
  - `POST /users/logout/`

- **Verify Phone Number**
  - `POST /users/verify/`

- **Resend Verification Code**
  - `POST /users/verify/resend/`

- **Update User Info**
  - `PUT /users/update-user/`

- **Update User Photo**
  - `PUT /users/update-user-photo/`

- **Forgot Password**
  - `POST /users/forgot-password/`

- **Reset Password**
  - `POST /users/reset-password/`

## Contributing

Contributions are welcome! Please submit a pull request or create an issue for any suggestions or improvements.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- [Django](https://www.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
