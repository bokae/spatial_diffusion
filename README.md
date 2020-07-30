# spatial_diffusion
Codes for the SI simulation of the spatial diffusion project.

Example ABM run with visualization:
```
echo '{"num_runs":4,"q":0.125}' | python ./SI.py  | ./visualizer.py
```

First JSON is the config, middle script contains the simulation class, visualizer.py puts the fraction of infected nodes as a function of time on a plot with the original data.
