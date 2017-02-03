#
#

import os
from xml.dom import minidom, Node
from dxfwrite import DXFEngine as dxf

#drawing.add(dxf.line((0, 0), (10, 0), color=7))
#drawing.add_layer('TEXTLAYER', color=2)
#drawing.add(dxf.text('Test', insert=(0, 0.2), layer='TEXTLAYER'))
#drawing.save()

# "50,150 50,200 200,200 200,100" -> [(50,50), (50, 200), ... (200,100)]
def make_points(s):
    points = []
    for w in s.split():
        ww = w.split(',')
        points.append((float(ww[0]), float(ww[1])))
    return points

def draw_defs(svg, drawing):
    return

# "M110.07,-58.97A6.77,6.77 0 0,0 118.35,-60.88"
# "m 318.4839,-29.6019 1.18156,0.102826 1.13018,-0.20549 1.07882,-0.410966 0.92468,-0.66784 0.77058,-0.873301"
# "M 10,215 210,215 110, 42 z M 10,100 210,100 110,273 z"
def draw_path(path, drawing, shift):
    id = path.getAttribute('id')
    style = path.getAttribute('style')
    d = path.getAttribute('d')
    d_orig = d # DEBUG

    d = d.replace('M', 'M ')
    d = d.replace('m', 'm ')
    d = d.replace('L', ' L ')
    d = d.replace('l', ' l ')
    d = d.replace('A', ' A ')
    d = d.replace('Q', ' Q ')
    d = d.replace('C', ' C ')
    d = d.replace('z', ' z ')
    d = d.replace(',', ' ')
    words = d.split()
    closed = False
    points = []
    pos = 0
    abs_coord = True
    try:
        while pos < len(words):
            w = words[pos]
            pos += 1
            if w == 'M' or w == 'm':
                draw_points(drawing, apply_transform(points, shift), closed)
                points = [(float(words[pos]), float(words[pos+1]))]
                closed = False
                abs_coord = (w == 'M')
                pos += 2
            elif w == 'Z' or w == 'z':
                closed = True
            elif w == 'L' or w == 'l':
                abs_coord = (w == 'L')
                if abs_coord:
                    points.append((float(words[pos]), float(words[pos + 1])))
                else:
                    points.append((float(words[pos]) + points[-1][0], float(words[pos+1]) + points[-1][1]))
                pos += 2
            elif w == 'A':
                pos += 7
            elif w == 'Q':
                pos += 2
            elif w == 'C' or w == 'c':
                pos += 6
            else:
                if abs_coord:
                    points.append((float(w), float(words[pos])))
                else:
                    points.append((float(w) + points[-1][0], float(words[pos]) + points[-1][1]))
                pos += 1
    except:
        print ("Error: d=%s" % d_orig)
        print ("Error: d=%s" % d)
        raise

    if len(points) > 0:
        draw_points(drawing, apply_transform(points, shift), closed)
    return
        
def draw_points(drawing, points, closed):
    if len(points) == 0:
        return
    polyline = dxf.polyline()
    polyline.add_vertices(points)
    polyline.close(status=closed)
    drawing.add(polyline)
    
    return

def translate(x, y):
    return (x, y)

def apply_transform(points, shift):
    if len(points) == 0:
        return points
    for i in range(len(points)):
        points[i] = (points[i][0] + shift[0], points[i][1] + shift[1])
    #print ("points: ", points)
    return points

def draw_group(svg, drawing, shift=(0, 0)):
    transform = svg.getAttribute('transform')
    if transform:
        print("transform %s" % transform)
        if transform.startswith('translate'):
            (s0, s1) = eval(transform)
            shift = (shift[0] + s0, shift[1] + s1)
        print("shift: (%g, %g)" % shift)

    for cp in svg.childNodes:
        #print(cp.__class__)
        if cp.nodeType == Node.ELEMENT_NODE:
            #print(cp.tagName)
            if cp.tagName == 'rect':
                # make rect
                x = float(cp.getAttribute('x'))
                y = float(cp.getAttribute('y'))
                width = float(cp.getAttribute('width'))
                height = float(cp.getAttribute('height'))
                polyline = dxf.polyline()
                polyline.add_vertices( [(x, y), (x + width, y), (x + width, y + height), (x, y + height)] )
                polyline.close(status=True)
                drawing.add(polyline)
            elif cp.tagName == 'text':
                # make text
                x = float(cp.getAttribute('x'))
                y = float(cp.getAttribute('y'))
            elif cp.tagName == 'circle':
                cx = float(cp.getAttribute('cx'))
                cy = float(cp.getAttribute('cy'))
                r = float(cp.getAttribute('r'))
                circle = dxf.circle(r, (cx, cy))
                drawing.add(circle)
            elif cp.tagName == 'g':
                draw_group(cp, drawing, shift)
            elif cp.tagName == 'svg':
                draw_group(cp, drawing, shift)
            elif cp.tagName == 'defs':
                draw_defs(cp, drawing)
            elif cp.tagName == 'line':
                x1 = float(cp.getAttribute('x1'))
                y1 = float(cp.getAttribute('y1'))
                x2 = float(cp.getAttribute('x2'))
                y2 = float(cp.getAttribute('y2'))
                line = dxf.line((x1, y1), (x2, y2))
                drawing.add(line)
            elif cp.tagName == 'polyline':
                points = make_points(cp.getAttribute('points'))
                polyline = dxf.polyline()
                polyline.add_vertices(points)
                drawing.add(polyline)
            elif cp.tagName == 'path':
                draw_path(cp, drawing, shift)
            else:
                print("*** unknown tag: <%s> ***" % cp.tagName) 
    return

if __name__ == '__main__':
    #svg_file = "svg_code_0.svg"
    svg_file = "svg_i-16.svg"
    #svg_file = "svg_traktor.svg"
    #svg_file = "svg_code_1.svg"
    #svg_file = "svg_code_2.svg"
    #svg_file = "svg_code_3.svg"
    #svg_file = "svg_code_4.svg"
    #svg_file = "svg_code_5.svg"

    dxf_file = os.path.basename(svg_file) + '.dxf'

    doc = minidom.parse(svg_file)
    drawing = dxf.drawing(dxf_file)

    svg = doc.documentElement
    draw_group(svg, drawing)
    drawing.save()
    print ("Saved: %s" % dxf_file)

#doc.unlink()
