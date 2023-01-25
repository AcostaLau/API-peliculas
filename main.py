
# el path sirve para el tipo de parametros de ruta y query para tipos de parametros query
from fastapi import FastAPI, Body, Path, Query, Request, HTTPException, Depends


# me sirve para enviar contenido en formato json
from fastapi.responses import JSONResponse
# me permite crear esquemas, field sirve para validar datos
from pydantic import BaseModel, Field

from typing import Optional

from fastapi.security import HTTPBearer
from jwt_manager import create_token, validate_token
app = FastAPI()


# de esta manera le cambio el titulo a mi aplicacion
app.title = "Mi aplicacion con Fast APi"
# puedo cambiar la version de la app con este comando
# app.version = "0.0.1"


class JTWBearer(HTTPBearer):
    async def __call__(self, request: Request):
        auth = await super().__call__(request)
        data = validate_token(auth.credentials)
        if data['email'] != "admin@gmail.com":
            raise HTTPException(
                status_code=403, detail="Las credernciales son invalidas")


class User(BaseModel):
    email: str
    password: str


class Movie(BaseModel):
    # le digo que puede ser de tipo entero o None y que por defecto sea None
    id: Optional[int] = None
    # con el field estamos validando el input, de forma que tiene que tener 1 como minimo y 15 como maximo
    title: str = Field(min_length=1, max_length=15)

    overview: str = Field(min_length=1, max_length=100)

    # con le le indico el maximo del numero que puede ir
    year: int = Field(le=2023)

    rating: float = Field(le=10, ge=1)

    category: str = Field(min_length=1, max_length=15)

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "title": 'Nombre pelicula',
                "overview": "Resumen pelicula",
                "year": 2023,
                "rating": 9.2,
                "category": "Categoria de la pelicula"
            }
        }


movies = [
    {
        "id": 1,
        "title": "Avatar",
        "overview": "En un exuberante planeta llamado Pandora viven los Na'vi, seres que ...",
        "year": "2009",
        "rating": 7.8,
        "category": "Accion"
    }
]


@app.get("/", tags=['Home'])
def read_root():
    return {"Hello": "World"}


@app.post("/login", tags=["auth"])
def login(user: User):
    if user.email == "admin@gmail.com" and user.password == "admin":
        token: str = create_token(user.dict())
    return JSONResponse(content=token, status_code=200)


# devuelvo listado de peliculas


@app.get('/movies', tags=['movies'], status_code=200, dependencies=[Depends(JTWBearer)])
def get_movies():
    return JSONResponse(content=movies, status_code=200)


# busco la pelicula por su id, parametros de ruta
@app.get('/movies/{id}', tags=['movies'], status_code=200)
# estoy validando que el paraemtro sea mayor o igual a 1 y menor o igual que 2000
def get_movie(id: int = Path(ge=1, le=2000)):
    movie = list(filter(lambda x: x['id'] == id, movies))
    if movie:
        return JSONResponse(content=movie, status_code=200)
    else:
        return JSONResponse(content=[], status_code=404)

# filtro peliculas por categoria, parametros query


@app.get('/movies/', tags=['movies'])
def get_movies_category(category: str = Query(min_length=5, max_length=15)):
    movie = list(filter(lambda x: x['category'] == category, movies))

    if movie:
        return JSONResponse(content=movie)
    else:
        return JSONResponse(content=[])


@app.post('/movies', tags=['movies'], status_code=201)
def create_movie(movie: Movie):
    # el objeto a diccionario para mantener la integridad de la lista original
    movies.append(dict(movie))
    for item in movies:
        print(type(item))
    return JSONResponse(content={"mensaje": "Se ha registrado la pelicula"}, status_code=201)


# para modificar la pelicula necesitamos el id, por eso lo requerimos como parametro de ruta
@app.put('/movies/{id}', tags=['movies'], status_code=200)
def modificate_movie(id: int, movie: Movie) -> dict:
    for movie_item in movies:
        if movie_item['id'] == id:

            # El operador ** es utilizado para desempaquetar un diccionario en argumentos de una función. En este caso, se está utilizando para crear una nueva instancia de la clase Movie y asignarle los valores del diccionario que se obtiene al llamar al método dict() en la instancia movie.

            new_movie = Movie(**movie.dict())
            movie_item.update(new_movie.dict())
            return JSONResponse(content={"mensaje": "la pelicula ha sido modificada"}, status_code=200)


# elimino un elemento de la lista


@app.delete('/movies/{id}', tags=['movies'], status_code=200)
def delete_movie(id: int):
    for movie in movies:
        if movie['id'] == id:
            movies.remove(movie)
            return JSONResponse(content={
                "mensaje": "Se ha eliminado correctamente"
            }, status_code=200)
        else:
            return JSONResponse(content={
                "mensaje": "No se encuentra esa pelicula"
            })
