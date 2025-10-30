import os
import math
import polyiamond
import re
import pickle

def eisToCar(eisInt):
    a, b = eisInt
    bwRe = -b/2
    bwIm = b*math.sqrt(3)/2
    x = a + bwRe
    y = bwIm
    return (x, y)

# p is a cartesian point
def rotate30(p):
    ''' (1, 0) -> (sqrt(3)/2, 1/2)
        (0, 1) -> (-1/2, sqrt(3)/2)
    \\begin{pmatrix}
    sqrt(3)/2 & -1/2 \\
    1/2       & sqrt(3)/2
    \\end{pmatrix}
    '''
    x, y = p
    sqrt3o2 = math.sqrt(3)/2
    rot_x = x*sqrt3o2 + y*-0.5
    rot_y = x*0.5 + y*sqrt3o2
    return rot_x, rot_y
    

def getPath(eisen_path: list[tuple[int]], make_cycle = True):
    length = len(eisen_path)
    path = ''
    for i, eis in enumerate(eisen_path):
        x, y = rotate30(eisToCar(eis))
        path += '({},{})--'.format(x, y)
        if i == length-1:
            if make_cycle:
                path += 'cycle'
            else:
                path = path[0:-2]
    return path

def getTeXpreamble(fileName: str) -> str:
    with open(fileName, 'r') as readFH:
        return ''.join(readFH.readlines())

def orientationsPicture(hname: str, hexiamond: set[tuple[int]]):
    oris = polyiamond.orientations(hname, hexiamond)
    picture = '\\Large\\noindent\\texttt{Rotations:}\n'
    
    def drawOris(oris, picture):
        picture += '\\[\n'
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
                
    picture = drawOris(oris['rotations'], picture)
    picture += '\n \\texttt{Mirrors:}\n'
    picture = drawOris(oris['mirrors'], picture)
                
    return picture

def pdfOrientations(no_extension_fname: str):
    body = ''
    for hname, hexiamond in polyiamond.HEXIAMONDS.items():
        body += orientationsPicture(hname, hexiamond)
        body += '\\pagebreak\n\n'
    makePDF(body, no_extension_fname)

def pdfGrid(no_extension_fname: str, eisen_path, points, triangles, point_size = 0.125):
    body = '\\[\n\\begin{tikzpicture}\n'
    body += '\\draw[line width = 3pt] {};\n'.format(getPath(eisen_path[0:-1]))
    # for p in points:
    #     x, y = eisToCar(p)
    #     body += '\\filldraw ({},{}) circle ({});\n'.format(x, y, point_size)
    for tri in triangles:
        body += '\\draw {};\n'.format(getPath(tri))
    body += '\\end{tikzpicture}\n\\]\n'
    makePDF(body, no_extension_fname)

def tikzGrid(eisen_path, points, triangles, no_lattice = True):
    commands = '\\draw[line width = 3pt, color = white] {};\n'.format(getPath(eisen_path[0:-1]))
    commands = '\\draw[line width = 1pt] {};\n'.format(getPath(eisen_path[0:-1]))
    if no_lattice:
        return commands
    for tri in triangles:
        commands += '\\draw[densely dotted] {};\n'.format(getPath(tri))
    return commands

def pdfPlacements(no_extension_fname: str):
    grid = polyiamond.makeHexagonishGrid()
    grid_path, interior_points, grid_triangles = grid['perim'], grid['points'], grid['triangles']

    tikz_grid = tikzGrid(grid_path, interior_points, grid_triangles)
    
    hexi_p = polyiamond.getPlacements(grid, polyiamond.HEXIAMONDS)
    body = ''
    for hname, placements in hexi_p.items():
        # if hname != 'hexagon':
        #     continue
        for placement in placements:
            body += '\\[\n\\begin{tikzpicture}\n'
            body += tikz_grid            
            path = getPath(placement[0])
            body += '\\filldraw[color = {}] {};\n'.format(hname, path)
            body += '\\draw[line width = 3pt] {};\n'.format(path)            
            body += '\\end{tikzpicture}\n\\]\n\\pagebreak\n\n'
    makePDF(body, no_extension_fname)

def pdfHexiamondNames(no_extension_fname: str):
    body = '\\begin{figure}\n\\captionsetup[subfigure]{labelformat=empty}\n'
    i = 1
    for hname, hex_path in polyiamond.HEXIAMONDS.items():
            
        body += '\\begin{subfigure}[b]{4.75pc}\\centering%\\resizebox{!}{7pc}\n{\\begin{tikzpicture}[scale=.525]\n'
        path = getPath(hex_path)
        body += '\\filldraw[color = {}] {};\n'.format(hname, path)
        body += '\\draw[line width = 1.5pt] {};\n'.format(path)
        x,y = polyiamond.averageCar(hex_path)
        body += '\\end{tikzpicture}}\n'
        body += '\\caption{{{}}}\n'.format('\large\\texttt{{{}}}'.format(hname))
        body += '\\end{subfigure}'
        if i % 6 == 0:
            body += '\n\n\\vspace{1ex}\n\n'
        i += 1
    body += '\\end{figure}\n'
    makePDF(body, no_extension_fname)

def pdfCovers(no_extension_fname, covers):
    
    grid = polyiamond.makeHexagonishGrid()
    grid_path = grid['perim']

    blt = 2.75 # black line thickness
    wlt = .9   # white line thickness
    rness = 1  # corner roundedness
    
    body = ''
    for cover in covers:
        body += '\\[\\begin{tikzpicture}\n'
        for polyname, placement in cover.items():
            hname = re.search('[^-]*', polyname).group(0)
            path = getPath(placement[0])
            body += '\\begin{scope}\n'
            body += '\\clip[rounded corners={r}pt] {p};\n'.format(p=path,r=rness)            
            body += '\\filldraw[color = {n},line cap=butt,rounded corners={r}pt] {p};\n'.format(n=hname, r=rness, p=path)
            body += '\\path[draw=black,line width={lw},line cap=butt,rounded corners = {r}pt] {p};\n'.format(lw=blt,r=rness,p=path)    
            body += '\\end{scope}\n'
    
        body += '\\path[draw=black,line width={lw}pt,line cap=butt,rounded corners={r}pt] {p};\n'.format(lw=blt,r=rness,p=getPath(grid_path))

        for polyname, placement in cover.items():
            hname = re.search('[^-]*', polyname).group(0)
            path = getPath(placement[0])
            body += '\\path[draw=white,line cap=butt,line width={lw}pt,rounded corners={r}pt] {p};\n'.format(lw=wlt,r=rness,p=path)            
            
        body += '\\end{tikzpicture}\\]\n\n\\pagebreak\n\n'
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

def oldMain():
    pdfHexiamondNames('name-hexiamonds')
    pdfOrientations('hexiamond-orientations')
    # pdfPlacements('all-placements')
    
    grid = polyiamond.makeHexagonishGrid()
    grid_path, interior_points, grid_triangles = grid['perim'], grid['points'], grid['triangles']
    pdfGrid('hexagonish-grid', grid_path, interior_points, grid_triangles)    
    

if __name__ == '__main__':
    with open('a-few-covers.pkl', 'rb') as f:
        covers = pickle.load(f)
    pdfCovers('one-cover', covers[38:39])
    
