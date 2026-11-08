# Pathing nodes

Retail FFXI mob pathing nodes for every zone, on one map: https://frankie-hz.github.io/nodes/

- **Retail (roam data):** node centers, arrival radii and links extracted from retail mob roam traces.
- **No generated nodes:** nodes generated where no roam data reached were dropped, as trust probes in Valkurm landed near them no more often than chance. Zones with no roam data are left out until they are probed.
- **Suspected duplicates** (dashed orange): retail nodes inside a trust-confirmed neighbour's circle where no trust ever landed.
- **Chase model** (`chase/`): every captured retail chase leg against the current chase model, worst first, with the retail fly, the model fly and the player's path over the nodes.
- **Live trust probing:** zones being probed in game show each trust probe, the nodes it confirmed and new nodes found, updated every few minutes.

`zones/<zone>.json` holds `nodes` as `[x, z, y, radius, source]` (source 0 = retail), the
original node `ids`, and `links` as pairs of node indexes. `tools/build_zones.py` builds them from the LSB `nodes.yaml` export.

Built with the pathing node pipeline in [xi-visualizer](https://github.com/Frankie-hz/xi-visualizer) (fork of sruon's xi-visualizer).
