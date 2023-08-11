# wallet-backend-django
Mini wallet API backend service with Django

### Features
<hr>

1. Initialize wallet account
2. Enable & disabled wallet
3. View Wallet
4. View Transaction
5. Deposit & withdrawn money

### Requirements
<hr>

1. Python 3.8+
2. Docker

### Local Configuration
<hr>

1. clone source code from github

2. go to project directory

   ```shell
   cd wallet-backend-django
   ```

3. create your own project env
   ```shell
   python3 -m venv env
   ```

4. activate your project env
   ``` shell
   source env/bin/activate
   ```

5. go to your project directory and install requirement.txt

   ```shell
   pip install requirement.txt
   ```
   
6. run docker compose

   ```shell
   docker compose up -d
   ```

7. migrate all models to database.

   for sending your models structure to database used command

   ```shell
   python3 manage.py migrate
   ```

   if you have any changes in your models.py, to push your model to database :

   ```shell
   python3 manage.py makemigrations
   ```
   ( this command will create a migrations version inside migrations/version folder)

   then

   ```shell
   python3 manage.py migrate
   ```
   
8. then run the apps.
   ```shell
   python3 manage.py runserver
   ```

### Run The Test and Coverage
<hr>

1. run test case.
   ```shell
   python3 manage.py test
   ```
   
   the output should be like this:
   ```shell
   Found 8 test(s).
   Creating test database for alias 'default'...
   System check identified no issues (0 silenced).
   ........
   ----------------------------------------------------------------------
   Ran 8 tests in 2.507s
   
   OK
   Destroying test database for alias 'default'...
   ```
   
2. run test coverage.
   ```shell
   coverage run --source='.' manage.py test src.wallet
   coverage report
   ```
   
   the output should be like this:
   ```shell
   Found 8 test(s).
   Creating test database for alias 'default'...
   System check identified no issues (0 silenced).
   ........
   ----------------------------------------------------------------------
   Ran 8 tests in 2.512s
   
   OK
   Destroying test database for alias 'default'...
   
   Name                                    Stmts   Miss  Cover
   -----------------------------------------------------------
   manage.py                                  12      2    83%
   src/__init__.py                             0      0   100%
   src/asgi.py                                 4      4     0%
   src/settings.py                            21      0   100%
   src/urls.py                                 2      0   100%
   src/wallet/__init__.py                      0      0   100%
   src/wallet/admin.py                         1      0   100%
   src/wallet/apps.py                          4      0   100%
   src/wallet/decorators.py                   36      0   100%
   src/wallet/factory.py                      21      0   100%
   src/wallet/migrations/0001_initial.py       8      0   100%
   src/wallet/migrations/__init__.py           0      0   100%
   src/wallet/models.py                       46      6    87%
   src/wallet/serializers.py                  53      0   100%
   src/wallet/tests.py                       128      0   100%
   src/wallet/urls.py                          3      0   100%
   src/wallet/utils.py                         4      0   100%
   src/wallet/views.py                       102      0   100%
   src/wsgi.py                                 4      4     0%
   -----------------------------------------------------------
   TOTAL                                     449     16    96%
   ```
### Postman
<hr>

You can try API with postman by import the [collection](Wallet.postman_collection.json) and [environment](Wallet.postman_environment.json) file
