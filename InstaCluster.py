from sklearn.cluster import KMeans
import numpy as np
import csv
from matplotlib import pyplot as plt

def convert_csv(filename):

	with open(filename,newline='') as fv:
		reader=csv.reader(fv)
		data=[row for row in reader]

	for row in data:
		row.pop(0)
		for i in range(len(row)):
			row[i]=int(row[i])
		

	return np.array(data).astype('float64')

def display_clusters(model,samples):

	labels=model.predict(samples)
	print(labels)

	# Assign the columns of new_points: xs and ys
	xs = samples[:,0]
	ys = samples[:,1]

	# Make a scatter plot of xs and ys, using labels to define the colors
	plt.scatter(xs, ys, c=labels, alpha=0.5)

	# Assign the cluster centers: centroids
	centroids = model.cluster_centers_

	# Assign the columns of centroids: centroids_x, centroids_y
	centroids_x = centroids[:,0]
	centroids_y = centroids[:,1]

	# Make a scatter plot of centroids_x and centroids_y
	plt.scatter(centroids_x, centroids_y, marker='D', s=50)
	plt.show()



def evaluate_model(samples):
	num_clusters = range(1, 6)
	inertias = []

	for k in num_clusters:
    	# Create a KMeans instance with k clusters: model

		model = KMeans(n_clusters=k)
    
    	# Fit model to samples
		model.fit(samples)
    
    	# Append the inertia to the list of inertias
		inertias.append(model.inertia_)
    
	# Plot ks vs inertias
	plt.plot(num_clusters, inertias, '-o')
	plt.xlabel('number of clusters, k')
	plt.ylabel('inertia')
	plt.xticks(num_clusters)
	plt.show()

samples=convert_csv('InstaData.csv')
model=KMeans(3)
model.fit(samples[0:20])
display_clusters(model,samples[0:20])

