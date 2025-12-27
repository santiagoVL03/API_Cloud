import cv2
import numpy as np
import requests
from typing import List, Optional
import time
import logging

logger = logging.getLogger(__name__)


class CameraUtil:
    """Utility class for capturing frames from IP camera."""
    
    def __init__(self, camera_ip: str = "192.168.15.66"):
        """
        Initialize CameraUtil with camera IP address.
        
        Args:
            camera_ip: IP address of the camera (default: 192.168.15.66)
        """
        self.camera_ip = camera_ip
        self.video_url = f"http://{camera_ip}:8080/video"
        
    def capture_frames(self, num_frames: int = 24, delay: float = 0.1) -> List[np.ndarray]:
        """
        Capture multiple frames from IP camera.
        
        Args:
            num_frames: Number of frames to capture (default: 24)
            delay: Delay between frame captures in seconds (default: 0.1)
            
        Returns:
            List of captured frames as numpy arrays (BGR format)
        """
        frames = []
        cap = None
        
        try:
            logger.info(f"Connecting to camera at {self.video_url}")
            cap = cv2.VideoCapture(self.video_url)
            
            if not cap.isOpened():
                logger.error(f"Failed to open video stream from {self.video_url}")
                return frames
            
            logger.info(f"Capturing {num_frames} frames...")
            
            for i in range(num_frames):
                ret, frame = cap.read()
                
                if ret and frame is not None:
                    frames.append(frame.copy())
                    logger.info(f"Captured frame {i+1}/{num_frames}")
                else:
                    logger.warning(f"Failed to capture frame {i+1}/{num_frames}")
                
                # Small delay between captures
                if delay > 0 and i < num_frames - 1:
                    time.sleep(delay)
            
            logger.info(f"Successfully captured {len(frames)} frames")
            
        except Exception as e:
            logger.error(f"Error capturing frames: {str(e)}")
            
        finally:
            if cap is not None:
                cap.release()
                logger.info("Camera connection released")
        
        return frames
    
    def test_camera_connection(self) -> bool:
        """
        Test if camera is accessible.
        
        Returns:
            True if camera is accessible, False otherwise
        """
        try:
            cap = cv2.VideoCapture(self.video_url)
            is_opened = cap.isOpened()
            cap.release()
            
            if is_opened:
                logger.info(f"Camera at {self.video_url} is accessible")
            else:
                logger.warning(f"Cannot access camera at {self.video_url}")
            
            return is_opened
            
        except Exception as e:
            logger.error(f"Error testing camera connection: {str(e)}")
            return False
    
    def capture_single_frame(self) -> Optional[np.ndarray]:
        """
        Capture a single frame from the camera.
        
        Returns:
            Single frame as numpy array or None if capture fails
        """
        frames = self.capture_frames(num_frames=1, delay=0)
        return frames[0] if frames else None