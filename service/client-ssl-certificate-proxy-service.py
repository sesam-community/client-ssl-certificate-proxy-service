import json
import requests
from flask import Flask, Response
import os
import logger
import cherrypy

app = Flask(__name__)
logger = logger.Logger('client-ssl-certificate-proxy-service')
pkey_file = 'pkey.pem'
cert_file = 'cert.pem'
ca_file = 'ca.pem'

url = os.environ.get("base_url")
username = os.environ.get("username")
pw = os.environ.get("password")
cert = os.environ.get("certificate").replace(r'\n', '\n')
pkey = os.environ.get("private_key").replace(r'\n', '\n')
ca = os.environ.get("ca_cert").replace(r'\n', '\n')


def write_certificate():
    open(pkey_file, 'wb').write(bytes(pkey, 'ascii'))
    open(cert_file, 'wb').write(bytes(cert, 'ascii'))
    open(ca_file, 'wb').write(bytes(ca, 'ascii'))


def stream_json(clean):
    first = True
    yield '['
    for i, row in enumerate(clean):
        if not first:
            yield ','
        else:
            first = False
        yield json.dumps(row)
    yield ']'


def stream_odata_json(odata):
    """fetch entities from given Odata url and dumps back to client as JSON stream"""
    first = True
    yield '['
    data = json.loads(odata)

    for value in data['value']:
        if not first:
            yield ','
        else:
            first = False

        value['_id'] = value['ProjectId']

        yield json.dumps(value)

    yield ']'


@app.route("/<path:path>", methods=["GET"])
def get(path):
    request_url = "{0}{1}".format(url, path)
    request_cert = (cert_file, pkey_file)

    logger.info("Request url: %s", request_url)

    try:
        request_data = requests.get(request_url, auth=(username, pw), cert=request_cert, verify=ca_file).text
        #entities = json.loads(request_data)
    except Exception as e:
        logger.warning("Exception occurred when download data from '%s': '%s'", request_url, e)
        raise

    return Response(stream_odata_json(request_data), mimetype='application/json')

    #return Response(
    #        stream_json(entities),
    #        mimetype='application/json'
    #    )


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
