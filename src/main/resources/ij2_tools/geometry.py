import math


def in_circle(point, center, radius):
	return ((point[0] - center[0])**2 + (point[1] - center[1])**2) < radius**2
	

def get_circle_points(x_center, y_center, radius, n=20):
		points = []
		for i in range(0, n+1):
			x = math.cos(2*math.pi/n*i) * radius + x_center
			y =  math.sin(2*math.pi/n*i) * radius + y_center
			points.append([x, y])
		return points
	
	
def get_two_circles_points(x1, y1, x2, y2, radius, n=20):
	xcen, ycen = (x1 + x2) / 2, (y1 + y2) / 2
	
	points1 = get_circle_points(x1, y1, radius, n=n)
	points2 = get_circle_points(x2, y2, radius, n=n)
	
	points1_in_circle_index = [i for i, point in enumerate(points1) if in_circle(point, [x2, y2], radius)]
	points2_in_circle_index = [i for i, point in enumerate(points2) if in_circle(point, [x1, y1], radius)]
	
	points1 = points1[points1_in_circle_index[-1] + 1:] + points1[:points1_in_circle_index[0]]
	points2 = points2[points2_in_circle_index[-1] + 1:] + points2[:points2_in_circle_index[0]]

	return points1 + points2