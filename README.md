# Spatial Diffusion

This repository contains the codes of the simulation for the article

Lengyel, B., Bokányi, E., Di Clemente, R. et al. The role of geography in the complex diffusion of innovations. Sci Rep 10, 15065 (2020). https://doi.org/10.1038/s41598-020-72137-w

https://www.nature.com/articles/s41598-020-72137-w

Comments and questions are welcome either as an issue or as an e-mail to `eszter.bokanyi` (at) `uni-corvinus.hu`.

## Content

Codes for the SI simulation of the spatial diffusion project.

Example ABM run with visualization:
```
echo '{"num_runs":4,"q":0.125}' | python ./SI.py  | ./visualizer.py
```

First JSON is the config, middle script contains the simulation class, visualizer.py puts the fraction of infected nodes as a function of time on a plot with the original data.
