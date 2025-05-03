import time
import TestFirebase as TF

# Strart the timer
start_time = time.perf_counter()

# Update data of first node
TF.updateData("181020","Speed","170")

#wait till the seconed node change speed
while True:
	speed = TF.readData("181030","Speed")
	if speed == 50:
		break

# Get the timer value
end_time = time.perf_counter()

# Calculate the time difference in milliseconds
time_difference = (end_time - start_time) * 1000/2

# Print the result
print("Time difference:", time_difference, "milliseconds")
