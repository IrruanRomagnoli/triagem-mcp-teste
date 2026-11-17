// Servidor local somente leitura: serve a UI React e data/issues.json. Não fala com o GitHub.
const http = require("http");
const fs = require("fs");
const path = require("path");

const PORT = process.env.PORT || 3000;
const root = __dirname;
const nm = (p) => path.join(root, "node_modules", p);

// URL -> arquivo (React e Babel saem do node_modules, funciona offline)
const routes = {
  "/": path.join(root, "public/index.html"),
  "/app.jsx": path.join(root, "public/app.jsx"),
  "/api/issues": path.join(root, "data/issues.json"),
  "/vendor/react.js": nm("react/umd/react.production.min.js"),
  "/vendor/react-dom.js": nm("react-dom/umd/react-dom.production.min.js"),
  "/vendor/babel.js": nm("@babel/standalone/babel.min.js"),
};
const types = { ".html": "text/html", ".jsx": "text/javascript", ".js": "text/javascript", ".json": "application/json" };

http
  .createServer((req, res) => {
    const file = routes[req.url.split("?")[0]];
    if (!file) return res.writeHead(404).end("Não encontrado");
    fs.readFile(file, (err, data) => {
      if (err) return res.writeHead(500).end("Erro ao ler arquivo");
      res.writeHead(200, { "Content-Type": `${types[path.extname(file)]}; charset=utf-8` }).end(data);
    });
  })
  .listen(PORT, () => console.log(`Dashboard em http://localhost:${PORT}`));
