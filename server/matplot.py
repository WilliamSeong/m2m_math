import matplotlib.pyplot as plt

fig, ax = plt.subplots(1, figsize=(9,3))
fig.subplots_adjust(left=0, right=.3, top=1, bottom=0)

# Set background color to white
fig.patch.set_facecolor('white')
ax.set_facecolor('white')

# Create a circle patch
circle = plt.Circle((0.4, 0.5), .3, fill=False)

ax.plot([.4, .7], [.5, 0.5], 'k-')
ax.plot(0.4, 0.5, 'ko', markersize=4)  # Center dot

# Add the circle to the axes
ax.add_patch(circle)

# Set the limits of the plot
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)

# Ensure the aspect ratio is equal so that the circle is not distorted
ax.set_aspect('equal', adjustable='box')

# Remove axes ticks and labels for a cleaner look, if desired
ax.set_xticks([])
ax.set_yticks([])

for spine in ax.spines.values():
    spine.set_visible(False)


# Show the plot
# plt.show()

# Save the plot
fig.savefig('plotcircles.png')
