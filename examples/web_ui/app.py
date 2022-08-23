from aiohttp import web
import json
import anki
from car import Car

routes = web.RouteTableDef()
cars: dict[int, Car] = {}
config = ...
controller = anki.Controller()
with open('./config.json', 'r') as f:
    config = json.loads(''.join(f.readlines()))

async def build_response(id: int):
    if not id in cars:
        return {'error': f'The id {id} doesn\'t exists'}
    res = {
        'id': cars[id].id,
        'speed': cars[id].speed,
        'current_track_piece': cars[id].current_track_piece,
        'map': cars[id].map,
        'is_connected': cars[id].is_connected
    }
    return res

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
    res = await build_response(int(request.match_info['id']))
    return web.json_response(data=res)

@routes.post(r'/api/car/{id:\d+}')
async def create_car(request: web.Request):
    id = int(request.match_info['id'])
    cars[id] = Car(id, controller)
    await cars[id].create_vehicle()
    res = await build_response(id)
    return web.json_response(data=res)

@routes.delete(r'/api/car/{id:\d+}')
async def delete_car(request: web.Request):
    id = int(request.match_info['id'])
    await cars[id].delete()
    cars.pop(id)
    res = {
        'deleted': True
    }
    return web.json_response(data=res)

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