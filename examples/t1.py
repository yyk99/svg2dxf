#
# Borrowed from https://pypi.python.org/pypi/dxfwrite/
#

from dxfwrite import DXFEngine as dxf

drawing = dxf.drawing('test.dxf')
drawing.add(dxf.line((0, 0), (10, 0), color=7))
drawing.add_layer('TEXTLAYER', color=2)
drawing.add(dxf.text('Test', insert=(0, 0.2), layer='TEXTLAYER'))
drawing.save()
