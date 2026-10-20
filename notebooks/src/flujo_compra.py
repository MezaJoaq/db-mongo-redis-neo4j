from pymongo import MongoClient
import redis 
import datetime
from neo4j import GraphDatabase
from src.databases import (usuarios,artistas,lugares,eventos,compras)
from src.consultas import (reservas_vigentes, entradas_vendidas)

FECHA_REFERENCIA = "2026-10-01"
ahora = datetime.datetime.now()

def entradas_disponibles(redis_client,db,id_evento,cantidad,cupo):
    entradas_disponibles = cupo - reservas_vigentes(redis_client,id_evento) - entradas_vendidas(db,id_evento)
    if (entradas_disponibles < cantidad):
        print("No hay entradas disponibles para la cantidad pedida")
        return False
    else: return True

def reservar_entrada(id_usuario,id_evento,cant,redis_client,db):
    #Crea la clave de redis
    evento = db.eventos.find_one({"evento_id" : id_evento})
    if not evento:
            print("No se encontro el evento")
            return False
    
    sesion = f"sesion:usuario:{id_usuario}"
    if redis_client.exists(sesion):
        cupo = evento.get("cupo", 0)
        nombre_evento = evento.get("nombre")
        if entradas_disponibles(redis_client,db,id_evento,cant,cupo):
            clave = f"reserva:evento:{id_evento}:usuario:{id_usuario}"
            valor = f"{cant}"
            redis_client.set(clave,valor, ex = 600)
            print(f"Se reservaron {cant} entradas para el evento {nombre_evento}")
        else:
            return False
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
        print("La compra se realizo correctamente")
        redis_client.delete(reserva_vigente)
    else: 
        print("ERROR: La reserva esta cancelada o expiro su tiempo")

def cancelar_reserva(db,redis_client,id_usuario,id_evento):
    reserva_cancelada = f"reserva:evento:{id_evento}:usuario:{id_usuario}"
    if redis_client.exists(reserva_cancelada):
        redis_client.delete(reserva_cancelada)
        print("La reserva se cancelo correctamente")
    else: print("No existe una reserva para este evento")

    #SUMAR EL TOTAL DE DISPONIBLIDAD
