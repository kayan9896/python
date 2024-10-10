import sys
import math
from PyQt5.QtWidgets import (QApplication, QGraphicsView, QGraphicsScene, QGraphicsItem, 
                             QGraphicsEllipseItem, QGraphicsLineItem, QMainWindow, 
                             QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QWidget)
from PyQt5.QtGui import QImage, QPixmap, QPen, QTransform
from PyQt5.QtCore import Qt, QRectF, QPointF


class PointItem(QGraphicsEllipseItem):
    """Custom QGraphicsEllipseItem to represent a point with drag and click behavior."""
    def __init__(self, v, x, y, radius=5):
        super().__init__(x - radius, y - radius, radius * 2, radius * 2)
        self.setBrush(Qt.red)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.setCursor(Qt.PointingHandCursor)
        self.radius = radius
        self.viewer = v
        self.click = 0

    def mousePressEvent(self, event):
        """Handle mouse press event to add a point."""
        if self.click == 0:
            return
        if event.button() == Qt.LeftButton:
            self.viewer.eventFilter(self.viewer, event)

    def mouseReleaseEvent(self, event):
        """Handle deleting point when clicking without moving."""
        if self.click == 0:
            self.click = 1
            return
        if event.button() == Qt.LeftButton:
            # If no movement happened, delete the point
            if event.scenePos() == event.buttonDownScenePos(Qt.LeftButton):
                self.viewer.remove_point(self)
            self.viewer.update_line()
            super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        self.setPos(self.mapToScene(event.pos()))
        self.viewer.update_line()


class ImageViewer(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.points = []
        self.line = None

    def load_image(self, image_path):
        """Load an image into the scene."""
        image = QImage(image_path)
        pixmap = QPixmap.fromImage(image)
        self.scene.addPixmap(pixmap)
        self.setSceneRect(QRectF(pixmap.rect()))  # Fit the scene to the image size

    def add_point(self, x, y):
        """Add a point to the scene and handle interactions."""
        point = PointItem(self, 0, 0)
        self.scene.addItem(point)
        self.points.append(point)
        point.setPos(x, y)
        point.installSceneEventFilter(point)
        self.update_line()

    def remove_point(self, point):
        """Remove a point from the scene."""
        self.scene.removeItem(point)
        self.points.remove(point)
        self.update_line()

    def update_line(self):
        """Update the line connecting two points or remove it."""
        if len(self.points) == 2:
            if self.line is None:
                self.line = QGraphicsLineItem()
                pen = QPen(Qt.blue, 2)
                self.line.setPen(pen)
                self.scene.addItem(self.line)
            p1 = self.points[0].scenePos()
            p2 = self.points[1].scenePos()
            self.line.setLine(p1.x(), p1.y(), p2.x(), p2.y())

            # Calculate and display the distance
            distance = self.calculate_distance(p1, p2)
            self.viewer_distance_label.setText(f"Distance: {distance:.2f} units")
        else:
            if self.line is not None:
                self.scene.removeItem(self.line)
                self.line = None
                self.viewer_distance_label.setText("Distance: N/A")

    def calculate_distance(self, p1, p2):
        """Calculate the Euclidean distance between two points."""
        return math.sqrt((p1.x() - p2.x()) ** 2 + (p1.y() - p2.y()) ** 2)

    def mousePressEvent(self, event):
        """Handle mouse press event to add a point."""
        if event.button() == Qt.LeftButton:
            scene_pos = self.mapToScene(event.pos())
            items_at_pos = self.scene.items(QPointF(scene_pos))
            for i in items_at_pos:
                if isinstance(i, PointItem):
                    super().mousePressEvent(event)
                    return
            if len(self.points) < 2:
                self.add_point(scene_pos.x(), scene_pos.y())
            else:
                print("Only two points are allowed.")
        super().mousePressEvent(event)

    def zoom_in(self):
        """Zoom in on the image."""
        self.scale(1.2, 1.2)

    def zoom_out(self):
        """Zoom out of the image."""
        self.scale(0.8, 0.8)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set up the central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)

        # Image viewer area (3/4 of the width)
        self.viewer = ImageViewer()
        layout.addWidget(self.viewer, 3)  # 3/4 of the width

        # Control panel area (1/4 of the width)
        control_panel = QWidget()
        control_layout = QVBoxLayout(control_panel)
        layout.addWidget(control_panel, 1)  # 1/4 of the width

        # Zoom in button
        zoom_in_button = QPushButton("Zoom In")
        zoom_in_button.clicked.connect(self.viewer.zoom_in)
        control_layout.addWidget(zoom_in_button)

        # Zoom out button
        zoom_out_button = QPushButton("Zoom Out")
        zoom_out_button.clicked.connect(self.viewer.zoom_out)
        control_layout.addWidget(zoom_out_button)

        # Distance label
        self.viewer.viewer_distance_label = QLabel("Distance: N/A")
        control_layout.addWidget(self.viewer.viewer_distance_label)

    def load_image(self, image_path):
        self.viewer.load_image(image_path)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.load_image('heatmap.png')  # Load the image
    window.setWindowTitle("Biomedical Image Viewer")
    window.show()

    sys.exit(app.exec_())
