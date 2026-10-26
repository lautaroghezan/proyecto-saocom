# 🎓 Proyecto de Machine Learning — La Rosaura

## Pregunta ampliada

¿Es posible integrar **SAOCOM + Sentinel-2 + topografía + datos agronómicos** para (1) reconstruir el uso histórico de los 16 potreros y (2) identificar ambientes de manejo dentro de los potreros de maíz útiles para fertilización selectiva?

## Diseño en dos modelos

### Modelo 1 — reconstrucción histórica de uso

Unidad: `potrero × campaña`. Clases: `maíz`, `pastura`, `otro`, `incierto`. Se utilizará la **firma temporal/fenológica**, no una regla simple de biomasa. Sentinel-2 aporta información óptica e índices de vegetación; SAOCOM aporta series SAR L-band HH/HV/VH/VV y continuidad ante nubosidad. La salida debe incluir confianza/probabilidad y permitir `incierto`.

### Modelo 2 — ambientes para fertilización

Se ejecuta sólo sobre potreros/campañas identificados como maíz con evidencia suficiente. Unidad: celda/píxel espacial dentro del potrero observada en múltiples fechas. Integra SAR multitemporal, óptico, DEM/topografía, suelo y manejo. Primero clustering; supervisado sólo si existe target agronómico observado confiable.

## Geometría

Los 16 potreros aportados por el productor están versionados como `data/potreros_la_rosaura.geojson` en el repositorio geoespacial, con IDs `L01`–`L16`. Son la unidad espacial estable para unir sensores, campañas y observaciones.

## SAOCOM validado

Producto piloto `EOL1DSARSAO1A14948810`, 07/09/2024: L1D TOPSAR/TNB, QP HH/HV/VH/VV, FLOAT32, EPSG:32721, ~43,55 × 42,33 m y `Sigma0Type=AMPLITUDE`. Para amplitud positiva: `sigma0_dB = 20*log10(amplitud)`.

## Variables candidatas

**SAOCOM:** sigma0 HH/HV/VH/VV, diferencias justificadas, estadísticos temporales.  
**Sentinel-2:** reflectancias e índices ópticos/fenológicos, calidad/nubes, máximos, mínimos, amplitud, pendientes y fechas características.  
**Topografía:** elevación, pendiente, orientación/posición relativa.  
**Manejo/campo:** suelo, siembra, híbrido, densidad, fertilización, clima, observaciones y producción cuando existan.  
**Historia inferida:** cultivo campaña previa, años desde último maíz y frecuencia de maíz, siempre conservando incertidumbre.

## Validación

No usar `train_test_split` aleatorio de píxeles como única evidencia. Priorizar separación por potrero/bloque espacial y generalización temporal entre campañas. La reconstrucción histórica necesita campañas/lotes de referencia cuando podamos verificarlos. Los clusters no se etiquetarán alto/medio/bajo potencial sin validación agronómica. SHAP describe el modelo, no causalidad.

## Resultado esperado

```text
16 potreros
   ↓
SAOCOM + Sentinel-2
   ↓
series temporales por potrero
   ↓
maíz / pastura / otro / incierto + confianza
   ↓
selección de potreros/campañas de maíz
   ↓
SAR + óptico + DEM + suelo + manejo
   ↓
ambientes de manejo
   ↓
validación agronómica
   ↓
decisión posterior de fertilización
```

## Estado

- [x] AOI confirmado.
- [x] 16 potreros incorporados (`L01`–`L16`).
- [x] Primer SAOCOM real inspeccionado y radiometría verificada.
- [x] Pipeline adaptado a recorte por potrero.
- [x] Diseño de constelación virtual SAOCOM–Sentinel-2 definido.
- [ ] Ejecutar producto piloto sobre L01–L16.
- [ ] Construir serie Sentinel-2 histórica.
- [ ] Procesar serie SAOCOM multitemporal.
- [ ] Reconstruir cultivo por potrero/campaña con confianza.
- [ ] Incorporar DEM, suelo y manejo.
- [ ] Construir dataset analítico.
- [ ] Entrenar/validar Modelo 1 y ambientes del Modelo 2.

No se usarán rendimientos simulados ni se inferirán dosis directamente desde radar.
