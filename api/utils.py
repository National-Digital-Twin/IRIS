# SPDX-License-Identifier: Apache-2.0
# © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
# and is legally attributed to the Department for Business and Trade (UK) as the governing entity.

pass_through_headers = [
    "X-Auth-Request-Access-Token",
    "Authorization",
]

def get_headers(headers):
    forward_headers = {}
    for header in pass_through_headers:
        hv = headers.get(header)
        if hv is not None:
            forward_headers[header] = hv
    return forward_headers