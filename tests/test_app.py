import copy,itertools,json,threading,unittest
from urllib.request import Request,urlopen
from urllib.error import HTTPError
from backend.server import make_server
from backend.solver import solve,graph_data
PLAN={'depot':'12','capacity':500,'closed':[],'stops':[{'node':n,'name':s,'kg':k} for n,s,k in [('0','Market',65),('24','Gardens',80),('4','Bus stop',50),('20','Apartments',95),('8','School',45)]]}
class AppTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.server=make_server(0);cls.base=f'http://127.0.0.1:{cls.server.server_port}';cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start()
 @classmethod
 def tearDownClass(cls):cls.server.shutdown();cls.server.server_close();cls.thread.join()
 def api(self,p):
  req=Request(self.base+'/api/optimize',data=json.dumps(p).encode(),headers={'Content-Type':'application/json'})
  try:
   with urlopen(req) as r:return r.status,json.load(r)
  except HTTPError as e:return e.code,json.load(e)
 def test_example(self):
  code,r=self.api(PLAN);self.assertEqual(code,200);self.assertEqual((r['original']['km'],r['optimized']['km'],r['load']),(13.8,8.4,335));self.assertTrue(r['engine'].startswith('Python'));self.assertEqual(sorted(r['optimized']['order'][1:-1]),[1,2,3,4,5])
 def test_optimum(self):
  p=copy.deepcopy(PLAN);p['stops']=p['stops'][:4];expected=min(solve({**p,'stops':list(o)})['original']['km'] for o in itertools.permutations(p['stops']));self.assertEqual(solve(p)['optimized']['km'],expected)
 def test_capacity(self):
  code,r=self.api({**PLAN,'capacity':300});self.assertEqual(code,400);self.assertIn('Over capacity',r['error'])
 def test_unreachable(self):
  closed=[e['id'] for e in graph_data()['edges'] if '12' in (e['a'],e['b'])];code,r=self.api({**PLAN,'closed':closed});self.assertEqual(code,400);self.assertIn('unreachable',r['error'])
 def test_bad_shapes(self):
  for p in [None,[],{}, {'stops':None},{**PLAN,'stops':[None]},{**PLAN,'closed':[{}]},{**PLAN,'capacity':True}]:
   with self.subTest(p=p):self.assertEqual(self.api(p)[0],400)
 def test_bad_stops(self):
  for stops in [[],PLAN['stops']*3,[PLAN['stops'][0]]*2,[{'node':'12','name':'Depot','kg':40}],[{'node':'0','name':'','kg':40}],[{'node':'0','name':'Market','kg':-1}]]:
   with self.subTest(stops=stops):self.assertEqual(self.api({**PLAN,'stops':stops})[0],400)
 def test_assets(self):
  with urlopen(self.base+'/api/graph') as r:self.assertEqual(json.load(r),graph_data())
  for p in ['/','/app.js','/style.css','/solver.js','/assets/journal-cover.png','/assets/journal-serif.woff','/api/health']:
   with self.subTest(p=p),urlopen(self.base+p) as r:self.assertEqual(r.status,200);r.read()
 def test_source_not_served(self):
  for p in ['/backend/solver.py','/../backend/solver.py','/assets/']:
   with self.subTest(p=p),self.assertRaises(HTTPError) as cm:urlopen(self.base+p)
   self.assertEqual(cm.exception.code,404)
 def test_malformed_json(self):
  req=Request(self.base+'/api/optimize',data=b'{bad',headers={'Content-Type':'application/json'})
  with self.assertRaises(HTTPError) as cm:urlopen(req)
  self.assertEqual(cm.exception.code,400)
if __name__=='__main__':unittest.main()
