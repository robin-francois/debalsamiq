#!/usr/bin/env python3

import sqlite3
import sys
import json
import base64
import drawsvg as draw


def writeImg(id, data, ext):
    with open(id+"."+ext,'wb') as file:
        file.write(base64.b64decode(data))
        
filename = sys.argv[1]

connection = sqlite3.connect(filename)
connection.row_factory = sqlite3.Row
cursor = connection.cursor()

cursor.execute("SELECT * from THUMBNAILS")
rows = cursor.fetchall()

print("Extracting thumbnails in working directory")
for row in rows:
    attributes = row['attributes']
    jsonAttributes = json.loads(attributes)
    name = jsonAttributes['resourceID']
    b64image = jsonAttributes['image']
    writeImg(name, b64image, "png")
print("---")

print("INFO")
cursor.execute("SELECT * from INFO")
rows = cursor.fetchall()
for row in rows:
    name = row['NAME']
    value = row['VALUE']
    if name == "SchemaVersion":
        if float(value) < 2.0:
            print("SchemaVersion not supported yet")
            sys.exit(1)
print("---")
print("RESOURCES")
cursor.execute("SELECT * from RESOURCES")
rows = cursor.fetchall()
for row in rows:
    id = row['id']
    attributes = row['attributes']
    jsonAttributes = json.loads(attributes)
    kind = jsonAttributes['kind']
    data = row['data']
    if kind!='asset':
        processedData = json.loads(data)
        for key in processedData['mockup'].keys():
            if key=='controls':
                continue
            print(key, processedData['mockup'][key])
        canvasH = str(int(processedData['mockup']['measuredH'])+5)
        canvasW = str(int(processedData['mockup']['measuredW'])+5)
        print()
        d = draw.Drawing(int(canvasW),int(canvasH))
        d.embed_google_font('Balsamiq Sans')
        
        
        ElementDict = dict()
        
        # Order element first
        for element in processedData['mockup']['controls']['control']:
            ElementDict[int(element['zOrder'])]=element
            
        orderedList = list(ElementDict.keys())
        orderedList.sort()
        
        print(orderedList)
        
        # In order now, draw the elements
        for elementOrder in orderedList:
            element = ElementDict[elementOrder]
            typeID = element['typeID']
            print("[INFO]", element)
            
            # Phone
            if typeID == "AndroidPhone":
                phoneDict = dict()
                screenDict = dict()
                statusBar = dict()
                phoneDict['x'] = int(element['x'])
                phoneDict['y'] = int(element['y'])
                phoneDict['rx'] = 30
                phoneDict['ry'] = 30
                phoneDict['width'] = int(element['measuredW'])
                phoneDict['height'] = int(element['measuredH'])
                phoneDict['fill'] = 'white'
                phoneDict['stroke'] = 'grey'
                phoneDict['stroke_width'] = 7
                screenDict['x'] = int(element['x'])+15
                screenDict['y'] = int(element['y'])+75
                screenDict['width'] = int(element['measuredW'])-30
                screenDict['height'] = int(element['measuredH'])-150
                screenDict['fill'] = 'white'
                screenDict['stroke'] = 'grey'
                screenDict['stroke_width'] = 7
                statusBar['x'] = int(element['x'])+19
                statusBar['y'] = int(element['y'])+78
                statusBar['width'] = int(element['measuredW'])-37
                statusBar['height'] = 18
                statusBar['fill'] = 'lightgray'
                statusBar['stroke_width'] = 0
                
                d.append(draw.Rectangle(**phoneDict))
                d.append(draw.Rectangle(**screenDict))
                d.append(draw.Rectangle(**statusBar))

            
            # Canvas
            if typeID == "Canvas":
                rectDict = dict()
                rectDict['width'] = int(element['w'])
                if 'h' in element:
                    rectDict['height'] = element['h']
                else:
                    rectDict['height'] = 70
                rectDict['x'] = int(element['x'])
                rectDict['y'] = int(element['y'])
                rectDict['fill'] = 'white'
                rectDict['stroke'] = 'black'
                rectDict['stroke_width'] = 2
                if 'properties' in element.keys():
                    if 'color' in element['properties'].keys():
                        padding = 6
                        value = int(element['properties']['color'])
                        rectDict['fill'] = f"{value:#0{padding}x}".replace("0x","#")
                    if 'borderColor' in element['properties'].keys():
                        padding = 6
                        value = int(element['properties']['borderColor'])
                        rectDict['stroke'] = f"{value:#0{padding}x}".replace("0x","#")
                    if 'borderStyle' in element['properties'].keys():
                        if element['properties']['borderStyle'] == "roundedSolid":                            
                            rectDict['rx'] = 15
                            rectDict['ry'] = 15
                d.append(draw.Rectangle(**rectDict))
            
            # RoundButton
            if typeID == "RoundButton":
                roundBtnDict = dict()
                roundBtnDict['cx'] = int(element['x'])+int(element['w'])/2
                roundBtnDict['cy'] = int(element['y'])+int(element['h'])/2
                roundBtnDict['r'] = int(element['w'])/2
                roundBtnDict['fill'] = 'white'
                roundBtnDict['stroke'] = 'black'
                roundBtnDict['stroke_width'] = 2
                d.append(draw.Circle(**roundBtnDict))
            
                
            if typeID == "Paragraph" or typeID=="Button":
                x = element['x']
                y = element['y']
                w = element['w']
                h = element['h']
                d.append(draw.Raw('<svg x="{0}" y="{1}" width="{2}" height="{3}">'.format(x,y,w,h)))
                textDict = dict()
                
                if typeID=="Button":
                    rectDict = dict()
                    rectDict['width'] = int(element['w'])
                    if 'h' in element:
                        rectDict['height'] = element['h']
                    else:
                        rectDict['height'] = 70
                    rectDict['x'] = 0
                    rectDict['y'] = 0
                    rectDict['fill'] = 'white'
                    rectDict['stroke'] = 'black'
                    rectDict['stroke_width'] = 5
                    if 'properties' in element.keys():
                        if 'color' in element['properties'].keys():
                            padding = 6
                            value = int(element['properties']['color'])
                            rectDict['fill'] = f"{value:#0{padding}x}".replace("0x","#")
                        if 'borderColor' in element['properties'].keys():
                            padding = 6
                            value = int(element['properties']['borderColor'])
                            rectDict['stroke'] = f"{value:#0{padding}x}".replace("0x","#")
                        if 'borderStyle' in element['properties'].keys():
                            if element['properties']['borderStyle'] == "roundedSolid":                            
                                rectDict['rx'] = 15
                                rectDict['ry'] = 15
                        d.append(draw.Rectangle(**rectDict))                    
                    

                textDict['fill'] = 'black'
                textDict['text'] = element['properties']['text']
                textDict['font_size'] = '40'
                if typeID=="Button":
                    if 'icon' in element['properties'].keys():
                        if 'size' in element['properties']['icon']:
                            sizeIcon = element['properties']['icon']['size']
                            if sizeIcon == "small":
                                textDict['font_size'] = 15
                textDict['font_family'] = 'Balsamiq Sans'
                if 'size' in element['properties'].keys():
                    textDict['font_size'] = element['properties']['size']
                if "align" in element['properties'].keys():
                    if element['properties']['align'] == "center":
                        textDict['text_anchor']='middle'
                        textDict['x'] = str(int(w)/2)
                else:
                    textDict['x'] = 0
                    
                if typeID=="Button":
                    textDict['text_anchor']='middle'
                    textDict['x'] = str(int(w)/2)
                textDict['y'] = int(h)/2
                textDict['dominant_baseline']='middle'
                if 'properties' in element.keys():
                    if 'color' in element['properties'].keys() and typeID != "Button":
                        padding = 6
                        value = int(element['properties']['color'])
                        textDict['fill'] = f"{value:#0{padding}x}".replace("0x","#")
                    if 'color' in element['properties'].keys() and typeID == "Button":
                        textDict['fill'] = 'white'
                    if 'bold' in element['properties'].keys():
                            if element['properties']['bold'] == "true":
                                textDict['font_weight'] = 'bold'
                    # if 'align' in element['properties'].keys():
                    #     if element['properties']['align'] == "center":
                    #         textDict['text_anchor'] = 'middle'
                d.append(draw.Text(**textDict))
                d.append(draw.Raw('</svg>'))
            
            # Title
            if typeID == "Title":
                textDict = dict()
                textDict['x'] = int(element['x'])
                textDict['y'] = int(element['y'])
                textDict['fill'] = 'black'
                textDict['text'] = element['properties']['text']
                textDict['font_size'] = '40'
                textDict['font_family'] = 'Balsamiq Sans'
                if 'size' in element['properties'].keys():
                    textDict['font_size'] = element['properties']['size']
                if 'properties' in element.keys():
                    if 'color' in element['properties'].keys():
                        padding = 6
                        value = int(element['properties']['color'])
                        textDict['fill'] = f"{value:#0{padding}x}".replace("0x","#")
                    if 'bold' in element['properties'].keys():
                            if element['properties']['bold'] == "true":
                                textDict['font_weight'] = 'bold'
                    # if 'align' in element['properties'].keys():
                    #     if element['properties']['align'] == "center":
                    #         textDict['text_anchor'] = 'middle'
                textDict['y'] += int(textDict['font_size'])
                d.append(draw.Text(**textDict))
                
        
        d.save_svg(processedData['mockup']['attributes']['name']+".svg")
    else:
        writeImg(id, data, jsonAttributes['extension'])
    print(id, jsonAttributes)
    print("-")
print("---")