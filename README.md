# Some-service usage

## Setting up environment

Working directory is expected to be as such:

```bash
$ pwd
(...)/some-service
```

Some-service depends on external packages, thus correct environment must be set
before running the service. Assuming python in version **3.8** is present on the
server, virtual environment is to be set accordingly:

```bash
$ python -m venv venv
$ . venv/bin/activate
(venv) $ which python
(...)/some-service/venv/bin/python
(venv) $ python -m pip install -r requirements.txt
```

At this moment environment is ready for service to run properly.

---

## Running the service

If service is supposed to be ran from different working directory, `PYTHONPATH`
environment variable must be set correctly with:

```bash
(venv) $ export PYTHONPATH=`(...)/some-service`
```

After preparation, run the service with:
```bash
(venv) $ uvicorn some-service:app
```
With this setup, server should now start serving on `127.0.0.1:8000`, thus
performing get on `127.0.0.1:8000/` should yield a `"GET /HTTP/1.1" 200 OK`.

As well as `{"message": "Server OK"}` json in the browser.

---

## Development

As for development environment, additional requirements are to be fulfilled.
To do so simply run:
```bash
(venv) $ python -m pip install -r requirements-dev.txt
```
Which will complement lacking venv with packages used for typechecking, testing
or documentation pages generation.

---

## Configuration

Some Service needs environment variable to work correctly, without it GET requests
to `/api/v1/getSomeData` will fail with
`"GET /api/v1/getSomeData HTTP/1.1" 500 Internal Server Error`.

To avoid that, `MESSAGE_VALUE` environment variable must be set beforehand.

```bash
(venv) $ export MESSAGE_VALUE="message value"
```

Now server will work as intended.
