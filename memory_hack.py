import falcon
from pathlib import Path
import os
from falcon_multipart.middleware import MultipartMiddleware
from app import ScriptResource, SearchResource, MainResource, AOBResource, InfoResource, CodeListResource
from app.main import initialize
from app.helpers.data_store import DataStore
from app.middleware.auth_middleware import BasicAuthMiddleware
from hypercorn.config import Config
from hypercorn.asyncio import serve
import asyncio

if __name__ == '__main__':
    pt = Path(__file__).parent.joinpath('app')
    os.chdir(pt)
    
    auth_middleware = BasicAuthMiddleware()
    
    app = falcon.App(middleware=[MultipartMiddleware()])
    
    # Add auth middleware using add_middleware method
    app.add_middleware(auth_middleware)
    
    initialize()
    app.add_route('/', MainResource())
    app.add_route('/search', SearchResource())
    app.add_route('/codelist', CodeListResource())
    app.add_route('/script', ScriptResource())
    app.add_route('/aob', AOBResource())
    app.add_route('/info', InfoResource())
    app.add_static_route('/resources/static', pt.joinpath("resources/static/").absolute())

    config = Config()
    config.bind = ["0.0.0.0:5000"]
    root = Path(__file__).parent
    config.certfile = str(root / "cert.pem")
    config.keyfile = str(root / "key.pem")
    config.use_reloader = True

    print('Serving on https://0.0.0.0:5000...')

    asyncio.run(serve(app, config))