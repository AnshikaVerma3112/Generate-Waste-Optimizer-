"""Exact single-vehicle routing on a simulated road graph (standard library only)."""
import heapq, math

def graph_data():
    import json
    from pathlib import Path
    return json.loads((Path(__file__).parent / 'data' / 'graph.json').read_text(encoding='utf-8'))


def solve(data):
    validate_payload(data)
    g=graph_data(); ids={n['id'] for n in g['nodes']}
    depot=str(data.get('depot','12')); stops=data.get('stops',[])
    if depot not in ids: raise ValueError('Choose a valid depot.')
    if not 1<=len(stops)<=10: raise ValueError('Add between 1 and 10 collection stops.')
    seen=set(); total=0
    for s in stops:
        node=str(s['node']); kg=float(s['kg'])
        if node not in ids or node==depot or node in seen: raise ValueError('Stops must be unique and different from the depot.')
        if not math.isfinite(kg) or kg<=0: raise ValueError('Every stop needs a positive, finite waste load.')
        if not isinstance(s.get('name'),str) or not s['name'].strip() or len(s['name'])>80: raise ValueError('Stop names must contain 1–80 characters.')
        seen.add(node);total+=kg
    capacity=float(data.get('capacity',0))
    if not math.isfinite(capacity) or capacity<=0: raise ValueError('Set a positive vehicle capacity.')
    if total>capacity: raise ValueError(f'Over capacity: {total:g} kg of waste exceeds {capacity:g} kg. Increase capacity or remove stops.')
    closed=set(data.get('closed',[])); adj={n:[] for n in ids}
    for e in g['edges']:
        if e['id'] not in closed:
            adj[e['a']].append((e['b'],e['km']));adj[e['b']].append((e['a'],e['km']))
    points=[depot]+[str(s['node']) for s in stops]; matrix=[];paths=[]
    for src in points:
        dist={src:0}; prev={}; heap=[(0,src)]
        while heap:
            d,u=heapq.heappop(heap)
            if d>dist[u]+1e-9: continue
            for v,w in adj[u]:
                nd=d+w
                if nd<dist.get(v,float('inf'))-1e-9:
                    dist[v]=nd;prev[v]=u;heapq.heappush(heap,(nd,v))
        if any(p not in dist for p in points): raise ValueError('A required stop is unreachable. Reopen roads or change the stops.')
        row=[]
        for dst in points:
            route=[dst]
            while route[-1]!=src:route.append(prev[route[-1]])
            row.append(route[::-1])
        matrix.append([dist[p] for p in points]);paths.append(row)
    n=len(stops);dp={}
    for j in range(n):dp[(1<<j,j)]=(matrix[0][j+1],[j+1])
    for mask in range(1,1<<n):
        for j in range(n):
            if (mask,j) not in dp:continue
            cost,path=dp[mask,j]
            for k in range(n):
                if mask&(1<<k):continue
                key=(mask|(1<<k),k);candidate=cost+matrix[j+1][k+1]
                if key not in dp or candidate<dp[key][0]-1e-9:dp[key]=(candidate,path+[k+1])
    best=min((v[0]+matrix[j+1][0],v[1]) for (mask,j),v in dp.items() if mask==(1<<n)-1)
    def result(order):
        legs=[{'from':points[a],'to':points[b],'km':round(matrix[a][b],3),'path':paths[a][b]} for a,b in zip(order,order[1:])]
        return {'order':order,'km':round(sum(x['km'] for x in legs),3),'legs':legs}
    return {'original':result([0]+list(range(1,n+1))+[0]),'optimized':result([0]+best[1]+[0]),'load':total,'capacity':capacity,'engine':'Python · Dijkstra + Held–Karp'}


def validate_payload(data):
    if not isinstance(data, dict):
        raise ValueError('Send a JSON object containing depot, capacity, stops and closed.')
    if not isinstance(data.get('stops'), list):
        raise ValueError('Stops must be a list.')
    for stop in data['stops']:
        if not isinstance(stop, dict) or not all(k in stop for k in ('node', 'kg', 'name')):
            raise ValueError('Each stop needs node, name and kg.')
        if isinstance(stop['kg'], bool):
            raise ValueError('Waste loads must be numbers.')
    if isinstance(data.get('capacity'), bool):
        raise ValueError('Capacity must be a number.')
    closed = data.get('closed', [])
    allowed = {edge['id'] for edge in graph_data()['edges']}
    if not isinstance(closed, list) or any(not isinstance(x, str) or x not in allowed for x in closed):
        raise ValueError('Closed roads must be a list of valid road IDs.')
