from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, roc_auc_score

def evaluar_modelo(y_real, y_pred, y_pred_proba, nombre_modelo):
    """
    Decorador DataOps: 
    Calcula las métricas de éxito del modelo para el Dashboard, incluyendo Gini y Matriz de Confusión.
    """
    #calculos matemáticos base
    acc = accuracy_score(y_real, y_pred)
    prec = precision_score(y_real, y_pred, zero_division=0)
    rec = recall_score(y_real, y_pred, zero_division=0)
    f1 = f1_score(y_real, y_pred, zero_division=0)
    cm = confusion_matrix(y_real, y_pred)
    auc = roc_auc_score(y_real, y_pred_proba)
    gini = (2 * auc) - 1  #fórmula matemática estándar para derivar Gini desde AUC
    
    #reporte en consola
    print(f"\n[Resultados del Juez] - {nombre_modelo}")
    print(f"  -> Exactitud (Accuracy): {acc * 100:.2f}% (Predicciones correctas totales)")
    print(f"  -> Precisión: {prec * 100:.2f}% (De los que predijo 'Sí', cuántos eran realmente 'Sí')")
    print(f"  -> Recall: {rec * 100:.2f}% (De todos los 'Sí' reales, cuántos logró encontrar)")
    print(f"  -> F1-Score: {f1 * 100:.2f}% (Equilibrio entre Precisión y Recall)")
    print(f"  -> Área ROC (AUC): {auc * 100:.2f}% (Capacidad de distinguir entre Sí y No)")
    print(f"  -> Índice Gini: {gini * 100:.2f}% (Poder de discriminación del modelo)")
    
    #retorna un diccionario con las notas para mandarlas a Streamlit después
    return {
        "modelo": nombre_modelo,
        "accuracy": acc,
        "precision": prec,
        "recall": rec,
        "f1": f1,
        "auc": auc,
        "gini": gini,
        "matriz_confusion": cm.tolist()
    }