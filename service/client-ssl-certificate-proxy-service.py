import requests
from flask import Flask, Response, request
import os
import logger
import cherrypy
import json

app = Flask(__name__)
logger = logger.Logger('client-ssl-certificate-proxy-service')
pkey_file = 'pkey.pem'
cert_file = 'cert.pem'

url = os.environ.get("base_url")
username = os.environ.get("username")
pw = os.environ.get("password")
cert = os.environ.get("certificate").replace(r'\n', '\n')
pkey = os.environ.get("private_key").replace(r'\n', '\n')
log_response_data = os.environ.get("log_response_data", "false").lower() == "true"
headers = json.loads('{"Content-Type": "application/json"}')


class BasicUrlSystem:
    def __init__(self, config):
        self._config = config

    def make_session(self):
        session = requests.Session()
        session.headers = self._config["headers"]
        session.verify = True
        return session


session_factory = BasicUrlSystem({"headers": headers})


def write_certificate():
    open(pkey_file, 'wb').write(bytes(pkey, 'ascii'))
    open(cert_file, 'wb').write(bytes(cert, 'ascii'))


@app.route("/<path:path>", methods=["GET"])
def get(path):
    request_url = "{0}{1}".format(url, path)
    request_cert = (cert_file, pkey_file)

    logger.info("Request url: %s", request_url)

    try:
        with session_factory.make_session() as s:
            request_data = s.request("GET", request_url, auth=(username, pw), cert=request_cert, headers=headers)
            #request_data = requests.get(request_url, auth=(username, pw), cert=request_cert)
            if log_response_data:
                logger.info("Data received: '%s'", request_data.text)
    except Exception as e:
        logger.warning("Exception occurred when download data from '%s': '%s'", request_url, e)
        raise

    return Response(
            request_data,
            mimetype='application/json'
        )


if __name__ == '__main__':
    write_certificate()

    cherrypy.tree.graft(app, '/')

    # Set the configuration of the web server to production mode
    cherrypy.config.update({
        'environment': 'production',
        'engine.autoreload_on': False,
        'log.screen': True,
        'server.socket_port': 5002,
        'server.socket_host': '0.0.0.0'
    })

    # Start the CherryPy WSGI web server
    cherrypy.engine.start()
    cherrypy.engine.block()
