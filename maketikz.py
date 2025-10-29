import os
import math
import hexiamonds

def eisToCar(eisInt):
    a, b = eisInt
    bwRe = -b/2
    bwIm = b*math.sqrt(3)/2
    x = a + bwRe
    y = bwIm
    return x, y

def getPath(eisen_path: list[tuple[int]]):
    length = len(eisen_path)
    path = ''
    for i, eis in enumerate(eisen_path):
        x, y = eisToCar(eis)
        path += '({},{})--'.format(x, y)
        if i == length-1:
            path += 'cycle'
    return path

def getTeXpreamble(fileName: str) -> str:
    with open(fileName, 'r') as readFH:
        return ''.join(readFH.readlines())

def orientationsPicture(hname: str, hexiamond: set[tuple[int]]):
    oris = hexiamonds.orientations(hname, hexiamond)
    picture = '\\[\n'
    for i, ori in enumerate(oris):
        picture += '\\begin{tikzpicture}\n'
        path = getPath(ori[0])
        picture += '\\filldraw[color = {}] {};\n'.format(hname, path)
        picture += '\\draw[line width = 4pt] {};\n'.format(path)        
        picture += '\\end{tikzpicture} \ \ \ \n'
        if (i+1) % 3 == 0:
            picture += '\\]\n\n\\['
    picture += '\\]'
    return picture

def drawOrientations(no_extension_fname: str):
    body = ''
    for hname, hexiamond in hexiamonds.HEXIAMONDS.items():
        body += orientationsPicture(hname, hexiamond)
        body += '\\pagebreak\n\n'
    makePDF(body, no_extension_fname)
        

def makePDF(body: str, no_extension_fname: str):
    os.chdir('pictures/')
    tex_file = '{}.tex'.format(no_extension_fname)
    
    with open(tex_file, 'w') as f:
        f.write('\\documentclass{article}')
        f.write(getTeXpreamble('../preamble-tikz.tex'))
        f.write('\\begin{document}')
        f.write(body)
        f.write('\\end{document}')
        
    os.system('pdflatex {}'.format(tex_file))
    
    os.chdir('..')

if __name__ == '__main__':
    drawOrientations('hex-orientations')
    
