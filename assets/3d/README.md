# Van 3D — modello della miniatura del tour Apeira

Modello 3D del furgoncino che percorre la mappa interattiva in `apeira.html`,
ricostruito dall'icona SVG originale (carrozzeria nera `#0B0B0B`, striscia
arancione `#C0703A`, finestrini bianchi, ruote).

## File

| File | Uso |
|------|-----|
| `van.glb` | Formato consigliato: web/AR, `<model-viewer>`, Blender, ecc. (colori inclusi) |
| `van.obj` | Interscambio universale, con colori per-vertice |
| `van-preview.png` | Anteprima renderizzata |
| `build_van.py` | Script parametrico che genera i modelli |

## Dettagli

- Orientamento: muso lungo **+X**, appoggiato sul piano **z = 0**.
- Unità: **millimetri** — dimensioni ~ **119 × 58 × 54 mm** (pronto per stampa 3D).
- Mesh chiusa (watertight), adatta allo slicing.

## Rigenerare / modificare

```bash
pip install numpy trimesh scipy
python assets/3d/build_van.py   # scrive in assets/3d/out/
```

Le proporzioni (lunghezza, altezza cabina, ruote, striscia…) sono parametri
in cima allo script: modificali e rilancia.
