import cv2
import numpy as np
from typing import List, Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class DetectionUtil:
    """
    Utility class for detecting fog and smoke using computer vision techniques.
    Uses non-ML approaches based on image analysis.
    """
    
    def __init__(self):
        """Initialize DetectionUtil with default parameters."""
        # FOG DETECTION - Adjusted thresholds based on real fog images
        # Real fog images typically have:
        # - Brightness: 130-160 (not extremely high like white paper)
        # - Contrast: 50-70 (some details visible through fog)
        # - Saturation: 30-50 (desaturated colors)
        
        self.fog_brightness_threshold = 130  # Lowered from 150
        self.fog_contrast_threshold = 60  # Raised from 50 (more tolerant)
        self.fog_saturation_threshold = 70  # Raised from 60 (more tolerant)
        self.fog_dynamic_range_threshold = 80  # New: pixel range indicator
        
        # Smoke detection thresholds
        self.smoke_brightness_range = (80, 200)  # Medium brightness
        self.smoke_edge_threshold = 20           # Blurred edges
        self.smoke_density_threshold = 0.3       # Coverage percentage
    
    def analyze_frames(self, frames: List[np.ndarray]) -> Dict[str, any]: # type: ignore
        """
        Analyze captured frames to detect fog or smoke.
        
        Args:
            frames: List of frames (BGR format) to analyze
            
        Returns:
            Dictionary with detection results:
            {
                'fog_detected': bool,
                'smoke_detected': bool,
                'probability_fog': float (0.0-1.0),
                'probability_smoke': float (0.0-1.0),
                'probability_vapor': float (0.0-1.0),
                'probability_smug': float (0.0-1.0),
                'analysis_details': dict
            }
        """
        if not frames:
            logger.warning("No frames to analyze")
            return self._empty_result()
        
        logger.info(f"Analyzing {len(frames)} frames for fog/smoke detection")
        
        # Analyze each frame
        fog_scores = []
        smoke_scores = []
        vapor_scores = []
        smug_scores = []
        
        for i, frame in enumerate(frames):
            fog_score = self._detect_fog_in_frame(frame)
            smoke_score = self._detect_smoke_in_frame(frame)
            vapor_score = self._detect_vapor_in_frame(frame)
            smug_score = self._detect_smug_in_frame(frame)
            
            fog_scores.append(fog_score)
            smoke_scores.append(smoke_score)
            vapor_scores.append(vapor_score)
            smug_scores.append(smug_score)
        
        # Average scores across all frames
        avg_fog = np.mean(fog_scores)
        avg_smoke = np.mean(smoke_scores)
        avg_vapor = np.mean(vapor_scores)
        avg_smug = np.mean(smug_scores)
        
        # Determine detection (threshold: 0.45)
        # Convert to native Python bool to avoid np.bool_ type issues
        fog_detected = bool(avg_fog > 0.45)
        smoke_detected = bool(avg_smoke > 0.45)

        result = {
            'fog_detected': fog_detected,
            'smoke_detected': smoke_detected,
            'probability_fog': round(float(avg_fog), 3),
            'probability_smoke': round(float(avg_smoke), 3),
            'probability_vapor': round(float(avg_vapor), 3),
            'probability_smug': round(float(avg_smug), 3),
            'analysis_details': {
                'frames_analyzed': len(frames),
                'fog_scores_range': (float(np.min(fog_scores)), float(np.max(fog_scores))),
                'smoke_scores_range': (float(np.min(smoke_scores)), float(np.max(smoke_scores))),
            }
        }
        
        logger.info(f"Detection result: Fog={fog_detected} ({avg_fog:.3f}), "
                   f"Smoke={smoke_detected} ({avg_smoke:.3f})")
        
        return result
    
    def _detect_fog_in_frame(self, frame: np.ndarray) -> float:
        """
        Detect fog in a single frame using brightness, contrast, and saturation.
        
        IMPROVED ALGORITHM:
        - Fog characteristics: High brightness OR low contrast + low saturation
        - More flexible: 2 out of 3 indicators = fog
        - Additional: Check for dynamic range (niebla hace píxeles similares)
        
        Args:
            frame: Input frame in BGR format
            
        Returns:
            Fog probability score (0.0-1.0)
        """
        # Convert to different color spaces
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # ===== MÉTODO 1: Análisis HSV =====
        brightness = np.mean(hsv[:, :, 2]) # type: ignore
        contrast = np.std(gray) # type: ignore
        saturation = np.mean(hsv[:, :, 1]) # type: ignore
        
        # Scores individuales (0-1, donde 1 = indica niebla)
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
        
        # ===== MÉTODO 2: Rango Dinámico =====
        # Niebla hace que los píxeles sean muy similares (bajo rango)
        min_brightness = np.min(hsv[:, :, 2])
        max_brightness = np.max(hsv[:, :, 2])
        dynamic_range = max_brightness - min_brightness
        
        # Rango bajo (<100) = posible niebla
        range_score = self._normalize_score(
            dynamic_range, # type: ignore
            100,  # max_val (rango bajo = niebla)
            0,    # min_val
            inverse=True  # Invertir: rango bajo = score alto
        )
        
        # ===== LÓGICA MEJORADA: Voting System =====
        # Contar cuántos indicadores sugieren niebla
        indicators = []
        
        # Indicator 1: Brillo alto
        if brightness_score > 0.4:
            indicators.append(("brightness", brightness_score))
        
        # Indicator 2: Contraste bajo
        if contrast_score > 0.4:
            indicators.append(("contrast", contrast_score))
        
        # Indicator 3: Saturación baja
        if saturation_score > 0.3:
            indicators.append(("saturation", saturation_score))
        
        # Indicator 4: Rango dinámico bajo
        if range_score > 0.4:
            indicators.append(("range", range_score))
        
        # Scoring logic:
        # - Si 2+ indicadores presentes = niebla probable
        # - Ponderar según el número de indicadores
        num_indicators = len(indicators)
        
        if num_indicators >= 2:
            # Al menos 2 indicadores = hay niebla
            avg_indicator_score = np.mean([score for _, score in indicators])
            
            # Ponderar: más indicadores = más confianza
            confidence_boost = min(num_indicators / 4.0, 1.0)
            fog_score = avg_indicator_score * (0.7 + 0.3 * confidence_boost)
        else:
            # Menos de 2 indicadores = sin niebla
            # Pero usar el promedio ponderado como baseline
            fog_score = (0.35 * brightness_score + 
                        0.35 * contrast_score + 
                        0.20 * saturation_score +
                        0.10 * range_score)
        
        # Detailed logging for debugging
        logger.debug(f"FOG DETECTION (IMPROVED):")
        logger.debug(f"  Brightness: {brightness:.2f} (th:{self.fog_brightness_threshold}) -> {brightness_score:.3f}")
        logger.debug(f"  Contrast: {contrast:.2f} (th:{self.fog_contrast_threshold}) -> {contrast_score:.3f}")
        logger.debug(f"  Saturation: {saturation:.2f} (th:{self.fog_saturation_threshold}) -> {saturation_score:.3f}")
        logger.debug(f"  Range: {dynamic_range:.2f} -> {range_score:.3f}")
        logger.debug(f"  Indicators ({num_indicators}): {[name for name, _ in indicators]}")
        logger.debug(f"  ► FINAL FOG SCORE: {fog_score:.3f}")
        
        return float(np.clip(fog_score, 0.0, 1.0))
    
    def _detect_smoke_in_frame(self, frame: np.ndarray) -> float:
        """
        Detect smoke in a single frame using edge detection and density.
        
        IMPROVED: Distinguish smoke from fog
        
        Smoke characteristics:
        - Can be ANY brightness (depends on fuego underneath)
        - Localized pockets of haze (not uniform)
        - Blurred/soft edges locally
        - CAN have low saturation (gray smoke)
        - Variable texture/density patterns
        
        Fog characteristics (to AVOID):
        - UNIFORM blur across entire image
        - GLOBAL low saturation + low contrast EVERYWHERE
        - Smooth, even distribution
        
        Key difference: Smoke has LOCALIZED density, Fog is GLOBAL
        
        Args:
            frame: Input frame in BGR format
            
        Returns:
            Smoke probability score (0.0-1.0)
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        try:
            saturation = np.mean(hsv[:, :, 1]) # type: ignore
            brightness = np.mean(gray) # type: ignore
            
            # ===== STEP 1: Check if this might be FOG instead of SMOKE =====
            # FOG GATE (improved): Check for UNIFORM global fog
            # Not just low saturation, but also:
            # - Low contrast EVERYWHERE (std < 20)
            # - Very low saturation (<35)
            # - Medium-low brightness (90-140)
            # AND these conditions PERSISTENT across entire image
            
            contrast_global = np.std(gray) # type: ignore
            
            # ONLY reject smoke if ALL fog conditions are met:
            is_likely_fog = (
                saturation < 35 and  # Very desaturated
                contrast_global < 25 and  # Very uniform blur
                brightness < 140  # Not bright like smoke+fire
            )
            
            if is_likely_fog:
                logger.debug(f"Smoke detection - Likely FOG (saturation:{saturation:.1f}, "
                            f"contrast:{contrast_global:.1f}, brightness:{brightness:.1f}). Score: 0.0")
                return 0.0
            
            # ===== STEP 2: Brightness analysis =====
            # Smoke can have wide brightness range:
            # - Gray smoke: 60-120
            # - Smoke+fire: 150-220 (bright from flames)
            # Fog is typically more constrained (130-160)
            brightness_score = 0.5  # Baseline
            
            if brightness < 60:
                # Very dark = probably night or clear dark areas
                brightness_score = 0.2
            elif brightness < 100:
                # Dark smoke without much fire = possible
                brightness_score = 0.8
            elif brightness < 150:
                # Medium brightness = good smoke range
                brightness_score = 1.0
            elif brightness < 200:
                # Bright (from fire) = still smoke
                brightness_score = 0.9
            else:
                # Very bright = clear sky or bright clear conditions
                brightness_score = 0.3
            
            # ===== STEP 3: Local contrast variation (KEY for smoke vs fog) =====
            # Smoke has VARIABLE local contrast (aglomerados of density)
            # Fog has UNIFORM low contrast everywhere
            
            # Calculate local contrast in different regions
            h, w = gray.shape
            region_h, region_w = h // 3, w // 3
            local_contrasts = []
            
            for i in range(0, h - region_h, region_h):
                for j in range(0, w - region_w, region_w):
                    region = gray[i:i+region_h, j:j+region_w].flatten()
                    local_contrasts.append(float(np.std(region)))  # type: ignore
            
            if local_contrasts:
                # Variance of local contrasts = how different regions are
                contrast_variance = np.std(local_contrasts)
                local_contrast_mean = np.mean(local_contrasts)
                
                # Smoke: high variance (aglomerados) + medium-low mean contrast
                # Fog: low variance (uniform) + very low mean contrast
                localization_score = 0.0
                if local_contrast_mean > 15:  # Not completely uniform fog
                    localization_score = min(contrast_variance / 30, 1.0)
                else:
                    # Low mean contrast = could be fog or dense smoke
                    localization_score = contrast_variance / 10 * 0.5
            else:
                localization_score = 0.5
            
            # ===== STEP 4: Edge detection (Canny) =====
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / edges.size
            
            # Smoke edges: moderate density (not crisp like clear, not absent like uniform fog)
            if edge_density < 0.005:
                # Very few edges = uniform fog
                edge_score = 0.2
            elif edge_density < 0.02:
                # Moderate edges = smoke or light fog
                edge_score = 0.8
            else:
                # High edges = clear or structured scene
                edge_score = 0.3
            
            # ===== STEP 5: Saturation adaptive factor =====
            # Smoke CAN have low saturation (gray smoke)
            # But humo with fuego might be more colored
            saturation_factor = 0.8  # Default: smoke usually grayish
            
            if saturation < 25:
                # Very gray = consistent with smoke
                saturation_factor = 0.9
            elif saturation < 50:
                # Still grayish = smoke
                saturation_factor = 0.85
            elif saturation < 80:
                # Getting colored = smoke with flames maybe
                saturation_factor = 0.7
            else:
                # Very colored = less likely smoke
                saturation_factor = 0.4
            
            
            # ===== STEP 6: Texture analysis =====
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
            
            # ===== FINAL SCORING =====
            # Weight components:
            # - brightness_score (0.25): Can vary widely with smoke+fire
            # - localization_score (0.35): KEY differentiator (localized vs uniform)
            # - edge_score (0.20): Moderate edges indicate smoke
            # - saturation_factor (0.20): Smoke is usually desaturated
            
            smoke_score = (0.25 * brightness_score +
                          0.35 * localization_score +
                          0.20 * edge_score +
                          0.20 * saturation_factor)
            
            logger.debug(f"Smoke detection - Brightness: {brightness:.2f} (score:{brightness_score:.2f}), "
                        f"Localization: {localization_score:.2f}, "
                        f"Edge density: {edge_density*100:.2f}% (score:{edge_score:.2f}), "
                        f"Saturation: {saturation:.2f} (factor:{saturation_factor:.2f}), "
                        f"Texture: {texture_mean:.2f} (score:{texture_score:.2f}), "
                        f"Final Score: {smoke_score:.3f}")
            
            return float(np.clip(smoke_score, 0.0, 1.0))
        
        except Exception as e:
            logger.error(f"Error in smoke detection: {str(e)}")
            return 0.0
    
    def _detect_vapor_in_frame(self, frame: np.ndarray) -> float:
        """
        Detect water vapor (water mist, light fog, light rain mist).
        
        Vapor characteristics:
        - High brightness (water reflects light)
        - Very low saturation (white/grayish)
        - Can appear uniform or localized
        - Lighter than fog, not as dense
        
        Vapor vs Fog:
        - Vapor: brightness 150-200+, saturation <70
        - Fog: brightness 130-160, saturation <50
        
        Args:
            frame: Input frame in BGR format
            
        Returns:
            Vapor probability score (0.0-1.0)
        """
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        brightness = np.mean(hsv[:, :, 2]) # type: ignore
        saturation = np.mean(hsv[:, :, 1]) # type: ignore
        contrast = np.std(gray) # type: ignore
        
        # ===== STEP 1: Brightness score =====
        # Vapor is typically bright (water scatters light)
        brightness_score = 0.0
        if brightness < 140:
            # Too dark for vapor
            brightness_score = 0.0
        elif brightness < 160:
            # Lower end of vapor range
            brightness_score = (brightness - 140) / 20.0 * 0.7
        elif brightness < 200:
            # Optimal vapor range
            brightness_score = 1.0
        else:
            # Very bright but still possible (overexposed)
            brightness_score = 0.8
        
        # ===== STEP 2: Saturation score =====
        # Vapor is VERY desaturated (whitish/grayish)
        saturation_score = 0.0
        if saturation < 30:
            # Very desaturated = ideal for vapor
            saturation_score = 1.0
        elif saturation < 50:
            # Low saturation = still good
            saturation_score = 1.0 - (saturation - 30) / 20.0 * 0.3
        elif saturation < 70:
            # Medium saturation = possible but less likely
            saturation_score = max(0.0, 0.7 - (saturation - 50) / 20.0 * 0.5)
        else:
            # Too saturated for vapor
            saturation_score = 0.0
        
        # ===== STEP 3: Contrast analysis =====
        # Vapor has VERY low contrast (like fog)
        # But slightly higher than pure fog
        contrast_score = 0.0
        if contrast < 20:
            # Very low contrast = likely vapor/fog
            contrast_score = 1.0
        elif contrast < 40:
            # Low contrast = possible vapor
            contrast_score = 1.0 - (contrast - 20) / 20.0 * 0.4
        elif contrast < 60:
            # Medium contrast = less vapor-like
            contrast_score = max(0.0, 0.6 - (contrast - 40) / 20.0 * 0.5)
        else:
            # High contrast = not vapor
            contrast_score = 0.0
        
        # ===== STEP 4: Distinguish from FOG =====
        # Fog is denser and darker than vapor
        # Vapor is lighter and more transparent
        
        # If all conditions point to HIGH brightness + LOW saturation → likely VAPOR
        # If conditions point to MEDIUM brightness + VERY LOW saturation + UNIFORM → likely FOG
        
        is_more_fog_like = (brightness < 150 and saturation < 40 and contrast < 25)
        
        if is_more_fog_like:
            # Characteristics more consistent with fog
            # Reduce vapor score
            fog_penalty = 0.6
        else:
            fog_penalty = 1.0
        
        # ===== FINAL SCORING =====
        # Combine scores with emphasis on high brightness + low saturation
        vapor_score = (0.35 * brightness_score +
                      0.35 * saturation_score +
                      0.20 * contrast_score +
                      0.10 * 1.0) * fog_penalty  # 10% baseline
        
        logger.debug(f"Vapor detection - Brightness: {brightness:.2f} (score:{brightness_score:.2f}), "
                    f"Saturation: {saturation:.2f} (score:{saturation_score:.2f}), "
                    f"Contrast: {contrast:.2f} (score:{contrast_score:.2f}), "
                    f"Fog penalty: {fog_penalty:.2f}, "
                    f"Final Score: {vapor_score:.3f}")
        
        return float(np.clip(vapor_score, 0.0, 1.0))
    
    def _detect_smug_in_frame(self, frame: np.ndarray) -> float:
        """
        Detect smog/smug (urban pollution haze from vehicle emissions).
        
        Smog characteristics:
        - Yellowish/brownish tint (vehicle exhaust)
        - Medium to low brightness
        - LOW CONTRAST (turbid/hazy appearance)fog_brightness_threshold
        - NOT just presence of yellow/brown colors
        
        Args:
            frame: Input frame in BGR format
            
        Returns:
            Smug probability score (0.0-1.0)
        """
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        try:
            # Get color and brightness information
            hue = hsv[:, :, 0]
            saturation = hsv[:, :, 1]
            value = hsv[:, :, 2]
            brightness = np.mean(value) # type: ignore
            contrast = np.std(gray) # type: ignore
            
            # CRITICAL FIX: Smug is NOT just yellow/brown colors
            # It's yellow/brown colors WITH turbidity (low contrast + medium darkness)
            
            # 1. Look for yellowish/brownish hues (15-35 in OpenCV's 0-179 scale)
            #    BUT also require moderate saturation (not vivid, but not desaturated)
            yellow_brown_mask = ((hue >= 15) & (hue <= 35) & 
                                 (saturation > 20) & (saturation < 150))
            color_coverage = np.sum(yellow_brown_mask) / yellow_brown_mask.size
            
            # 2. Brightness should be medium (not too bright like clear sky)
            brightness_factor = 0.0
            if 100 <= brightness <= 180:  # Medium brightness range for smug
                brightness_factor = 1.0
            elif brightness > 180:
                brightness_factor = max(0, 1 - (brightness - 180) / 75)  # Penalize very bright
            else:
                brightness_factor = max(0, (brightness - 80) / 20)  # Penalize very dark
            
            # 3. MOST IMPORTANT: Low contrast indicates turbidity/haziness
            # Smug has low contrast (hard to see through), not sharp images
            contrast_factor = 0.0
            if contrast < 50:  # Low contrast = turbid
                contrast_factor = 1.0
            elif contrast < 100:
                contrast_factor = 1.0 - (contrast - 50) / 50  # Gradually decrease
            # else: high contrast = clear air, not smug
            
            # Combined score: ALL factors must be present
            # If any factor is low, smug probability is low
            smug_score = color_coverage * brightness_factor * contrast_factor
            
            logger.debug(f"Smug detection - Color coverage: {color_coverage*100:.2f}%, "
                        f"Brightness: {brightness:.2f} (factor: {brightness_factor:.2f}), "
                        f"Contrast: {contrast:.2f} (factor: {contrast_factor:.2f}), "
                        f"Final score: {smug_score:.3f}")
            
            return float(np.clip(smug_score, 0.0, 1.0))
        
        except Exception as e:
            logger.error(f"Error in smug detection: {str(e)}")
            return 0.0
    
    def _normalize_score(self, value: float, min_val: float, max_val: float, 
                        inverse: bool = False) -> float:
        """
        Normalize a value to 0-1 range.
        
        Args:
            value: Value to normalize
            min_val: Minimum value of the range
            max_val: Maximum value of the range
            inverse: If True, higher values result in lower scores
            
        Returns:
            Normalized score (0.0-1.0)
        """
        if max_val == min_val:
            return 0.5
        
        normalized = (value - min_val) / (max_val - min_val)
        normalized = np.clip(normalized, 0.0, 1.0)
        
        if inverse:
            normalized = 1.0 - normalized
        
        return float(normalized)
    
    def _empty_result(self) -> Dict[str, any]: # type: ignore
        """Return empty detection result."""
        return {
            'fog_detected': False,
            'smoke_detected': False,
            'probability_fog': 0.0,
            'probability_smoke': 0.0,
            'probability_vapor': 0.0,
            'probability_smug': 0.0,
            'analysis_details': {
                'frames_analyzed': 0,
                'error': 'No frames available for analysis'
            }
        }