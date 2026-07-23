#!/usr/bin/env python3
"""
Genera un modello 3D del van della miniatura di Apeira.
Ricostruisce in 3D l'icona SVG (carrozzeria nera, striscia arancione,
finestrini bianchi, ruote nere con cerchi chiari) come un vero furgone.

Esporta:  assets/3d/van.glb  e  assets/3d/van.obj (+ .mtl)
Van orientato lungo +X (muso davanti), appoggiato sul piano z=0.
Unita': millimetri  (van ~ 120 mm di lunghezza -> stampabile).
"""
import os
import numpy as np
import trimesh

# ---- palette (dalla miniatura SVG) ----
INK    = [11, 11, 11, 255]     # #0B0B0B carrozzeria / pneumatici
ORANGE = [192, 112, 58, 255]   # #C0703A striscia
WHITE  = [245, 245, 245, 255]  # #fff finestrini / cerchi
GLASS  = [60, 70, 80, 255]     # parabrezza (vetro scuro)

def box(sx, sy, sz, center, color):
    """Box con dimensioni (sx,sy,sz) centrato in `center`, colorato."""
    m = trimesh.creation.box(extents=[sx, sy, sz])
    m.apply_translation(center)
    m.visual.face_colors = color
    return m

def wheel(radius, width, center, color=INK, hub=WHITE):
    """Ruota = cilindro (asse Y) + cerchio chiaro sui due lati."""
    parts = []
    tyre = trimesh.creation.cylinder(radius=radius, height=width, sections=48)
    # cilindro trimesh ha asse Z -> ruoto perche' l'asse ruota sia Y
    tyre.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2, [1, 0, 0]))
    tyre.apply_translation(center)
    tyre.visual.face_colors = color
    parts.append(tyre)
    for side in (-1, 1):
        hubdisc = trimesh.creation.cylinder(radius=radius*0.42, height=width*0.5, sections=32)
        hubdisc.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2, [1, 0, 0]))
        c = list(center); c[1] += side * (width*0.5)
        hubdisc.apply_translation(c)
        hubdisc.visual.face_colors = hub
        parts.append(hubdisc)
    return parts

meshes = []

# ---- proporzioni generali ----
W          = 52.0           # larghezza (Y)
r_w        = 15.0           # raggio ruota
w_w        = 9.0            # larghezza ruota
axle_z     = r_w            # centro ruote a z = raggio (appoggiate a terra)
body_bot   = 8.0            # sotto-scocca
cabin_top  = 54.0           # tetto cabina
hood_top   = 34.0           # tetto cofano (piu' basso)

x_rear     = -58.0          # coda
x_cabin_f  =  22.0          # dove finisce la cabina alta
x_hood_f   =  60.0          # muso

# ---- 1) sotto-scocca / telaio (basso, tutta la lunghezza) ----
chassis_len = x_hood_f - x_rear
meshes.append(box(chassis_len, W*0.92, 10.0,
                  [(x_rear + x_hood_f)/2, 0, body_bot + 5.0], INK))

# ---- 2) corpo cabina/cargo alto (parte posteriore) ----
cabin_len = x_cabin_f - x_rear
cabin_cx  = (x_rear + x_cabin_f) / 2
cabin_cz  = (body_bot + cabin_top) / 2
meshes.append(box(cabin_len, W, cabin_top - body_bot,
                  [cabin_cx, 0, cabin_cz], INK))

# ---- 3) cofano anteriore (piu' basso) ----
hood_len = x_hood_f - x_cabin_f
hood_cx  = (x_cabin_f + x_hood_f) / 2
meshes.append(box(hood_len, W, hood_top - body_bot,
                  [hood_cx, 0, (body_bot + hood_top)/2], INK))

# ---- 4) parabrezza inclinato (cuneo tra tetto cabina e cofano) ----
# prisma triangolare: collega il tetto alto della cabina al tetto del cofano
z0, z1 = hood_top, cabin_top
x0, x1 = x_cabin_f, x_cabin_f + 16.0
hy = W/2 * 0.98
verts = np.array([
    [x0, -hy, z0], [x0, hy, z0],
    [x0, -hy, z1], [x0, hy, z1],
    [x1, -hy, z0], [x1, hy, z0],
])
faces = np.array([
    [0,1,3],[0,3,2],      # retro (verticale, lato cabina)
    [0,4,5],[0,5,1],      # base
    [2,3,5],[2,5,4],      # piano inclinato (parabrezza)
    [0,2,4],              # lato sinistro
    [1,5,3],              # lato destro
])
wedge = trimesh.Trimesh(vertices=verts, faces=faces, process=True)
wedge.visual.face_colors = GLASS
meshes.append(wedge)

# ---- 5) striscia arancione (lungo entrambe le fiancate) ----
stripe_z = 26.0
stripe_h = 5.5
for side in (-1, 1):
    y = side * (W/2 + 0.4)
    meshes.append(box(chassis_len*0.98, 1.2, stripe_h,
                      [(x_rear + x_hood_f)/2, y, stripe_z], ORANGE))

# ---- 6) finestrini cabina (bianchi, sulle fiancate) ----
win_z = (stripe_z + stripe_h/2 + cabin_top) / 2 + 2
win_h = 12.0
for side in (-1, 1):
    y = side * (W/2 + 0.5)
    # finestrino posteriore
    meshes.append(box(20.0, 1.0, win_h, [x_rear + 18.0, y, win_z], WHITE))
    # finestrino anteriore (portiera)
    meshes.append(box(16.0, 1.0, win_h, [x_cabin_f - 11.0, y, win_z], WHITE))

# ---- 7) fanali anteriori ----
for side in (-1, 1):
    y = side * (W/2 * 0.55)
    meshes.append(box(1.2, 6.0, 4.0, [x_hood_f + 0.3, y, body_bot + 8.0], WHITE))

# ---- 8) ruote (4: due assi, due lati) ----
ax_front = x_hood_f - 16.0
ax_rear  = x_rear + 18.0
for ax in (ax_front, ax_rear):
    for side in (-1, 1):
        y = side * (W/2 - w_w/2 + 1.0)
        meshes.extend(wheel(r_w, w_w, [ax, y, axle_z]))

# ---- assembla ----
scene = trimesh.Scene(meshes)

out_dir = os.path.join(os.path.dirname(__file__), "out")
os.makedirs(out_dir, exist_ok=True)
glb_path = os.path.join(out_dir, "van.glb")
scene.export(glb_path)

# OBJ: unisco in un'unica mesh con colori per-vertice
combined = trimesh.util.concatenate(meshes)
obj_path = os.path.join(out_dir, "van.obj")
combined.export(obj_path, include_color=True)

print("Bounds (mm):", np.round(combined.bounds, 1).tolist())
size = combined.bounds[1] - combined.bounds[0]
print("Dimensioni L x W x H (mm):", np.round(size, 1).tolist())
print("Vertici:", len(combined.vertices), " Facce:", len(combined.faces), " Watertight:", combined.is_watertight)
print("Esportato:", glb_path)
print("Esportato:", obj_path)
