import json
import logging
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Вспомогательные константы
# ---------------------------------------------------------------------------

DEFAULTS = {
    "FONT_SIZE": 8,
    "TICK_MARK_COUNT_X": 15,
    "TICK_MARK_COUNT_Y": 10,
    "LEVEL_LOG": "INFO",
    "ANALYS_AIM": "Значение развертки. Положение ГСМ",
    "GSM_A_CUR": "ГСМ-А.Текущее положение",
    "GSM_B_CUR": "ГСМ-Б.Текущее положение",
}


# ===========================================================================
# AxeName
# ===========================================================================


@pytest.mark.unit
class TestAxeName:
    def test_axename_list_signals_value(self):
        # Arrange / Act
        from config.config import AxeName

        # Assert
        assert AxeName.LIST_SIGNALS.value == "Список сигналов"

    def test_axename_base_axe_value(self):
        from config.config import AxeName

        assert AxeName.BASE_AXE.value == "Основная Ось"

    def test_axename_secondary_axe_value(self):
        from config.config import AxeName

        assert AxeName.SECONDARY_AXE.value == "Вспомогательная Ось"

    def test_axename_time_axe_value(self):
        from config.config import AxeName

        assert AxeName.TIME_AXE.value == "Ось Времени"

    def test_axename_has_exactly_four_members(self):
        from config.config import AxeName

        assert len(AxeName) == 4

    def test_axename_members_are_unique(self):
        from config.config import AxeName

        values = [m.value for m in AxeName]
        assert len(values) == len(set(values))


# ===========================================================================
# get_base_path
# ===========================================================================


@pytest.mark.unit
class TestGetBasePath:
    def test_get_base_path_finds_pyproject_toml(self, tmp_path):
        # Arrange
        (tmp_path / "pyproject.toml").touch()
        fake_file = tmp_path / "src" / "config" / "config.py"
        fake_file.parent.mkdir(parents=True)
        fake_file.touch()

        # Act
        with patch("config.config.__file__", str(fake_file)):
            from config.config import get_base_path

            result = get_base_path()

        # Assert
        assert result == tmp_path

    def test_get_base_path_finds_readme_md(self, tmp_path):
        # Arrange
        (tmp_path / "Readme.md").touch()
        fake_file = tmp_path / "src" / "config" / "config.py"
        fake_file.parent.mkdir(parents=True)
        fake_file.touch()

        with patch("config.config.__file__", str(fake_file)):
            from config.config import get_base_path

            result = get_base_path()

        assert result == tmp_path

    def test_get_base_path_frozen_returns_executable_parent(self, tmp_path):
        # Arrange — эмулируем frozen-сборку (PyInstaller)
        fake_exe = tmp_path / "myapp.exe"
        fake_exe.touch()

        mock_sys = MagicMock()
        mock_sys.frozen = True
        mock_sys.executable = str(fake_exe)

        with patch("config.config.sys", mock_sys):
            from config.config import get_base_path

            result = get_base_path()

        # Assert
        assert result == tmp_path

    def test_get_base_path_no_marker_returns_fallback(self, tmp_path):
        # Arrange — директория без маркерных файлов
        fake_file = tmp_path / "src" / "config" / "config.py"
        fake_file.parent.mkdir(parents=True)
        fake_file.touch()

        with patch("config.config.__file__", str(fake_file)):
            from config.config import get_base_path

            result = get_base_path()

        # Assert — возвращает parent.parent от __file__
        assert isinstance(result, Path)


# ===========================================================================
# _load_settings  (тестируем через публичный load_runtime_settings)
# ===========================================================================


@pytest.mark.unit
class TestLoadRuntimeSettings:
    """
    load_runtime_settings() модифицирует глобальный _SETTINGS.
    Мокируем файловую систему через tmp_path + patch _SETTINGS_FILE.
    """

    def _reload_with_file(self, settings_path, monkeypatch):
        """Хелпер: патчит _SETTINGS_FILE и перезапускает load_runtime_settings."""
        import config.config as cfg

        monkeypatch.setattr(cfg, "_SETTINGS_FILE", settings_path)
        monkeypatch.setattr(cfg, "_SETTINGS", {})
        cfg.load_runtime_settings()
        return cfg

    # --- happy path: файл существует и содержит валидный JSON ---

    def test_load_runtime_settings_valid_json_overrides_defaults(
        self, tmp_path, monkeypatch
    ):
        # Arrange
        settings_file = tmp_path / "settings.json"
        settings_file.write_text(json.dumps({"FONT_SIZE": 42}), encoding="utf-8")

        # Act
        cfg = self._reload_with_file(settings_file, monkeypatch)

        # Assert
        assert cfg._SETTINGS["FONT_SIZE"] == 42

    def test_load_runtime_settings_valid_json_keeps_missing_defaults(
        self, tmp_path, monkeypatch
    ):
        # Arrange
        settings_file = tmp_path / "settings.json"
        settings_file.write_text(json.dumps({"FONT_SIZE": 42}), encoding="utf-8")

        # Act
        cfg = self._reload_with_file(settings_file, monkeypatch)

        # Assert — ключи, которых нет в файле, берутся из DEFAULTS
        assert cfg._SETTINGS["TICK_MARK_COUNT_X"] == DEFAULTS["TICK_MARK_COUNT_X"]

    def test_load_runtime_settings_all_defaults_present_when_empty_json(
        self, tmp_path, monkeypatch
    ):
        # Arrange — пустой объект: все значения из дефолтов
        settings_file = tmp_path / "settings.json"
        settings_file.write_text("{}", encoding="utf-8")

        # Act
        cfg = self._reload_with_file(settings_file, monkeypatch)

        # Assert
        for key, value in DEFAULTS.items():
            assert cfg._SETTINGS[key] == value

    # --- edge case: файл не существует ---

    def test_load_runtime_settings_missing_file_creates_defaults(
        self, tmp_path, monkeypatch
    ):
        # Arrange
        settings_file = tmp_path / "settings.json"
        assert not settings_file.exists()

        # Act
        cfg = self._reload_with_file(settings_file, monkeypatch)

        # Assert — дефолты загружены
        assert cfg._SETTINGS == DEFAULTS

    def test_load_runtime_settings_missing_file_creates_json_on_disk(
        self, tmp_path, monkeypatch
    ):
        # Arrange
        settings_file = tmp_path / "settings.json"

        # Act
        self._reload_with_file(settings_file, monkeypatch)

        # Assert — файл был создан
        assert settings_file.exists()

    def test_load_runtime_settings_missing_file_created_json_is_valid(
        self, tmp_path, monkeypatch
    ):
        # Arrange
        settings_file = tmp_path / "settings.json"

        # Act
        self._reload_with_file(settings_file, monkeypatch)

        # Assert — созданный файл содержит валидный JSON
        data = json.loads(settings_file.read_text(encoding="utf-8"))
        assert data == DEFAULTS

    # --- негативный сценарий: битый JSON ---

    def test_load_runtime_settings_invalid_json_falls_back_to_defaults(
        self, tmp_path, monkeypatch
    ):
        # Arrange
        settings_file = tmp_path / "settings.json"
        settings_file.write_text("{ not valid json !!!", encoding="utf-8")

        # Act
        cfg = self._reload_with_file(settings_file, monkeypatch)

        # Assert
        assert cfg._SETTINGS == DEFAULTS

    # --- негативный сценарий: ошибка чтения файла ---

    def test_load_runtime_settings_os_error_falls_back_to_defaults(
        self, tmp_path, monkeypatch
    ):
        # Arrange
        settings_file = tmp_path / "settings.json"
        settings_file.write_text("{}", encoding="utf-8")

        import config.config as cfg

        monkeypatch.setattr(cfg, "_SETTINGS_FILE", settings_file)
        monkeypatch.setattr(cfg, "_SETTINGS", {})

        original_open = Path.open

        def broken_open(self, *args, **kwargs):
            if self == settings_file:
                raise OSError("disk error")
            return original_open(self, *args, **kwargs)

        monkeypatch.setattr(Path, "open", broken_open)

        # Act
        cfg.load_runtime_settings()

        # Assert
        assert cfg._SETTINGS == DEFAULTS

    # --- edge case: пользователь передаёт полный набор настроек ---

    def test_load_runtime_settings_full_override_no_defaults_leaked(
        self, tmp_path, monkeypatch
    ):
        # Arrange
        custom = {
            "FONT_SIZE": 16,
            "TICK_MARK_COUNT_X": 20,
            "TICK_MARK_COUNT_Y": 5,
            "LEVEL_LOG": "DEBUG",
            "ANALYS_AIM": "custom aim",
            "GSM_A_CUR": "custom_a",
            "GSM_B_CUR": "custom_b",
        }
        settings_file = tmp_path / "settings.json"
        settings_file.write_text(json.dumps(custom), encoding="utf-8")

        # Act
        cfg = self._reload_with_file(settings_file, monkeypatch)

        # Assert — все значения пользовательские
        for key, value in custom.items():
            assert cfg._SETTINGS[key] == value

    # --- логирование: overridden-ключи ---

    def test_load_runtime_settings_logs_overridden_keys(
        self, tmp_path, monkeypatch, caplog
    ):
        # Arrange
        settings_file = tmp_path / "settings.json"
        settings_file.write_text(json.dumps({"FONT_SIZE": 99}), encoding="utf-8")

        # Act
        with caplog.at_level(logging.INFO, logger="config.config"):
            self._reload_with_file(settings_file, monkeypatch)

        # Assert — в логах упоминается переопределённый ключ
        assert "FONT_SIZE" in caplog.text


# ===========================================================================
# Публичные константы (значения по умолчанию при пустом _SETTINGS)
# ===========================================================================


@pytest.mark.unit
class TestPublicConstants:
    """
    Константы вычисляются в момент импорта через _get().
    Проверяем, что при пустом _SETTINGS они равны дефолтным значениям.
    """

    def test_font_size_default(self, monkeypatch):
        import config.config as cfg

        monkeypatch.setattr(cfg, "_SETTINGS", {})

        result = cfg._get("FONT_SIZE", 8)

        assert result == 8

    def test_tick_mark_count_x_default(self, monkeypatch):
        import config.config as cfg

        monkeypatch.setattr(cfg, "_SETTINGS", {})

        result = cfg._get("TICK_MARK_COUNT_X", 15)

        assert result == 15

    def test_tick_mark_count_y_default(self, monkeypatch):
        import config.config as cfg

        monkeypatch.setattr(cfg, "_SETTINGS", {})

        result = cfg._get("TICK_MARK_COUNT_Y", 10)

        assert result == 10

    def test_level_log_default_is_info(self, monkeypatch):
        import config.config as cfg

        monkeypatch.setattr(cfg, "_SETTINGS", {})

        level_str = cfg._get("LEVEL_LOG", "INFO")
        result = getattr(logging, str(level_str).upper(), logging.INFO)

        assert result == logging.INFO

    def test_level_log_debug_resolves_correctly(self, monkeypatch):
        import config.config as cfg

        monkeypatch.setattr(cfg, "_SETTINGS", {"LEVEL_LOG": "DEBUG"})

        level_str = cfg._get("LEVEL_LOG", "INFO")
        result = getattr(logging, str(level_str).upper(), logging.INFO)

        assert result == logging.DEBUG

    def test_level_log_invalid_value_falls_back_to_info(self, monkeypatch):
        import config.config as cfg

        monkeypatch.setattr(cfg, "_SETTINGS", {"LEVEL_LOG": "NOTAVALUE"})

        level_str = cfg._get("LEVEL_LOG", "INFO")
        result = getattr(logging, str(level_str).upper(), logging.INFO)

        assert result == logging.INFO

    def test_get_returns_value_from_settings(self, monkeypatch):
        import config.config as cfg

        monkeypatch.setattr(cfg, "_SETTINGS", {"FONT_SIZE": 24})

        result = cfg._get("FONT_SIZE", 8)

        assert result == 24

    def test_get_returns_default_when_key_missing(self, monkeypatch):
        import config.config as cfg

        monkeypatch.setattr(cfg, "_SETTINGS", {})

        result = cfg._get("NONEXISTENT_KEY", "fallback")

        assert result == "fallback"


# ===========================================================================
# Строковые константы модуля
# ===========================================================================


@pytest.mark.unit
class TestModuleStringConstants:
    def test_combined_time_value(self):
        from config.config import COMBINED_TIME

        assert COMBINED_TIME == "Время"

    def test_default_time_value(self):
        from config.config import DEFAULT_TIME

        assert DEFAULT_TIME == "дата/время"

    def test_default_ms_value(self):
        from config.config import DEFAULT_MS

        assert DEFAULT_MS == "миллисекунды"

    def test_format_contains_levelname(self):
        from config.config import FORMAT

        assert "%(levelname)s" in FORMAT

    def test_format_contains_asctime(self):
        from config.config import FORMAT

        assert "%(asctime)s" in FORMAT
