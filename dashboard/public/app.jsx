const { useState, useEffect } = React;

const COLORS = { bug: "var(--bug)", enhancement: "var(--enhancement)", question: "var(--question)", documentation: "var(--documentation)" };

const fmtData = (iso) => new Date(iso).toLocaleString("pt-BR", { dateStyle: "short", timeStyle: "short" });
const minutos = (a, b) => Math.round((new Date(b) - new Date(a)) / 60000);

// Troca `texto` por <code>texto</code>
function Texto({ children }) {
  return children.split(/(`[^`]+`)/).map((p, i) =>
    p.startsWith("`") ? <code key={i}>{p.slice(1, -1)}</code> : p
  );
}

function Stat({ n, label, color, total }) {
  return (
    <div className="stat">
      <div className="n" style={color && { color }}>{n}</div>
      <div className="l">{label}</div>
      {total && <div className="bar"><i style={{ width: `${(n / total) * 100}%`, background: color }} /></div>}
    </div>
  );
}

function Card({ issue }) {
  const { number, title, body, author, created_at, label, response } = issue;
  return (
    <article className="card">
      <div className="top">
        <span className="num">#{number}</span>
        <span className="badge" style={{ "--c": COLORS[label] }}>{label}</span>
      </div>
      <h3>{title}</h3>
      <p className="body">{body.trim()}</p>
      <div className="meta">aberta por {author} · {fmtData(created_at)}</div>
      <div className="reply">
        <div className="who">
          <span>Resposta da triagem · {fmtData(response.created_at)} · {minutos(created_at, response.created_at)} min após abrir</span>
          <a href={response.url} target="_blank" rel="noreferrer">ver no GitHub ↗</a>
        </div>
        <Texto>{response.body}</Texto>
      </div>
    </article>
  );
}

// "auto" segue o sistema; claro/escuro forçam data-theme e ficam salvos no navegador
function TemaToggle() {
  const [tema, setTema] = useState(() => document.documentElement.dataset.theme || "auto");
  const escolher = (t) => {
    setTema(t);
    if (t === "auto") delete document.documentElement.dataset.theme;
    else document.documentElement.dataset.theme = t;
    try { t === "auto" ? localStorage.removeItem("tema") : localStorage.setItem("tema", t); } catch (e) {}
  };
  return (
    <div className="theme" role="group" aria-label="Tema">
      {[["auto", "Auto"], ["light", "Claro"], ["dark", "Escuro"]].map(([v, nome]) => (
        <button key={v} aria-pressed={tema === v} onClick={() => escolher(v)}>{nome}</button>
      ))}
    </div>
  );
}

function App() {
  const [data, setData] = useState(null);
  const [erro, setErro] = useState(null);
  const [filtro, setFiltro] = useState("todas");

  useEffect(() => {
    fetch("/api/issues").then((r) => r.json()).then(setData).catch((e) => setErro(e.message));
  }, []);

  if (erro) return <div className="wrap">Erro ao carregar: {erro}</div>;
  if (!data) return <div className="wrap">Carregando…</div>;

  const { issues } = data;
  const labels = Object.keys(COLORS).filter((l) => issues.some((i) => i.label === l));
  const visiveis = filtro === "todas" ? issues : issues.filter((i) => i.label === filtro);

  return (
    <div className="wrap">
      <header>
        <div>
          <h1>Triagem de issues</h1>
          <p>{data.repo} · rodada TO-BE · propostas de um agente de IA, aprovadas por humano</p>
        </div>
        <TemaToggle />
      </header>

      <section className="stats">
        <Stat n={issues.length} label="issues triadas" />
        {labels.map((l) => (
          <Stat key={l} n={issues.filter((i) => i.label === l).length} label={l} color={COLORS[l]} total={issues.length} />
        ))}
      </section>

      <div className="filters">
        {["todas", ...labels].map((l) => (
          <button key={l} className="chip" aria-pressed={filtro === l} onClick={() => setFiltro(l)}>{l}</button>
        ))}
      </div>

      <section className="grid">
        {visiveis.map((i) => <Card key={i.number} issue={i} />)}
      </section>

      <footer>Dados lidos via MCP do GitHub ({data.fonte}). Este painel é somente leitura.</footer>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<App />);
