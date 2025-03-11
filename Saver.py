import xml.etree.ElementTree as ET

'''
Saver klasse um das Speicher aus der Main klasse zu entfernen und dne Code übersichtlicher zu machen

Hier gibt es methoden zum speichern in allen nötigen Dateiformaten: svg, xml, gcode
'''
class Saver:
    @staticmethod
    def save_coordinates_to_xml(coordinates, filename):
        root = ET.Element("Coordinates")

        for coord in coordinates:
            point = ET.SubElement(root, "Point")
            ET.SubElement(point, "X").text = str(coord[0])
            ET.SubElement(point, "Y").text = str(coord[1])

        tree = ET.ElementTree(root)
        tree.write(filename)
        print(f"Koordinaten gespeichert in: {filename}")

    @staticmethod
    def save_coordinates_to_svg(coordinates, filename):
        svg_content = f'<svg xmlns="http://www.w3.org/2000/svg" width="800" height="600" viewBox="0 0 800 600">\n'
        svg_content += '  <g stroke="black" fill="none">\n'

        for coord in coordinates:
            x, y = coord
            svg_content += f'    <circle cx="{x}" cy="{y}" r="1"/>\n'

        svg_content += '  </g>\n</svg>'

        with open(filename, 'w') as f:
            f.write(svg_content)
        print(f"Koordinaten gespeichert in: {filename}")

    @staticmethod
    def save_coordinates_to_gcode(coordinates, filename):
        with open(filename, 'w') as f:
            f.write("G21 ; Setze Einheiten auf Millimeter\n")
            f.write("G90 ; Absolute Positionierung\n")
            f.write("G28 ; Referenzfahrt\n")

            if coordinates:
                f.write(f"G0 X{coordinates[0][0]} Y{coordinates[0][1]}\n")

                for x, y in coordinates[1:]:
                    f.write(f"G1 X{x} Y{y} F1000 ; Bewege mit Vorschubgeschwindigkeit\n")

            f.write("G0 X0 Y0 ; Zurück zur Startposition\n")
            f.write("M30 ; Programmende\n")
        print(f"Koordinaten gespeichert in: {filename}")
