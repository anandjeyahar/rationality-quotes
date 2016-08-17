import sys
import math

def conv(d1,d2) :
    n1 = len(d1)
    n2 = len(d2)
    d = []
    for i in range(n1+n2-1) :
	c = sum( ( d1[j]*d2[i-j] for j in range(n1) if 0<=i-j<n2 ) )
	d.append(c)
    return d

def read(stream) :
    m = {}
    d = []
    for l in stream :
	itemnum,score = map( int, l.strip().split() )
	if score<0 :
	    score = 0
	if score in m :
	    m[score] += itemnum
	else :
	    m[score] = itemnum
    mi = min(m.keys())
    ma = max(m.keys())
    su = sum(m.values())
    for i in range(ma+1) :
	d.append( float(m.get(i,0))/su )
    return d

d = read(file("scoredistribution"))

def fastdistexp(d,e) :
    if e==1 :
	return d[:]

    dd = fastdistexp(d,e/2)
    dd = conv(dd,dd)
    if e%2==1 :
	return conv(dd,d)
    else :
	return dd
	
def distexp(d,exponent) :
    dd = d[:]
    for i in range(exponent-1) :
	dd = conv(dd,d)
    return dd

def probOfAtLeast(d,x) :
    return sum( d[int(math.ceil(x)):] )

def writeDist(d) :
    for i,p in enumerate(d) :
	print "%d\t%g\t%g" % (i,p,probOfAtLeast(d,i))

# writeDist(distexp(d,54))
# sys.exit()

def test() :
    for x in range(0,300,10) :
	print x,probOfAtLeast(dd,x)

def main() :
    for l in sys.stdin :
	a = l.strip().split()
	assert len(a)==3
	name = a[0]
	score = int(float(a[1])+0.5)
	num = int(a[2])
	dd = fastdistexp(d,num)
	print "* %.5f (%.2f in %d): %s" % ( probOfAtLeast(dd,score), float(score)/num, num, name )
	sys.stdout.flush()

main()
