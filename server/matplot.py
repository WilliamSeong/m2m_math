import matplotlib.pyplot as plt

fig, ax = plt.subplots(1, figsize=(9,3))
fig.subplots_adjust(left=.05, right=.3, top=.8, bottom=.2)

# Set background color to white
fig.patch.set_facecolor('white')
ax.set_facecolor('white')

# Create a circle patch
circle = plt.Circle((4, 5), 3, fill=False)

# Create radius line
ax.plot([4, 7], [5, 5], 'k-') # line from (.4, .5) to (.7, .5)
ax.plot(4, 5, 'ko', markersize=4)  # Center dot

# Create radius label
ax.text(5.5, 5.2, f"{3} ft", ha='center')

# Add the circle to the axes
ax.add_patch(circle)

# Set the limits of the plot
# ax.set_xlim(0, 1)
# ax.set_ylim(0, 1)

# Ensure the aspect ratio is equal so that the circle is not distorted
ax.set_aspect('equal', adjustable='box')

# ax.text(1, 9, f"2. What is the area of the circle? Use 3.14 for i and round to the nearest whole number.", ha='left')

fig.text(.05, .85, "2. What is the area of the circle? Use 3.14 for π and round to the nearest whole number.", ha='left', fontsize=12)

fig.text(0.12, 0.1, "[A] 28 ft²", ha='center', fontsize=12)
fig.text(0.32, 0.1, "[B] 9 ft²", ha='center', fontsize=12)
fig.text(0.52, 0.1, "[C] 113 ft²", ha='center', fontsize=12)
fig.text(0.72, 0.1, "[D] 30 ft²", ha='center', fontsize=12)

# Remove axes ticks and labels for a cleaner look, if desired
ax.set_xticks([])
ax.set_yticks([])

for spine in ax.spines.values():
    spine.set_visible(False)


# Show the plot
# plt.show()

# Save the plot
fig.savefig('plotcircles.png')
