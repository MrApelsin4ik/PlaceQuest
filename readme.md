# PlaceQuest

## Overview
This project is aimed at enriching the knowledge of teenagers and tourists in the field of history and literature.

## Features
- **Attraction list**: You can find a lot of different attractions you can visit.
- **Games**: You can play some games and compete with other users in your literature knowledge.

## Technology
- **Backend**: Django
- **DB**: sqlite3 (In production you can use MySQL or other)

## Installation and Setup
There are no specific library requirements. Simply install the project dependencies and run the Django server to get started.

1. Clone the repository:
   ```bash
   git clone https://github.com/MrApelsin4ik/PlaceQuest
   ```
2. Using env:
   ```bash
   source ./django_env/bin/activate
   ```
3. Run migrations:
   ```bash
   python manage.py makemigrations
   ```
    ```bash
   python manage.py migrate
   ```
4. Put your server's ip to settings.py:
   Change ALLOWED_HOSTS = [] like this:
   ```bash
   ALLOWED_HOSTS = ['192.168.0.117']
   ```
6. Start the server:
   ```bash
   python manage.py runserver 0.0.0.0:80
   ```

## Usage
Once logged in or registered, the main page provides access to all the core features:
- See attraction list
- Play games
- See rating
- e.t.c.

## Demo Video
Check out the [demo video](<(https://github.com/user-attachments/assets/b0813805-3501-4364-a685-a31d694648d2)>) showcasing the prototype of the tool and its features.

## License
This project is currently freely available for use.





