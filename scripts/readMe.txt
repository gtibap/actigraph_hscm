visual_mat_act.py
figures: day02_vm.png, day02_incl_thigh.png, day02_incl_chest.png

pressure_selected_pixel.py
figures: day02_graph_p00.png, day02_graph_p01.png, day02_pressure_p00.png, day02_pressure_p01.png 

groups_activity_7.py
It plots actigraphy data (e.i. Vector Magnitude and inclinometers), a stems plot that shows spending times of motor activity and inactivity (two scales, two colors, in the same plot). Interactive mouse selection on the stems plot to generate the corresponding plot of the actigraphy data.

groups_activity_statistics.py (last updated: April 8, 2023)
It calculates total number of motor-activity units; to be part of a motor-activity unit each Vector Magnitude (VM) sample has to be greater than 3 counts; additionally, VM samples included in the same motor-activity unit have a time difference less than 10s to the nearest included sample.
