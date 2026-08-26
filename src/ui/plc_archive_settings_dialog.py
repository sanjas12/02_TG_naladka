from PyQt5.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QLabel,
    QVBoxLayout,
)


class PlcArchiveSettingsDialog(QDialog):
    """Настройки отображения анализа архивов PLC."""

    def __init__(self, event_window_seconds: float, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Настройки анализа архивов PLC")
        self.setMinimumWidth(470)

        layout = QVBoxLayout(self)
        layout.addWidget(
            QLabel(
                "Номера на графике и события в правой таблице отображаются, "
                "когда видимый диапазон времени не превышает заданное значение."
            )
        )
        form = QFormLayout()
        self.event_window = QDoubleSpinBox(self)
        self.event_window.setRange(0.1, 60.0)
        self.event_window.setDecimals(1)
        self.event_window.setSingleStep(0.1)
        self.event_window.setSuffix(" с")
        self.event_window.setValue(event_window_seconds)
        form.addRow("Показывать события при масштабе до:", self.event_window)
        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel, parent=self
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def event_window_seconds(self) -> float:
        """Возвращает выбранный порог видимого диапазона."""
        return self.event_window.value()
