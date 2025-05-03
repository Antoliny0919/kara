
### Installation

1. Clone the repo
   ```sh
   git clone https://github.com/Antoliny0919/kara.git
   ```
2. create your virtual environment
   ```sh
   python -m venv venv
   ```
   activate in Linux:
   ```sh
   source venv/bin/activate
   ```
   activate in Windows:
   ```sh
   venv\Scripts\activate
   ```

Update later...

### Testing

**Before running the tests, make sure to create and activate the virtual environment!**

> **Did you run it with Docker?**: You need to define the database-related environment variables before testing.
> ```shell
> DATABASE_URL=postgres://kara:kara@localhost:5432/kara
> POSTGRES_USER=kara
> POSTGRES_PASSWORD=kara
> POSTGRES_DB=kara
> ```

Tests can be written using [Django's TestCase syntax](https://docs.djangoproject.com/en/5.0/topics/testing/overview/)
or using [`pytest`](https://docs.pytest.org/).

To run the tests:

```shell
python manage.py test --settings=config.settings.test
or
pytest
```

There are also Playwright tests that can be run explicitly. These require the application to
be running in another terminal. To run the tests:

```shell
# Be sure playwright is properly installed and has a test user for accessing /admin
playwright install --with-deps
# This is the actual test command
pytest -m playwright
# Run the tests in headed mode (so you can see the browser)
pytest -m playwright --headed
