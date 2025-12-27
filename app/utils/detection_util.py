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
        # Fog detection thresholds
        self.fog_brightness_threshold = 180  # High brightness (white/gray fog)
        self.fog_contrast_threshold = 30     # Low contrast
        self.fog_saturation_threshold = 50   # Low saturation
        
        # Smoke detection thresholds
        self.smoke_brightness_range = (80, 200)  # Medium brightness
        self.smoke_edge_threshold = 20           # Blurred edges
        self.smoke_density_threshold = 0.3       # Coverage percentage
    
    def analyze_frames(self, frames: List[np.ndarray]) -> Dict[str, any]:
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
        
        # Determine detection (threshold: 0.5)
        fog_detected = avg_fog > 0.5
        smoke_detected = avg_smoke > 0.5
        
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
        
        Fog characteristics:
        - High overall brightness (whitish/grayish appearance)
        - Low contrast (reduced visibility)
        - Low color saturation (washed out colors)
        
        Args:
            frame: Input frame in BGR format
            
        Returns:
            Fog probability score (0.0-1.0)
        """
        # Convert to different color spaces
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # 1. Brightness analysis (V channel in HSV)
        brightness = np.mean(hsv[:, :, 2])
        brightness_score = self._normalize_score(
            brightness, 
            self.fog_brightness_threshold, 
            255, 
            inverse=False
        )
        
        # 2. Contrast analysis (standard deviation of grayscale)
        contrast = np.std(gray)
        contrast_score = self._normalize_score(
            contrast, 
            0, 
            self.fog_contrast_threshold, 
            inverse=True
        )
        
        # 3. Saturation analysis (S channel in HSV)
        saturation = np.mean(hsv[:, :, 1])
        saturation_score = self._normalize_score(
            saturation, 
            0, 
            self.fog_saturation_threshold, 
            inverse=True
        )
        
        # Weighted combination
        fog_score = (0.4 * brightness_score + 
                     0.4 * contrast_score + 
                     0.2 * saturation_score)
        
        return float(np.clip(fog_score, 0.0, 1.0))
    
    def _detect_smoke_in_frame(self, frame: np.ndarray) -> float:
        """
        Detect smoke in a single frame using edge detection and density.
        
        Smoke characteristics:
        - Medium brightness (darker than fog, lighter than clear)
        - Blurred/soft edges
        - Concentrated in certain areas
        
        Args:
            frame: Input frame in BGR format
            
        Returns:
            Smoke probability score (0.0-1.0)
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # 1. Brightness in expected range
        brightness = np.mean(gray)
        in_brightness_range = (self.smoke_brightness_range[0] <= brightness <= 
                              self.smoke_brightness_range[1])
        brightness_score = 1.0 if in_brightness_range else 0.3
        
        # 2. Edge detection (Canny)
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.sum(edges > 0) / edges.size
        edge_score = self._normalize_score(
            edge_density * 100, 
            0, 
            self.smoke_edge_threshold, 
            inverse=True
        )
        
        # 3. Texture analysis (local standard deviation)
        kernel_size = 15
        mean_filtered = cv2.blur(gray.astype(float), (kernel_size, kernel_size))
        squared_diff = (gray.astype(float) - mean_filtered) ** 2
        local_std = np.sqrt(cv2.blur(squared_diff, (kernel_size, kernel_size)))
        texture_score = np.mean(local_std) / 50.0  # Normalize
        
        # Weighted combination
        smoke_score = (0.3 * brightness_score + 
                       0.4 * edge_score + 
                       0.3 * texture_score)
        
        return float(np.clip(smoke_score, 0.0, 1.0))
    
    def _detect_vapor_in_frame(self, frame: np.ndarray) -> float:
        """
        Detect water vapor (similar to fog but less dense).
        
        Args:
            frame: Input frame in BGR format
            
        Returns:
            Vapor probability score (0.0-1.0)
        """
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Vapor is lighter than fog
        brightness = np.mean(hsv[:, :, 2])
        saturation = np.mean(hsv[:, :, 1])
        
        # High brightness, very low saturation
        vapor_score = 0.0
        if brightness > 160 and saturation < 60:
            vapor_score = (brightness - 160) / 95.0 * 0.6
            vapor_score += (60 - saturation) / 60.0 * 0.4
        
        return float(np.clip(vapor_score, 0.0, 1.0))
    
    def _detect_smug_in_frame(self, frame: np.ndarray) -> float:
        """
        Detect smog/smug (urban pollution haze).
        
        Args:
            frame: Input frame in BGR format
            
        Returns:
            Smug probability score (0.0-1.0)
        """
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Smug characteristics: yellowish/brownish tint, medium brightness
        hue = hsv[:, :, 0]
        saturation = hsv[:, :, 1]
        brightness = np.mean(gray)
        
        # Look for yellowish/brownish hues (15-35 in OpenCV's 0-179 scale)
        yellow_brown_mask = ((hue >= 15) & (hue <= 35) & (saturation > 20))
        smug_coverage = np.sum(yellow_brown_mask) / yellow_brown_mask.size
        
        smug_score = smug_coverage * 2.0  # Amplify the signal
        
        return float(np.clip(smug_score, 0.0, 1.0))
    
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
    
    def _empty_result(self) -> Dict[str, any]:
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