#! /usr/bin/env python

# Python Standard Library Modules
import csv
from shapely.geometry import Polygon
import argparse
import matplotlib.pyplot as plt
import shapefile

# FUNCTIONALITY:
#          This function iterates thru all the shapes in the stateline shapefiles and
#          rounds its coord values to have only 5 digits beyond the decimal point (ex: 12.3456789 = 12.34568).
#          Then appends these to a list to output.
# OUTPUT:  statepoints - list of coords representing state vertices
def getStatePoints():
    # reads shapefile for states
    stateshapes = shapefile.Reader('state_shapes/cb_2018_us_state_500k.shp')
    # load array with all state border vertices
    statepoints = []
    for shp in stateshapes.shapeRecords():
        for pt in shp.shape.points:
            statepoints.append((round(pt[0], 5), round(pt[1], 5)))
    return statepoints

# FUNCTIONALITY:
#          This function iterates thru all the shapes in the river shapefiles and
#          rounds its coord values to have only 5 digits beyond the decimal point (ex: 12.3456789 = 12.34568).
#          Then appends these to a list to output.
# OUTPUT:  riverpoints - list of coords representing state vertices
def getRiverPoints():
    # reads shapefile for rivers
    rivershapes = shapefile.Reader('rivers/USA_Rivers_and_Streams.shp')
    # load array with all state border vertices
    riverpoints = []
    for shp in rivershapes.shapeRecords():
        # MIGHT NOT NEED TO ROUND
        for pt in shp.shape.points:
            riverpoints.append((round(pt[0], 5), round(pt[1], 5)))
    return riverpoints

#  createCoordMatrix without the rivers
def createCoordMatrix2(statepoints):
    # I know this is very space inefficient and there is probably a better ways to do this with a hashmap or something
    # but the constant time access did speed up the process. So here we initialize the enormous 2d list
    rows, cols = (360*10**5,180*10**5)
    pointmatrix = [[0] * cols] * rows

    #iterate thru all statepoints, set all coords where a state vertice exists to 1
    for pt in statepoints:
        # shift over and multiply by 10^4 to offset rounding
        lat = int((pt[0] + 180) * 10**5)
        long = int(pt[1] * 10**5)
        #print(pt)
        pointmatrix[lat][long] = 1
    return pointmatrix

# INPUTS:  statepoints - a list of points representing vertices of state borders
#          riverpoints - a list of points representing vertices along major US rivers (very long)
# FUNCTIONALITY:
#          For each point in riverpoints and statepoints, this function adds 180 to the latitude value so that
#          negative values cannot occur. Then it multiplies every value by 10^5 so that we have integer values for each
#          coordinate so that they can be used to index 2d list/array. Then the function iterates thru all river
#          and state points to set indexes to 1
#
# OUTPUTS: pointmatrix - a 2d list of boolean values where row refers to latitude, col refers to longitude
#                        if pointmatrix[row][col] == 1, coordinate is a part of a state line or river
#                        if pointmatrix[row][col] == 0, coordinate is not part of a state line or river
def createCoordMatrix(statepoints, riverpoints):
    # I know this is very space inefficient and there is probably a better ways to do this with a hashmap or something
    # but the constant time access did speed up the process. So here we initialize the enormous 2d list
    rows, cols = (360*10**5,180*10**5)
    pointmatrix = [[0] * cols] * rows

    #iterate thru all statepoints, set all coords where a state vertice exists to 1
    for pt in statepoints:
        # shift over and multiply by 10^4 to offset rounding
        lat = int((pt[0] + 180) * 10**5)
        long = int(pt[1] * 10**5)
        #print(pt)
        pointmatrix[lat][long] = 1
    #iterate thru all riverpoints, set all coords where a river vertice exists to 1 (very slow/long list)
    for pt in riverpoints:
        # shift over and multiply by 10^5 to offset rounding
        lat = int((pt[0] + 180) * 10**5)
        long = int(pt[1] * 10**5)
        pointmatrix[lat][long] = 1
    #retunr 2d list
    return pointmatrix



# INPUTS:  shape - the district being looked at
#          pointmatrix - a 2d list of points representing vertices which coords are part of state or river border
# FUNCTIONALITY:
#          This function first calculates the number of points in the districts shape and then subtracts any
#          points that can be explained by a river or a state line
# OUTPUTS: totalpts - total number of vertices unaccounted for by rivers/state borders
def countVertices(shape, pointmatrix):
    # get total points in shape
    totalpts = len(shape.points)
    #print(totalpts)
    #check if vertice is part of the river/state borders
    for point in shape.points:
        lat = int((round(point[0], 5) + 180) * 10**5)
        long = int(round(point[1], 5) * 10**5)
        if pointmatrix[lat][long]:
            totalpts -= 1
    #print(totalpts)
    return totalpts

# INPUTS:  pointmatrix - a 2d list of boolean values where row refers to latitude, col refers to longitude
#                        if pointmatrix[row][col] == 1, coordinate is a part of a state line or river
#                        if pointmatrix[row][col] == 0, coordinate is not part of a state line or river
# FUNCTIONALITY:
#          For each district shape. A grayscale value is calculated (VERY CRUDELY) and is used to fill each shape
#
def drawDistricts():
    # open US districts shapefile
    file = "data/tl_2018_us_cd116.shp"
    districts = shapefile.Reader(file)
    # maxVertices = max(countVertices(rec.shape, pointmatrix) for rec in districts.shapeRecords())

    #iterate thru all districts
    for rec in districts.shapeRecords():
        # calculate CRUDE grayscale value (0 = black, 1 = white). Divide by ugly crud number I used to achieve a grayscale

        # vertice method commented out
            # black is more gerrymandered
            # grayscale = 1 - countVertices(rec.shape, pointmatrix) / maxVertices #10000
            # grayscale = min(grayscale, 1.0)
            # grayscale = max(grayscale, 0.0)
            #color = str(grayscale)

        #area/perim method
        shape = Polygon(rec.shape.points)
        shp_area = shape.area
        shp_perim = shape.length

        ratio = shp_perim / shp_area
        greyscale = ratio / 20
        #round down
        if greyscale > 1:
            greyscale = 1.0
        #invert colors
        greyscale = 1 - greyscale

        # get points to plot
        x = [i[0] for i in rec.shape.points[:]]
        y = [i[1] for i in rec.shape.points[:]]

        # draw with whiteborders
        plt.plot(x, y, 'w', linewidth=0.2)

        #fill district with grayscale value
        color = str(greyscale)
        plt.fill(x,y, color)

# I dont use this function. It is meant to draw the state lines and it sorta works but some state come out wonky
def drawStates():
    stateshapes = shapefile.Reader('state_shapes/cb_2018_us_state_500k.shp')
    # load array with all state border vertices
    statepoints = []
    for rec in stateshapes.shapeRecords():
        listx = []
        listy = []
        for x, y in rec.shape.points:
            listx.append(x)
            listy.append(y)
        plt.plot(listx, listy)

# INPUT: pointmatrix - a 2d list of boolean values where row refers to latitude, col refers to longitude
#                        if pointmatrix[row][col] == 1, coordinate is a part of a state line or river
#                        if pointmatrix[row][col] == 0, coordinate is not part of a state line or river
# FUNCTIONALITY:
#               Draw the map using matplotlib
#
# Previously was "drawMap(pointmatrix, args):"
def drawMap(args):
    #output with matplotlib
        dimensions = getDimensions(args.region)
        # dimensions of popup plot window
        plt.figure(figsize=[12, 7])
        # set background color to gray
        plt.gca().set_facecolor("0.5")
        # set scale to mutiples of 10?
        plt.plot(range(0, 10))
        # set coord ranges
        xmin, xmax = dimensions[0]
        ymin, ymax = dimensions[1]

        #this value will eventually be used to name pdf file
        plt.title(args.output)
        # add and subtract 1 to each direction to give a little buffer around the ranges we are looking at
        plt.xlim(round(xmin - 1), round(xmax + 1))
        plt.ylim(round(ymin - 1), round(ymax + 1))
        drawDistricts()
        plt.show()

# FUNCTIONALITY: I really crudely made the project prompt the user to enter state name, abreviation, or empty string to zoom
#                the graph on different areas if necessary
# OUTPUT:        A Pair of Pairs in format ((xmin, xmax),(ymin,ymax))
# FUNCTIONALITY: I made the project take cmd line args to enter state name, abreviation, or empty string to zoom
#                the graph on different areas if necessary
# OUTPUT:        A Pair of Pairs in format ((xmin, xmax),(ymin,ymax))
def getDimensions(region):
    # if empty string input, show entire continental US
    if region is None:
        #defaults for continental US
        return ((-130, -50), (24, 50))
    # otherwise see if the input refers to a state in csv file. If so, use corresponding dimensions
    else:
        with open('state_shapes/statebounds.csv', mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            #iterate thru csv file to search for match
            for row in csv_reader:
                if row["STUSPS"].lower() == region or row["NAME"].lower() == region:
                    return ((float(row["xmin"]),float(row["xmax"])),(float(row["ymin"]),float(row["ymax"])))
            # if invalid input, reprompt
    raise ValueError("This state name or abbreviation does not exist")


# main function
def main():
    # argument parsing
    parser = argparse.ArgumentParser(
        description="Generate pdf map displaying different levels of gerrymandering in US congressional districts")
    region_string = "(Optional) The region to be represented in the map. Can be state name or abbreviation"
    parser.add_argument("-region", help=region_string, dest="region", type=str, required=False)
    output_string = "(Optional) The name of the map pdf file to be created. Default is MyMap.pdf"
    parser.add_argument("-mapname", help=output_string, dest="output", type=str, default="MyMap.pdf")
    parser.set_defaults()
    args = parser.parse_args()
    # logic
    #state_points = getStatePoints()
    #river_points = getRiverPoints()
    #point_matrix = createCoordMatrix2(state_points)
    drawMap(args)


# necessary for some reason lol
if __name__ == "__main__":
    # execute only if run as a script
    main()


