from sqlalchemy.orm import Session
from models.models import Todo, Tag

from aiohttp import web

from sqlalchemy import *

async def get_all_todos(request):
    engine = request.app['db']
    with Session(engine) as session:
        allTodos = session.query(Todo).all()
        allTodosJson = [todo.to_json(withRelationship=True) for todo in allTodos]

    return web.json_response(
        allTodosJson
    )

async def create_todo(request):
    data = await request.json()
    engine = request.app['db']

    try:
        newTodo = Todo(**data)
        with Session(engine) as session:
            session.add(newTodo)
            #Flush the todo to the DB
            session.flush()
            #Assign url, commit transaction at last
            url = str(request.url.join(request.app.router['one_todo'].url_for(id=str(newTodo.id))))
            newTodo.url = url
            session.add(newTodo)
            jsonTodo = newTodo.to_json()
            session.commit()
        return web.json_response(jsonTodo)
    except Exception as e:
        web.json_response({'error': repr(e)}, status=500)

async def get_one_todo(request):
    engine = request.app['db']
    id = int(request.match_info['id'])

    with Session(engine) as session:
        todo = session.get(Todo, id)
    
        if todo:
            return web.json_response(todo.to_json(withRelationship=True))
        return web.json_response({'error': 'Todo not found'}, status=404)   

async def remove_all_todos(request):
    engine = request.app['db']
    with Session(engine) as session:
        session.query(Todo).delete()
        session.commit()
    return web.Response(status=204)

async def update_todo(request):
    engine = request.app['db']
    id = int(request.match_info['id'])

    with Session(engine) as session:
        toUpdateTodo = session.get(Todo, id)

        if toUpdateTodo is None:
            return web.json_response({'error': 'Todo not found'}, status=404)

        data = await request.json()
        for key, value in data.items():
            setattr(toUpdateTodo, key, value)
        updatedJson = toUpdateTodo.to_json()
        
        session.add(toUpdateTodo)
        session.commit()

        return web.json_response(updatedJson)

def remove_todo(request):
    engine = request.app['db']
    id = int(request.match_info['id'])

    with Session(engine) as session:
        toDeleteTodo = session.get(Todo, id)

        if toDeleteTodo is None:
            return web.json_response({'error': 'Todo not found'}, status=404)
        session.delete(toDeleteTodo)
        session.commit()
        return web.Response(status=204)

def get_tags(request):
    engine = request.app['db']
    id = int(request.match_info['id'])

    with Session(engine) as session:
        todo = session.get(Todo, id)

        if todo is None:
            return web.json_response({'error': 'Todo not found'}, status=404)

        return web.json_response([tag.to_json() for tag in todo.tags])

async def tag(request):
    engine = request.app['db']
    id = int(request.match_info['id'])
    data = await request.json()

    #Retrieve tag ID
    try:
        tagID = data['id']
    except KeyError:
        return web.json_response({'error': 'Please provide tag ID in order to tag this TODO'}, status=400)

    #Retrieve tag to append
    with Session(engine) as session:
        tag = session.get(Tag, tagID)

        if tag is None:
            return web.json_response({'error': 'Tag not found'}, status=404)

    #Add Tag to todo's list, commit in order to add the relation to the rel table (sqlalchemy)
    with Session(engine) as session:
        todo = session.get(Todo, id)

        if todo is None:
            return web.json_response({'error': 'Todo not found'}, status=404)

        todo.tags.append(tag)
        tagAsJson = tag.to_json()
        session.add(todo)
        session.commit()
    return web.json_response(tagAsJson)

async def remove_todo_tag(request):
    engine = request.app['db']
    id = int(request.match_info['id'])
    tagID = int(request.match_info['tag_id'])

    #Retrieve tag to remove
    with Session(engine) as session:
        tag = session.get(Tag, tagID)

        if tag is None:
            return web.json_response({'error': 'Tag not found'}, status=404)

    with Session(engine) as session:
        todo = session.get(Todo, id)

        if todo is None:
            return web.json_response({'error': 'Todo not found'}, status=404)

        if tag not in todo.tags:
            return web.json_response({'error': "Tag not found whithing todo's tags"}, status=404)

        todo.tags.remove(tag)
        session.add(todo)
        session.commit()
        
    return web.Response(status=204)

async def delete_tags(request):
    engine = request.app['db']
    id = int(request.match_info['id'])

    with Session(engine) as session:
        todo = session.get(Todo, id)

        if todo is None:
            return web.json_response({'error': 'Todo not found'}, status=404)

        todo.tags.clear()
        session.add(todo)
        session.commit()
    return web.Response(status=204)