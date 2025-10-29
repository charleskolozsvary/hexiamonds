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
    grid = makeHexagonishGrid()
    hexi_p = getPlacements(grid, HEXIAMONDS)
    sum_p = 0
    for hname, placements in hexi_p.items():
        sum_p += len(placements)
        print('{:20s}: {:10}'.format(hname, len(placements)))
    print()
    print('{:20s}  {:10}'.format('total', sum_p))
