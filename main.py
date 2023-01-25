
# el path sirve para el tipo de parametros de ruta y query para tipos de parametros query
from fastapi import FastAPI, Body, Path, Query

# me permite crear esquemas, field sirve para validar datos
from pydantic import BaseModel, Field

from typing import Optional

app = FastAPI()


# de esta manera le cambio el titulo a mi aplicacion
app.title = "Mi aplicacion con Fast APi"
# puedo cambiar la version de la app con este comando
# app.version = "0.0.1"


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


# devuelvo listado de peliculas
@app.get('/movies', tags=['movies'])
def get_movies():
    return movies


# busco la pelicula por su id, parametros de ruta
@app.get('/movies/{id}', tags=['movies'])
# estoy validando que el paraemtro sea mayor o igual a 1 y menor o igual que 2000
def get_movie(id: int = Path(ge=1, le=2000)):
    movie = list(filter(lambda x: x['id'] == id, movies))
    if movie:
        return movie if len(movie) > 0 else 'No se encontro esa pelicula'
    else:
        return []

# filtro peliculas por categoria, parametros query


@app.get('/movies/', tags=['movies'])
def get_movies_category(category: str = Query(min_length=5, max_length=15)):
    movie = list(filter(lambda x: x['category'] == category, movies))

    if movie:
        return movie
    else:
        return []


@app.post('/movies', tags=['movies'])
def create_movie(movie: Movie):
    # el objeto a diccionario para mantener la integridad de la lista original
    movies.append(dict(movie))
    for item in movies:
        print(type(item))
    return movies


# para modificar la pelicula necesitamos el id, por eso lo requerimos como parametro de ruta
@app.put('/movies/{id}', tags=['movies'])
def modificate_movie(id: int, movie: Movie) -> dict:
    for movie_item in movies:
        if movie_item['id'] == id:

            # El operador ** es utilizado para desempaquetar un diccionario en argumentos de una función. En este caso, se está utilizando para crear una nueva instancia de la clase Movie y asignarle los valores del diccionario que se obtiene al llamar al método dict() en la instancia movie.

            new_movie = Movie(**movie.dict())
            movie_item.update(new_movie.dict())
            return movie_item


# elimino un elemento de la lista


@app.delete('/movies/{id}', tags=['movies'])
def delete_movie(id: int):
    for movie in movies:
        if movie['id'] == id:
            movies.remove(movie)
            return movies
        else:
            return 'No existe ese id'
