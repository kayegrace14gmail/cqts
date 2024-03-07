# Coffee Quality Tracking System

This repository contains the source code and implementation documents for the Coffee Quality Tracking System. The system consists of a Django web application for the backend, an Android mobile app for image processing AI

## Overview

The Coffee Quality Tracking System aims to track the consistency of coffee quality from the cooperative level to the exporters and buyers. It involves quality assurance officers at cooperatives using a web interface to register farmers and capture details of coffee batches. Exporters and buyers can use a mobile app to scan QR codes on batches for quality confirmation.


### Setup

1. Install Python and Django on your system.
2. Clone this repository and navigate to the `web_app` directory.
3. Create a virtual environment: `python -m venv env`.
4. Activate the virtual environment: `source env/bin/activate` (Linux/Mac) or `env\Scripts\activate` (Windows).
5. Install the required dependencies: `pip install -r requirements.txt`.
6. Run database migrations: `python manage.py migrate`.
7. Create a superuser: `python manage.py createsuperuser`.
8. Start the development server: `python manage.py runserver`.

### Access

- Access the Django admin panel at `http://127.0.0.1:8000/admin/`.
- Use the superuser credentials to log in and manage the application.

## Contributors

- LWANGA KAYE GRACE
- WABWIIRE EDRICK
- FELIX ALIGUMA
- MAYAMBALA MARK

## License

This project is licensed under the GNU Public LICENSE. Feel free to use, modify, and distribute it as per the terms of the license.
