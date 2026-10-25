export function solve(data,g){
 const ids=new Set(g.nodes.map(n=>n.id)),stops=data.stops,depot=String(data.depot),capacity=Number(data.capacity);
 if(!ids.has(depot))throw Error('Choose a valid depot.');
 if(!Array.isArray(stops)||stops.length<1||stops.length>10)throw Error('Add between 1 and 10 collection stops.');
 let total=0,seen=new Set();
 for(const s of stops){if(!ids.has(String(s.node))||String(s.node)===depot||seen.has(String(s.node)))throw Error('Stops must be unique and different from the depot.');if(!Number.isFinite(Number(s.kg))||Number(s.kg)<=0)throw Error('Every stop needs a positive, finite waste load.');if(typeof s.name!=='string'||!s.name.trim()||s.name.length>80)throw Error('Stop names must contain 1–80 characters.');seen.add(String(s.node));total+=Number(s.kg);}
 if(!Number.isFinite(capacity)||capacity<=0)throw Error('Set a positive vehicle capacity.');if(total>capacity)throw Error(`Over capacity: ${total} kg of waste exceeds ${capacity} kg. Increase capacity or remove stops.`);
 const adj=Object.fromEntries([...ids].map(n=>[n,[]])),closed=new Set(data.closed);
 for(const e of g.edges)if(!closed.has(e.id)){adj[e.a].push([e.b,e.km]);adj[e.b].push([e.a,e.km]);}
 const points=[depot,...stops.map(s=>String(s.node))],matrix=[],paths=[];
 for(const src of points){const dist=Object.fromEntries([...ids].map(n=>[n,Infinity])),prev={},visited=new Set();dist[src]=0;
 for(let count=0;count<ids.size;count++){let u=null;for(const v of ids)if(!visited.has(v)&&(u===null||dist[v]<dist[u]))u=v;if(u===null||!Number.isFinite(dist[u]))break;visited.add(u);for(const [v,w] of adj[u])if(dist[u]+w<dist[v]-1e-9){dist[v]=dist[u]+w;prev[v]=u;}}
 if(points.some(p=>!Number.isFinite(dist[p])))throw Error('A required stop is unreachable. Reopen roads or change the stops.');
 matrix.push(points.map(p=>dist[p]));paths.push(points.map(dst=>{let r=[dst];while(r.at(-1)!==src)r.push(prev[r.at(-1)]);return r.reverse();}));}
 const n=stops.length,dp=new Map(),key=(mask,j)=>mask+':'+j;
 for(let j=0;j<n;j++)dp.set(key(1<<j,j),[matrix[0][j+1],[j+1]]);
 for(let mask=1;mask<1<<n;mask++)for(let j=0;j<n;j++){const v=dp.get(key(mask,j));if(!v)continue;for(let k=0;k<n;k++)if(!(mask&(1<<k))){const id=key(mask|(1<<k),k),cost=v[0]+matrix[j+1][k+1];if(!dp.has(id)||cost<dp.get(id)[0]-1e-9)dp.set(id,[cost,[...v[1],k+1]]);}}
 let best=null;for(let j=0;j<n;j++){const v=dp.get(key((1<<n)-1,j)),cost=v[0]+matrix[j+1][0];if(!best||cost<best[0]-1e-9)best=[cost,v[1]];}
 function result(order){const legs=order.slice(1).map((b,i)=>({from:points[order[i]],to:points[b],km:+matrix[order[i]][b].toFixed(3),path:paths[order[i]][b]}));return {order,legs,km:+legs.reduce((s,l)=>s+l.km,0).toFixed(3)};}
 return {original:result([0,...stops.map((_,i)=>i+1),0]),optimized:result([0,...best[1],0]),load:total,capacity,engine:'Browser · Dijkstra + Held–Karp'};
}
