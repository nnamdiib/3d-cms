# 3DToolBox

## How To Run:

1. Install the packages in the requirements.txt file using `pip install -r requirements.txt`

2. Run migrations for the database. This will create a local SQLite DB where app data will be stored. `python manage.py migrate`

3. To create Admin site user, use `python manage.py createsuperuser`

4. Finally, to start the development server, use `python manage.py runserver`.
You can specify a specific port to run the server, like: `python manage.py runserver 8888` to start the server on port 8888.

5. Open a browser and navigate to 127.0.0.1:8000/cms to see the app homepage.

6. Navigate to 127.0.0.1:8000/admin for the admin site.

## Things I am Doing Next (In Order):

1. Finishing up the front end.

2. Finalising the whole STL-to-image conundrum. Deciding on a package to use once and for all.

3. Add some tests.