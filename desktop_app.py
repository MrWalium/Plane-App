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
    
    def mouseReleaseEvent(self, event):
        self.setIcon(self.normal_icon)
        return super().mouseReleaseEvent(event)



class CustomTitleBar(QWidget):
    def __init__(self, parent, button_size, if_title, change_cursor):
        super().__init__(parent)
        self.initial_pos = None
        title_bar_layout = QHBoxLayout(self)
        title_bar_layout.setContentsMargins(13, 7, 7, 10)
        title_bar_layout.setSpacing(2)
        self.change_cursor = change_cursor
        if(if_title):
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
        else:
            title_bar_layout.addStretch()

        self.is_max = False

        # Min button
        self.min_button = WindowButton(self, "icons\\min.svg", "icons\\min_hover.svg", "icons\\min_pressed.svg")

        # Max button
        self.max_button = WindowButton(self, "icons\\max.svg", "icons\\max_hover.svg", "icons\\max_pressed.svg")

        # Close button
        self.close_button = WindowButton(self, "icons\\close.svg", "icons\\close_hover.svg", "icons\\close_pressed.svg")

        # Normal button
        self.normal_button = WindowButton(self, "icons\\max.svg", "icons\\normal_hover.svg", "icons\\normal_pressed.svg")
        # self.normal_button = WindowButton(self, "icons\\close.svg", "icons\\close_hover.svg", "icons\\close_pressed.svg")
        self.normal_button.setVisible(False)

        # Actions
        self.min_button.clicked.connect(self.window().showMinimized)
        self.max_button.clicked.connect(lambda: self.windowMaxed(True))
        self.close_button.clicked.connect(self.window().close)
        self.normal_button.clicked.connect(lambda: self.windowMaxed(False))

        # Add buttons
        buttons = [
            self.min_button,
            self.normal_button,
            self.max_button,
            self.close_button,
        ]
        for button in buttons:
            button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            button.setFixedSize(QSize(button_size, button_size))
            button.setStyleSheet(
                """QToolButton {
                        border: none;
                        padding: 2px;
                    }
                """
            )
            
            title_bar_layout.addWidget(button)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.initial_pos = event.position().toPoint()
            if self.change_cursor: self.setCursor(Qt.CursorShape.SizeAllCursor)
        super().mousePressEvent(event)
        event.accept()

    def mouseMoveEvent(self, event):
        if not self.is_max and self.initial_pos is not None:
            delta = event.position().toPoint() - self.initial_pos
            self.window().move(
                self.window().x() + delta.x(),
                self.window().y() + delta.y(),
            )
        super().mouseMoveEvent(event)
        event.accept()

    def mouseReleaseEvent(self, event):
        self.initial_pos = None
        if self.change_cursor and event.button() == Qt.MouseButton.LeftButton:
            self.setCursor(Qt.CursorShape.ArrowCursor)
        super().mouseReleaseEvent(event)
        event.accept()
    
    def windowMaxed(self, maxed):
        self.is_max = maxed
        self.is_min = False
        if maxed:
            self.normal_button.setVisible(True)
            self.max_button.setVisible(False)
            self.window().showFullScreen()
        else:
            self.normal_button.setVisible(False)
            self.max_button.setVisible(True)
            self.window().showNormal()



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.firstMonitor = get_monitors()[0]

        self.setWindowTitle("Plane App")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMinimumSize(QSize(int(self.firstMonitor.width/3), int(self.firstMonitor.height/3)))
        # self.resize(QSize(int(firstMonitor.width/2), int(firstMonitor.height/2)))
        self.setNormal()

        central_widget = QWidget()
        # This container holds the window contents, so we can style it.
        central_widget.setObjectName("Container")
        central_widget.setStyleSheet(
            """#Container {
                    background: qlineargradient(x1:0 y1:0, x2:1 y2:1, stop:0 #555361 stop:1 #353145);
                    border-radius: 5px;
                }
            """
        )
        self.title_bar = CustomTitleBar(self, 18, False, False)

        work_space_layout = QHBoxLayout()
        work_space_layout.setContentsMargins(11, 11, 11, 11)
        hello_label = QLabel("Hello, World!", self)
        hello_label.setStyleSheet("color: white;")
        work_space_layout.addWidget(hello_label)

        centra_widget_layout = QHBoxLayout()
        centra_widget_layout.setContentsMargins(0, 0, 0, 0)
        centra_widget_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        centra_widget_layout.addLayout(work_space_layout)
        centra_widget_layout.addWidget(self.title_bar)

        central_widget.setLayout(centra_widget_layout)
        self.setCentralWidget(central_widget)

        self.setMouseTracking(True)
        central_widget.setMouseTracking(True)
        self.side_resize_margin = 8
        self.corner_resize_margin = 10
    
    def setNormal(self):
        self.resize(QSize(int(self.firstMonitor.width/2), int(self.firstMonitor.height/2)))
        self.setWindowState(Qt.WindowState.WindowNoState)
    
    def changeEvent(self, event):
        if event.type() == QEvent.Type.WindowStateChange:
            if self.isMinimized():
                self.showMinimized()
            else:
                if self.title_bar.is_max:
                    self.showFullScreen()
                else:
                    self.showNormal()
        super().changeEvent(event)
        event.accept()
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and not self.isFullScreen():
            edge = self.getEdge(event.position().toPoint())
            corner = self.getCorner(event.position().toPoint())
            if corner:
                self.windowHandle().startSystemResize(self.cornerToEdges(corner))
            if edge:
                self.windowHandle().startSystemResize(edge)
        super().mousePressEvent(event)

    def updateCursor(self, pos):
        if self.title_bar.geometry().contains(pos):
            self.setCursor(Qt.CursorShape.ArrowCursor)
            return
        if not self.isFullScreen():
            edge = self.getEdge(pos)
            corner = self.getCorner(pos)
            if corner == Qt.Corner.BottomRightCorner or corner == Qt.Corner.TopLeftCorner:
                self.setCursor(Qt.CursorShape.SizeFDiagCursor)
            elif corner == Qt.Corner.BottomLeftCorner or corner == Qt.Corner.TopRightCorner:
                self.setCursor(Qt.CursorShape.SizeBDiagCursor)
            elif edge == Qt.Edge.RightEdge or edge == Qt.Edge.LeftEdge:
                self.setCursor(Qt.CursorShape.SizeHorCursor)
            elif edge == Qt.Edge.BottomEdge:
                self.setCursor(Qt.CursorShape.SizeVerCursor)
            else:
                self.setCursor(Qt.CursorShape.ArrowCursor)
        
    def mouseMoveEvent(self, event):
        self.updateCursor(event.position().toPoint())
        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        self.updateCursor(event.position().toPoint())
        super().mouseReleaseEvent(event)
    

    def getEdge(self, pos):
        """ Helper to determine which edge the mouse is over """
        rect = self.rect()
        edge = None
        
        if pos.x() >= rect.width() - self.side_resize_margin:
            edge = Qt.Edge.RightEdge
        elif pos.x() <= self.side_resize_margin:
            edge = Qt.Edge.LeftEdge
        elif pos.y() >= rect.height() - self.side_resize_margin:
            edge = Qt.Edge.BottomEdge
        elif pos.y() <= self.side_resize_margin:
            edge = Qt.Edge.TopEdge
            
        return edge
    
    def getCorner(self, pos):
        rect = self.rect()
        corner = None

        if pos.x() >= rect.width() - self.corner_resize_margin and pos.y() >= rect.height() - self.corner_resize_margin:
            corner = Qt.Corner.BottomRightCorner
        elif pos.x() <= self.corner_resize_margin and pos.y() >= rect.height() - self.corner_resize_margin:
            corner = Qt.Corner.BottomLeftCorner
        elif pos.x() >= rect.width() - self.corner_resize_margin and pos.y() <= self.corner_resize_margin:
            corner = Qt.Corner.TopRightCorner
        elif pos.x() <= self.corner_resize_margin and pos.y() <= self.corner_resize_margin:
            corner = Qt.Corner.TopLeftCorner
        
        return corner
    
    def cornerToEdges(self, corner):
        edges = None

        if corner == Qt.Corner.TopRightCorner:
            edges = Qt.Edge.RightEdge | Qt.Edge.TopEdge
        elif corner == Qt.Corner.TopLeftCorner:
            edges = Qt.Edge.LeftEdge | Qt.Edge.TopEdge
        elif corner == Qt.Corner.BottomLeftCorner:
            edges = Qt.Edge.LeftEdge | Qt.Edge.BottomEdge
        elif corner == Qt.Corner.BottomRightCorner:
            edges = Qt.Edge.RightEdge | Qt.Edge.BottomEdge
        
        return edges



app = QApplication([])

window = MainWindow()
window.show()

app.exec()
