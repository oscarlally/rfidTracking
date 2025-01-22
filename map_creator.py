import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('TkAgg')

# Load the image
img = mpimg.imread('./Data/Map.png')  # Replace with the actual path

# Display the image
plt.imshow(img)
plt.axis('off')  # Turn off axis labels and ticks (optional)
plt.show()