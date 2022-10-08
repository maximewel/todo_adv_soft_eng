import logging
from aiohttp import web
import aiohttp_cors
import aiomysql

TODOS = {
    0: {'title': 'build an API', 'order': 1, 'completed': False},
    1: {'title': '?????', 'order': 2, 'completed': False},
    2: {'title': 'profit!', 'order': 3, 'completed': False}
}

def completed_to_bool(todo: dict) -> None:
    try:
        todo['completed'] = bool(todo['completed'])
        todo['order'] = todo.pop('position')
    except KeyError:
        print(f"OY")

async def get_all_todos(request):
    db: aiomysql.Connection = request.app['db']
    cursor: aiomysql.Cursor = await db.cursor()
    sql = "SELECT * FROM todo"
    await cursor.execute(sql)
    res = await cursor.fetchall()

    for r in res:
        completed_to_bool(r)

    print(res)

    return web.json_response(
        res
    )

def remove_all_todos(request):
    TODOS.clear()
    return web.Response(status=204)

def get_one_todo(request):
    id = int(request.match_info['id'])

    if id not in TODOS:
        return web.json_response({'error': 'Todo not found'}, status=404)

    return web.json_response({'id': id, **TODOS[id]})

async def create_todo(request):
    data = await request.json()

    if 'title' not in data:
        return web.json_response({'error': '"title" is a required field'})
    title = data['title']
    if not isinstance(title, str) or not len(title):
        return web.json_response({'error': '"title" must be a string with at least one character'})

    data['completed'] = bool(data.get('completed', False))
    new_id = max(TODOS.keys(), default=0) + 1
    data['url'] = str(request.url.join(request.app.router['one_todo'].url_for(id=str(new_id))))

    TODOS[new_id] = data

    return web.Response(
        headers={'Location': data['url']},
        status=303
    )

async def update_todo(request):
    id = int(request.match_info['id'])

    if id not in TODOS:
        return web.json_response({'error': 'Todo not found'}, status=404)

    data = await request.json()
    TODOS[id].update(data)

    return web.json_response(TODOS[id])

def remove_todo(request):
    id = int(request.match_info['id'])

    if id not in TODOS:
        return web.json_response({'error': 'Todo not found'})

    del TODOS[id]

    return web.Response(status=204)

async def create_connection() -> aiomysql.Connection:
    conn = await aiomysql.connect(
                                    host='127.0.0.1', port=3306,
                                    user='root', password='root', db='todo_db',
                                    cursorclass = aiomysql.cursors.DictCursor
                                )
    return conn

async def init_router(app: web.Application) -> None:
    # Configure default CORS settings.
    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
                allow_methods="*",
            )
    })

    cors.add(app.router.add_get('/todos/', get_all_todos, name='all_todos'))
    cors.add(app.router.add_delete('/todos/', remove_all_todos, name='remove_todos'))
    cors.add(app.router.add_post('/todos/', create_todo, name='create_todo'))
    cors.add(app.router.add_get('/todos/{id:\d+}', get_one_todo, name='one_todo'))
    cors.add(app.router.add_patch('/todos/{id:\d+}', update_todo, name='update_todo'))
    cors.add(app.router.add_delete('/todos/{id:\d+}', remove_todo, name='remove_todo'))

async def app_factory() -> web.Application:
    app = web.Application()

    #Add DB to app
    db = await create_connection()
    app['db'] = db

    #Add routes
    await init_router(app)

    logging.basicConfig(level=logging.DEBUG)

    return app

if __name__ == '__main__':
    web.run_app(app_factory(), port=8080)