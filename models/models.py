from ctypes.wintypes import tagSIZE
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship

from sqlalchemy import Table, Column, Integer, String, ForeignKey, Boolean

Base = declarative_base()

tag_todo_table = Table(
    "tag_todo",
    Base.metadata,
    Column("tag", ForeignKey("tag.id", ondelete='CASCADE'), primary_key=True),
    Column("todo", ForeignKey("todo.id", ondelete='CASCADE'), primary_key=True),
)

class Todo(Base):
    __tablename__ = "todo"
    json_serialize_keys = ["id", "title", "url", "completed", "order"]

    id = Column(Integer, primary_key=True)
    title = Column(String(50), nullable=False)
    url = Column(String(100), nullable=True)
    completed = Column(Boolean, nullable=True, default=False)
    order = Column("position", Integer, nullable=True)

    tags = relationship(
        "Tag", secondary=tag_todo_table, back_populates="todos"
    )

    def __repr__(self):
        return f"Todo(id={self.id!r}, title={self.title!r}, url={self.url!r}, completed={self.completed!r}, order={self.order!r})"
    
    def to_json(self, withRelationship: Boolean = False):
        res = {k:v for k,v in self.__dict__.items() if k in self.json_serialize_keys}
        if withRelationship:
            res.update({"tags": [tag.to_json() for tag in self.tags]})
        return res

    def __eq__(self, other):
        return isinstance(other, Todo) and  self.id == other.id

    def __hash__(self):
        return hash(self.id)

class Tag(Base):
    __tablename__ = "tag"
    json_serialize_keys = ["id", "title", "url", "todos"]

    id = Column(Integer, primary_key=True)
    title = Column(String(50), nullable=False, unique=True)
    url = Column(String(100), nullable=True)

    todos = relationship(
        "Todo", secondary=tag_todo_table, back_populates="tags"
    )

    def __repr__(self):
        return f"Tag(id={self.id!r}, title={self.title!r})"
    
    def to_json(self, withRelationship: Boolean = False):
        res = {k:v for k,v in self.__dict__.items() if k in self.json_serialize_keys}
        if withRelationship:
            res.update({"todos": [todo.to_json() for todo in self.todos]})
        return res
    
    def __eq__(self, other):
        return isinstance(other, Tag) and  self.id == other.id

    def __hash__(self):
        return hash(self.id)

def create(engine):
    Base.metadata.create_all(engine)