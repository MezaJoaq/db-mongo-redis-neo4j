def entradas_vendidas(db_mongo,id):
    compras_del_evento = db_mongo.compras.find({
            "evento_id": id,
            "estado": "confirmada"
    })

    total_entradas = sum([compra["cantidad"] for compra in compras_del_evento])
    return total_entradas

def reservas_vigentes(redis_client,id):
    clave_reserva = redis_client.keys(f'reserva:evento:{id}:*')
    total_reserva = 0
    if not clave_reserva:
        print("No se posee una reserva")
        return 0
    for clave in clave_reserva:
        tiempo_restante = redis_client.ttl(clave)
        # 3. Traemos los datos guardados (usuario, evento, cantidad)
        datos_reserva = redis_client.get(clave)
        if datos_reserva:
            total_reserva += int(datos_reserva)
            
        return total_reserva