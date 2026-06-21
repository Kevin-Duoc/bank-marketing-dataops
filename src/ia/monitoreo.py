import time
import tracemalloc
import gc

def medir_recursos(func):
    """
    Decorador DataOps: 
    Mide el tiempo de ejecución (Latencia) y el pico (Peak) de RAM consumida.
    """
    def wrapper(*args, **kwargs):
        #1 vaciar la RAM residual del modelo anterior para que el resultado sea exacto
        gc.collect()
        
        #2 iniciar rastreador de memoria de Python (reemplaza a psutil)
        tracemalloc.start()
        tiempo_inicio = time.time()
        
        #3 se ejecuta la función real (por ejemplo, entrenar el Random Forest)
        resultado = func(*args, **kwargs)
        
        #4 foto del sistema DESPUÉS de ejecutar
        tiempo_fin = time.time()
        current_memory, peak_memory = tracemalloc.get_traced_memory()
        
        #apagamos el rastreador para que no siga consumiendo recursos
        tracemalloc.stop() 
        
        #5 cálculo de diferencias (consumo real en su punto máximo)
        latencia = tiempo_fin - tiempo_inicio
        ram_consumida = peak_memory / (1024 * 1024) #convertido a Megabytes

        print(f"\n[Telemetría de Hardware] - Proceso: {func.__name__}")
        print(f"  -> Latencia (Tiempo): {latencia:.4f} segundos")
        print(f"  -> Consumo de RAM (Peak): {ram_consumida:.2f} MB")
        
        #si la función devuelve las métricas, le inyectamos el hardware
        if isinstance(resultado, dict):
            resultado['ram_mb'] = round(ram_consumida, 2)
            resultado['tiempo_s'] = round(latencia, 4)
            
        return resultado
    return wrapper