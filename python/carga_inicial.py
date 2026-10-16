from pymongo import MongoClient
from databases import (usuarios,artistas,lugares,eventos,compras)

#Insertar colecciones en mongodb
def insert_mongo(db):
    #Limpia las colecciones por si se vuelve a ejecutar la funcion
    db.usuarios.delete_many({})
    db.artistas.delete_many({})
    db.lugares.delete_many({})
    db.eventos.delete_many({})
    db.compras.delete_many({})
    #Inserta las bases de datos en las colecciones correspondientes
    db.usuarios.insert_many(usuarios)
    db.artistas.insert_many(artistas)
    db.lugares.insert_many(lugares)
    db.eventos.insert_many(eventos)
    db.compras.insert_many(compras)