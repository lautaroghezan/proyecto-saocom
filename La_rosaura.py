"""Pipeline SAOCOM — La Rosaura.

Procesa productos L1D reales a dos escalas: establecimiento y 16 potreros.
Las geometrías maestras están en data/potreros_la_rosaura.geojson. SAOCOM se
integra luego con Sentinel-2 para reconstruir uso histórico (maíz/pastura/otro)
y, en los potreros de maíz, estudiar ambientes para fertilización selectiva.

No se interpreta sigma0 como humedad, biomasa, rendimiento ni dosis directa.
"""
from __future__ import annotations
import argparse, csv, json, re, sys, zipfile
from pathlib import Path
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import numpy as np
import rasterio
from rasterio.mask import mask
from rasterio.warp import transform_geom

PRODUCTO_PILOTO = "EOL1DSARSAO1A14948810"
AOI_WGS84 = {"type":"Polygon","coordinates":[[[-59.346855,-37.204333],[-59.339680,-37.198350],[-59.322638,-37.211288],[-59.329805,-37.217224],[-59.346855,-37.204333]]]}
POTREROS_DEFAULT = Path(__file__).resolve().parent / "data" / "potreros_la_rosaura.geojson"
POL_RE = re.compile(r"-(hh|hv|vh|vv)-m$", re.IGNORECASE)

def cargar_potreros(path: Path) -> list[dict]:
    obj=json.loads(path.read_text(encoding="utf-8"))
    feats=obj.get("features",[])
    if len(feats)!=16: raise ValueError(f"Se esperaban 16 potreros y se encontraron {len(feats)}")
    ids=[f.get("properties",{}).get("potrero_id") for f in feats]
    if len(set(ids))!=16 or any(not x for x in ids): raise ValueError("potrero_id faltante o duplicado")
    return feats

def extraer_zip(z:Path,d:Path)->Path:
    d.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(z,"r") as f:f.extractall(d)
    return d

def preparar_producto(e:Path,w:Path)->Path:
    if e.is_dir():return e
    if e.is_file() and e.suffix.lower()==".zip":return extraer_zip(e,w/e.stem)
    raise ValueError("La entrada debe ser ZIP CONAE o carpeta extraída")

def es_raster_saocom(p:Path)->bool:
    if not p.is_file() or p.suffix.lower()==".xml" or "Data" not in p.parts:return False
    try:
        with rasterio.open(p) as s:return s.driver=="GTiff" and s.count>=1
    except rasterio.errors.RasterioIOError:return False

def listar_rasters(d:Path)->list[Path]:
    x=d/"Data"; return sorted(p for p in x.iterdir() if es_raster_saocom(p)) if x.exists() else []
def polarizacion(p:Path)->str|None:
    m=POL_RE.search(p.name);return m.group(1).upper() if m else None
def leer_sigma0_type(d:Path)->str|None:
    p=d/"Config"/"L1PROCConf.xml"
    if not p.exists():return None
    n=ET.parse(p).getroot().find(".//Sigma0Type")
    return n.text.strip().upper() if n is not None and n.text else None
def validos(a):
    a=np.asarray(a,dtype="float64");return a[np.isfinite(a)]
def estadisticas(a)->dict:
    v=validos(a)
    if not v.size:return {"n":0,"min":None,"media":None,"mediana":None,"p25":None,"p75":None,"max":None}
    return {"n":int(v.size),"min":float(v.min()),"media":float(v.mean()),"mediana":float(np.median(v)),"p25":float(np.percentile(v,25)),"p75":float(np.percentile(v,75)),"max":float(v.max())}
def amplitud_a_db(a):
    a=np.asarray(a,dtype="float64");o=np.full(a.shape,np.nan,dtype="float32");ok=np.isfinite(a)&(a>0);o[ok]=20*np.log10(a[ok]);return o
def guardar_tif(path,data,profile,transform):
    path.parent.mkdir(parents=True,exist_ok=True);p=profile.copy();p.update(driver="GTiff",height=data.shape[-2],width=data.shape[-1],count=1,transform=transform,dtype="float32",nodata=np.nan)
    with rasterio.open(path,"w",**p) as d:d.write(data.astype("float32"),1)
def recortar(src,geom_wgs84):
    g=transform_geom("EPSG:4326",src.crs,geom_wgs84,precision=7);ma,t=mask(src,[g],crop=True,filled=False);return ma[0].filled(np.nan).astype("float32"),t
def procesar_raster(path:Path,salida:Path,sigma:str|None,potreros:list[dict])->dict:
    pol=polarizacion(path) or "NA";res={"polarizacion":pol,"potreros":[]}
    with rasterio.open(path) as src:
        if src.crs is None:raise ValueError("Raster sin CRS")
        amp,t=recortar(src,AOI_WGS84);base=salida/"recortes_aoi"/f"{pol}_La_Rosaura";guardar_tif(base.with_name(base.name+"_amplitud.tif"),amp,src.profile,t)
        res["establecimiento"]={"shape":list(amp.shape),"amplitud":estadisticas(amp)}
        if sigma=="AMPLITUDE":
            db=amplitud_a_db(amp);guardar_tif(base.with_name(base.name+"_sigma0_db.tif"),db,src.profile,t);res["establecimiento"]["sigma0_db"]=estadisticas(db)
        for f in potreros:
            pid=f["properties"]["potrero_id"];pa,pt=recortar(src,f["geometry"]);pb=salida/"recortes_potreros"/pid/f"{pol}_{pid}"
            guardar_tif(pb.with_name(pb.name+"_amplitud.tif"),pa,src.profile,pt);r={"potrero_id":pid,"shape":list(pa.shape),"amplitud":estadisticas(pa)}
            if sigma=="AMPLITUDE":
                pdb=amplitud_a_db(pa);guardar_tif(pb.with_name(pb.name+"_sigma0_db.tif"),pdb,src.profile,pt);r["sigma0_db"]=estadisticas(pdb)
            res["potreros"].append(r)
    return res

def guardar_tabla(resultados:list[dict],path:Path,product_id:str):
    rows=[]
    for r in resultados:
        for p in r["potreros"]:
            s=p.get("sigma0_db",{});rows.append({"product_id":product_id,"potrero_id":p["potrero_id"],"polarizacion":r["polarizacion"],**{f"sigma0_db_{k}":s.get(k) for k in ["n","media","mediana","p25","p75"]}})
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
def ejecutar(entrada:Path,salida:Path,product_id:str,potreros_path:Path)->int:
    salida.mkdir(parents=True,exist_ok=True);potreros=cargar_potreros(potreros_path);d=preparar_producto(entrada,salida/"extraidos");rasters=listar_rasters(d);sigma=leer_sigma0_type(d)
    print(f"Producto {product_id} | rasters={len(rasters)} | potreros={len(potreros)} | Sigma0Type={sigma}")
    if not rasters:return 2
    resultados=[];errores=[]
    for p in rasters:
        try:resultados.append(procesar_raster(p,salida,sigma,potreros));print(f"✔ {polarizacion(p)}: establecimiento + 16 potreros")
        except Exception as e:errores.append(f"{p.name}: {type(e).__name__}: {e}")
    inv={"producto":product_id,"aoi_wgs84":AOI_WGS84,"potreros_fuente":str(potreros_path),"n_potreros":len(potreros),"sigma0_type":sigma,"resultados":resultados,"errores":errores,"advertencias":["SAOCOM no identifica por sí solo maíz/pastura.","La clasificación histórica se basará en series temporales multisensor SAOCOM + Sentinel-2.","No inferir dosis de fertilizante sin validación agronómica."]}
    (salida/"inspeccion_saocom.json").write_text(json.dumps(inv,indent=2,ensure_ascii=False),encoding="utf-8")
    if resultados:guardar_tabla(resultados,salida/"tablas"/"resumen_saocom_por_potrero.csv",product_id)
    return 0 if resultados else 3
def parser():
    p=argparse.ArgumentParser();p.add_argument("entrada",type=Path);p.add_argument("--salida",type=Path,default=Path("data")/"procesado"/PRODUCTO_PILOTO);p.add_argument("--product-id",default=PRODUCTO_PILOTO);p.add_argument("--potreros",type=Path,default=POTREROS_DEFAULT);return p
def main():
    a=parser().parse_args()
    try:return ejecutar(a.entrada,a.salida,a.product_id,a.potreros)
    except Exception as e:print(f"❌ {type(e).__name__}: {e}",file=sys.stderr);return 1
if __name__=="__main__":raise SystemExit(main())
