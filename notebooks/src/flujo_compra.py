from pymongo import MongoClient
import redis 
import datetime
from neo4j import GraphDatabase
from notebooks.src.databases import (usuarios,artistas,lugares,eventos,compras)

FECHA_REFERENCIA = "2026-10-01"
ahora = datetime.datetime.now()

def reservar_entrada(id_usuario,id_evento,cant,redis_client):
    #Crea la clave de redis
    sesion = f"sesion:usuario:{id_usuario}"
    if redis_client.exists(sesion):
        #if(CONSULTA DE TOTAL DE ENTRADAS (CAMBIAR CUANDO SE HAGA EL PUNTO 3):
        clave = f"reserva:evento:{id_evento}:usuario:{id_usuario}"
        valor = f"{cant}"
        redis_client.set(clave,valor, ex = 600)
    else:
        print("El usuario no posee una sesion activa")

def confirmar_reserva(db,redis_client,id_usuario,id_evento):
    reserva_vigente = f"reserva:evento:{id_evento}:usuario:{id_usuario}"
    
    if redis_client.exists(reserva_vigente):
        cantidad = int(redis_client.get(reserva_vigente))
        
        ultima_compra = db.compras.find_one(sort=[("compra_id", -1)])
        nueva_id = (ultima_compra["compra_id"] + 1) if ultima_compra else 1

        precio_evento = db.eventos.find_one({"evento_id" : id_evento})
        
        compra_gen = {
                            "compra_id" : nueva_id,
                            "usuario_id" : id_usuario,
                            "evento_id" : id_evento,
                            "cantidad" : cantidad,
                            "precio_unitario" : precio_evento["precio"],
                            "total" : cantidad * precio_evento["precio"],
                            "fecha_compra" : FECHA_REFERENCIA,
                            "estado" : "confirmada"
                        }
        db.compras.insert_one(compra_gen)
        redis_client.delete(reserva_vigente)
    else: 
        print("ERROR: El tiempo de reserva expiro")

def cancelar_reserva(db,redis_client,id_usuario,id_evento):
    reserva_cancelada = f"reserva:evento:{id_evento}:usuario:{id_usuario}"
    redis_client.delete(reserva_cancelada)
    #SUMAR EL TOTAL DE DISPONIBLIDAD
