from sqlalchemy.orm import Session
from models.models import Tag

from aiohttp import web

from sqlalchemy import *

async def get_all_tags(request):
    engine = request.app['db']
    with Session(engine) as session:
        allTags = session.query(Tag).all()

        return web.json_response(
            [tag.to_json(withRelationship=True) for tag in allTags]
        )

async def create_tag(request):
    data = await request.json()
    engine = request.app['db']

    try:
        newTag = Tag(**data)
        with Session(engine) as session:
            session.add(newTag)
            #Flush the Tag to the DB
            session.flush()
            #Assign url, commit transaction at last
            url = str(request.url.join(request.app.router['one_tag'].url_for(id=str(newTag.id))))
            newTag.url = url
            jsonTag = newTag.to_json()
            session.add(newTag)
            session.commit()
        return web.json_response(jsonTag)
    except Exception as e:
        web.json_response({'error': repr(e)}, status=500)

async def get_one_tag(request):
    engine = request.app['db']
    id = int(request.match_info['id'])

    with Session(engine) as session:
        tag = session.get(Tag, id)
    
        if tag:
            return web.json_response(tag.to_json(withRelationship=True))

        return web.json_response({'error': 'Tag not found'}, status=404)   

async def remove_all_tags(request):
    engine = request.app['db']
    with Session(engine) as session:
        session.query(Tag).delete()
        session.commit()
    return web.Response(status=204)

async def update_tag(request):
    engine = request.app['db']
    id = int(request.match_info['id'])

    with Session(engine) as session:
        toUpdateTag = session.get(Tag, id)

        if toUpdateTag is None:
            return web.json_response({'error': 'Tag not found'}, status=404)

        data = await request.json()
        for key, value in data.items():
            setattr(toUpdateTag, key, value)
        updatedJson = toUpdateTag.to_json()
        
        session.add(toUpdateTag)
        session.commit()

        return web.json_response(updatedJson)

def remove_tag(request):
    engine = request.app['db']
    id = int(request.match_info['id'])

    with Session(engine) as session:
        toDeleteTag = session.get(Tag, id)

        if toDeleteTag is None:
            return web.json_response({'error': 'Tag not found'}, status=404)
        session.delete(toDeleteTag)
        session.commit()
        return web.Response(status=204)

def get_todos(request):
    engine = request.app['db']
    id = int(request.match_info['id'])

    with Session(engine) as session:
        tag = session.get(Tag, id)

        if tag is None:
            return web.json_response({'error': 'Tag not found'}, status=404)

        return web.json_response([todo.to_json() for todo in tag.todos])