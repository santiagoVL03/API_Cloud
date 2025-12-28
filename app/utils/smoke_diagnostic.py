"""
Diagnóstico detallado para smoke detection.
Analiza cada componente de la detección de humo.
"""

import cv2
import numpy as np
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def analyze_smoke_components(image_path: str):
    """Analizar los 3 componentes de smoke detection."""
    
    frame = cv2.imread(image_path)
    if frame is None:
        logger.error(f"No se pudo leer: {image_path}")
        return
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    logger.info("="*70)
    logger.info(f"ANÁLISIS DE COMPONENTES DE SMOKE DETECTION")
    logger.info(f"Imagen: {image_path}")
    logger.info("="*70)
    
    # ===== COMPONENTE 1: BRIGHTNESS =====
    brightness = np.mean(gray)
    smoke_brightness_range = (80, 200)
    in_range = smoke_brightness_range[0] <= brightness <= smoke_brightness_range[1]
    brightness_score = 1.0 if in_range else 0.3
    
    logger.info("\n[1/3] BRIGHTNESS SCORE")
    logger.info(f"  Valor: {brightness:.2f}")
    logger.info(f"  Rango esperado (humo): {smoke_brightness_range}")
    logger.info(f"  ¿Dentro del rango? {in_range}")
    logger.info(f"  Score: {brightness_score:.3f}")
    
    # ===== COMPONENTE 2: EDGE DETECTION =====
    edges = cv2.Canny(gray, 50, 150)
    edge_density = np.sum(edges > 0) / edges.size
    smoke_edge_threshold = 20
    
    # Normalizar (inverse=True, así que bajo edge_density = score alto)
    edge_score = 1.0 - np.clip(edge_density * 100 / smoke_edge_threshold, 0, 1.0)
    
    logger.info("\n[2/3] EDGE DETECTION SCORE (Canny)")
    logger.info(f"  Edge Density: {edge_density*100:.2f}%")
    logger.info(f"  Threshold: {smoke_edge_threshold}%")
    logger.info(f"  Interpretación: {edge_density*100:.2f}% de píxeles son bordes")
    logger.info(f"  Score (inverse): {edge_score:.3f}")
    logger.info(f"  ⚠️  PROBLEMA: Niebla tiene BAJA densidad de bordes (difusa)")
    logger.info(f"        → Bajo edge_score = score alto en detección = FALSO POSITIVO")
    
    # ===== COMPONENTE 3: TEXTURE =====
    kernel_size = 15
    gray_float = gray.astype(float)
    mean_filtered = cv2.blur(gray_float, (kernel_size, kernel_size))
    squared_diff = (gray_float - mean_filtered) ** 2
    local_var = cv2.blur(squared_diff, (kernel_size, kernel_size))
    local_var = np.maximum(local_var, 0)
    local_std = np.sqrt(local_var)
    
    texture_mean = np.nanmean(local_std)
    if np.isnan(texture_mean) or texture_mean == 0:
        texture_score = 0.0
    else:
        texture_score = min(texture_mean / 50.0, 1.0)
    
    logger.info("\n[3/3] TEXTURE SCORE (Local Std Dev)")
    logger.info(f"  Texture Mean: {texture_mean:.2f}")
    logger.info(f"  Score: {texture_score:.3f}")
    logger.info(f"  ⚠️  PROBLEMA: Niebla es uniforme (baja variación local)")
    logger.info(f"        → Bajo texture_mean = bajo texture_score")
    
    # ===== SCORE FINAL =====
    smoke_score = (0.3 * brightness_score + 
                   0.4 * edge_score + 
                   0.3 * texture_score)
    
    logger.info("\n" + "="*70)
    logger.info("SCORE FINAL")
    logger.info("="*70)
    logger.info(f"  Brightness Score: {brightness_score:.3f} × 0.30 = {0.3 * brightness_score:.3f}")
    logger.info(f"  Edge Score:       {edge_score:.3f} × 0.40 = {0.4 * edge_score:.3f}  ← CULPABLE")
    logger.info(f"  Texture Score:    {texture_score:.3f} × 0.30 = {0.3 * texture_score:.3f}")
    logger.info(f"  {'─'*70}")
    logger.info(f"  SMOKE SCORE: {smoke_score:.3f}")
    logger.info(f"  ¿Es humo? {'✓ SÍ (>0.5)' if smoke_score > 0.5 else '✗ NO (≤0.5)'}")
    
    # ===== ANÁLISIS DEL PROBLEMA =====
    logger.info("\n" + "="*70)
    logger.info("ANÁLISIS DEL PROBLEMA")
    logger.info("="*70)
    logger.info(f"""
    ❌ FALSO POSITIVO: Niebla detectada como HUMO

    Razón:
    ------
    La niebla y el humo comparten características:
    1. Ambos tienen BORDES BORROSOS (bajo edge_density)
    2. Ambos tienen BAJA TEXTURA (uniforme)
    3. Ambos pueden tener brillo en rango 80-200

    El algoritmo actual CONFUNDE estos rasgos:
    - Edge Score alto (0.40 × peso) ← Borrosidad = humo según la lógica
    - Texture bajo (0.30 × peso) ← Uniforme = normal en niebla

    ✅ SOLUCIÓN:
    -----------
    Agregar DIFERENCIADORES:
    • Niebla: Afecta TODA la imagen uniformemente
    • Humo: Afecta ÁREAS ESPECÍFICAS (concentrado)

    • Niebla: Saturación BAJA (<50)
    • Humo: Saturación MEDIA (50-100)

    • Niebla: Contraste BAJO en general
    • Humo: Contraste VARIABLE (bordes oscuros/claros)
    """)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python smoke_diagnostic.py <image_path>")
        sys.exit(1)
    
    analyze_smoke_components(sys.argv[1])
