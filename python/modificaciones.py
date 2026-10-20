from pymongo import MongoClient
import redis 
import datetime
from neo4j import GraphDatabase
from databases import (usuarios,artistas,lugares,eventos,compras)

FECHA_REFERENCIA = "2026-10-01"
ahora = datetime.datetime.now()
#1
def aumentar_precio_rosario(db):
    #Busca dinamicamente los ids en rosario
    lugares_rosario = db.lugares.find({"ciudad": "Rosario"})
    id_rosario = [lugar["lugar_id"] for lugar in lugares_rosario]

    db.eventos.update_many({"lugar_id" : id_rosario, 
                            "fecha": {"gte": FECHA_REFERENCIA}},
                           {"$mul": {"precio":1.10}  }
                           )
#2
def agregar_servicio2(db):
    #Agrega con addToSet para no duplicar en la lista
    db.lugares.update_one({"lugar_id" : 2},
                            {"$addToSet": {"servicios": "accesibilidad"}}
                            )
#3
def cancelar_evento7(db,redis_cliente):
    db.eventos.update_one({"evento_id" : 7},
                          {"$set" : {"estado" : "cancelado"}})

    db.compras.update_many({"evento_id" : 7, "estado" : "confirmada"},
                           {"$set" : {"estado" : "reembolsada"}})

    reserva = f"reserva:evento:7:*"
    claves_reserva = redis_cliente.keys(reserva)
    if claves_reserva:
        redis_cliente.delete(*claves_reserva)
#4
def eliminar_usuario6(db,redis_cliente,usuario_id,driver):
    db.usuarios.delete_one({"usuario_id" : usuario_id})
    #Las compras deberian quedar en el sistema porque son informacion necesaria para el negocio
    db.compras.update_many({"usuario_id" : usuario_id},
                           {"$set" : {"estado" : "anulado"}})
    #Elimino al usuario de las otras bases
    sesiones_eliminada = f"sesion:usuario:{usuario_id}"
    reserva_eliminada = f"reserva:evento:*:usuario:{usuario_id}"
    claves_sesion = redis_cliente.keys(sesiones_eliminada)
    claves_reserva = redis_cliente.keys(reserva_eliminada)
    redis_cliente.delete(*claves_sesion)
    redis_cliente.delete(*claves_reserva)

    usuario_neo4j = f"""MATCH (u:Usuario {usuario_id: $usuario_id}) DETACH DELETE u"""

    with driver.session() as session:
        resultado = session.run(usuario_neo4j, usuario_id = usuario_id)
#5
def eliminar_amistades(usuario_id,db,driver):
    usuario_neo4j = f"""MATCH (u:Usuario {usuario_id: $usuario_id})-[r:AMIGO_DE]-()
                        DELETE r"""
    with driver.session() as session:
            resultado = session.run(usuario_neo4j, usuario_id = usuario_id)
    
