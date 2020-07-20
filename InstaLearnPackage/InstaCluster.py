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

	xs = samples[:,0]
	ys = samples[:,1]

	plt.scatter(xs, ys, c=labels, alpha=0.5)

	centroids = model.cluster_centers_

	centroids_x = centroids[:,0]
	centroids_y = centroids[:,1]


	plt.scatter(centroids_x, centroids_y, marker='D', s=50)
	plt.show()



def evaluate_model(samples):
	num_clusters = range(1, 6)
	inertias = []

	for k in num_clusters:


		model = KMeans(n_clusters=k)
    

		model.fit(samples)
    
    	
		inertias.append(model.inertia_)
    

	plt.plot(num_clusters, inertias, '-o')
	plt.xlabel('number of clusters, k')
	plt.ylabel('inertia')
	plt.xticks(num_clusters)
	plt.show()


