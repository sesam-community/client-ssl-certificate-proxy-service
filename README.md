## Client side SSL certificate proxy service

A simple service that serves as a proxy for signing request calls to an API with a client side SSL certificate (PFX).

[![SesamCommunity CI&CD](https://github.com/sesam-community/client-ssl-certificate-proxy-service/actions/workflows/sesam-community-ci-cd.yml/badge.svg)](https://github.com/sesam-community/client-ssl-certificate-proxy-service/actions/workflows/sesam-community-ci-cd.yml)

### Environment variables:

`base_url` - the base url of the API service.

`certificate` - the certificate content of the PFX file.

`private_key` - the private key content of the PFX file.

`username` - username to the API service.

`password` - password to the API service.

`log_response_data` - set this value to true to log the received data for debugging purposes, default value: false.


### Example system config:

```json
{
  "_id": "client-ssl-certificate-proxy-system",
  "type": "system:microservice",
  "docker": {
    "environment": {
      "base_url": "https://base.url.to.api/",
      "certificate": "$SECRET(pfx_certificate)",
      "private_key": "$SECRET(pfx_privatekey)",
      "username": "username-to-api",
      "password": "$SECRET(secret-password-to-api)",
      "page_number": "1",
      "page_size": "1000",
      "protocol": "json"
    },
    "image": "sesamcommunity/client-ssl-certificate-proxy-service:latest",
    "port": 5001
  }
}

```

### Example pipe using the microservice above

```json
{
  "_id": "client-ssl-certificate-proxy-pipe",
  "type": "pipe",
  "source": {
    "is_chronological": false,
    "is_since_comparable": false,
    "supports_since": false,
    "system": "client-ssl-certificate-proxy-system",
    "type": "json",
    "url": "api-path"
  }
}

```