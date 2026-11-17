# Dashboard de triagem

Painel local (React + Node) com as issues triadas na rodada TO-BE e as respostas da triagem.
Somente leitura: não fala com o GitHub, lê `data/issues.json`.

## Rodar

Requer Node 18+.

```
cd dashboard
npm install
npm start
```

Abra http://localhost:3000. Outra porta: `PORT=4000 npm start`.

O seletor Auto/Claro/Escuro fica no canto superior direito.
