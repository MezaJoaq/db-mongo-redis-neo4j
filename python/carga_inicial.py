from pymongo import MongoClient
import redis 
import datetime
from databases import (usuarios,artistas,lugares,eventos,compras)

FECHA_REFERENCIA = "2026-10-01"
ahora = datetime.datetime.now()
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

def insert_redis(redis_client):
    #Carga inicial de las sesiones (como indica en el trabajo)
    usuarios_reserva = [3,6]
    sesiones_activas = [1,2,6]
    busquedas_recientes = ["rock","electrónica","folk","cumbia"]
    for sesion in sesiones_activas:
        #Creo la clave de redis
        clave = f"sesion:usuario:{sesion}"
        #Valor de la fecha de refencia mas la hora de sesion
        valor = f"{FECHA_REFERENCIA}/{ahora.time()}"
        #Define la sesion del cliente
        redis_client.set(clave, valor, ex= 1800)
    for id in usuarios_reserva:
        #Crea la clave de redis
        if(id == 3):
            clave = f"reserva:evento:5:usuario:{id}"
            valor = f"2"
        if(id == 6):
            clave = f"reserva:evento:4:usuario:{id}"
            valor = f"3"
        redis_client.set(clave,valor, ex = 600)
    for genero in busquedas_recientes:
        clave = f"busqueda:reciente:{genero}"
        if(genero == "rock"):
            valor = f"7"
        elif(genero == "electrónica"):
            valor = f"5"
        elif(genero == "folk"):
            valor = f"3"
        elif(genero == "cumbia"):
            valor = f"2"
        redis_client.set(clave,valor, ex = 300)

            
    