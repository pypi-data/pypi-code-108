"""
======================COPYRIGHT/LICENSE START==========================

Util.py: Useful functions for scripts in this directory and its subdirectories

Copyright (C) 2005-2008 Wim Vranken (European Bioinformatics Institute)

=======================================================================

This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2.1 of the License, or (at your option) any later version.
 
A copy of this license can be found in ../../../../license/LGPL.license
 
This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
Lesser General Public License for more details.
 
You should have received a copy of the GNU Lesser General Public
License along with this library; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA


======================COPYRIGHT/LICENSE END============================

for further information, please contact :

- CCPN website (http://www.ccpn.ac.uk/)
- PDBe website (http://www.ebi.ac.uk/pdbe/)

- contact Wim Vranken (wim@ebi.ac.uk)
=======================================================================

If you are using this software for academic purposes, we suggest
quoting the following references:

===========================REFERENCE START=============================
R. Fogh, J. Ionides, E. Ulrich, W. Boucher, W. Vranken, J.P. Linge, M.
Habeck, W. Rieping, T.N. Bhat, J. Westbrook, K. Henrick, G. Gilliland,
H. Berman, J. Thornton, M. Nilges, J. Markley and E. Laue (2002). The
CCPN project: An interim report on a data model for the NMR community
(Progress report). Nature Struct. Biol. 9, 416-418.

Wim F. Vranken, Wayne Boucher, Tim J. Stevens, Rasmus
H. Fogh, Anne Pajon, Miguel Llinas, Eldon L. Ulrich, John L. Markley, John
Ionides and Ernest D. Laue (2005). The CCPN Data Model for NMR Spectroscopy:
Development of a Software Pipeline. Proteins 59, 687 - 696.

===========================REFERENCE END===============================
"""

import re
from b2bTools.general.ccpn.format.general.Constants import defaultSeqInsertCode

# characters that can be used as a one-digit index
indexChars = '123456789'

#######################
# Regular expressions #
#######################

def getRegularExpressions(format = None):

  patt = {}
  
  patt['emptyline'] = re.compile("^\s*$")
  patt['hash'] = re.compile("^\s*\#")
  patt['exclamation'] = re.compile("^\s*\!")
  patt['underscore'] = re.compile("^\s*\_")
  patt['colon'] = re.compile(":")
  patt['onlyDollar'] = re.compile("^\$$")
  patt['onlydigit'] = re.compile("^\d+$")
  patt['onlyFloat'] = re.compile("^\d+\.\d+$")
  patt['bracketEither'] = re.compile("\(|\)")
  patt['bracketOpen'] = re.compile("\s*\(")
  patt['bracketClose'] = re.compile("\)")
  patt['nucleusLetterDigit'] = re.compile("^([A-Za-z])(\d+)")
  patt['seqInsertCode'] = re.compile("^([A-Za-z]*)(\d+)([A-Za-z]*)")
  patt['anySpace'] = re.compile("\s")
  
  if format == 'amber':

    patt[format + 'RestraintStart'] = re.compile("(\&rst)")
    patt[format + 'RestraintEnd'] = re.compile("(\&end)")
  
  elif format == 'ansig':

    patt[format + 'CurlyBrace'] = re.compile("\{(.*)\}")

  elif format == 'auremol':

    patt[format + 'Section'] = re.compile("^\s*section_(.+)$")
    patt[format + 'SubSection'] = re.compile("^\s*([A-Z_]+)\:")

  elif format == 'autoAssign':
    patt[format + 'specPhase'] = re.compile("phase:\s*\{(.*)\}\s*\{\s*$")
    patt[format + 'onlyCurlyBraceEnd'] = re.compile("^\}$")   
    patt[format + 'CurlyBrace'] = re.compile("\{\s*(.*)\s*\}")
    patt[format + 'seqCode1Or3LetterAndCode'] = re.compile("([A-Z][a-z]{0,2})(\d+)")
    patt[format + 'spinSystemInfo'] = re.compile(".+(\(.+\))")

  elif format == 'aqua':
    patt[format + 'Count'] = re.compile("^count (\d+) type (.+)$")   
    patt[format + 'UpperDistance'] = re.compile("^NOEUPP")
    patt[format + 'LowerDistance'] = re.compile("^NOELOW")
    patt[format + 'EndComment']    = re.compile("\#(.+)$")

  elif format == 'bruker':
    patt[format + 'StartDoubleHash'] = re.compile("^\#\#")
    patt[format + 'StartDoubleHashDollar'] = re.compile("^\#\#\$")
    patt[format + 'StartDoubleDollar'] = re.compile("^\$\$")
    patt[format + 'SharpBracketOpen'] = re.compile("^\<")
    patt[format + 'SharpBracketClose'] = re.compile("\>$")
    patt[format + 'SharpBracketEither'] = re.compile("\<|\>")
    patt[format + 'BracketsListIndicator'] = re.compile("\(\d+\.\.\d+\)")
    patt[format + 'Date'] = re.compile("2\d\d\d-\d\d-\d\d")
    patt[format + 'DigitDotDigit'] = re.compile("^\-?\d*\.?\d+$")
    patt[format + 'Dot'] = re.compile("\.")
    patt[format + 'BracketCloseNumber'] = re.compile("\)\s*\d")
    patt[format + 'FinalReturn'] = re.compile("\n$")
    patt[format + 'BracketMultiValue'] = re.compile("\((\d+)\-(\d+)\)")
    patt[format + 'InOrDecrement'] = re.compile("\s*(i|d)d(\d+)")
    patt[format + 'HashComment'] = re.compile("^\s*\#(.+)")
    patt[format + 'SemiColonComment'] = re.compile("^\s*\;(.*)")
    patt[format + 'PulseName'] = re.compile("\/([^\/]+)\"")
    patt[format + 'FnMode'] = re.compile("FnMode?\s*(.+)\s*", re.I)
    patt[format + 'EchoAntiEcho'] = re.compile("igrad|\*EA", re.I)
    patt[format + 'PathwayElements'] = re.compile("(F\d+)\s*\(([^\)]+)\)")
    patt[format + 'DimIncrement'] = re.compile("in(\d+)\s*\=\s*inf(\d+)\s*\\s*/\s*(\d+)")
    patt[format + 'phaseSensitive'] = re.compile("\;\s*phase sensitive")
    patt[format + 'constantTime'] = re.compile("constant time")
    patt[format + 'semiconstantTime'] = re.compile("semi-constant time")
    patt[format + 'tSearch'] = re.compile("(t\d)")
    patt[format + 'Version'] = re.compile("Version\s*(\d+\.*\d*)")

  elif format == 'charmm':

    patt[format + 'NumberAtoms'] = re.compile("^\s*(\d+)\s*$")
    patt[format + 'AtomLine'] = re.compile("^\s*\d+\s+\d+\s+[A-Za-z]+\s+")

  # This is for CNS/xplor
  elif format == 'cns':
  
    patt[format + 'DistancePeakInfoLine'] = re.compile("peak",re.IGNORECASE)
    patt[format + 'MultiSign'] = re.compile("[\%\#\*\+]")
    patt[format + 'RestrNum'] = re.compile("\{\s*(\-?\d+)\s*\}")
    patt[format + 'Assign'] = re.compile("assi",re.IGNORECASE)
    patt[format + 'AssignOr'] = re.compile("or",re.IGNORECASE)
    patt[format + 'ChemShiftFormat'] = re.compile("attr\s+store",re.IGNORECASE)
    patt[format + 'ChemShiftStore'] = re.compile("do.+store\d+\s*\=\s*(\-?\d*\.?\d*)\s*\)",re.IGNORECASE)
    patt[format + 'ChainCode'] = re.compile("segid\s+(\"([A-Za-z0-9 ]+)\"|([A-Za-z0-9]+))\s*",re.IGNORECASE)
    patt[format + 'Class'] = re.compile("class\s+",re.IGNORECASE)
    patt[format + 'SeqCode'] = re.compile("resid?u?e?\s+(\-?\d+[a-zA-Z]?)\s*",re.IGNORECASE)
    patt[format + 'AtomName'] = re.compile("name\s+([A-Z0-9\%\#\*\+]+\'?)",re.IGNORECASE)
    patt[format + 'RestrDistances'] = re.compile("([\d\.]+)\s+(-?[\d\.]+)\s+(-?[\d\.?]+)")
    patt[format + 'RestrAngles'] = re.compile("(\d+\.?\d*)\s+(-?\+?\d+\.?\d*)\s+(\+?\d+\.?\d*)\s+(\d)")
    patt[format + 'RestrCoupling'] = re.compile("(\d+\.?\d*)\s+(\d+\.?\d*)")
    patt[format + 'RestrCsa'] = re.compile("(-?\d+\.?\d*)\s+(\d+\.?\d*)\s*(\d+\.?\d*)?")
    patt[format + 'RestrRdc'] = re.compile("(-?\d+\.?\d*)\s+(\d+\.?\d*)\s*(\d+\.?\d*)?")
    patt[format + 'RestrInnerOr'] = re.compile("\s*or",re.IGNORECASE)
    patt[format + 'InnerElementPatt'] = re.compile("\(([^\)\(]+)\)",re.M)
    patt[format + 'LongCommentStart'] = re.compile("\{")
    patt[format + 'LongCommentEnd'] = re.compile("\}")

  elif format == 'csi':
  
    patt[format + 'Comment'] = re.compile("^\s*\>")

  elif format in ['dyana','cyana']:
  
    patt[format + 'CoordinateInfoLine'] = re.compile("\s*\d+\s+[A-Z0-9]+\s+\d+\s+")
    patt[format + 'CoordinateAtomLine'] = re.compile("^ATOM|^HETATM")
    patt[format + 'NewModel'] = re.compile("^MODEL\s+(\d+)")

  elif format == 'mars':
    
    patt[format + 'AtomNameHeader'] = re.compile("^\s*([\sNCHABO\-1])+\s*$")
    patt[format + 'AtomInfo'] = re.compile("([A-Z]+)(\-\d)?")

  elif format == 'mol':

    patt[format + 'Counts'] = re.compile("^([0-9 ][0-9 ][0-9]){6}")
    patt[format + 'Atoms'] = re.compile("^([0-9\- ][0-9\- ][0-9\- ][0-9\- ][0-9]\.[0-9][0-9 ][0-9 ][0-9 ]){3}")
    patt[format + 'Bonds'] = re.compile("^([0-9 ][0-9 ][0-9]){4}([0-9 ][0-9 ][0-9 ])([0-9 ][0-9 ][0-9])")

  elif format == 'mol2':
    
    patt[format + 'TriposTag'] = re.compile("\@\<TRIPOS\>(.+)")

  elif format == 'monte':

    patt[format + 'Comment'] = re.compile("^\s*(\#\#|\%\%)")
    patt[format + 'Assignment'] = re.compile("([A-Za-z]+)?([0-9]+|\?)?")
    patt[format + 'AtomInfo'] = re.compile("([A-Za-z0-9]+)(\(.+\)|\-1)?")

  elif format in ['nmrDraw','talos']:
  
    patt[format + 'Remark'] = re.compile("^REMARK")
    patt[format + 'Dataline'] = re.compile("^DATA") 
    patt[format + 'Vars'] = re.compile("^VARS")
    patt[format + 'Format'] = re.compile("^FORMAT")
    
  elif format == 'nmrView':

    patt[format + 'DigitSpace'] = re.compile("^\d+\s+")
    patt[format + 'CurlyBrace'] = re.compile("\{([^{}]*)\}")
    patt[format + 'CurlyBraceStart'] = re.compile("\{")    
    patt[format + 'CurlyBraceEnd'] = re.compile("\}\s+")    
    patt[format + 'NumbersNoBrace'] = re.compile("^(\d+\.\d+\s*){2}")

  elif format == 'nmrStar':

    patt[format + 'EndSaveTag'] = re.compile("save_$")

  elif format == 'pdb':

    patt[format + 'NewModel'] = re.compile("^MODEL\s+(\d+)")
    patt[format + 'AllAtom'] = re.compile("^ATOM|^HETATM")
    patt[format + 'HetAtom'] = re.compile("^HETATM")
    patt[format + 'Header'] = re.compile("^HEADER")
    patt[format + 'Title'] = re.compile("^TITLE")
    patt[format + 'Remark4'] = re.compile("^REMARK   4 ([a-zA-Z0-9]{4}) COMPLIES WITH FORMAT V.\s*(\d+\.\d+)\s*\,")
    patt[format + 'Compound'] = re.compile("^COMPND\s+\d*\s+")
    patt[format + 'DbReference'] = re.compile("^DBREF")
    patt[format + 'SequenceChange'] = re.compile("^SEQADV")
    patt[format + 'Sequence'] = re.compile("^SEQRES")
    patt[format + 'Source'] = re.compile("^SOURCE\s+\d*\s+(.+)")
    patt[format + 'Keywds'] = re.compile("^KEYWDS\s+\d*\s+(.+)")
    patt[format + 'ExpData'] = re.compile("^EXPDATA\s+\d*\s+(.+)")
    patt[format + 'Authors'] = re.compile("^AUTHOR\s+\d*\s+(.+)")
    patt[format + 'Journal'] = re.compile("^JRNL\s+(AUTH|TITL|REF|REFN|PUBL|EDIT)\s+\d*\s+(.+)")
    patt[format + 'Reference'] = re.compile("^REFERENCE\s+(\d+)")
    patt[format + 'ReferenceJournal'] = re.compile("\s*(AUTH|TITL|REF|REFN|PUBL|EDIT)\s+\d*\s+(.+)")
    patt[format + 'Remarks'] = re.compile("^REMARK\s+(\d+)\s+(.+)")
    patt[format + 'HetGroup'] = re.compile("^HET\s+")
    patt[format + 'HetName'] = re.compile("^HETNAM")
    patt[format + 'HetSynonym'] = re.compile("^HETSYN")
    patt[format + 'HetFormula'] = re.compile("^FORMUL")
    patt[format + 'Bonds'] = re.compile("^CONECT")
    patt[format + 'SsBond'] = re.compile("^SSBOND")
    patt[format + 'Link'] = re.compile("^LINK")
    patt[format + 'SecStruc'] = re.compile("^(HELIX|TURN|SHEET)")
    patt[format + 'Termination'] = re.compile("^TER ")

  elif format == 'pipp':
    patt[format + '?_AXIS'] = re.compile("^(.+)_AXIS")
    patt[format + 'Shift'] = re.compile("^\s*(.+)\s+([0-9]*\.?[0-9]+)\s+\((.+)\)\s*$")
    patt[format + 'ShiftNoAss'] = re.compile("^\s*(.+)\s+([0-9]*\.?[0-9]+)\s*$")

  elif format == 'pistachio':
    patt[format + 'Comment'] = re.compile("^\s*\%.+")
  
  elif format == 'sparky':
    patt[format + 'SharpBracketBetween'] = re.compile("^\<(.+)\>$")
    patt[format + 'LabelCodeName'] = re.compile("([A-Z]?)((\d+\,?)+)(.+)")
    patt[format + 'BracketBetween'] = re.compile("\((.+)\)")

  # Addition Maxim Mayzel, Gothenburg
  elif format == 'targetedAcquisition':
    patt[format + 'seqCode1Or1LetterAndCode'] = re.compile("([A-Z])(\d+)")
    #patt[format + 'spinSystemInfo'] = re.compile(".+(\(.+\))")
    patt[format + 'figOfMerit'] = re.compile("([B|G|M])\s*(\d+\.*\d*)")

  elif format == 'xeasy':
    patt[format + 'IName'] = re.compile("^\#\s*INAME\s+(\d)\s*(.+)$")
    patt[format + 'CyanaFormat'] = re.compile("^\#\s*CYANAFORMAT\s+(.+)\s*$")
    patt[format + 'PeakInfo'] = re.compile("^\s*([^#]+)\s*\#?.*$")


  """
  
  #
  # TODO: WHERE ARE THESE USED!!?!
  #
  patt['infoDirs'] = re.compile("^info\..+")
  patt['projectDirs'] = re.compile("^project\..+")
  patt['varFiles'] = re.compile("^vars\..+")
  patt['nmrStarFiles'] = re.compile("^bmr(\d+)\.str")
   # patt[format + 'DMXTypes'] = re.compile("^DMX|DRX|Avance$")
   # patt[format + 'AllTypes'] = re.compile("^DMX|DRX|Avance|AM|AMX$")

  # This is for nmrPipe
  patt['var2pipe'] = re.compile("var2pipe$")
  patt['bruk2pipe'] = re.compile("bruk2pipe$")
  patt['pipe'] = re.compile("\|")
  patt['backslash'] = re.compile('\\\\')
  patt['dashstart'] = re.compile("^\-")
  patt['x'] = re.compile("^x")
  patt['y'] = re.compile("^y")
  patt['z'] = re.compile("^z")
  patt['a'] = re.compile("^a[^(q2d)]")

  # This is for dataNavigator
  patt['pipe2Dproc'] = re.compile("^test\.ft$")
  patt['pipe3Dproc'] = re.compile("^test(\d+)\.ft$")

  # These are for nmrPipe and Azara exec... scripts.
  patt['pipeConv'] = re.compile("^autoconv\.([HCN]+)\.com$")
  patt['pipeProc'] = re.compile("^autoproc\.([HCN]+)\.com$")

  # These are for DataManager
  patt['Varian'] = re.compile("procpar$")
  patt['Bruker'] = re.compile("acqu\d?s?$")

  # For converters, exportNmrProcPars
  patt['sensitivityEnhanced'] = re.compile("(echoAntiEcho|ranceKay) dim (\d)")
  """
  return patt

patt = getRegularExpressions()

def getSeqAndInsertCode(seqCode):

  seqInsertCode = defaultSeqInsertCode
  
  if seqCode != None:
    try:
      seqCode = int(seqCode)
    except:
      searchObj = patt['seqInsertCode'].search(str(seqCode))
      if searchObj:
        try:
          seqCode = int(searchObj.group(2))       
          if searchObj.group(1) or searchObj.group(3):
            seqInsertCode = searchObj.group(1) + searchObj.group(3)

        except:
          seqCode = None
      else:
        seqCode = None
  
  return (seqCode,seqInsertCode)
  
def standardNucleusName(name):

  if (not name):
    name = '1H'
  elif ((name[0].upper() == 'H') or (name.upper() == '1H')):
    name = '1H'
  elif ((name[0].upper() == 'C') or (name.upper() == '13C')):
    name = '13C'
  elif ((name[0].upper() == 'N') or (name.upper() == '15N')):
    name = '15N'
  elif ((name[0].upper() == 'P') or (name.upper() == '31P')):
    name = '31P'
  else:
    name = '1H'

  return name

