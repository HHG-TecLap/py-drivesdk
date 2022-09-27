from aiohttp import web
import json
import anki
import time

routes = web.RouteTableDef()
vehicles: dict[int, anki.Vehicle] = {}
config = ...
controller = anki.Controller()
with open('./config.json', 'r') as f:
    config = json.loads(''.join(f.readlines()))

async def build_response(id: int):
    if not id in vehicles:
        return web.json_response(data={'error': f'The id {id} doesn\'t exists'}, status=404)

    json_map = []
    current_track_piece = None
    current_lane = None
    if vehicles[id].map:
        for j in vehicles[id].map:
            json_map.append({'clockwise': j.clockwise, 'type_name': j.type.name, 'loc': j.loc})
    
    if vehicles[id].current_track_piece: current_track_piece = {'clockwise': vehicles[id].current_track_piece.clockwise, 'type': vehicles[id].current_track_piece.type.name, 'loc': vehicles[id].current_track_piece.loc}

    if vehicles[id].road_offset == ...: road_offset = None
    else: road_offset = vehicles[id].road_offset

    if vehicles[id].current_lane4: current_lane = vehicles[id].current_lane4.lane_name

    res = {
        'id': vehicles[id].id,
        'speed': vehicles[id].speed,
        'current_track_piece': current_track_piece,
        'map_position': vehicles[id].map_position,
        'map': json_map,
        'is_connected': vehicles[id].is_connected,
        'current_lane': current_lane,
        'road_offset': road_offset
    }
    return web.json_response(data=res)

async def edit_car(id: int, jsonPayload) -> web.json_response:
    for key in jsonPayload:
        if key == 'speed':
            await vehicles[id].setSpeed(speed=jsonPayload[key])

        elif key == 'is_connected':
            if jsonPayload[key] == True and vehicles[id].is_connected == False:
                try:
                    vehicles[id].connect()
                except:
                    return web.json_response({'error': 'Server got itself in trouble'}, status=500)
            elif jsonPayload[key] == False and vehicles[id].is_connected == True:
                try:
                    vehicles[id].disconnect()
                except:
                    return web.json_response({'error': 'Server got itself in trouble'}, status=500)

        elif key == 'id':
            return web.json_response({'error': 'You can\'t edit the id'}, status=400)

        elif key == 'map':
            return web.json_response({'error': 'You can\'t edit the map'}, status=400)

        elif key == 'current_track_piece':
            return web.json_response({'error': 'You can\'t edit the current track piece'}, status=400)

        else:
            pass
    
    return await build_response(id=id)

# Index
@routes.get('/')
async def index(request: web.Request):
    return web.Response(text='Index')

# Dashboard for the Cars
@routes.get(r'/car/{id:\d+}')
async def car_dashboard(request: web.Request):
    if int(request.match_info['id']) > int(config['max_cars']): return web.Response(status=400, text= 'The ID of the car is bigger than the max amount of cars')
    body = ...
    with open('./templates/car_dashboard.html') as f:
        body = ''.join(f.readlines()).replace(r'%id%', request.match_info['id'])
    return web.Response(body=body, content_type='text/html')


# API
@routes.get(r'/api/car/{id:\d+}')
async def get_car_information(request: web.Request):
    return await build_response(int(request.match_info['id']))

@routes.post(r'/api/car/{id:\d+}')
async def create_car(request: web.Request):
    id = int(request.match_info['id'])
    if id in vehicles:
        return web.json_response(data={'error': f'The id {id} already exists'}, status=400)
    vehicles[id] = await controller.connectOne(id)
    return await build_response(id)

@routes.delete(r'/api/car/{id:\d+}')
async def delete_car(request: web.Request):
    id = int(request.match_info['id'])
    if not id in vehicles:
        return web.json_response(data={'error': f'The id {id} doesn\'t exists'}, status=404)
    await vehicles[id].disconnect()
    vehicles.pop(id)
    res = {
        'deleted': True
    }
    return web.json_response(data=res)

@routes.patch(r'/api/car/{id:\d+}')
async def patch_car(request: web.Request):
    id = int(request.match_info['id'])
    if not id in vehicles:
        return web.json_response(data={'error': f'The id {id} doesn\'t exists'}, status=404)
    if not request.body_exists:
        return web.json_response(data={'error': 'No request body'}, status=400)

    return await edit_car(id=id, jsonPayload=await request.json())

@routes.post('/api/scan')
async def scan(request: web.Request):
    if controller.map:
        return web.json_response({'error': 'The map is already scanned'}, status=409)
    map_obj = await controller.scan(align_pre_scan=True)
    res = []
    for j in map_obj:
        res.append({'clockwise': j.clockwise, 'type_name': j.type.name, 'loc': j.loc})
    return web.json_response({'map': res})

# ws
@routes.get('/api/ws')
async def ws_hanler(request: web.Request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    async for msg in ws:
        content = msg.json()
        if content['type'] == 'get':
            await ws.send_json(data={'test': 'DATA'})
        elif content['type'] == 'edit':
            pass

    print('websocket connection closed')

    return ws
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
