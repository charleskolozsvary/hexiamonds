import math
import itertools
# coordinate (a, b) corresponds to Eisenstein integer a + b\omega

# hexiamond names from https://mathworld.wolfram.com/Hexiamond.html
HEXIAMONDS = {'bar'      : [(0,0), (1,0), (2,0), (3,0), (4,1), (3,1), (2,1), (1,1)],
              'crook'    : [(0,0), (1,0), (2,0), (3,1), (2,1), (1,1), (1,2), (0,1)], 
              'crown'    : [(0,0), (1,0), (2,0), (3,1), (2,1), (2,2), (1,1), (0,1)],
              'sphinx'   : [(0,0), (1,0), (2,0), (3,0), (3,1), (2,1), (2,2), (1,1)],
              'snake'    : [(0,0), (0,-1),(1,0), (2,0), (3,1), (3,2), (2,1), (1,1)],
              'yacht'    : [(0,0), (1,0), (2,0), (3,1), (3,2), (2,1), (2,2), (1,1)],
              'chevron'  : [(0,0), (1,0), (2,0), (3,1), (4,2), (3,2), (2,1), (1,1)],
              'signpost' : [(0,0), (0,-1),(1,0), (2,0), (3,1), (2,1), (2,2), (1,1)],
              'lobster'  : [(0,0), (0,-1),(1,0),(1,-1), (2,0), (2,1), (2,2), (1,1)],
              'hook'     : [(0,0), (1,0), (2,1), (2,0), (3,1), (3,2), (2,2), (1,1)],
              'hexagon'  : [(0,0), (1,0), (2,1), (2,2), (1,2), (0,1)],
              'butterfly': [(0,0), (1,0), (2,0), (2,1), (3,2), (2,2), (1,2), (1,1)]}

def sumTuples(t1: tuple[int], t2: tuple[int]):
    return tuple(sum(z) for z in zip(t1, t2))

def triwise(p: list[int]):
    return list(map(lambda x: [x[0][0], x[0][1], x[1][1]], itertools.pairwise(itertools.pairwise(p))))

def eisToCar(eisInt):
    a, b = eisInt
    bwRe = -b/2
    bwIm = b*math.sqrt(3)/2
    x = a + bwRe
    y = bwIm
    return (x, y)

def distance(p1, p2):
    return math.sqrt((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2)

def averageCar(eisens):
    cartesians = list(map(lambda x: eisToCar(x), eisens))
    avgx = sum(map(lambda x: x[0], cartesians)) / len(eisens)
    avgy = sum(map(lambda x: x[1], cartesians)) / len(eisens)
    return (avgx, avgy)

# return triangles that make up a hexiamond
def getTriangles(in_eisen_path: list[tuple[int]], hname: str):

    is_convex = not (hname == 'hook' or hname == 'yacht' or hname == 'lobster')
    
    eisen_path = in_eisen_path.copy()
    triangles = set()

    if hname == 'hexagon': #this is kind of gross
        eisen_path += [(1,1)]

    trips = triwise(eisen_path)
    triplets = {frozenset(three): three for three in trips}

    center = averageCar(eisen_path)
    
    def trisAround(eisen: tuple[int]):
        tris = set()
        directions = [(1,0),(1,1),(0,1),(-1,0),(-1,-1),(0,-1)]
        prev = (0,-1)
        for direc in directions:
            tris.add(frozenset({eisen, sumTuples(eisen, direc), sumTuples(eisen, prev)}))
            prev = direc
        return tris

    def inEisens(tri: set[tuple[int]]):
        for e in tri:
            if e not in eisen_path:
                return False
        if is_convex: #yeah, also sloppy but works
            return True
        if tri in triplets: # detect empty concave trianlge
            threePath = triplets[tri]
            distance_from_center_first = distance(eisToCar(threePath[0]), center)
            distance_from_center_second = distance(eisToCar(threePath[1]), center)
            if distance_from_center_first > distance_from_center_second:
                return False
        return True
            
    for point in eisen_path:
        tsAround = trisAround(point)
        for t in tsAround:
            if inEisens(t):
                triangles.add(t)
                
    return triangles

# \sigma: rotate passed Eisenstein integers by 60 degrees counter-clockwise
# (multiply by 1+\omega)
# \sigma(a + b\omega) = (a + b\omega)(1+\omega) = (a-b) + a\omega
def rotate60(eisen_path: list[tuple[int]]):
    return list(map(lambda x: (x[0]-x[1], x[0]), eisen_path))

# \tau: reflect passed Eisenstein integers across the line z(1+\omega), 
# where z \in \mathbb{Z}
# \tau(a + b\omega) = b + a\omega
def reflect(eisen_path: list[tuple[int]]):
    return list(map(lambda x: (x[1], x[0]), eisen_path))

# subtract the minimum real value from each Eisenstein integer and
# subtract the minimum complex value from each Eisenstein integer
def normalize(eisen_path: list[tuple[int]]):
    mina = min(map(lambda x: x[0], eisen_path))
    minb = min(map(lambda x: x[1], eisen_path))
    return list(map(lambda x: (x[0]-mina, x[1]-minb), eisen_path))

# return unique orientations as a list of tuples of the form (closed_Eisenstein_integer_path, sets_of_triangles)
def orientations(hname: str, hexiamond: list[tuple[int]]):

    unique_triangle_sets = set()

    unique_rot = []
    unique_ref = []
    
    prev = hexiamond

    def addIfUnique(u_paths, eisen_path, path_tris):
        if path_tris not in unique_triangle_sets:
            frz_tris = frozenset(path_tris)
            unique_triangle_sets.add(frz_tris)
            u_paths.append((eisen_path, path_tris))
    
    for _ in range(6):
        rotated = normalize(rotate60(prev))
        tri_rot = getTriangles(rotated, hname)
        addIfUnique(unique_rot, rotated, tri_rot)
        prev = rotated

    for rot_path,rot_tri in unique_rot:
        reflected = normalize(reflect(rot_path))
        tri_ref = getTriangles(reflected, hname)
        addIfUnique(unique_ref, reflected, tri_ref)
        
    return {'rotations':unique_rot, 'mirrors':unique_ref}

# return the manhattan distance from the eisenInt to the origin
def manhattanDist(a, b):
    return abs(a) + abs(b) if a*b <= 0 else max(abs(a), abs(b))

def makeHexagonishGrid():
    start = (-3,-5)
    transitions = [(1,0),(1,1),(1,0),(1,1),(1,0),(1,1),
                   (0,1),(1,1),(0,1),(1,1),(0,1),
                   (-1,0),(0,1),(-1,0),(0,1),(-1,0),
                   (-1,-1),(-1,0),(-1,-1),(-1,0),(-1,-1),
                   (0,-1),(-1,-1),(0,-1),(-1,-1),(0,-1),
                   (1,0),(0,-1),(1,0),(0,-1)]
    grid_perimeter = [start]
    for t in transitions:
        grid_perimeter.append(sumTuples(grid_perimeter[-1], t))

    min_dist = min(map(lambda x: manhattanDist(x[0], x[1]), grid_perimeter))

    grid_points = set(grid_perimeter)

    for b in range(-5, 5):
        for a in range(-5, 5):
            if manhattanDist(a, b) <= min_dist:
                grid_points.add((a,b))
                
    grid_points = sorted(grid_points)
        
    return {'perim': grid_perimeter, 'points': grid_points, 'triangles': getTriangles(grid_points, '')}

def getPlacements(grid, hexiamonds):
    hexi_placements = {hname : [] for hname in hexiamonds}

    def shiftTriangles(tris, point):
        triangles = set()
        for tri in tris:
            shifted_tri = set()
            for t in tri:
                shifted_tri.add(sumTuples(t, point))
            triangles.add(frozenset(shifted_tri))
        return triangles
    
    def oriPlacementsInGrid(ori_path, ori_triangles, hname):
        count = 0
        placements = []
        for point in grid['points']:
            shifted_path = list(map(lambda x: sumTuples(x, point), ori_path))
            if all(map(lambda x: x in grid['points'], shifted_path)): #if the perimeter is in the grid, so are the triangles
                shifted_triangles = shiftTriangles(ori_triangles, point)
                placements.append((shifted_path, shifted_triangles))
                count += 1
        assert count == len(placements)
        return placements
    
    for hname, hexiamond in hexiamonds.items():
        orients = orientations(hname, hexiamond)
        oris_rot, oris_ref = orients['rotations'], orients['mirrors']

        def addOrientations(iterable, add_key):
            for ori in iterable:
                ori_placements = oriPlacementsInGrid(ori[0], ori[1], hname)
                key = hname+add_key
                if key not in hexi_placements:
                    hexi_placements[key] = []
                hexi_placements[hname+add_key] += ori_placements

        if len(oris_ref) > 0:
            addOrientations(oris_ref, '-mirrored')
            
        addOrientations(oris_rot, '')
            
    return hexi_placements

if __name__ == '__main__':
    print("Orientations:")
    for hname, hexiamond in HEXIAMONDS.items():
        oris = orientations(hname, hexiamond)
        rot, mir = oris['rotations'], oris['mirrors']
        print('{:14}: {:2}'.format(hname+' rot', len(rot)))
        print('{:14}: {:2}'.format(hname+' mir', len(mir)))
        print('{:14}: {:2}'.format('total', len(rot) + len(mir)))
        print()

    print("Placements:")
    grid = makeHexagonishGrid()
    hexi_p = getPlacements(grid, HEXIAMONDS)
    sum_p = 0
    for hname, placements in hexi_p.items():
        sum_p += len(placements)
        print('{:20s}: {:10}'.format(hname, len(placements)))
    print()
    print('{:20s}  {:10}'.format('total', sum_p))
        
