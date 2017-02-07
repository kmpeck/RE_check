"""Script for analyzing the introduction of RE sites during deep mutational scanning

Kayla Peck, 2017. 

For command line arguments, run::

    python RE_check.py -h

"""

import os
import sys
import math
import argparse

def Parser():
	"""Returns command line parser."""
	parser = argparse.ArgumentParser(
			description='Script by  Kayla Peck to analyze the introduction of restriction sites during deep mutational scanning.',
			formatter_class=argparse.ArgumentDefaultsHelpFormatter,
			)

	parser.add_argument('sequencefile', help='the name of a file giving the sequence for which you are mutagenizing')
	parser.add_argument('firstcodon', type=int, help='first codon in infile to mutagenize')
	parser.add_argument('outfile', help='name of restriction enzyme output file')
	parser.add_argument('cutsite', type=str, help='specific restriction enzyme cutsite you would like to analyze')
    
	return parser
	
def NPermutations():
	"""Creates a three nucleotide set of all permutations of nucleotides (NNN)
	
	Returns a list of all permutations for NNN
	"""
	permutations = []
	library = ['N','N','N']
	for i in 'ATGC':
		library[0] = i
		for j in 'ATGC':
			library[1] = j
			for k in 'ATGC':           
				library[2] = k
				permutations.append(''.join([nt for nt in library if nt.istitle()]))
				
	return permutations

def MutagenizeCodon(seq, codon, cutsite, permutations):

	"""Creates oligos to tile a gene and introduce NNN at each codon.

	*seq* : sequence of the gene. 
	*codon* : codon to mutagenize.
	*cutsite* : restriction enzyme cutsite sequence to check for.

	Mutates a codon to NNN.

	Returns a list of all matches to the cutsite generated by NNN at that codon.
	"""

	nc = len(cutsite) #length of restriction enzyme cutsite
	n = len(seq)
	assert len(seq) % 3 == 0, "length of sequence not a multiple of 3"
	seq = ''.join([nt for nt in seq if nt.istitle()])
	
	icodon = (codon-1) * 3
	perm_seq_all = []
	
	for i in range(0,len(permutations)):
		perm_seq = seq[max(0,icodon-nc):icodon] + permutations[i] + seq[min(n,icodon+3):min(n,icodon+3+nc)]
		perm_seq_all.append(perm_seq)
	
	RE_data = []
	for i in range(0,len(perm_seq_all)):
		if cutsite in perm_seq_all[i]:
			RE_data.append((codon, perm_seq_all[i]))
	
	if len(RE_data) > 0:
		return RE_data


def main():
	parser = Parser()
	args = vars(parser.parse_args())

	print("Read the following command line arguments")
	for (argname, argvalue) in args.items():
		print("\t%s = %s" % (argname, argvalue))

	#Read in sequence file
	sequencefile = args['sequencefile']
	if not os.path.isfile(sequencefile):
		raise IOError("Cannot find sequencefile %s" % sequencefile)
	sequence = open(sequencefile).read() 
	sequence = sequence.replace(' ', '')
	sequence = sequence.replace('\n', '')
	sequence = sequence.upper()
	print( "Read a sequence of length %d from %s:\n%s" % (len(sequence), sequencefile, sequence))
	outfile = args['outfile']
	cutsite = args['cutsite']
	firstcodon =  args['firstcodon']
	print( "\nThe sequence will be scanned starting at codon %d and searching for the cutsite %s." % (firstcodon, cutsite))

	#Generate permutations needed for scanning
	permutations = NPermutations()
	
    #Scan each codon for the presence of the cutsite
	scanlength = len(sequence)//3 - firstcodon + 1
	introduced_REsites = []
	for i in range(0,scanlength):
		RE_data = MutagenizeCodon(sequence, firstcodon+i, cutsite, permutations)
		if RE_data is not None:
			introduced_REsites.append(RE_data)
		#print RE_data

	print( "\nThere were %d introduced cutsites for the sequence %s" % (len(introduced_REsites), cutsite))
    
	if len(introduced_REsites) > 0:
		print( "\nNow writing these introduced cutsites to %s" % outfile)
		f = open(outfile, 'w+')
		f.write("Cutsite: %s\r\n" % cutsite)
		f.write("Introduced sites: %d\r\n" % len(introduced_REsites))
		f.write("Input sequence file: %s\r\n" % sequencefile)
		f.write("\r\nCodon\tSequence\r\n")
		for i in range(0,len(introduced_REsites)):
			#print(introduced_REsites[i][0])
			f.write("%d\t%s\r\n" % (introduced_REsites[i][0]))
		f.close()
	else:
		print( "\nNo cutsites to print, program done.\n")

main() # run the main program
