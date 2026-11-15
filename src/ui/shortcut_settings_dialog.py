from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGroupBox,
    QKeySequenceEdit,
    QLabel,
    QMessageBox,
    QVBoxLayout,
)


class ShortcutSettingsDialog(QDialog):
    """Окно переназначения горячих клавиш приложения."""

    def __init__(
        self,
        plc_archive_shortcut: str,
        add_all_signals_shortcut: str,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Настройка горячих клавиш")
        self.setMinimumWidth(480)

        layout = QVBoxLayout(self)
        layout.addWidget(
            QLabel(
                "Нажмите новую клавишу или сочетание клавиш, затем сохраните настройки."
            )
        )

        shortcuts_group = QGroupBox("Анализ")
        shortcuts_layout = QFormLayout(shortcuts_group)
        self.plc_archive_shortcut = QKeySequenceEdit(
            QKeySequence(plc_archive_shortcut), self
        )
        shortcuts_layout.addRow("Анализ архивов PLC:", self.plc_archive_shortcut)
        layout.addWidget(shortcuts_group)

        signals_group = QGroupBox("Добавление сигналов")
        signals_layout = QFormLayout(signals_group)
        self.add_all_signals_shortcut = QKeySequenceEdit(
            QKeySequence(add_all_signals_shortcut), self
        )
        signals_layout.addRow("Добавить все сигналы:", self.add_all_signals_shortcut)
        layout.addWidget(signals_group)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel, parent=self
        )
        buttons.accepted.connect(self._validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def plc_shortcut(self) -> str:
        """Возвращает хоткей анализа PLC в переносимом формате Qt."""
        return self.plc_archive_shortcut.keySequence().toString(
            QKeySequence.PortableText
        )

    def add_all_shortcut(self) -> str:
        """Возвращает хоткей добавления всех сигналов."""
        return self.add_all_signals_shortcut.keySequence().toString(
            QKeySequence.PortableText
        )

    def _validate_and_accept(self) -> None:
        if not self.plc_shortcut() or not self.add_all_shortcut():
            QMessageBox.warning(
                self,
                "Горячая клавиша не задана",
                "Назначьте обе горячие клавиши.",
            )
            return
        if self.plc_shortcut().casefold() == self.add_all_shortcut().casefold():
            QMessageBox.warning(
                self,
                "Конфликт горячих клавиш",
                "Для команд должны быть назначены разные горячие клавиши.",
            )
            return
        self.accept()
