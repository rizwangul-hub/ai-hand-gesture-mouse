"""MediaPipe Hand Tracking wrapper supporting both Tasks API and legacy solutions."""

import os
import urllib.request
from typing import List, Optional, Tuple
import cv2
import numpy as np

import mediapipe as mp
from core.types import HandInfo, LandmarkPoint
from utils.logger import logger

MODEL_URL = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
MODEL_FILENAME = "hand_landmarker.task"


class HandTracker:
    """Detects 21 hand landmarks using Google MediaPipe HandLandmarker."""

    def __init__(self, model_path: Optional[str] = None, num_hands: int = 2):
        self.num_hands = num_hands
        self.model_path = model_path or os.path.join(os.path.dirname(os.path.dirname(__file__)), MODEL_FILENAME)
        self._detector = None
        self._use_tasks_api = False
        self._use_solutions_api = False
        self._init_mediapipe()

    def _ensure_model_file(self) -> bool:
        """Download the hand landmarker model asset if not present."""
        if os.path.exists(self.model_path) and os.path.getsize(self.model_path) > 1000:
            return True

        try:
            logger.info(f"Model file not found at {self.model_path}. Downloading from Google CDN...")
            os.makedirs(os.path.dirname(os.path.abspath(self.model_path)), exist_ok=True)
            urllib.request.urlretrieve(MODEL_URL, self.model_path)
            logger.info("MediaPipe HandLandmarker model downloaded successfully.")
            return True
        except Exception as exc:
            logger.error(f"Failed to download hand_landmarker model: {exc}")
            return False

    def _init_mediapipe(self):
        """Initialize the optimal available MediaPipe pipeline."""
        # Try modern MediaPipe Tasks API first
        if hasattr(mp, "tasks"):
            try:
                if self._ensure_model_file():
                    from mediapipe.tasks import python
                    from mediapipe.tasks.python import vision

                    base_options = python.BaseOptions(model_asset_path=self.model_path)
                    options = vision.HandLandmarkerOptions(
                        base_options=base_options,
                        running_mode=vision.RunningMode.IMAGE,
                        num_hands=self.num_hands,
                        min_hand_detection_confidence=0.5,
                        min_hand_presence_confidence=0.5,
                        min_tracking_confidence=0.5,
                    )
                    self._detector = vision.HandLandmarker.create_from_options(options)
                    self._use_tasks_api = True
                    logger.info("Initialized MediaPipe Tasks HandLandmarker successfully.")
                    return
            except Exception as exc:
                logger.warning(f"Failed to initialize MediaPipe Tasks API: {exc}")

        # Fallback to legacy solutions API if present
        if hasattr(mp, "solutions") and hasattr(mp.solutions, "hands"):
            try:
                self._solutions_hands = mp.solutions.hands.Hands(
                    static_image_mode=False,
                    max_num_hands=self.num_hands,
                    min_detection_confidence=0.5,
                    min_tracking_confidence=0.5,
                )
                self._use_solutions_api = True
                logger.info("Initialized legacy MediaPipe Solutions Hands.")
                return
            except Exception as exc:
                logger.warning(f"Failed to initialize MediaPipe Solutions: {exc}")

        logger.error("Could not initialize any MediaPipe hand tracking backend.")

    def process_frame(self, frame_bgr: np.ndarray) -> List[HandInfo]:
        """
        Process a BGR image frame and return detected hands with normalized landmarks.
        """
        if frame_bgr is None:
            return []

        rgb_frame = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        hands_found: List[HandInfo] = []

        if self._use_tasks_api and self._detector:
            try:
                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
                result = self._detector.detect(mp_image)

                if result.hand_landmarks:
                    for i, landmarks in enumerate(result.hand_landmarks):
                        # Extract handedness label if available
                        handedness = "Right"
                        confidence = 1.0
                        if result.handedness and i < len(result.handedness):
                            cat = result.handedness[i][0]
                            handedness = cat.category_name
                            confidence = cat.score

                        pts = [
                            LandmarkPoint(x=lm.x, y=lm.y, z=lm.z if hasattr(lm, "z") else 0.0)
                            for lm in landmarks
                        ]
                        hands_found.append(HandInfo(landmarks=pts, handedness=handedness, confidence=confidence))
                return hands_found
            except Exception as exc:
                logger.error(f"Error during HandLandmarker inference: {exc}")
                return []

        elif self._use_solutions_api and self._solutions_hands:
            try:
                result = self._solutions_hands.process(rgb_frame)
                if result.multi_hand_landmarks:
                    for i, lm_list in enumerate(result.multi_hand_landmarks):
                        handedness = "Right"
                        if result.multi_handedness and i < len(result.multi_handedness):
                            handedness = result.multi_handedness[i].classification[0].label

                        pts = [LandmarkPoint(x=lm.x, y=lm.y, z=lm.z) for lm in lm_list.landmark]
                        hands_found.append(HandInfo(landmarks=pts, handedness=handedness, confidence=0.9))
                return hands_found
            except Exception as exc:
                logger.error(f"Error during Solutions Hands inference: {exc}")
                return []

        return []

    def close(self):
        """Release underlying detector resources."""
        if self._detector and hasattr(self._detector, "close"):
            try:
                self._detector.close()
            except Exception:
                pass
            self._detector = None
