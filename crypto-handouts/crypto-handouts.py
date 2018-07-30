import matplotlib.pyplot as plt
import networkx as nx
import random
from PyPDF2 import PdfFileWriter, PdfFileReader
import StringIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch

def make_handout(name):
  pdf_text = PdfFileReader(open("template.pdf", "rb"))
  pdf_graphs = PdfFileReader(open(name + "public.pdf", "rb"))
  output_file = PdfFileWriter()

  graphs_page = pdf_graphs.getPage(0)
  text_page = pdf_text.getPage(0)
  text_page.mergeTranslatedPage(graphs_page, 75, 0)
  text_page.mergeTranslatedPage(graphs_page, 75, 375)

  packet = StringIO.StringIO()
  can = canvas.Canvas(packet, pagesize=letter)
  can.setFont('Helvetica-Bold', 14)
  can.drawString(1*inch, 9.5*inch, "Person %s's public map. Use this to send a message to person %s." % (name, name))
  can.drawString(1*inch, 4.5*inch, "Person %s's public map. Use this to send a message to person %s." % (name, name))
  can.save()
  packet.seek(0)
  new_pdf = PdfFileReader(packet)
  text_page.mergePage(new_pdf.getPage(0))

  output_file.addPage(text_page)
  with open(name + "handout.pdf", "wb") as outputStream:
    output_file.write(outputStream)

# Return true if A, B, C are oriented counterclockwise.
def ccw(A,B,C):
  return (C.y-A.y) * (B.x-A.x) > (B.y-A.y) * (C.x-A.x)

# Return true if line segments AB and CD intersect.
def intersect(A,B,C,D):
  return ccw(A,C,D) != ccw(B,C,D) and ccw(A,B,C) != ccw(A,B,D)

class Point:
  def __init__(self,x,y):
    self.x = x
    self.y = y

def intersections(elist, pos):
  count = 0
  for x in elist:
    for y in elist:
      if len(set([x[0],x[1],y[0],y[1]])) != 4:
        continue
      a = Point(pos[x[0]][0], pos[x[0]][1])
      b = Point(pos[x[1]][0], pos[x[1]][1])
      c = Point(pos[y[0]][0], pos[y[0]][1])
      d = Point(pos[y[1]][0], pos[y[1]][1])
      if intersect(a,b,c,d):
        count += 1
        # Note: This currently short-circuits after the first intersection.
        return count
  return count

def planar(G, pos):
  elist = [(u, v) for (u, v, d) in G.edges(data=True)]
  return intersections(elist, pos) == 0

def draw_graph(G, pos, secret_pool, valence_pool, name):
  elarge = [(u, v) for (u, v, d) in G.edges(data=True)]

  c = intersections(elarge, pos)

  nodes = nx.draw_networkx_nodes(G, pos, nodelist=secret_pool+valence_pool, node_color='white', node_size=300)
  nodes.set_edgecolor('black')
  nx.draw_networkx_edges(G, pos, edgelist=elarge, width=2)
  nx.draw_networkx_labels(G, pos, font_size=12, font_family='sans-serif')

  plt.axis('off')
  plt.savefig(name + "public.pdf", transparent=True)
  nodes = nx.draw_networkx_nodes(G, pos, nodelist=secret_pool, node_color='white', node_size=800, linewidths=3)
  nodes.set_edgecolor('green')
  plt.title("Person %s's private map. Person %s can use this to decrypt a message." % (name, name))
  plt.savefig(name + "private.pdf", transparent=True)
  plt.clf()

def remap_list(l, mapping):
  new = []
  for e in l:
    new.append(mapping[e])
  return new

def shuffle_graph(graph, valence_pool, secret_pool):
  elements = len(set(valence_pool).union(set(secret_pool)))
  reordered = range(elements)
  random.shuffle(reordered)
  mapping = dict()
  for i in range(elements):
    mapping[i] = chr(reordered[i]+97)
  shuffled_graph = dict()
  for k in graph:
    new_key = mapping[k]
    shuffled_graph[new_key] = remap_list(graph[k], mapping)
  return (shuffled_graph, remap_list(valence_pool, mapping), remap_list(secret_pool, mapping))

def random_map():
  G = nx.Graph()

  secrets = random.randint(2,3)
  valence = []
  graph = dict()
  next_valence = secrets
  valence_pool = []
  secret_pool = []

  # add some valence nodes to each secret node
  for i in range(secrets):
    secret_pool.append(i)
    num_valence = random.randint(1,3)
    this_valence = []
    for j in range(num_valence):
      this_valence.append(next_valence)
      valence_pool.append(next_valence)
      next_valence+=1
    graph[i] = this_valence

  # reorder the nodes so the secret ones aren't the first n, and swap ints for chars
  graph, valence_pool, secret_pool = shuffle_graph(graph, valence_pool, secret_pool)

  # connect some of the valence nodes to some other valence nodes
  for v in valence_pool:
    graph[v] = [random.choice(valence_pool)]

  for k in graph:
    for n in graph[k]:
      G.add_edge(k, n, weight=1)
  return (G, secret_pool, valence_pool)

def main():
  person_number = 0
  seed = 0
  while person_number < 30:
    seed += 1
    random.seed(seed)
    G, secret_pool, valence_pool = random_map()
    if not nx.is_connected(G):
      continue
    pos = nx.spring_layout(G, iterations=100, random_state=0)  # positions for all nodes
    if not planar(G, pos):
      continue
    name = str(seed)
    name = str(person_number)
    person_number += 1
    draw_graph(G, pos, secret_pool, valence_pool, name)
    make_handout(name)

main()
