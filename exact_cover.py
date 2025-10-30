'''template from Hooks11 this will be what generates the exact covers in better alignment with the file's name'''

import polyiamond
import pickle

def makeProblemMatrix(grid, poly_placements):
    rows = {}
    idx = 0
    keys = set()
    
    for polyname, placements in poly_placements.items():
        keys.add(polyname)
        for placement in placements:
            placement = placement[1]
            row = {polyname: 1}
            for base_shape in placement:
                keys.add(base_shape)
                row[base_shape] = 1
            rows[idx] = row
            idx += 1

    assert len(grid) == (len(keys)-len(poly_placements))
            
    return rows, keys

def getCovers(rows, primaryKeys, maxSolutions = 100):
    pkCounts = {}
    for row in rows.values():
        for key in row:
            if key not in primaryKeys: 
                continue 
            if key in pkCounts:
                pkCounts[key] += 1
            else:
                pkCounts[key] = 1
    
    def chooseKey(counts): #choose key with minimum rows
        return {v:k for k,v in counts.items()}[min(counts.values())]
    
    solutions = [] #list of lists of row indices
            
    def search(curr_sol, curr_rows, curr_kcounts, curr_filled_baseshapes):
        if len(curr_kcounts) == 0:
            print('SOLUTION FOUND')
            solutions.append(curr_sol)
            return

        if len(solutions) >= maxSolutions:
            raise Exception ('Done finding solutions')
        
        coverKey = chooseKey(curr_kcounts)
        
        candidateRows = [] 
        for cridx, crow in curr_rows.items():
            if coverKey in crow:
                candidateRows.append(cridx)

        if len(candidateRows) == 0:
            return #return unsuccessfully
        
        for chosenRowIdx in candidateRows:
            chRow = curr_rows[chosenRowIdx]
            
            next_sol = curr_sol.copy()
            next_rows = curr_rows.copy()
            next_kcounts = curr_kcounts.copy()
            next_filled_baseshapes = curr_filled_baseshapes.copy()
            
            next_sol.append(chosenRowIdx)            
            for cridx, crow in curr_rows.items():
                willDelete = False
                for key in crow:
                    if key in chRow:
                        willDelete = True
                        break
                if willDelete:
                    for key in crow:
                        if key in primaryKeys:
                            next_kcounts[key] -= 1
                    del next_rows[cridx]

            chpoly = None
            for key in chRow:
                if type(key) is str:
                    chpoly = key
                    break
            assert chpoly is not None, "somehow chpoly is still None"

            ## remove keys that belong to chosen row
            for key in chRow:
                if type(key) is not str:
                    next_filled_baseshapes[key] = chpoly
                if key not in primaryKeys:
                    continue
                assert next_kcounts[key] == 0
                del next_kcounts[key]
                    
            search(next_sol, next_rows, next_kcounts, next_filled_baseshapes)

    try:
        search([], rows, pkCounts, {})
    except Exception as message:
        return translateCovers(solutions, rows)

# The incoming covers are lists of row indices from the problem matrix.
# The outgoing covers are lists of dictionaries with polyform names
# as keys and occupied base shapes as values
def translateCovers(covers_in, matrix):
    covers_out = []
    for cover_in in covers_in:
        cover_out = {}
        rows = [matrix[ridx] for ridx in cover_in]
        for row in rows:
            polyname = None
            base_shapes = []
            for key in row:
                if type(key) is not str:
                    base_shapes.append(key)
                else:
                    assert polyname is None, "..."
                    polyname = key
            cover_out[polyname] = base_shapes
        covers_out.append(cover_out)
    return covers_out

def getPathsForPlacementsInCovers(covers, poly_placements):

    new_covers = []
    
    def getPath(polyname, triangles):
        triangles = frozenset(triangles)
        placements = poly_placements[polyname]
        placement_tris = list(map(lambda x: x[1], placements))
        assert triangles in placement_tris, "hmmm"
        for path, tris in placements:
            if tris == triangles:
                return path
        assert False, "shouldn't happen"
        
    for cover in covers:
        new_cover = {polyname : [] for polyname in cover}
        for polyname, triangles in cover.items():
            path = getPath(polyname, triangles)
            new_cover[polyname] = (path, triangles)
        new_covers.append(new_cover)
    return new_covers
            

if __name__ == '__main__':
    grid = polyiamond.makeHexagonishGrid()
    hexi_p = polyiamond.getPlacements(grid, polyiamond.HEXIAMONDS)
    matrix, primaryKeys = makeProblemMatrix(grid['triangles'], hexi_p)

    print('len(hexi_p):', len(hexi_p))
    print("len(grid['triangles']):", len(grid['triangles']))
    print('len(matrix):', len(matrix))
    print('len(primaryKeys):', len(primaryKeys))
    print('len(matrix[0]):', len(matrix[0]))

    covers = getCovers(matrix, primaryKeys)

    new_covers = getPathsForPlacementsInCovers(covers, hexi_p)

    with open('a-few-covers.pkl', 'wb') as f:
        pickle.dump(new_covers, f)
