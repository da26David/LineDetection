import cv2
import numpy as np
import xml.etree.ElementTree as ET

# Funktion zum Erkennen der schwarzen Zeichnung auf einem weißen Blatt
def detect_drawing(frame):
    # Frame in Graustufen umwandeln
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Histogramm-Anpassung zur Verbesserung des Kontrasts
    gray = cv2.equalizeHist(gray)

    # Gaussian Blur zur Rauschreduzierung
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Dynamische Schwellenwertoperation
    thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY_INV, 11, 2)

    return thresh

# Funktion zum Bereinigen des Schwellenbildes von weißen Punkten
def clean_image(thresh):
    # Median-Filter zur Rauschreduzierung
    filtered = cv2.medianBlur(thresh, 5)

    # Morphologische Operationen, um kleine Störungen zu entfernen
    kernel = np.ones((3, 3), np.uint8)  # Definiere einen 3x3 Kernel
    cleaned_image = cv2.morphologyEx(filtered, cv2.MORPH_CLOSE, kernel)

    # Optional: Erosion, um noch kleinere Punkte zu entfernen
    cleaned_image = cv2.erode(cleaned_image, kernel, iterations=1)

    return cleaned_image

# Funktion zum Extrahieren der Koordinaten der weißen Linien
def extract_coordinates(cleaned_image):
    # Konturen finden
    contours, _ = cv2.findContours(cleaned_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    coordinates = []  # Liste zur Speicherung der Koordinaten

    for contour in contours:
        for point in contour:
            coordinates.append(tuple(point[0]))  # Füge die Koordinaten des Punktes hinzu

    return coordinates

# Funktion zum Speichern der Koordinaten in einer XML-Datei
def save_coordinates_to_xml(coordinates, filename):
    root = ET.Element("Coordinates")

    for coord in coordinates:
        point = ET.SubElement(root, "Point")
        ET.SubElement(point, "X").text = str(coord[0])
        ET.SubElement(point, "Y").text = str(coord[1])

    tree = ET.ElementTree(root)
    tree.write(filename)

# Funktion zum Speichern der Koordinaten in einer SVG-Datei
def save_coordinates_to_svg(coordinates, filename):
    # SVG Header
    svg_content = f'<svg xmlns="http://www.w3.org/2000/svg" width="800" height="600" viewBox="0 0 800 600">\n'
    svg_content += '  <g stroke="black" fill="none">\n'

    # Linien aus den Koordinaten erstellen
    for coord in coordinates:
        x, y = coord
        svg_content += f'    <circle cx="{x}" cy="{y}" r="1"/>\n'  # Kleine Kreise für die Punkte

    svg_content += '  </g>\n</svg>'

    # Speichere den SVG-Inhalt in einer Datei
    with open(filename, 'w') as f:
        f.write(svg_content)
def save_coordinates_to_gcode(coordinates, filename):
    with open(filename, 'w') as f:
        f.write("G21 ; Setze Einheiten auf Millimeter\n")
        f.write("G90 ; Absolute Positionierung\n")
        f.write("G28 ; Referenzfahrt\n")

        if coordinates:
            # Gehe zur ersten Position ohne zu zeichnen
            f.write(f"G0 X{coordinates[0][0]} Y{coordinates[0][1]}\n")

            # Zeichne Linien zwischen den Punkten
            for x, y in coordinates[1:]:
                f.write(f"G1 X{x} Y{y} F1000 ; Bewege mit Vorschubgeschwindigkeit\n")

        f.write("G0 X0 Y0 ; Zurück zur Startposition\n")
        f.write("M30 ; Programmende\n")


def lines_to_gcode(lines, scale=1.0):
    gcode = ["G21 ; Set units to mm", "G90 ; Absolute positioning"]

    for i, (x1, y1, x2, y2) in enumerate(lines):
        x1, y1, x2, y2 = x1 * scale, y1 * scale, x2 * scale, y2 * scale

        if i == 0:
            gcode.append(f"G0 X{x1:.2f} Y{y1:.2f} ; Move to start")
        gcode.append(f"G1 X{x2:.2f} Y{y2:.2f} F1000 ; Draw line")

    gcode.append("G0 X0 Y0 ; Move back to origin")

    return gcode


# Zugriff auf die Webcam
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Fehler: Webcam konnte nicht geöffnet werden")
    exit()

while True:
    # Frame von der Webcam holen
    ret, frame = cap.read()
    if not ret:
        print("Fehler beim Lesen des Frames")
        break

    # Zeichnung auf dem Blatt erkennen
    thresholded = detect_drawing(frame)

    # Bereinige das Schwellenbild von weißen Punkten
    cleaned_image = clean_image(thresholded)

    # Extrahiere die Koordinaten der weißen Linien
    coordinates = extract_coordinates(cleaned_image)

    # Zeige das bereinigte Bild
    cv2.imshow('Bereinigtes Schwellenbild', cleaned_image)

    # Breche ab, wenn 'q' gedrückt wird oder mache ein Snapshot mit 's'
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('s'):
        # Speichere das bereinigte Bild
        cv2.imwrite('cleaned_image.png', cleaned_image)
        print("Bereinigtes Bild gespeichert als: cleaned_image.png")

        # Speichere die Koordinaten in einer XML-Datei
        save_coordinates_to_xml(coordinates, 'coordinates.xml')
        print("Koordinaten gespeichert in: coordinates.xml")

        # Speichere die Koordinaten in einer SVG-Datei
        save_coordinates_to_svg(coordinates, 'coordinates.svg')
        print("Koordinaten gespeichert in: coordinsates.svg")

        save_coordinates_to_gcode(coordinates, 'coordinates.gcode')
        print("Koordinaten gespecihert in: coordinates.gcode")



# Beispielaufruf:
# save_coordinates_to_gcode(coordinates, 'drawing.gcode')

# Ressourcen freigeben
cap.release()
cv2.destroyAllWindows()
