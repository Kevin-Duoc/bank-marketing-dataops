from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

def evaluar_modelo(y_real, y_pred, nombre_modelo):
    """
    Decorador DataOps: 
    Calcula las métricas de éxito del modelo para el Dashboard.
    """
    #calculos matemáticos de la matriz de confusión
    acc = accuracy_score(y_real, y_pred)
    prec = precision_score(y_real, y_pred, zero_division=0)
    rec = recall_score(y_real, y_pred, zero_division=0)
    f1 = f1_score(y_real, y_pred, zero_division=0)
    
    #reporte en consola
    print(f"\n[Resultados del Juez] - {nombre_modelo}")
    print(f"  -> Exactitud (Accuracy): {acc * 100:.2f}% (Predicciones correctas totales)")
    print(f"  -> Precisión: {prec * 100:.2f}% (De los que predijo 'Sí', cuántos eran realmente 'Sí')")
    print(f"  -> Recall: {rec * 100:.2f}% (De todos los 'Sí' reales, cuántos logró encontrar)")
    print(f"  -> F1-Score: {f1 * 100:.2f}% (Equilibrio entre Precisión y Recall)")
    
    #retorna un diccionario con las notas para mandarlas a Streamlit después
    return {
        "modelo": nombre_modelo,
        "accuracy": acc,
        "precision": prec,
        "recall": rec,
        "f1": f1
    }