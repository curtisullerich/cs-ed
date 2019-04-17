# dependencies
# pip install reportlab
# pip install pypdf2

# Useful for creating PNG versions of the generated PDFs.
# for f in *.pdf ; do convert -density 150 $f -quality 100 $f.png ; done
# rename 's/pdf.png/png/' *.pdf.png

from reportlab.pdfgen import canvas
import random
from PyPDF2 import PdfFileWriter, PdfFileReader

edge = 70 # pixels per tile edge
random.seed(0)

# in a 2 row, 3 column grid 0,0 is the bottom left and 1,2 is the top right
def place_tile(can, bool, row, col):
  if bool:
    image = 'white.png'
  else:
    image = 'black.png'
  can.drawImage(image, col*edge, row*edge, edge, edge, mask='auto')

def make_grid(size):
  grid = []
  for row in range(size-1):
    grid.append([])
    trues = 0
    for col in range(size):
      grid[row].append([])
      if col == size-1:
        # if it's odd, make the last one true/white.
        grid[row][col] = trues%2 == 1
      else:
        val = random.random() < 0.5
        grid[row][col] = val
        if val:
          trues+=1
  grid.append([])
  for i in range(size):
    grid[-1].append([])
  for col in range(size):
    trues = 0
    for row in range(size-1):
      if grid[row][col]:
        trues+=1
    # if it's odd, make the last one true/white.
    grid[size-1][col] = trues%2 == 1
  return grid

def output(filename, grid):
  size = len(grid)
  c = canvas.Canvas(filename)
  c.setPageSize((size*edge, size*edge))
  for row in range(size):
    for col in range(size):
      place_tile(c, grid[row][col], row, col)
  c.showPage()
  c.save()

def flip_tile(grid):
  size = len(grid)
  mutr = random.randint(0, size-1)
  mutc = random.randint(0, size-1)
  grid[mutr][mutc] = not grid[mutr][mutc]

def main():
 for i in range(10):
  for size in range(3,11):
    grid = make_grid(size)
    flip_tile(grid)
    output('%sx%s-%s.pdf' % (size, size, i), grid)

main()
