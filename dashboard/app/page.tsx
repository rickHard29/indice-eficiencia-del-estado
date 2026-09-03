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
  { name: 'Educación', detail: 'Roles y recursos en prueba', tone: 'amber', progress: 56 },
  { name: 'Salud', detail: 'Recursos directos contrastados', tone: 'teal', progress: 61 },
  { name: 'Administración', detail: 'Acceso y equidad en revisión', tone: 'blue', progress: 58 },
  { name: 'Seguridad y justicia', detail: '30 países en sensibilidad multifuente', tone: 'violet', progress: 54 },
];

const milestones = [
  ['Base reproducible', 'Listo', 'Fuentes, pruebas y trazabilidad versionadas.'],
  ['Cobertura común', 'Listo', 'La sensibilidad de seguridad alcanza 30 países comparables.'],
  ['Ranking experimental', 'Pendiente', 'Requiere metodología v1 congelada y las demás dimensiones completas.'],
  ['Ranking oficial IEE v1', 'Bloqueado', 'Solo tras revisión independiente y publicación del protocolo.'],
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
                Seguimos la construcción pública, verificable y prudente de un índice comparativo. Este sitio muestra evidencia y avance; todavía no publica un ranking oficial.
              </p>
            </div>
            <div className="rounded-2xl border border-[#547069] bg-[#1d3a34] p-6">
              <p className="text-sm text-[#b5c8b8]">Estado actual</p>
              <p className="mt-2 text-3xl font-semibold">En construcción</p>
              <p className="mt-3 text-sm leading-6 text-[#d7e2d7]">La siguiente publicación será una metodología v1 y un corte experimental sujeto a revisión.</p>
            </div>
          </div>
        </div>
      </section>

      <section className="px-6 py-12 sm:px-10 lg:px-16">
        <div className="mx-auto max-w-6xl">
          <div className="grid gap-4 md:grid-cols-4">
            {[
              ['38%', 'Implementación del proyecto', Flag],
              ['110', 'Pruebas automatizadas superadas', ShieldCheck],
              ['30 / 30', 'Sensibilidad de seguridad: mínimo común alcanzado', Database],
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
                <p className="text-sm text-[#68736c]">Avance de preparación de evidencia, no puntajes de países.</p>
              </div>
            </div>
            <div className="mt-8 space-y-6">
              {dimensions.map((dimension) => (
                <div key={dimension.name}>
                  <div className="mb-2 flex justify-between gap-4 text-sm">
                    <span className="font-medium">{dimension.name}</span>
                    <span className="text-[#66716a]">{dimension.progress}%</span>
                  </div>
                  <div className="h-2 overflow-hidden rounded-full bg-[#eceae4]">
                    <div className={`bar-${dimension.tone} h-full rounded-full`} style={{ width: `${dimension.progress}%` }} />
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

      <section className="border-y border-[#d8d6cf] bg-[#efede6] px-6 py-12 sm:px-10 lg:px-16">
        <div className="mx-auto max-w-6xl">
          <p className="text-sm font-medium tracking-[0.12em] text-[#557067] uppercase">Ruta de lanzamiento</p>
          <h2 className="mt-3 max-w-2xl font-serif text-4xl leading-tight">Qué debe ocurrir antes de que exista un ranking.</h2>
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
        <div className="mx-auto flex max-w-6xl flex-col justify-between gap-6 rounded-3xl bg-[#142b27] p-8 text-white sm:flex-row sm:items-center sm:p-10">
          <div><p className="text-sm text-[#b9ccc0]">El trabajo es público y versionado.</p><h2 className="mt-2 font-serif text-3xl">Consulta el código, las fuentes y las decisiones.</h2></div>
          <a className="inline-flex shrink-0 items-center gap-2 rounded-full bg-[#dfb84f] px-5 py-3 text-sm font-semibold text-[#1f2a23] transition hover:bg-[#edca6a]" href="https://github.com/rickHard29/indice-eficiencia-del-estado" target="_blank" rel="noreferrer">
            Ver repositorio <ArrowUpRight className="h-4 w-4" />
          </a>
        </div>
      </section>

      <footer className="px-6 pb-8 text-center text-xs text-[#748078]">IEE · Datos y metodología en evolución · Actualizado con el corte v2.9 del proyecto</footer>
    </main>
  );
}
