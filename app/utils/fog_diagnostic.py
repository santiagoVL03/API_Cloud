"""
Herramienta de diagnóstico para detectar problemas con detección de niebla.
Analiza una imagen y muestra exactamente qué valores está calculando.
"""

import cv2
import numpy as np
import logging
from pathlib import Path

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class FogDiagnostic:
    """Diagnóstico detallado de detección de niebla."""
    
    def __init__(self):
        """Inicializar con thresholds por defecto."""
        self.fog_brightness_threshold = 150
        self.fog_contrast_threshold = 50
        self.fog_saturation_threshold = 60
    
    def analyze_image(self, image_path: str) -> dict:
        """
        Analizar una imagen completa y devolver todos los valores intermedios.
        
        Args:
            image_path: Ruta a la imagen
            
        Returns:
            Diccionario con todos los valores analizados
        """
        # Leer imagen
        frame = cv2.imread(image_path)
        if frame is None:
            logger.error(f"No se pudo leer la imagen: {image_path}")
            return {}
        
        logger.info(f"Analizando imagen: {image_path}")
        logger.info(f"Dimensiones: {frame.shape}")
        
        # Convertir a espacios de color
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # ========== ANÁLISIS DE BRILLO ==========
        brightness = np.mean(hsv[:, :, 2])
        brightness_min = np.min(hsv[:, :, 2])
        brightness_max = np.max(hsv[:, :, 2])
        brightness_std = np.std(hsv[:, :, 2])
        
        logger.info("\n=== BRILLO (V channel en HSV) ===")
        logger.info(f"  Promedio: {brightness:.2f}")
        logger.info(f"  Mínimo: {brightness_min:.2f}")
        logger.info(f"  Máximo: {brightness_max:.2f}")
        logger.info(f"  Desv. Est.: {brightness_std:.2f}")
        logger.info(f"  Threshold: {self.fog_brightness_threshold}")
        logger.info(f"  ¿Cumple? {'✓ SÍ (brillo alto)' if brightness >= self.fog_brightness_threshold else '✗ NO (brillo bajo)'}")
        
        # ========== ANÁLISIS DE CONTRASTE ==========
        contrast = np.std(gray)
        contrast_min = np.min(gray)
        contrast_max = np.max(gray)
        
        logger.info("\n=== CONTRASTE (Desv. Est. escala grises) ===")
        logger.info(f"  Desv. Est.: {contrast:.2f}")
        logger.info(f"  Mínimo: {contrast_min:.2f}")
        logger.info(f"  Máximo: {contrast_max:.2f}")
        logger.info(f"  Rango: {contrast_max - contrast_min:.2f}")
        logger.info(f"  Threshold: {self.fog_contrast_threshold}")
        logger.info(f"  ¿Cumple? {'✓ SÍ (contraste bajo)' if contrast <= self.fog_contrast_threshold else '✗ NO (contraste alto)'}")
        
        # ========== ANÁLISIS DE SATURACIÓN ==========
        saturation = np.mean(hsv[:, :, 1])
        saturation_min = np.min(hsv[:, :, 1])
        saturation_max = np.max(hsv[:, :, 1])
        saturation_std = np.std(hsv[:, :, 1])
        
        logger.info("\n=== SATURACIÓN (S channel en HSV) ===")
        logger.info(f"  Promedio: {saturation:.2f}")
        logger.info(f"  Mínimo: {saturation_min:.2f}")
        logger.info(f"  Máximo: {saturation_max:.2f}")
        logger.info(f"  Desv. Est.: {saturation_std:.2f}")
        logger.info(f"  Threshold: {self.fog_saturation_threshold}")
        logger.info(f"  ¿Cumple? {'✓ SÍ (baja saturación)' if saturation <= self.fog_saturation_threshold else '✗ NO (alta saturación)'}")
        
        # ========== ANÁLISIS DE TONALIDAD ==========
        hue = hsv[:, :, 0]
        logger.info("\n=== TONALIDAD (H channel en HSV) ===")
        logger.info(f"  Promedio: {np.mean(hue):.2f}")
        logger.info(f"  Mínimo: {np.min(hue):.2f}")
        logger.info(f"  Máximo: {np.max(hue):.2f}")
        
        # ========== CÁLCULO DE SCORES ==========
        brightness_score = self._normalize_score(
            brightness, 
            self.fog_brightness_threshold, 
            255, 
            inverse=False
        )
        contrast_score = self._normalize_score(
            contrast, 
            0, 
            self.fog_contrast_threshold, 
            inverse=True
        )
        saturation_score = self._normalize_score(
            saturation, 
            0, 
            self.fog_saturation_threshold, 
            inverse=True
        )
        
        fog_score = (0.4 * brightness_score + 
                     0.4 * contrast_score + 
                     0.2 * saturation_score)
        
        logger.info("\n=== SCORES NORMALIZADOS ===")
        logger.info(f"  Brightness Score: {brightness_score:.3f} (40%)")
        logger.info(f"  Contrast Score: {contrast_score:.3f} (40%)")
        logger.info(f"  Saturation Score: {saturation_score:.3f} (20%)")
        logger.info(f"  ► FINAL FOG SCORE: {fog_score:.3f}")
        logger.info(f"  Detectada como niebla? {'✓ SÍ (score > 0.5)' if fog_score > 0.5 else '✗ NO (score ≤ 0.5)'}")
        
        # ========== ANÁLISIS DE DISTRIBUCIÓN DE PÍXELES ==========
        logger.info("\n=== DISTRIBUCIÓN DE PÍXELES ===")
        bright_pixels = np.sum(gray > 200)
        medium_pixels = np.sum((gray >= 100) & (gray <= 200))
        dark_pixels = np.sum(gray < 100)
        
        total = gray.size
        logger.info(f"  Píxeles muy brillantes (>200): {bright_pixels} ({bright_pixels/total*100:.1f}%)")
        logger.info(f"  Píxeles medio (100-200): {medium_pixels} ({medium_pixels/total*100:.1f}%)")
        logger.info(f"  Píxeles oscuros (<100): {dark_pixels} ({dark_pixels/total*100:.1f}%)")
        
        # Retornar resultado
        return {
            'brightness': brightness,
            'contrast': contrast,
            'saturation': saturation,
            'brightness_score': brightness_score,
            'contrast_score': contrast_score,
            'saturation_score': saturation_score,
            'fog_score': fog_score,
            'is_fog': fog_score > 0.5
        }
    
    def _normalize_score(self, value: float, min_val: float, max_val: float, 
                        inverse: bool = False) -> float:
        """Normalizar valor a rango 0-1."""
        if max_val == min_val:
            return 0.5
        
        normalized = (value - min_val) / (max_val - min_val)
        normalized = np.clip(normalized, 0.0, 1.0)
        
        if inverse:
            normalized = 1.0 - normalized
        
        return float(normalized)
    
    def compare_images(self, image_paths: list):
        """
        Comparar múltiples imágenes y mostrar diferencias.
        
        Args:
            image_paths: Lista de rutas a imágenes
        """
        results = []
        for path in image_paths:
            result = self.analyze_image(path)
            result['path'] = path
            results.append(result)
        
        logger.info("\n" + "="*70)
        logger.info("COMPARACIÓN DE IMÁGENES")
        logger.info("="*70)
        
        for result in results:
            logger.info(f"\n{Path(result['path']).name}:")
            logger.info(f"  Brightness: {result['brightness']:.2f}, Contrast: {result['contrast']:.2f}, Saturation: {result['saturation']:.2f}")
            logger.info(f"  FOG SCORE: {result['fog_score']:.3f} - {'✓ NIEBLA' if result['is_fog'] else '✗ SIN NIEBLA'}")


if __name__ == "__main__":
    import sys
    
    diagnostic = FogDiagnostic()
    
    if len(sys.argv) > 1:
        # Analizar imagen(es) pasadas como argumento
        image_paths = sys.argv[1:]
        diagnostic.compare_images(image_paths)
    else:
        print("Uso: python fog_diagnostic.py <image_path1> [image_path2] ...")
        print("\nEjemplo:")
        print("  python fog_diagnostic.py foggy_image.jpg clear_image.jpg")
