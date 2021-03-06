import falcon
from falcon_cors import CORS
from .plugins import bootstrap as bootstrap_plugins
from .automation import bootstrap as bootstrap_automations
from .log import bootstrap as bootstrap_log


def configure():
    cors = CORS(allow_all_origins=True, allow_all_methods=True, allow_all_headers=True)

    api = falcon.API(middleware=[cors.middleware])

    bootstrap_plugins(api)
    bootstrap_automations(api)
    bootstrap_log(api)

    return api
