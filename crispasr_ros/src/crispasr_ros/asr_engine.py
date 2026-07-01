"""CrispASR Engine wrapper for transcribing audio buffers using GGML models.
"""

from __future__ import annotations

import os
import logging
import numpy as np

from crispasr_ros.runtime_paths import ensure_crispasr_runtime_paths

ensure_crispasr_runtime_paths(__file__)

from crispasr import Session

logger = logging.getLogger("crispasr_ros.asr_engine")

class ASREngine:
    """ASR Engine that wraps the CrispASR Session class for transcription."""

    def __init__(
        self,
        model_path: str,
        n_threads: int = 4,
        frequency_penalty: float = 0.0,
    ) -> None:
        """Initialize the ASREngine.

        Args:
            model_path: Path to the GGUF model file.
            n_threads: Number of threads to run inference on.
            frequency_penalty: Repeated-token frequency penalty. 0 disables it.

        Raises:
            FileNotFoundError: If the model file does not exist.
        """
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")
            
        logger.info(f"Loading ASR model: {model_path}")
        self.session = Session(model_path, n_threads=n_threads)
        if frequency_penalty > 0.0:
            try:
                self.session.set_frequency_penalty(frequency_penalty)
                logger.info(f"Applied frequency penalty: {frequency_penalty}")
            except Exception as e:
                logger.warning(f"Could not apply frequency penalty: {e}")
        logger.info(f"ASR Model loaded. Backend: {self.session.backend}")

    def transcribe(self, pcm_f32: np.ndarray, language: str | None = None) -> str:
        """Transcribe floating point PCM samples to text.

        Args:
            pcm_f32: Floating point PCM samples normalized to [-1.0, 1.0] at 16kHz.
            language: Optional ISO 639-1 language code (e.g., "ja", "en").

        Returns:
            The transcribed text segment, or empty string on failure or empty input.
        """
        if len(pcm_f32) == 0:
            return ""
        try:
            segments = self.session.transcribe(pcm_f32, language=language)
            text = " ".join([seg.text for seg in segments]).strip()
            return text
        except Exception as e:
            logger.error(f"Error during transcription: {e}")
            return ""

    def offload_to_cpu(self) -> None:
        """Offload the model's active weights from VRAM to Host System RAM."""
        try:
            self.session.offload_to_cpu()
        except Exception as e:
            logger.error(f"Error during offload: {e}")
            raise

    def load_to_gpu(self) -> None:
        """Load the model's weights from Host System RAM back to VRAM."""
        try:
            self.session.load_to_gpu()
        except Exception as e:
            logger.error(f"Error during load: {e}")
            raise
