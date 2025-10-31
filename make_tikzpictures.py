import os
import math
import polyiamond
import re
import pickle
import pymupdf
import sys
import subprocess

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
    

def tikzPath(eisen_path: list[tuple[int]], rotate=True):
    length = len(eisen_path)
    path = ''
    for i, eis in enumerate(eisen_path):
        x, y = eisToCar(eis)
        if rotate:
            x, y = rotate30((x,y))
        path += '({},{})--'.format(x, y)
        if i == length-1:
            path += 'cycle'
    return path

def getTeXpreamble(fileName: str) -> str:
    with open(fileName, 'r') as readFH:
        return ''.join(readFH.readlines())

def orientationsTeX(hname: str, hexiamond: set[tuple[int]]):
    oris = polyiamond.orientations(hname, hexiamond)
    tex = '\\Large\\noindent\\texttt{Rotations:}\n'
    
    def drawOris(oris, tex):
        tex += '\\[\n'
        for i, ori in enumerate(oris):
            tex += '\\begin{tikzpicture}\n'
            path = tikzPath(ori[0], rotate=False)
            tex += '\\filldraw[color = {}] {};\n'.format(hname, path)
            tex += '\\draw[line width = 4pt] {};\n'.format(path)        
            tex += '\\end{tikzpicture} \\ \\ \\ \n'
            if (i+1) % 3 == 0:
                tex += '\\]\n\n\\['
        tex += '\\]'
        return tex
                
    tex = drawOris(oris['rotations'], tex)
    tex += '\n \\texttt{Mirrors:}\n'
    tex = drawOris(oris['mirrors'], tex)
                
    return tex

def pdfOrientations(no_extension_fname: str):
    body = ''
    for hname, hexiamond in polyiamond.HEXIAMONDS.items():
        body += orientationsTeX(hname, hexiamond)
        body += '\\pagebreak\n\n'
    makePDF(body, no_extension_fname)

def tikzGrid(eisen_path, points, triangles, lattice = True, draw_points = False):
    commands = '\\draw[line width = 3pt] {};\n'.format(tikzPath(eisen_path[0:-1]))
    point_size = 0.125
    if draw_points:
        for p in points:
            x, y = eisToCar(p)
            commands += '\\filldraw ({},{}) circle ({});\n'.format(x, y, point_size)
    if lattice:
        for tri in triangles:
            commands += '\\draw {};\n'.format(tikzPath(tri))
    return commands    

def pdfGrid(no_extension_fname: str, eisen_path, points, triangles):
    body = '\\[\n\\begin{tikzpicture}\n'
    body += tikzGrid(eisen_path, points, triangles)
    body += '\\end{tikzpicture}\n\\]\n'
    makePDF(body, no_extension_fname)

def pdfPlacements(no_extension_fname: str, hnames):
    grid = polyiamond.makeHexagonishGrid()
    grid_path, interior_points, grid_triangles = grid['perim'], grid['points'], grid['triangles']

    tikz_grid = tikzGrid(grid_path, interior_points, grid_triangles)
    
    hexi_p = polyiamond.getPlacements(grid, polyiamond.HEXIAMONDS)
    body = ''
    for hname, placements in hexi_p.items():
        if hname not in hnames:
            continue
        for placement in placements:
            body += '\\[\n\\begin{tikzpicture}\n'
            body += tikz_grid            
            path = tikzPath(placement[0])
            body += '\\filldraw[color = {}] {};\n'.format(hname, path)
            body += '\\draw[line width = 3pt] {};\n'.format(path)            
            body += '\\end{tikzpicture}\n\\]\n\\pagebreak\n\n'
    makePDF(body, 'placements/{}'.format(no_extension_fname), doc_class = 'article')

def pdfHexiamondNames(no_extension_fname: str):
    body = '\\begin{minipage}{30pc}\n'
    
    topsep = '2ex'
    bottomsep = '.5ex'
    body += '\n\\vspace{{{}}}\n\n'.format(topsep)
    body += '\\begin{figure}\n\\centering\\captionsetup[subfigure]{labelformat=empty}\n'
    i = 1
    
    for hname, hex_path in polyiamond.HEXIAMONDS.items():    
        body += '\\begin{subfigure}[b]{4.75pc}\\centering%\\resizebox{!}{7pc}\n{\\begin{tikzpicture}[scale=.525]\n'
        path = tikzPath(hex_path, rotate=False)
        body += '\\filldraw[color = {}] {};\n'.format(hname, path)
        body += '\\draw[line width = 1.5pt] {};\n'.format(path)
        x,y = polyiamond.averageCar(hex_path)
        body += '\\end{tikzpicture}}\n'
        body += '\\caption{{{}}}\n'.format('\\large\\texttt{{{}}}'.format(hname))
        body += '\\end{subfigure}'
        if i == 6:
            body += '\n\n\\vspace{1ex}\n\n'
        i += 1
        
    body += '\\end{figure}\n'
    body += '\\vspace{{{}}}'.format(bottomsep)
    body += '\\end{minipage}'
    makePDF(body, no_extension_fname, doc_class = 'standalone')

def tikzCover(cover, grid_path, blt, wlt, rness):
    picture = '\\begin{tikzpicture}\n'
    for polyname, placement in cover.items():
        hname = re.search('[^-]*', polyname).group(0)
        path = tikzPath(placement[0])
        picture += '\\begin{scope}\n'
        picture += '\\clip[rounded corners={r}pt] {p};\n'.format(p=path,r=rness)            
        picture += '\\filldraw[color = {n},line cap=butt,rounded corners={r}pt] {p};\n'.format(n=hname, r=rness, p=path)
        picture += '\\path[draw=black,line width={lw},line cap=butt,rounded corners = {r}pt] {p};\n'.format(lw=blt,r=rness,p=path)    
        picture += '\\end{scope}\n'
    
    picture += '\\path[draw=black,line width={lw}pt,line cap=butt,rounded corners={r}pt] {p};\n'.format(lw=blt,r=rness,p=tikzPath(grid_path))

    for polyname, placement in cover.items():
        hname = re.search('[^-]*', polyname).group(0)
        path = tikzPath(placement[0])
        picture += '\\path[draw=white,line cap=butt,line width={lw}pt,rounded corners={r}pt] {p};\n'.format(lw=wlt,r=rness,p=path)                    
    picture += '\\end{tikzpicture}\n'
    return picture

def pdfCovers(no_extension_fname, covers, doc_class = 'article'):
    grid = polyiamond.makeHexagonishGrid()
    grid_path = grid['perim']

    blt = 2.75 # black line thickness
    wlt = .9   # white line thickness
    rness = 1  # corner roundedness

    is_article = doc_class == 'article'

    minipage_width = '25pc'
    topsep = '5ex'
    bottomsep = '5ex'
    
    body = ''
    if not is_article:
        body += '\\begin{minipage}'
        body += '{{{}}}\n'.format(minipage_width)
        body += '\\begin{figure}\\centering'
        body += '\\vspace{{{}}}\n\n'.format(topsep)
        
    for cover in covers:
        if is_article:
            body += '\\[\n'
            
        body += tikzCover(cover, grid_path, blt, wlt, rness)
        
        if is_article:
            body += '\\]\n\n\\pagebreak\n\n'
            
    if not is_article:
        body += '\n\\vspace{{{}}}\n\n'.format(bottomsep)
        body += '\\end{figure}\\end{minipage}\n'        
        
    makePDF(body, no_extension_fname, doc_class)
    

def makePDF(body: str, no_extension_fname: str, doc_class = 'article'):
    cwd = os.getcwd()
    
    os.chdir('pictures/')

    dirname = os.path.dirname(no_extension_fname)

    if dirname != '':
        os.chdir(dirname)

    basename = os.path.basename(no_extension_fname)
    
    tex_file = '{}.tex'.format(basename)
    
    with open(tex_file, 'w') as f:
        f.write('\\documentclass{{{cls}}}\n'.format(cls=doc_class))
        f.write(getTeXpreamble('{}/preamble-tikz.tex'.format(cwd)))
        f.write('\\begin{document}')
        f.write(body)
        f.write('\\end{document}')

    script_name = re.search('[^.]+', sys.argv[0]).group(0)

    log_fname = '{}/log_{}.txt'.format(cwd,script_name)
    print('Running pdflatex {}'.format(tex_file))
    try: 
        with open(log_fname, 'w') as f:
            subprocess.run(['pdflatex', '-interaction=nonstopmode', tex_file], stdout=f, stderr=subprocess.STDOUT, check=True)
    except subprocess.CalledProcessError as e:
        print("\n! pdflatex failed")
        with open(log_fname, 'r') as f:
            print("".join(f.readlines()[-15:]))

    if doc_class == 'standalone':
        pdf = pymupdf.open('{}.pdf'.format(basename))
        page = pdf[0]
        image = page.get_pixmap(dpi=1080)
        fname = '{}.png'.format(basename)
        image.save(fname, 'png', jpg_quality=100)

    os.chdir(cwd)

def oldMain(do_placements = False):
    grid = polyiamond.makeHexagonishGrid()
    grid_path, interior_points, grid_triangles = grid['perim'], grid['points'], grid['triangles']
    
    pdfHexiamondNames('names')
    pdfOrientations('orientations')
    pdfGrid('grid', grid_path, interior_points, grid_triangles)

    if do_placements:
        for hname in ['hexagon', 'butterfly', 'hook', 'yacht']:
            pdfPlacements(hname, [hname])

def coverMain(do_100_covers = False):
    with open('a-few-covers.pkl', 'rb') as f:
        covers = pickle.load(f)
    
    if do_100_covers:
        pdfCovers('100-covers', covers)
    else:
        pdfCovers('example-cover', covers[76:77], doc_class = 'standalone')
        pdfCovers('nice-cover', covers[38:39], doc_class = 'standalone')

if __name__ == '__main__':
    oldMain()
    coverMain()
    
