from pymongo import MongoClient
import redis 
import datetime
from neo4j import GraphDatabase
from databases import (usuarios,artistas,lugares,eventos,compras)

FECHA_REFERENCIA = "2026-10-01"
ahora = datetime.datetime.now()

def aumentar_precio_rosario(db):
    #Busca dinamicamente los ids en rosario
    lugares_rosario = db.lugares.find({"ciudad": "Rosario"})
    id_rosario = [lugar["lugar_id"] for lugar in lugares_rosario]

    db.eventos.update_many({"lugar_id" : id_rosario, 
                            "fecha": {"gte": FECHA_REFERENCIA}},
                           {"$mul": {"precio":1.10}  }
                           )
def agregar_servicio2(db):
    #Agrega con addToSet para no duplicar en la lista
    db.lugares.update_one({"lugar_id" : 2},
                            {"$addToSet": {"servicios": "accesibilidad"}}
                            )
def cancelar_evento7(db,redis_cliente):
    db.eventos.update_one({"evento_id" : 7},
                          {"$set" : {"estado" : "cancelado"}})

    db.compras.update_many({"evento_id" : 7, "estado" : "confirmada"},
                           {"$set" : {"estado" : "reembolsada"}})

    reserva = f"reserva:evento:7:*"
    claves_reserva = redis_cliente.keys(reserva)
    if claves_reserva:
        redis_cliente.delete(*claves_reserva)

def eliminar_usuario6():
    