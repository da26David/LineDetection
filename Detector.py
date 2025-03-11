import cv2
import numpy as np
from Saver import Saver  # Externe Klasse zum Speichern von Koordinaten

# Funktion zum Erkennen der schwarzen Zeichnung auf einem weißen Blatt
def detect_drawing(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)
    blurred = cv2.GaussianBlur(gray, (7, 7), 0)
    thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY_INV, 11, 2)
    return thresh

# Funktion zum Bereinigen des Schwellenbildes von weißen Punkten
def clean_image(thresh):
    filtered = cv2.medianBlur(thresh, 5)
    kernel = np.ones((3, 3), np.uint8)
    cleaned_image = cv2.morphologyEx(filtered, cv2.MORPH_CLOSE, kernel)
    cleaned_image = cv2.erode(cleaned_image, kernel, iterations=1)
    return cleaned_image

# Funktion zum Extrahieren der Koordinaten der weißen Linien
def extract_coordinates(cleaned_image):
    contours, _ = cv2.findContours(cleaned_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    coordinates = []

    for contour in contours:
        for point in contour:
            coordinates.append(tuple(point[0]))
        # Trennungssignal (Stift heben)
        coordinates.append(None)

    return coordinates


# Zugriff auf die Webcam
cap = cv2.VideoCapture(1)

if not cap.isOpened():
    print("Fehler: Webcam konnte nicht geöffnet werden")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Fehler beim Lesen des Frames")
        break

    # Zeichnung erkennen und bereinigen
    thresholded = detect_drawing(frame)
    cleaned_image = clean_image(thresholded)

    # Koordinaten extrahieren
    coordinates = extract_coordinates(cleaned_image)

    # Zeige das bereinigte Bild
    cv2.imshow('Bereinigtes Schwellenbild', cleaned_image)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('s'):
        # Bild speichern
        cv2.imwrite('cleaned_image.png', cleaned_image)
        print("Bereinigtes Bild gespeichert als: cleaned_image.png")

        # Koordinaten speichern über die Saver-Klasse
        Saver.save_coordinates_to_xml(coordinates, 'coordinates.xml')
        Saver.save_coordinates_to_svg(coordinates, 'coordinates.svg')
        Saver.save_coordinates_to_gcode(coordinates, 'coordinates.gcode')

# Ressourcen freigeben
cap.release()
cv2.destroyAllWindows()
