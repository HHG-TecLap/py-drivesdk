from aiohttp import web
import json

routes = web.RouteTableDef()
cars = []
config = ...
with open('./config.json', 'r') as f:
    config = json.loads(''.join(f.readlines()))

# Index
@routes.get('/')
async def index(request: web.Request):
    return web.Response(text='Index')
    pass

# Dashboard for the Cars
@routes.get(r'/car/{id:\d+}')
async def car_dashboard(request: web.Request):
    if int(request.match_info['id']) > int(config['max_cars']): return web.Response(status=400, text= 'The ID of the car is bigger than the max amount of cars')
    body = ...
    with open('./templates/car_dashboard.html') as f:
        body = ''.join(f.readlines()).replace(r'%id%', request.match_info['id'])
    return web.Response(body=body, content_type='text/html')
    pass


# API
@routes.get(r'/api/car/{id:\d+}')
async def car_informations(request: web.Request):
    web.json_response(data={'Test': 'Test'})


def app_factory() -> web.Application:
    app = web.Application()
    app.add_routes(routes)
    return app

def main():
    app = app_factory()
    # Launch app
    web.run_app(app, host=config['host'],port=config['port'])

if __name__ == "__main__":
    main()