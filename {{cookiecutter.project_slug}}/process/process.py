"""Implementacja procesu przetwarzania (Process)."""

import base64
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol, Union

from core.config import load_config
from core.logging import get_logger
from core.utils import create_temp_file, generate_id
from process.process_base import ProcessBase


class Engine(Protocol):
    """Protokół dla silnika przetwarzania (Process Engine)."""

    def process(self, text: str, config: Optional[Dict[str, Any]] = None) -> bytes:
        """
        Przetwarza tekst.

        Args:
            text: Tekst do przetworzenia
            config: Konfiguracja przetwarzania

        Returns:
            Dane wynikowe w formacie bytes
        """
        ...

    def get_available_resources(self) -> List[Dict[str, Any]]:
        """
        Pobiera listę dostępnych zasobów.

        Returns:
            Lista dostępnych zasobów z metadanymi
        """
        ...

    def get_available_languages(self) -> List[str]:
        """
        Pobiera listę dostępnych języków.

        Returns:
            Lista kodów języków (np. 'en-US', 'pl-PL')
        """
        ...


class ProcessResult:
    """Klasa reprezentująca wynik przetwarzania."""

    def __init__(
        self, result_data: bytes, format: str = "wav", metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Inicjalizuje wynik przetwarzania.

        Args:
            result_data: Dane wynikowe w formacie bytes
            format: Format danych (wav, mp3, json, etc.)
            metadata: Dodatkowe metadane wynikowe
        """
        self.id = generate_id("result-")
        self.result_data = result_data
        self.format = format
        self.metadata = metadata or {}
        self._file_path = None

    def save_to_file(self, directory: Optional[Union[str, Path]] = None) -> str:
        """
        Zapisuje dane wynikowe do pliku.

        Args:
            directory: Katalog, w którym ma być zapisany plik

        Returns:
            Ścieżka do zapisanego pliku
        """
        if directory:
            os.makedirs(directory, exist_ok=True)
            file_path = os.path.join(directory, f"{self.id}.{self.format}")
        else:
            file_path = create_temp_file(self.result_data, suffix=f".{self.format}")

        if not isinstance(file_path, str):
            file_path = str(file_path)

        with open(file_path, "wb") as f:
            f.write(self.result_data)

        self._file_path = file_path
        return file_path

    def get_base64(self) -> str:
        """
        Zwraca dane wynikowe jako string base64.

        Returns:
            Dane wynikowe zakodowane w base64
        """
        return base64.b64encode(self.result_data).decode("utf-8")

    def get_file_path(self) -> Optional[str]:
        """
        Zwraca ścieżkę do pliku, jeśli został zapisany.

        Returns:
            Ścieżka do pliku lub None, jeśli plik nie został zapisany
        """
        return self._file_path

    def __str__(self) -> str:
        return (
            f"ProcessResult(id={self.id}, format={self.format}, size={len(self.result_data)} bytes)"
        )


class DefaultEngine:
    """Domyślna implementacja silnika przetwarzania."""

    def __init__(self, config: Dict[str, Any]):
        """Inicjalizuje silnik przetwarzania.

        Args:
            config: Konfiguracja silnika
        """
        self.config = config
        self.logger = get_logger("process.engine")
        self.logger.info("Inicjalizacja domyślnego silnika przetwarzania")

    def process(self, text: str, config: Optional[Dict[str, Any]] = None) -> bytes:
        """Przetwarza tekst.

        Args:
            text: Tekst do przetworzenia
            config: Konfiguracja przetwarzania

        Returns:
            Dane wynikowe w formacie bytes
        """
        if config is None:
            config = {}

        language = config.get("language", self.config.get("PROCESS_LANGUAGE", "en-US"))
        resource = config.get("resource", self.config.get("PROCESS_RESOURCE", "default"))

        self.logger.info(f"Przetwarzanie tekstu: '{text}' (język: {language}, zasób: {resource})")

        # W rzeczywistej implementacji tutaj byłoby wywołanie silnika przetwarzania
        # Na potrzeby przykładu zwracamy przykładowe dane wynikowe
        return b"SAMPLE_RESULT_DATA"

    def get_available_resources(self) -> List[Dict[str, Any]]:
        """Pobiera listę dostępnych zasobów.

        Returns:
            Lista dostępnych zasobów z metadanymi
        """
        return [
            {"name": "default", "language": "en-US", "type": "standard"},
            {"name": "resource1", "language": "en-US", "type": "enhanced"},
            {"name": "resource2", "language": "pl-PL", "type": "standard"},
        ]

    def get_available_languages(self) -> List[str]:
        """Pobiera listę dostępnych języków.

        Returns:
            Lista kodów języków (np. 'en-US', 'pl-PL')
        """
        return ["en-US", "pl-PL", "de-DE", "fr-FR", "es-ES"]


class Process(ProcessBase):
    """Główna klasa procesu przetwarzania."""

    def __init__(self):
        """Inicjalizuje proces przetwarzania."""
        self.config = load_config()
        self.logger = get_logger("process")
        self.engine = None
        self.resource_cache = {}
        self.initialize(self.config.as_dict())

    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize the Process with the given configuration.

        Args:
            config: Configuration dictionary for the Process
        """
        self.logger.info("Inicjalizacja procesu przetwarzania")
        self.engine = self._create_engine(config)

    def _create_engine(self, config: Dict[str, Any]) -> Engine:
        """Tworzy silnik przetwarzania na podstawie konfiguracji.

        Args:
            config: Konfiguracja silnika

        Returns:
            Instancja silnika przetwarzania
        """
        engine_type = config.get("PROCESS_ENGINE", "default")
        self.logger.info(f"Tworzenie silnika przetwarzania typu: {engine_type}")

        # W rzeczywistej implementacji tutaj byłoby ładowanie odpowiedniego adaptera
        # Na potrzeby przykładu zawsze zwracamy domyślny silnik
        return DefaultEngine(config)

    @staticmethod
    def get_parameters_schema() -> Dict[str, Any]:
        """Zwraca schemat parametrów procesu.

        Returns:
            Schemat parametrów w formacie JSON Schema
        """
        return {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Tekst do przetworzenia"},
                "config": {"type": "object", "description": "Konfiguracja przetwarzania"},
                "output_format": {
                    "type": "string",
                    "description": "Format wyjściowy (wav, mp3, json)",
                    "enum": ["wav", "mp3", "json"],
                },
                "save_to_file": {"type": "boolean", "description": "Czy zapisać wynik do pliku"},
                "output_dir": {
                    "type": "string",
                    "description": "Katalog, w którym ma być zapisany plik",
                },
            },
            "required": ["text"],
            "additionalProperties": False,
        }

    def run(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Wykonuje proces przetwarzania.

        Args:
            parameters: Parametry procesu
                text: Tekst do przetworzenia
                config: Opcjonalna konfiguracja przetwarzania
                output_format: Format wyjściowy (wav, mp3, json, etc.)
                save_to_file: Czy zapisać wynik do pliku
                output_dir: Katalog, w którym ma być zapisany plik

        Returns:
            Wynik procesu zawierający dane wynikowe
        """
        # Walidacja parametrów
        text = parameters.get("text", "")
        if not text:
            self.logger.error("Brak tekstu do przetworzenia")
            raise ValueError("Tekst jest wymagany")

        process_config = parameters.get("config", {})
        output_format = parameters.get("output_format", "wav")
        save_to_file = parameters.get("save_to_file", False)
        output_dir = parameters.get("output_dir")

        self.logger.info(f"Uruchamianie procesu przetwarzania dla tekstu: '{text}'")

        # Wykonanie przetwarzania
        result_data = self.engine.process(text, process_config)

        # Utworzenie wyniku
        result = ProcessResult(result_data, format=output_format)

        # Zapisanie do pliku, jeśli wymagane
        if save_to_file:
            file_path = result.save_to_file(output_dir)
            self.logger.info(f"Zapisano wynik do pliku: {file_path}")

        # Przygotowanie odpowiedzi
        response = {"result_id": result.id, "format": result.format, "base64": result.get_base64()}

        if result.get_file_path():
            response["file_path"] = result.get_file_path()

        # Cache the result for later retrieval
        self.resource_cache[result.id] = {
            "id": result.id,
            "data": result_data,
            "format": output_format,
            "metadata": result.metadata,
        }

        return response

    def get_available_resources(self) -> List[Dict[str, Any]]:
        """Get a list of available resources for this Process.

        Returns:
            List of dictionaries, each representing a resource
            Each dictionary must include 'name' and 'type' keys
        """
        return self.engine.get_available_resources()

    def get_available_languages(self) -> List[str]:
        """Pobiera listę dostępnych języków.

        Returns:
            Lista kodów języków (np. 'en-US', 'pl-PL')
        """
        return self.engine.get_available_languages()

    def get_resource_by_id(self, resource_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific resource by its ID.

        Args:
            resource_id: Unique identifier for the resource

        Returns:
            Dictionary containing the resource data, or None if not found
        """
        return self.resource_cache.get(resource_id)

    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the Process.

        Returns:
            Dictionary containing status information
                Must include 'status' key with a string value
                Must include 'version' key with the version string
                May include other status information
        """
        return {
            "status": "running",
            "version": "1.0.0",
            "engine_type": self.config.get("PROCESS_ENGINE", "default"),
            "resources_count": len(self.get_available_resources()),
            "languages_count": len(self.get_available_languages()),
        }


class DefaultProcess(Process):
    """Domyślna implementacja procesu przetwarzania."""

    def __init__(self):
        """Inicjalizuje domyślny proces przetwarzania."""
        super().__init__()
