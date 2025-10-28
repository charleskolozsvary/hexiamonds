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

# return all triangles which can be formed from the passed set of Eisensten integers
def getTriangles(eisens: set[tuple[int]]):
    
    triangles = set()
    
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
            if e not in eisens:
                return False
        return True
            
    for point in eisens:
        tsAround = trisAround(point)
        for t in tsAround:
            if inEisens(s):
                triangles.add(t)
                
    return triangles

# \sigma: rotate passed Eisenstein integers by 60 degrees counter-clockwise
# (multiply by 1+\omega)
# \sigma(a + b\omega) = (a + b\omega)(1+\omega) = (a-b) + a\omega
def rotate60(eisenInts: set[tuple[int]]):
    return set(map(lambda a, b: (a-b, a), eisenInts))

# \tau: reflect passed Eisenstein integers across the line z(1+\omega), 
# where z \in \mathbb{Z}
# \tau(a + b\omega) = b + a\omega
def reflect(eisenInts: set[tuple[int]]):
    return set(map(lambda a, b: (b, a), eisenInts))

# TODO
def normalize(eisenInts: set[tuple[int]]):
    return 0

if __name__ == '__main__':
    0
