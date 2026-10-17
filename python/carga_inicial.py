from pymongo import MongoClient
import redis 
import datetime
from neo4j import GraphDatabase
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
#Insertar clave/valor en redis
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
#Insertar relaciones en neo4j
def insert_neo4j(driver):
    #Crea los string para inicializarlo con session.run
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
    
    
    with driver.session() as session:
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

        
            
    