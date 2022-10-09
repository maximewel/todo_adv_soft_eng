import logging
from aiohttp import web
import aiohttp_cors

import sqlalchemy
from sqlalchemy import *

from models.models import create
from controllers.todo import *
from controllers.tags import *

async def create_connection(databaseConfig: dict) -> sqlalchemy.engine.Engine:
    engine = create_engine(f"mysql+pymysql://{databaseConfig['username']}:{databaseConfig['password']}@{databaseConfig['dbLocation']}/{databaseConfig['dbName']}?charset=utf8mb4")
    create(engine)
    return engine

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

    #TODOs
    #CRUD
    cors.add(app.router.add_get('/todos/', get_all_todos, name='all_todos'))
    cors.add(app.router.add_delete('/todos/', remove_all_todos, name='remove_todos'))
    cors.add(app.router.add_post('/todos/', create_todo, name='create_todo'))
    cors.add(app.router.add_get('/todos/{id:\d+}', get_one_todo, name='one_todo'))
    cors.add(app.router.add_patch('/todos/{id:\d+}', update_todo, name='update_todo'))
    cors.add(app.router.add_delete('/todos/{id:\d+}', remove_todo, name='remove_todo'))
    #Relationship
    cors.add(app.router.add_get('/todos/{id:\d+}/tags/', get_tags, name='list_todo_tags'))
    cors.add(app.router.add_post('/todos/{id:\d+}/tags/', tag, name='associate_tag'))
    cors.add(app.router.add_delete('/todos/{id:\d+}/tags/', delete_tags, name='delete_tags'))
    cors.add(app.router.add_delete('/todos/{id:\d+}/tags/{tag_id:\d+}', remove_todo_tag, name='remove_tag_from_todo'))

    #TAGS
    cors.add(app.router.add_get('/tags/', get_all_tags, name='all_tags'))
    cors.add(app.router.add_delete('/tags/', remove_all_tags, name='remove_tags'))
    cors.add(app.router.add_post('/tags/', create_tag, name='create_tag'))
    cors.add(app.router.add_get('/tags/{id:\d+}', get_one_tag, name='one_tag'))
    cors.add(app.router.add_patch('/tags/{id:\d+}', update_tag, name='update_tag'))
    cors.add(app.router.add_delete('/tags/{id:\d+}', remove_tag, name='remove_tag'))
    #Relationship
    cors.add(app.router.add_get('/tags/{id:\d+}/todos/', get_todos, name='list_tag_todos'))

async def app_factory(databaseConfig: dict) -> web.Application:
    app = web.Application()

    #Add DB to app
    engine = await create_connection(databaseConfig)
    app['db'] = engine

    #Add routes
    await init_router(app)

    logging.basicConfig(level=logging.DEBUG)

    return app

databaseConfig = {
        "username": "root",
        "password": "root",
        "dbLocation": "localhost",
        "dbName": "todo_db"
    }

if __name__ == '__main__':
    web.run_app(app_factory(databaseConfig), port=8080)