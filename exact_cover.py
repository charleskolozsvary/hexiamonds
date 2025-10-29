from polyiamond import sumTuples, getTriangles, orientations, HEXIAMONDS

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

# s is a set of triangles. A triangle is a frozen set of three tuples
# t is a list of sets of triangles
def sInT(s, t):
    for set_of_triangles in t:
        if s == set_of_triangles:
            # print(s)
            # print()
            # print(set_of_triangles)
            # print()
            return True
    return False

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
        # print(hname, count, len(placements))
        assert count == len(placements)
        return placements
    
    for hname, hexiamond in hexiamonds.items():
        orients = orientations(hname, hexiamond)
        for ori in orients:
            ori_placements = oriPlacementsInGrid(ori[0], ori[1], hname)
            hexi_placements[hname] += ori_placements
    return hexi_placements
            

if __name__ == '__main__':
    grid = makeHexagonishGrid()
    hexi_p = getPlacements(grid, HEXIAMONDS)
    sum_p = 0
    for hname, placements in hexi_p.items():
        sum_p += len(placements)
        print('{:10s}: {:10}'.format(hname, len(placements)))
    print(sum_p)

    #TODO: separate non-symmetrical hexiamond placements into up-to-rotation equivalent halves (different up to reflection)
