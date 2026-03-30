from PyQt6.QtCore import QEvent, QSize, Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from screeninfo import get_monitors

class WindowButton(QToolButton):
    def __init__(self, titleBar: QWidget, normal, hover, pressed):
        super().__init__(titleBar)

        self.normal_icon = QIcon(normal)
        self.hover_icon = QIcon(hover)
        self.pressed_icon = QIcon(pressed)
        self.setIcon(self.normal_icon)

    def enterEvent(self, event):
        self.setIcon(self.hover_icon)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.setIcon(self.normal_icon)
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        self.setIcon(self.pressed_icon)
        super().mousePressEvent(event)



class CustomTitleBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.initial_pos = None
        title_bar_layout = QHBoxLayout(self)
        title_bar_layout.setContentsMargins(1, 1, 1, 1)
        title_bar_layout.setSpacing(2)
        self.title = QLabel(f"{self.__class__.__name__}", self)
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setStyleSheet(
            """QLabel {
                    text-transform: uppercase;
                    font-size: 10pt;
                    margin-left: 48px;
                    color: white;
                }
            """
        )

        if title := parent.windowTitle():
            self.title.setText(title)
        title_bar_layout.addWidget(self.title)

        # Min button
        # self.min_button = QToolButton(self)
        # min_icon = QIcon()
        # min_icon.addFile("icons\\min.svg")
        # min_icon.addFile("icons\\min_hover.png", QSize(), QIcon.Mode.Active)
        # min_icon.addFile("icons\\min_pressed.png", QSize(), QIcon.Mode.Disabled)
        # self.min_button.setIcon(min_icon)
        self.min_button = WindowButton(self, "icons\\min.svg", "icons\\min_hover.svg", "icons\\min_pressed.svg")
        self.min_button.clicked.connect(self.window().showMinimized)

        # Max button
        # self.max_button = QToolButton(self)
        # max_icon = QIcon()
        # max_icon.addFile("icons\\max.svg")
        # self.max_button.setIcon(max_icon)
        self.max_button = WindowButton(self, "icons\\max.svg", "icons\\max_hover.svg", "icons\\max_pressed.svg")
        self.max_button.clicked.connect(self.window().showMaximized)

        # Close button
        # self.close_button = QToolButton(self)
        # close_icon = QIcon()
        # close_icon.addFile("icons\\close.svg")  # Close has only a single state.
        # self.close_button.setIcon(close_icon)
        self.close_button = WindowButton(self, "icons\\close.svg", "icons\\close_hover.svg", "icons\\close_pressed.svg")
        self.close_button.clicked.connect(self.window().close)

        # Normal button
        # self.normal_button = QToolButton(self)
        # normal_icon = QIcon()
        # normal_icon.addFile("icons\\max.svg")
        # self.normal_button.setIcon(normal_icon)
        self.normal_button = WindowButton(self, "icons\\max.svg", "icons\\max_hover.svg", "icons\\max_pressed.svg")
        self.normal_button.clicked.connect(self.window().showNormal)
        self.normal_button.setVisible(False)
        # Add buttons
        buttons = [
            self.min_button,
            self.normal_button,
            self.max_button,
            self.close_button,
        ]
        for button in buttons:
            button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            button.setFixedSize(QSize(16, 16))
            button.setStyleSheet(
                """QToolButton {
                        border: none;
                        padding: 2px;
                    }
                """
            )
            title_bar_layout.addWidget(button)

    def window_state_changed(self, state):
        if state == Qt.WindowState.WindowMaximized:
            self.normal_button.setVisible(True)
            self.max_button.setVisible(False)
        else:
            self.normal_button.setVisible(False)
            self.max_button.setVisible(True)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.initial_pos = event.position().toPoint()
        super().mousePressEvent(event)
        event.accept()

    def mouseMoveEvent(self, event):
        if self.initial_pos is not None:
            delta = event.position().toPoint() - self.initial_pos
            self.window().move(
                self.window().x() + delta.x(),
                self.window().y() + delta.y(),
            )
        super().mouseMoveEvent(event)
        event.accept()

    def mouseReleaseEvent(self, event):
        self.initial_pos = None
        super().mouseReleaseEvent(event)
        event.accept()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        firstMonitor = get_monitors()[0]

        self.setWindowTitle("Plane App")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMinimumSize(QSize(int(firstMonitor.width/3), int(firstMonitor.height/3)))
        self.resize(QSize(int(firstMonitor.width/2), int(firstMonitor.height/2)))

        central_widget = QWidget()
        # This container holds the window contents, so we can style it.
        central_widget.setObjectName("Container")
        central_widget.setStyleSheet(
            """#Container {
                    background: qlineargradient(x1:0 y1:0, x2:1 y2:1, stop:0 #051c2a stop:1 #44315f);
                    border-radius: 5px;
                }
            """
        )
        self.title_bar = CustomTitleBar(self)

        work_space_layout = QVBoxLayout()
        work_space_layout.setContentsMargins(11, 11, 11, 11)
        hello_label = QLabel("Hello, World!", self)
        hello_label.setStyleSheet("color: white;")
        work_space_layout.addWidget(hello_label)

        centra_widget_layout = QVBoxLayout()
        centra_widget_layout.setContentsMargins(0, 0, 0, 0)
        centra_widget_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        centra_widget_layout.addWidget(self.title_bar)
        centra_widget_layout.addLayout(work_space_layout)

        central_widget.setLayout(centra_widget_layout)
        self.setCentralWidget(central_widget)

    def changeEvent(self, event):
        if event.type() == QEvent.Type.WindowStateChange:
            self.title_bar.window_state_changed(self.windowState())
        super().changeEvent(event)
        event.accept()

app = QApplication([])

window = MainWindow()
window.show()

app.exec()
