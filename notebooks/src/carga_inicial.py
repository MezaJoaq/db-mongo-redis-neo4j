from pymongo import MongoClient
import redis 
import datetime
from neo4j import GraphDatabase
from src.databases import (usuarios,artistas,lugares,eventos,compras)
from pymongo.errors import PyMongoError
from redis.exceptions import RedisError
from neo4j.exceptions import Neo4jError

FECHA_REFERENCIA = "2026-10-01"
ahora = datetime.datetime.now()
#Insertar colecciones en mongodb
def insert_mongo(db):
    #Limpia las colecciones por si se vuelve a ejecutar la funcion
    colecciones = {
        "usuarios" : usuarios,
        "artistas" : artistas,
        "lugares" : lugares,
        "eventos" : eventos,
        "compras" : compras
    }
    print("Cargando datos en MongoDB")
    for nombre_col, lista_datos in colecciones.items():
        col = db[nombre_col]
        col.delete_many({})

        try:
            res = col.insert_many(lista_datos)
            print(f" • {nombre_col.capitalize()}: {len(res.inserted_ids)} insertados")
        except PyMongoError as e:
            print(f"Error al insertar la coleccion {nombre_col}:{e}")
            return False
    print("MongoDB cargado correctamente")
    return True

#Insertar clave/valor en redis
def insert_redis(redis_client):
    #Carga inicial de las sesiones (como indica en el trabajo)
    reserva = {
            "reserva:evento:5:usuario:3" : 2,
            "reserva:evento:4:usuario:6" : 3
            }
    sesiones_activas = [1,2,6]
    busquedas_recientes = {"rock" : 7,
                           "electrónica" : 5,
                           "folk" : 3,
                           "cumbia" : 2}
    redis_client.flushdb()
    try: 
        for sesion in sesiones_activas:
            #Creo la clave de redis
            clave = f"sesion:usuario:{sesion}"
            #Valor de la fecha de refencia mas la hora de sesion
            valor = f"{FECHA_REFERENCIA}/{ahora.time()}"
            #Define la sesion del cliente
            redis_client.set(clave, valor, ex=1800)

        for clave_reserva, valor_reserva in reserva.items():
            redis_client.set(clave_reserva, valor_reserva, ex=600)

        for genero, cant in busquedas_recientes.items():
            clave = f"busqueda:reciente:{genero}"
            clave_cache = f"cache:busqueda:reciente:{genero}"
            redis_client.set(clave_cache,cant, ex = 300)
            redis_client.set(clave,cant)
        print("Redis cargado con éxito.")
        return True
    except RedisError as e:
        print(f"Error en Redis: {e}") 
        return False
#Insertar relaciones en neo4j
def insert_neo4j(driver):
    #Crea los string para inicializarlo con session.run
    limpieza = """MATCH (n) DETACH DELETE n"""
    nodo_usuario = """MERGE (u:Usuario {usuario_id:$id, nombre:$nombre, ciudad:$ciudad})"""
    nodo_artista = """MERGE (a:Artista {artista_id:$id, nombre:$nombre, genero:$genero})"""
    relacion_amistades = """MATCH (u1:Usuario {usuario_id:$id1})
                            MATCH (u2:Usuario {usuario_id:$id2})
                            MERGE (u1)-[:AMIGO_DE]->(u2)"""
    relacion_seguidos = """MATCH (u:Usuario {usuario_id:$id_user})
                           MATCH (a:Artista {artista_id:$id_artista})
                           MERGE (u)-[:SIGUE]->(a)"""
    relacion_similares = """MATCH (a1:Artista {artista_id:$id1})
                            MATCH (a2:Artista {artista_id:$id2})
                            MERGE (a1)-[:SIMILAR_A]->(a2)"""
    
    try:
        with driver.session() as session:
            session.run(limpieza)
            for u in usuarios:
                session.run(nodo_usuario, id=u["usuario_id"], nombre=u["nombre"], ciudad=u["ciudad"])
            for a in artistas:
                session.run(nodo_artista, id=a["artista_id"], nombre=a["nombre"], genero=a["genero"])

            #Itera sobre los usuarios
            for u in usuarios:
                #Agarra el id de los amigos del usuario actual
                for id_amig in u["amigos"]:
                    #Crea la relacion con session.run
                    session.run(relacion_amistades, id1=u["usuario_id"],id2=id_amig)
                for id_art in u["sigue"]:
                    session.run(relacion_seguidos, id_user=u["usuario_id"],id_artista=id_art)
            for a in artistas:
                for id_similar in a["similares"]:
                    session.run(relacion_similares, id1=a["artista_id"], id2=id_similar)
        print("Neo4J se cargo correctamente")
        return True
    except Neo4jError as e: 
        print(f"Error de ejecución en Neo4j: {e}") 
        return False

        
            
    