import {
  ArrowUpRight,
  CircleAlert,
  Database,
  Flag,
  Globe2,
  LockKeyhole,
  Scale,
  ShieldCheck,
} from 'lucide-react';

const dimensions = [
  { name: 'Educación', detail: 'Sensibilidad de recurso v0.9', tone: 'amber', complete: 35 },
  { name: 'Salud', detail: 'Sensibilidad de recurso v0.8', tone: 'teal', complete: 34 },
  { name: 'Administración', detail: 'Sensibilidad v1.1', tone: 'blue', complete: 34 },
  { name: 'Seguridad y justicia', detail: 'Tres roles, sensibilidad multifuente v3.2', tone: 'violet', complete: 30 },
];

const milestones = [
  ['Paquete de revisión', 'Listo', 'Veintitrés artefactos trazables preparados para revisión metodológica independiente.'],
  ['Cortes por dimensión', 'Listo', 'Las cuatro dimensiones ya superan 30 países en sus propios contratos experimentales.'],
  ['Núcleo de resultados comparables', 'Listo', '33 países tienen los cuatro resultados validados. No incluye recursos, acceso ni equidad; no es IEE ni ranking.'],
  ['Ruta de completitud de cohorte', 'En curso', 'La ampliación requiere contratos comunes por dimensión, no excepciones nacionales. Salud v2 será la primera prueba de equivalencia.'],
  ['Cohorte común experimental', 'Listo', 'El corte vigente de 24 países quedó cerrado y es reproducible. El mínimo de 30 aún no se alcanza.'],
  ['Recuperación verificable v0.9', 'Listo', '5 de 5 hitos de evaluación resueltos. Las rutas que no superaron comparabilidad o acceso se cerraron sin sustituir datos.'],
  ['Ranking oficial IEE v1', 'Bloqueado', 'Solo tras revisión independiente y publicación del protocolo.'],
];

const exploratoryRanking = [
  [1, 'Japón', '95,31', '1–1'], [2, 'Corea del Sur', '92,19', '2–2'], [3, 'Suiza', '72,66', '3–12'], [4, 'Países Bajos', '71,88', '5–7'], [5, 'Irlanda', '71,09', '3–10'], [6, 'Dinamarca', '69,53', '4–13'], [7, 'Australia', '68,36', '3–11'], [8, 'Islandia', '66,41', '4–14'], [9, 'Eslovenia', '65,63', '4–15'], [10, 'España', '64,84', '5–14'], [11, 'Reino Unido', '64,06', '8–17'], [12, 'Suecia', '63,28', '8–15'], [13, 'Finlandia', '62,50', '7–16'], [14, 'Estonia', '60,16', '6–21'], [15, 'Canadá', '54,69', '13–23'], [16, 'Italia', '53,91', '7–22'], [17, 'Francia', '50,00', '16–21'], [18, 'Luxemburgo', '49,61', '12–23'], [19, 'Polonia', '48,44', '13–24'], [20, 'Chequia', '47,66', '17–24'], [21, 'Austria', '46,09', '19–20'], [22, 'Israel', '46,09', '15–27'], [23, 'Estados Unidos', '40,63', '18–25'], [24, 'Türkiye', '38,28', '20–27'], [25, 'Grecia', '36,72', '22–27'], [26, 'Lituania', '31,25', '24–28'], [27, 'Chile', '27,34', '26–30'], [28, 'Hungría', '25,00', '24–30'], [29, 'Letonia', '21,88', '28–31'], [30, 'Eslovaquia', '17,97', '26–31'], [31, 'Costa Rica', '12,50', '29–32'], [32, 'Colombia', '7,81', '32–33'], [33, 'México', '6,25', '31–33'],
];

export default function Home() {
  return (
    <main className="min-h-screen bg-[#f7f5ef] text-[#15231f]">
      <section className="border-b border-[#d8d6cf] bg-[#132b27] px-6 py-16 text-[#f7f5ef] sm:px-10 lg:px-16">
        <div className="mx-auto max-w-6xl">
          <div className="mb-10 flex items-center gap-3 text-sm font-medium tracking-[0.16em] text-[#c9d6c3] uppercase">
            <span className="h-2 w-2 rounded-full bg-[#dfb84f]" />
            Tablero de trazabilidad pública
          </div>
          <div className="grid gap-10 lg:grid-cols-[1.4fr_0.6fr] lg:items-end">
            <div>
              <p className="mb-4 text-sm tracking-[0.12em] text-[#b5c8b8] uppercase">Proyecto sin fines de lucro</p>
              <h1 className="max-w-3xl font-serif text-5xl leading-[0.96] tracking-tight sm:text-6xl">Índice de Eficiencia del Estado</h1>
              <p className="mt-6 max-w-2xl text-lg leading-8 text-[#d7e2d7]">
                Seguimos la construcción pública, verificable y prudente de un índice comparativo. El sitio muestra evidencia, avance y una comparación exploratoria; todavía no publica puntajes ni rankings IEE oficiales.
              </p>
            </div>
            <div className="rounded-2xl border border-[#547069] bg-[#1d3a34] p-6">
              <p className="text-sm text-[#b5c8b8]">Estado actual</p>
              <p className="mt-2 text-3xl font-semibold">En construcción</p>
              <p className="mt-3 text-sm leading-6 text-[#d7e2d7]">El ciclo técnico v0.7 y los cinco hitos de evaluación v0.9 están completos. Hay 33 países con resultados comparables y una cohorte IEE completa cerrada de 24, sin aceptar atajos ni depender de fuentes potencialmente pagadas.</p>
            </div>
          </div>
        </div>
      </section>

      <section className="px-6 py-12 sm:px-10 lg:px-16">
        <div className="mx-auto max-w-6xl">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
            {[
              ['100%', 'Ciclo técnico v0.7 completado', Flag],
              ['100%', 'Ruta v0.9: ciclo de evaluación completado', ShieldCheck],
              ['33 / 30', 'Resultados comparables: cuatro dimensiones, sin IEE', Globe2],
              ['24 / 30', 'Cohorte IEE completa cerrada: mínimo aún no alcanzado', Database],
              ['0', 'Rankings oficiales publicados', LockKeyhole],
            ].map(([value, label, Icon]) => {
              const CardIcon = Icon as typeof Flag;
              return (
                <article key={label as string} className="rounded-2xl border border-[#d8d6cf] bg-white p-5 shadow-sm">
                  <CardIcon className="h-5 w-5 text-[#28716b]" aria-hidden="true" />
                  <p className="mt-6 text-3xl font-semibold tracking-tight">{value}</p>
                  <p className="mt-2 text-sm leading-5 text-[#5a655f]">{label}</p>
                </article>
              );
            })}
          </div>
        </div>
      </section>

      <section className="px-6 pb-12 sm:px-10 lg:px-16">
        <div className="mx-auto grid max-w-6xl gap-8 lg:grid-cols-[1.15fr_0.85fr]">
          <article className="rounded-3xl border border-[#d8d6cf] bg-white p-7 sm:p-9">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-full bg-[#e6f0ed]">
                <Globe2 className="h-5 w-5 text-[#28716b]" />
              </div>
              <div>
                <p className="text-sm font-medium">Cobertura por dimensión</p>
                <p className="text-sm text-[#68736c]">Países completos en cada corte propio; no son puntajes de países.</p>
              </div>
            </div>
            <div className="mt-8 space-y-6">
              {dimensions.map((dimension) => (
                <div key={dimension.name}>
                  <div className="mb-2 flex justify-between gap-4 text-sm">
                    <span className="font-medium">{dimension.name}</span>
                    <span className="text-[#66716a]">{dimension.complete} / 38</span>
                  </div>
                  <div className="h-2 overflow-hidden rounded-full bg-[#eceae4]">
                    <div className={`bar-${dimension.tone} h-full rounded-full`} style={{ width: `${(dimension.complete / 38) * 100}%` }} />
                  </div>
                  <p className="mt-2 text-xs text-[#6e7771]">{dimension.detail}</p>
                </div>
              ))}
            </div>
          </article>

          <article className="rounded-3xl bg-[#e7eee8] p-7 sm:p-9">
            <div className="flex items-center gap-3">
              <Scale className="h-5 w-5 text-[#28716b]" />
              <p className="text-sm font-medium">Ejemplo de evidencia regional</p>
            </div>
            <h2 className="mt-6 font-serif text-3xl leading-tight">Colombia y Estados Unidos</h2>
            <p className="mt-3 text-sm leading-6 text-[#496057]">Indicador de dispersión territorial de seguridad, 2021. Mide la brecha P90–P10 ponderada por población.</p>
            <div className="mt-7 grid grid-cols-2 gap-4">
              <div className="rounded-2xl bg-white p-5"><p className="text-xs tracking-[0.12em] text-[#62746b] uppercase">Colombia</p><p className="mt-2 text-4xl font-semibold">35,5</p></div>
              <div className="rounded-2xl bg-white p-5"><p className="text-xs tracking-[0.12em] text-[#62746b] uppercase">Estados Unidos</p><p className="mt-2 text-4xl font-semibold">6,1</p></div>
            </div>
            <div className="mt-6 flex gap-3 rounded-xl border border-[#c3d1c5] bg-[#f5f8f3] p-4 text-sm leading-5 text-[#40594e]">
              <CircleAlert className="mt-0.5 h-5 w-5 shrink-0" />
              <p>Es una evidencia de una dimensión, no una calificación general ni una posición en un ranking.</p>
            </div>
          </article>
        </div>
      </section>

      <section className="border-y border-[#d8d6cf] bg-[#f1f5ef] px-6 py-12 sm:px-10 lg:px-16">
        <div className="mx-auto max-w-6xl">
          <div className="flex flex-col justify-between gap-5 sm:flex-row sm:items-end">
            <div>
              <p className="text-sm font-medium tracking-[0.12em] text-[#557067] uppercase">Publicación experimental</p>
              <h2 className="mt-3 font-serif text-4xl leading-tight">Ranking exploratorio de resultados v0.1</h2>
              <p className="mt-3 max-w-3xl text-sm leading-6 text-[#53645b]">Ordena 33 países por cuatro resultados observados, con pesos iguales. La columna “rango” muestra su mejor y peor posición al retirar una dimensión. No mide eficiencia, no usa recursos, acceso o equidad y no es el IEE oficial.</p>
            </div>
            <div className="rounded-xl border border-[#c3d1c5] bg-white px-4 py-3 text-sm text-[#40594e]">0 rankings IEE oficiales · 1 comparación exploratoria publicada</div>
          </div>
          <div className="mt-8 overflow-hidden rounded-2xl border border-[#d8d6cf] bg-white">
            <div className="grid grid-cols-[3.25rem_1fr_4.5rem_3.5rem] border-b border-[#e3e1da] bg-[#f8f7f3] px-5 py-3 text-xs font-semibold tracking-[0.1em] text-[#64736a] uppercase"><span>Pos.</span><span>País</span><span className="text-right">Puntaje</span><span className="text-right">Rango*</span></div>
            <div className="grid divide-y divide-[#eceae4] sm:grid-cols-2 sm:divide-x sm:divide-y-0">
              {[exploratoryRanking.slice(0, 17), exploratoryRanking.slice(17)].map((column, index) => (
                <div key={index} className="divide-y divide-[#eceae4]">
                  {column.map(([position, country, score, range]) => (
                    <div key={country as string} className="grid grid-cols-[3.25rem_1fr_4.5rem_3.5rem] items-center px-5 py-3 text-sm">
                      <span className="font-semibold text-[#28716b]">{position}</span><span>{country}</span><span className="text-right font-medium">{score}</span><span className="text-right text-[#557067]">{range}</span>
                    </div>
                  ))}
                </div>
              ))}
            </div>
          </div>
          <p className="mt-4 text-xs leading-5 text-[#69776e]">El puntaje es una posición normalizada de 0 a 100 dentro de esta muestra, no una calificación absoluta de gobiernos. *Rango: mejor–peor posición en cuatro recálculos que omiten una dimensión; no es un intervalo estadístico.</p>
        </div>
      </section>

      <section className="border-y border-[#d8d6cf] bg-[#efede6] px-6 py-12 sm:px-10 lg:px-16">
        <div className="mx-auto max-w-6xl">
          <p className="text-sm font-medium tracking-[0.12em] text-[#557067] uppercase">Ruta de lanzamiento</p>
          <h2 className="mt-3 max-w-2xl font-serif text-4xl leading-tight">Qué debe ocurrir antes de que exista una comparación agregada.</h2>
          <div className="mt-8 grid gap-4 md:grid-cols-2">
            {milestones.map(([title, state, text]) => (
              <article key={title} className="rounded-2xl border border-[#d4d2ca] bg-[#f9f8f4] p-5">
                <div className="flex items-start justify-between gap-3">
                  <h3 className="font-semibold">{title}</h3>
                  <span className={`dot-${state === 'Listo' ? 'teal' : state === 'En curso' ? 'amber' : 'violet'} mt-1.5 h-2.5 w-2.5 rounded-full`} />
                </div>
                <p className="mt-3 text-sm leading-6 text-[#5c6760]">{text}</p>
                <p className="mt-4 text-xs font-medium tracking-wide text-[#577068] uppercase">{state}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="px-6 py-12 sm:px-10 lg:px-16">
        <div className="mx-auto max-w-6xl rounded-3xl border border-[#c3d1c5] bg-[#e7eee8] p-8 sm:p-10">
          <p className="text-sm font-medium tracking-[0.12em] text-[#557067] uppercase">Revisión abierta</p>
          <div className="mt-4 grid gap-6 lg:grid-cols-[1.35fr_0.65fr] lg:items-end">
            <div>
              <h2 className="font-serif text-3xl leading-tight">Ayuda a poner a prueba el método, no a elegir ganadores.</h2>
              <p className="mt-3 max-w-2xl text-sm leading-6 text-[#496057]">Especialistas pueden cuestionar reglas metodológicas o proponer evidencia pública. Todo aporte debe explicar su impacto sobre comparabilidad; ningún comentario cambia el método ni crea un ranking IEE por sí solo.</p>
            </div>
            <div className="flex flex-col gap-3 sm:flex-row lg:flex-col">
              <a className="inline-flex items-center justify-center gap-2 rounded-full bg-[#28716b] px-5 py-3 text-sm font-semibold text-white transition hover:bg-[#1f5b56]" href="https://github.com/rickHard29/indice-eficiencia-del-estado/issues/1" target="_blank" rel="noreferrer">
                Revisar metodología <ArrowUpRight className="h-4 w-4" />
              </a>
              <a className="inline-flex items-center justify-center gap-2 rounded-full border border-[#79948a] bg-white px-5 py-3 text-sm font-semibold text-[#28534b] transition hover:bg-[#f7faf6]" href="https://github.com/rickHard29/indice-eficiencia-del-estado/issues/new?template=evidence-proposal.yml" target="_blank" rel="noreferrer">
                Proponer evidencia <ArrowUpRight className="h-4 w-4" />
              </a>
            </div>
          </div>
        </div>
      </section>

      <section className="px-6 py-12 sm:px-10 lg:px-16">
        <div className="mx-auto flex max-w-6xl flex-col justify-between gap-6 rounded-3xl bg-[#142b27] p-8 text-white sm:flex-row sm:items-center sm:p-10">
          <div><p className="text-sm text-[#b9ccc0]">El trabajo es público y versionado.</p><h2 className="mt-2 font-serif text-3xl">Consulta el código, las fuentes y las decisiones.</h2></div>
          <a className="inline-flex shrink-0 items-center gap-2 rounded-full bg-[#dfb84f] px-5 py-3 text-sm font-semibold text-[#1f2a23] transition hover:bg-[#edca6a]" href="https://github.com/rickHard29/indice-eficiencia-del-estado" target="_blank" rel="noreferrer">
            Ver repositorio <ArrowUpRight className="h-4 w-4" />
          </a>
        </div>
      </section>

      <footer className="px-6 pb-8 text-center text-xs text-[#748078]">IEE · Datos y metodología en evolución · Actualizado con el núcleo de resultados comparables v1.0</footer>
    </main>
  );
}
