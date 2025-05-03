import time
import TestFirebase as TF

#wait till the first node change speed
while True:
	speed = TF.readData("181020","Speed")
	if speed == 170:
		break

# Update data of seconed node
TF.updateData("181030","Speed","50")