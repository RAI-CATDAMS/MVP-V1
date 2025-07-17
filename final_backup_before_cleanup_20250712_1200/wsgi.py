from app import create_app

# Azure/Gunicorn will import `application`
application = create_app()
