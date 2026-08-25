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

    def __init__(self, current_shortcut: str, parent=None) -> None:
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
            QKeySequence(current_shortcut), self
        )
        shortcuts_layout.addRow("Анализ архивов PLC:", self.plc_archive_shortcut)
        layout.addWidget(shortcuts_group)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel, parent=self
        )
        buttons.accepted.connect(self._validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def shortcut(self) -> str:
        """Возвращает назначение в переносимом текстовом формате Qt."""
        return self.plc_archive_shortcut.keySequence().toString(
            QKeySequence.PortableText
        )

    def _validate_and_accept(self) -> None:
        if not self.shortcut():
            QMessageBox.warning(
                self,
                "Горячая клавиша не задана",
                "Назначьте горячую клавишу для анализа архивов PLC.",
            )
            return
        self.accept()
