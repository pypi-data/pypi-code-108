


import os
import sys
import typing

import jk_terminal_essentials

from .ArgOption import ArgOption
from .ParsedArgs import ParsedArgs
from .ArgsOptionDataDict import ArgsOptionDataDict
from .ArgUtils import ArgUtils
from .AvailableLicenseList import AvailableLicenseList
from .ArgCommand import ArgCommand
from .textmodel.VisSettings import VisSettings
from .textprimitives import *
from .textmodel import *
from .BashCompletionLocal import BashCompletionLocal




"""
BASH_COMPLETION_DIR_CANDIDATES = [
	"~/.config/bash_completion.d/",
	"~/.bash_completion.d/",
	"~/.local/share/bash-completion/",		# compare: https://github.com/scop/bash-completion, "Q. Where should I install my own local completions?"
]
"""



class ArgsParser(object):

	################################################################################################################################
	## Nested Helper Classes
	################################################################################################################################

	"""
	class _TextTableRow2(object):

		def __init__(self, col1, col2):
			self.col1 = col1
			self.col2 = col2
		#

	#
	"""

	"""
	class _TextTableRow3(object):

		def __init__(self, col1, col2, col3):
			self.col1 = col1
			self.col2 = col2
			self.col3 = col3
		#

	#
	"""

	"""
	class _TextTable2(object):

		def __init__(self):
			self.__rows = []
		#

		def addRow(self, col1, col2):
			assert isinstance(col1, str)
			assert isinstance(col2, str)

			self.__rows.append(ArgsParser._TextTableRow2(col1, col2))
		#

		def print(self, leftMargin, columnMargin, maxWidth, outputBuffer):
			assert isinstance(leftMargin, int)
			assert isinstance(columnMargin, int)
			assert isinstance(maxWidth, int)
			assert isinstance(outputBuffer, list)

			col1size = 0
			for textTableRow in self.__rows:
				if len(textTableRow.col1) > col1size:
					col1size = len(textTableRow.col1)
			col2pos = leftMargin + col1size + columnMargin
			col2size = maxWidth - 1 - col2pos

			for textTableRow in self.__rows:
				sb = ""
				col2Wrapped = ArgUtils.wrapWords(textTableRow.col2, col2size)
				for i in range(0, leftMargin):
					sb += ' '
				sb += textTableRow.col1
				while len(sb) < col2pos:
					sb += ' '
				sb += col2Wrapped[0]
				outputBuffer.append(sb)

				if len(col2Wrapped) > 1:
					sb = ""
					while len(sb) < col2pos:
						sb += ' '

					for j in range(1, len(col2Wrapped)):
						outputBuffer.append(sb + col2Wrapped[j])
		#

	#
	"""

	"""
	class _TextTable3(object):

		def __init__(self):
			self.__rows = []
		#

		def addRow(self, col1, col2, col3):
			assert isinstance(col1, str)
			assert isinstance(col2, str)
			assert isinstance(col3, str)

			self.__rows.append(ArgsParser._TextTableRow3(col1, col2, col3))
		#

		def print(self, leftMargin, columnMargin, maxWidth, outputBuffer):
			assert isinstance(leftMargin, int)
			assert isinstance(columnMargin, int)
			assert isinstance(maxWidth, int)
			assert isinstance(outputBuffer, list)

			col1size = 0
			col2size = 0
			for textTableRow in self.__rows:
				if len(textTableRow.col1) > col1size:
					col1size = len(textTableRow.col1)
				if len(textTableRow.col2) > col2size:
					col2size = len(textTableRow.col2)
			col2pos = leftMargin + col1size + columnMargin
			col3pos = col2pos + col2size + columnMargin
			col3size = maxWidth - 1 - col3pos

			for textTableRow in self.__rows:
				sb = ""
				col3Wrapped = ArgUtils.wrapWords(textTableRow.col3, col3size)
				for i in range(0, leftMargin):
					sb += ' '
				sb += textTableRow.col1
				while len(sb) < col2pos:
					sb += ' '
				sb += textTableRow.col2
				while len(sb) < col3pos:
					sb += ' '
				sb += col3Wrapped[0]
				outputBuffer.append(sb)

				if len(col3Wrapped) > 1:
					sb = ""
					while len(sb) < col3pos:
						sb += ' '

					for j in range(1, len(col3Wrapped)):
						outputBuffer.append(sb + col3Wrapped[j])
		#

	#
	"""

	################################################################################################################################
	## Constructor
	################################################################################################################################

	#
	# Constructor.
	#
	# @param		str appName						This is the command the application can be executed with. This typically is the file name.
	# @param		str shortAppDescription			A short textual description what this application does.
	#
	def __init__(self, appName:str, shortAppDescription:str):
		assert isinstance(appName, str)
		assert isinstance(shortAppDescription, str)

		# defaults

		self.titleCommandsStd = "Commands"
		self.titleCommandsExtra = "Extra Commands"

		# variables

		self.__commands = {}
		self.__commandsExtra = {}
		self.__longArgs = {}
		self.__shortArgs = {}
		self.__options = []
		self.__authorsList = []				# stores tuples of `(author-name, author-email, author-description)`
		self.__synopsisList = []			# stores strings that hold the synopsis
		self.__returnCodesList = []			# stores tuples of `(return-code, description)`
		self.__appName = appName
		self.__shortAppDescription = shortAppDescription
		self.__appName = appName
		self.__optionDataDefaults = ArgsOptionDataDict()
		self.__licenseTextLines = None
		self.__descriptionChapters = []		# stores TSection objects
		self.__extraHeadChapters = []		# stores TSection objects
		self.__extraMiddleChapters = []		# stores TSection objects
		self.__extraEndChapters = []		# stores TSection objects

		self.__visSettings = VisSettings()
	#

	################################################################################################################################
	## Public Properties
	################################################################################################################################

	@property
	def visSettings(self) -> VisSettings:
		return self.__visSettings
	#

	@property
	def optionDataDefaults(self) -> ArgsOptionDataDict:
		return self.__optionDataDefaults
	#

	@property
	def appName(self) -> str:
		return self.__appName
	#

	@property
	def shortAppDescription(self) -> str:
		return self.__shortAppDescription
	#

	@property
	def allOptionNames(self) -> list:
		allOptions = []
		for o in self.__options:
			if o.shortName:
				allOptions.append("-" + o.shortName)
			if o.longName:
				allOptions.append("--" + o.longName)
		return allOptions
	#

	@property
	def allCommandNames(self) -> list:
		return list(self.__commands.keys()) + list(self.__commandsExtra.keys())
	#

	################################################################################################################################
	## Helper Methods
	################################################################################################################################

	def __windowWidth(self):
		try:
			sz = os.get_terminal_size()
			return min(sz.columns - 1, 140)
		except:
			return 160
	#

	def __eatLongOption(self, optionName, args, argsPos, ret):
		assert isinstance(optionName, str)
		assert isinstance(args, list)
		assert isinstance(argsPos, int)
		assert isinstance(ret, ParsedArgs)

		o = self.__longArgs.get(optionName, None)
		if o is None:
			raise Exception("No such option: " + optionName)

		if argsPos + len(o.optionParameters) > len(args):
			raise Exception("Option " + o.longName + " expects " + str(len(o.optionParameters)) + " arguments!")

		optionArgs = []
		for i in range(0, len(o.optionParameters)):
			optionArgs.append(o.optionParameters[i].parse(args[argsPos + i]))
		argsPos += len(o.optionParameters)

		o._invokeOpt(optionArgs, ret)

		return (o, argsPos)
	#

	def __eatShortOption(self, optionName, args, argsPos, ret):
		assert isinstance(optionName, str)
		assert isinstance(args, list)
		assert isinstance(argsPos, int)
		assert isinstance(ret, ParsedArgs)

		o = self.__shortArgs.get(optionName, None)
		if o is None:
			raise Exception("No such option: " + optionName)

		if argsPos + len(o.optionParameters) > len(args):
			raise Exception("Option " + o.longName + " expects " + str(len(o.optionParameters)) + " arguments!")

		optionArgs = []
		for i in range(0, len(o.optionParameters)):
			optionArgs.append(o.optionParameters[i].parse(args[argsPos + i]))
		argsPos += len(o.optionParameters)

		o._invokeOpt(optionArgs, ret)

		return (o, argsPos)
	#

	"""
	def __eatShortOption(self, optionName, ret):
		assert isinstance(optionName, str)
		assert isinstance(ret, ParsedArgs)

		o = self.__shortArgs.get(optionName, None)
		if o is None:
			raise Exception("No such option: " + optionName)

		o._invokeOpt(None, ret)

		return o
	#
	"""

	def __convertTSection(self, v:VisSettings, chapter:TSection) -> ITextBlock:
		sec = TextBlockSequence(0, 0)

		sec.addBlock(TextBlock(v.title2_indent, chapter.title, v.title2_fgColor))
		sec.addBlock(TextEmpty(v.title2_paddingAfterTitle))

		for block in chapter.contentBlocks:
			sec.addBlock(TextBlock(v.section2_indent, block.text))
			sec.addBlock(TextEmpty(v.section2_gapBetweenSections))

		return sec
	#

	def __appendTitle1WithGap(self, v:VisSettings, title:str, ret:TextBlockSequence):
		ret.addBlock(TextBlock(v.title1_indent, v.title1_preprocessor(title) if v.title1_preprocessor else title, v.title1_fgColor))
		ret.addBlock(TextEmpty(v.title1_paddingAfterTitle))
	#

	def _txtCreateName(self, v:VisSettings) -> ITextBlock:
		return TextBlock(0, self.__appName + " - " + self.__shortAppDescription, v.appName_fgColor)
	#

	def _txtCreateSynopsis(self, v:VisSettings) -> ITextBlock:
		if not self.__synopsisList:
			return None

		ret = TextBlockSequence(0, 0)

		# title
		self.__appendTitle1WithGap(v, "Synopsis", ret)

		# content
		for synopsisText in self.__synopsisList:
			ret.addBlock(TextBlock(v.section1_indent, synopsisText, None))

		return ret
	#

	def _txtCreateOptions(self, v:VisSettings) -> ITextBlock:
		if not self.__options:
			return None

		ret = TextBlockSequence(0, 0)

		# title
		self.__appendTitle1WithGap(v, "Options", ret)

		# content
		grid = TextGridBlock(v.section1_indent, v.options_tableRowGap, v.options_tableColumnsGap, columnLayouterL2R)
		ret.addBlock(grid)
		for o in self.__options:
			if o.shortName is not None:
				sShortName = "-" + o.shortName
				for op in o.optionParameters:
					sShortName += " " + op.displayName
			else:
				sShortName = ""

			if o.longName is not None:
				sLongName = "--" + o.longName
				for op in o.optionParameters:
					sLongName += " " + op.displayName
			else:
				sLongName = ""

			grid.addRow([
				TextBlock(0, sShortName, v.options_fgColor),
				TextBlock(0, sLongName, v.options_fgColor),
				TextBlock(0, o.description),
			])

		return ret
	#

	def _txtCreateAuthors(self, v:VisSettings) -> ITextBlock:
		if not self.__authorsList:
			return None

		ret = TextBlockSequence(0, 0)

		# title
		self.__appendTitle1WithGap(v, "Authors", ret)

		# content
		for (name, email, description) in self.__authorsList:
			s = name
			if email:
				s += " <" + email + ">"
			if description:
				s += " - " + description
			ret.addBlock(TextBlock(v.section1_indent, s))

		return ret
	#

	def _txtReturnCodes(self, v:VisSettings) -> ITextBlock:
		if not self.__returnCodesList:
			return None

		ret = TextBlockSequence(0, 0)

		# title
		self.__appendTitle1WithGap(v, "Program Exit Codes", ret)

		# content
		grid = TextGridBlock(v.section1_indent, v.exitCodes_tableRowGap, v.exitCodes_tableColumnsGap, columnLayouterL2R)
		ret.addBlock(grid)
		for (retCode, retCodeDescription) in self.__returnCodesList:
			grid.addRow([
				TextBlock(0, str(retCode), v.exitCodes_fgColor),
				TextBlock(0, retCodeDescription),
			])

		return ret
	#

	def _txtCreateCommands(self, v:VisSettings) -> ITextBlock:
		if not self.__commands:
			return None

		ret = TextBlockSequence(0, 0)

		# title
		self.__appendTitle1WithGap(v, self.titleCommandsStd, ret)

		# content
		grid = TextGridBlock(v.section1_indent, v.commands_tableRowGap, v.commands_tableColumnsGap, columnLayouterL2R)
		ret.addBlock(grid)
		keys = list(self.__commands.keys())
		keys.sort()
		for key in keys:
			cmd = self.__commands[key]

			if cmd.isHidden:
				continue

			s = cmd.name
			for op in cmd.optionParameters:
				s += " " + op.displayName

			grid.addRow([
				TextBlock(0, s, v.commands_fgColor),
				TextBlock(0, cmd.description),
			])

		return ret
	#

	def _txtCreateExtraCommands(self, v:VisSettings) -> ITextBlock:
		if not self.__commandsExtra:
			return None

		ret = TextBlockSequence(0, 0)

		# title
		self.__appendTitle1WithGap(v, self.titleCommandsExtra, ret)

		# content
		grid = TextGridBlock(v.section1_indent, v.commands_tableRowGap, v.commands_tableColumnsGap, columnLayouterL2R)
		ret.addBlock(grid)
		keys = list(self.__commandsExtra.keys())
		keys.sort()
		for key in keys:
			cmd = self.__commandsExtra[key]
			s = cmd.name
			for op in cmd.optionParameters:
				s += " " + op.displayName
			grid.addRow([
				TextBlock(0, s, v.commands_fgColor),
				TextBlock(0, cmd.description),
			])

		return ret
	#

	def _txtCreateLicense(self, v:VisSettings) -> ITextBlock:
		if not self.__licenseTextLines:
			return None

		ret = TextBlockSequence(0, 0)

		# title
		self.__appendTitle1WithGap(v, "License", ret)

		# content
		for line in self.__licenseTextLines:
			ret.addBlock(TextBlock(v.section1_indent, line))
			ret.addBlock(TextEmpty(v.section2_gapBetweenSections))

		return ret
	#

	def _txtCreateDescription(self, v:VisSettings) -> ITextBlock:
		if not self.__descriptionChapters:
			return None

		ret = TextBlockSequence(0, 0)

		# title
		self.__appendTitle1WithGap(v, "Description", ret)

		# content
		for chapter in self.__descriptionChapters:
			if isinstance(chapter, TBlock):
				ret.addBlock(TextBlock(v.section1_indent, chapter.text))
				ret.addBlock(TextEmpty(v.section2_gapBetweenSections))
			else:
				assert isinstance(chapter, TSection)
				ret.addBlock(self.__convertTSection(v, chapter))

		return ret
	#

	def _txtCreateExtraHead(self, v:VisSettings) -> ITextBlock:
		# TODO: methods are almost identical: _txtCreateExtraHead(), _txtCreateExtraMiddle() and _txtCreateExtraHead()

		if not self.__extraHeadChapters:
			return None

		ret = TextBlockSequence(0, 0)

		for chapter in self.__extraHeadChapters:

			# title
			self.__appendTitle1WithGap(v, chapter.title, ret)

			# content
			bNeedGap = False
			for sub in chapter.contentBlocks:
				if bNeedGap:
					ret.addBlock(TextEmpty(v.section2_gapBetweenSections))
					bNeedGap = False
				if isinstance(sub, TSection):
					ret.addBlock(self.__convertTSection(v, sub))
				else:
					ret.addBlock(TextBlock(v.section1_indent, sub.text))
					bNeedGap = True

		return ret
	#

	def _txtCreateExtraMiddle(self, v:VisSettings) -> ITextBlock:
		# TODO: methods are almost identical: _txtCreateExtraHead(), _txtCreateExtraMiddle() and _txtCreateExtraHead()

		if not self.__extraMiddleChapters:
			return None

		ret = TextBlockSequence(0, 0)

		for chapter in self.__extraMiddleChapters:

			# title
			self.__appendTitle1WithGap(v, chapter.title, ret)

			# content
			bNeedGap = False
			for sub in chapter.contentBlocks:
				if bNeedGap:
					ret.addBlock(TextEmpty(v.section2_gapBetweenSections))
					bNeedGap = False
				if isinstance(sub, TSection):
					ret.addBlock(self.__convertTSection(v, sub))
				else:
					ret.addBlock(TextBlock(v.section1_indent, sub.text))
					bNeedGap = True

		return ret
	#

	def _txtCreateExtraEnd(self, v:VisSettings) -> ITextBlock:
		# TODO: methods are almost identical: _txtCreateExtraHead(), _txtCreateExtraMiddle() and _txtCreateExtraHead()

		if not self.__extraEndChapters:
			return None

		ret = TextBlockSequence(0, 0)

		for chapter in self.__extraEndChapters:

			# title
			self.__appendTitle1WithGap(v, chapter.title, ret)

			# content
			bNeedGap = False
			for sub in chapter.contentBlocks:
				if bNeedGap:
					ret.addBlock(TextEmpty(v.section2_gapBetweenSections))
					bNeedGap = False
				if isinstance(sub, TSection):
					ret.addBlock(self.__convertTSection(v, sub))
				else:
					ret.addBlock(TextBlock(v.section1_indent, sub.text))
					bNeedGap = True

		return ret
	#

	################################################################################################################################
	## Public Methods
	################################################################################################################################

	def hasCommand(self, name:str) -> bool:
		return (name in self.__commands) or (name in self.__commandsExtra)
	#

	def createCommand(self, name:str, description:str, bHidden:bool = False) -> ArgCommand:
		assert isinstance(name, str)
		assert name
		assert isinstance(description, str)
		assert description
		assert isinstance(bHidden, bool)

		o = ArgCommand(name, description, bHidden)
		if (o.name in self.__commands) or o.name in self.__commandsExtra:
			raise Exception("A command named '" + o.name + "' already exists!")
		self.__commands[o.name] = o

		return o
	#

	def createExtraCommand(self, name:str, description:str) -> ArgCommand:
		assert isinstance(name, str)
		assert name
		assert isinstance(description, str)
		assert description

		o = ArgCommand(name, description)
		if (o.name in self.__commands) or o.name in self.__commandsExtra:
			raise Exception("A command named '" + o.name + "' already exists!")
		self.__commandsExtra[o.name] = o

		return o
	#

	def createOption(self, shortName, longName, description) -> ArgOption:
		if shortName is not None:
			assert isinstance(shortName, str)
			assert len(shortName) == 1

		if longName is not None:
			assert isinstance(longName, str)

		assert isinstance(description, str)

		if (shortName is None) and (longName is None):
			raise Exception("Arguments need at least a long or a short name!")

		o = ArgOption(shortName, longName, description)

		if shortName is not None:
			if o.shortName in self.__shortArgs:
				raise Exception("Duplicate short argument: '-" + o.shortName + "'")
			self.__shortArgs[o.shortName] = o

		if longName is not None:
			if o.longName in self.__longArgs:
				raise Exception("Duplicate long argument: '--" + o.longName + "'")
			self.__longArgs[o.longName] = o

		self.__options.append(o)

		return o
	#

	def showHelp(self, bColor:bool = None):
		print()
		for line in self.buildHelpText(bColor = bColor):
			print(line)
		print()
	#

	#
	# Add information about an author of this software.
	#
	def createAuthor(self, name:str, email:str = None, description:str = None):
		assert isinstance(name, str)
		assert name
		if email is not None:
			assert isinstance(email, str)
			assert email

		self.__authorsList.append((name, email, description))

		return self
	#

	#
	# Create synopsis information
	#
	def createSynopsis(self, synopsis:str):
		assert isinstance(synopsis, str)
		assert synopsis

		self.__synopsisList.append(synopsis)

		return self
	#

	#
	# Add a return code.
	#
	# @param		int returnCode		The return code (= program exit status code)
	# @param		str description		The description for this return code
	#
	def createReturnCode(self, returnCode:int, description:str):
		assert isinstance(returnCode, int)
		assert isinstance(description, str)

		self.__returnCodesList.append((returnCode, description))

		return self
	#

	def setLicense(self, licenseID, **kwargs):
		assert isinstance(licenseID, str)

		availableLicenseList = AvailableLicenseList()
		self.__licenseTextLines = availableLicenseList.getText(licenseID, **kwargs)
		if self.__licenseTextLines is None:
			raise Exception("No such license: " + licenseID)

		return self
	#

	def addDescriptionChapter(self, chapterName:typing.Union[str,None], paragraphs:typing.Sequence = None) -> TSection:
		if chapterName is None:
			for p in paragraphs:
				self.__descriptionChapters.append(TBlock(p))
			sec = None

		else:
			assert isinstance(chapterName, str)
			if isinstance(paragraphs, str):
				sec = TSection(chapterName, [ paragraphs ])
			else:
				sec = TSection(chapterName, paragraphs)
			self.__descriptionChapters.append(sec)

		return sec
	#

	def addExtraChapterHead(self, section:TSection):
		assert isinstance(section, TSection)
		self.__extraHeadChapters.append(section)
		return self
	#

	def addExtraChapterMiddle(self, section:TSection):
		assert isinstance(section, TSection)
		self.__extraMiddleChapters.append(section)
		return self
	#

	def addExtraChapterEnd(self, section:TSection):
		assert isinstance(section, TSection)
		self.__extraEndChapters.append(section)
		return self
	#

	def buildHelpText(self, bColor:bool = None) -> list:
		if bColor is None:
			bColor = jk_terminal_essentials.checkTerminalSupportsColors()

		v = self.__visSettings
		doc = TextBlockSequence(0, v.section1_gapBetweenSections)

		# ----

		for provider in [
				self._txtCreateName,
				self._txtCreateSynopsis,
				self._txtCreateExtraHead,
				self._txtCreateDescription,
				self._txtCreateExtraMiddle,
				self._txtCreateOptions,
				self._txtCreateCommands,
				self._txtCreateExtraCommands,
				self._txtReturnCodes,
				self._txtCreateExtraEnd,
				self._txtCreateAuthors,
				self._txtCreateLicense,
			]:

			x = provider(v)
			if x:
				doc.addBlock(x)

		# ----

		doc.layout(self.__windowWidth())
		return [ str(x) for x in doc.getLines(bColor) ]
	#

	def parse(self, args = None):
		if args is None:
			args = list(sys.argv)
			args = args[1:]
		else:
			assert isinstance(args, list)
			for a in args:
				assert isinstance(a, str)

		# ----

		ret = ParsedArgs(self.__commands)
		for key in self.__optionDataDefaults:
			ret.optionData[key] = self.__optionDataDefaults[key]

		optionsRequired = []	# List<ArgOption>()
		for ao in self.__options:
			if ao.isRequired:
				optionsRequired.append(ao)

		# check options
		argsPos = 0
		while argsPos < len(args):
			#print("next: " + str(argsPos) + ", " + args[argsPos])
			current = args[argsPos]
			argsPos += 1

			if len(current) >= 2:
				if current[0] == '-':
					if current[1] == '-':
						# long option
						#print("current argsPos: " + str(argsPos))
						(op, argsPos) = self.__eatLongOption(current[2:], args, argsPos, ret)
						#print("new argsPos: " + str(argsPos))
						if op in optionsRequired:
							optionsRequired.remove(op)
						if ret.terminate:
							break
					else:
						# short option
						for i in range(1, len(current)):
							(op, argsPos) = self.__eatShortOption(current[i], args, argsPos, ret)
							if op in optionsRequired:
								optionsRequired.remove(op)
							if ret.terminate:
								break
					continue

			argsPos -= 1
			break

		if ret.terminate:
			return None

		if len(optionsRequired) > 0:
			raise Exception("Option required: " + str(optionsRequired[0]))

		ret.programArgs = args[argsPos:]

		return ret
	#

	"""
	#
	# @param	bool bWithLocal		If <c>True</c> a complete command is added for running the current script from "./" as well.
	#								This is not needed for system wide installations.
	#
	def createBashCompletionFileText(self, bWithLocal:bool = False):
		allOptions = []
		for o in self.__options:
			if o.shortName:
				allOptions.append("-" + o.shortName)
			if o.longName:
				allOptions.append("--" + o.longName)

		allCommands = list(self.__commands.keys()) + list(self.__commandsExtra.keys())

		lines = [
			"_" + self.__appName + "_()",
			"{",
			"	local cur prev opts",
			"	COMPREPLY=()",
			"	cur=\"${COMP_WORDS[COMP_CWORD]}\"",
			"	prev=\"${COMP_WORDS[COMP_CWORD-1]}\"",
			"	opts=\"" + " ".join(allOptions) + "\"",
			"	cmds=\"" + " ".join(allCommands) + "\"",
			"",
			"	if [[ ${cur} == -* ]] ; then",
			"		COMPREPLY=( $(compgen -W \"${opts}\" -- ${cur}) )",
			"		return 0",
			"	else",
			"		COMPREPLY=( $(compgen -W \"${cmds}\" -- ${cur}) )",
			"		return 0",
			"	fi",
			"}",
			"complete -F _" + self.__appName + "_ " + self.__appName,
		]
		if bWithLocal:
			lines.append("complete -F _" + self.__appName + "_ ./" + self.__appName)
		lines.append("")

		return "\n".join(lines)
	#

	#
	# This method generates the local bash completion file path. Or throws an exception if this feature is not configured or not supported.
	#
	def generateLocalBashCompletionFilePath(self, dirCandidates:list=None) -> str:
		if os.name == 'nt':
			raise Exception("Sorry, the bash completion feature is only supported for non-Windows operating systems.")

		# ----

		if dirCandidates is None:
			dirCandidates = BASH_COMPLETION_DIR_CANDIDATES
		else:
			for dc in dirCandidates:
				assert isinstance(dc, str)

		# ----

		homeDir = pwd.getpwuid(os.getuid()).pw_dir
		assert isinstance(homeDir, str)
		assert os.path.isdir(homeDir)

		installDirPath = None
		for dc in dirCandidates:
			if dc.startswith("~/"):
				p = os.path.join(homeDir, dc[2:])
				if os.path.isdir(p):
					installDirPath = p
					break

		if not installDirPath:
			raise Exception("No installation path exists! (You might want to create: '{}')".format(BASH_COMPLETION_DIR_CANDIDATES[0]))

		# ----

		return os.path.join(installDirPath, self.__appName.replace(".", "_"))
	#

	def installLocalBashCompletionFile(self, dirCandidates:list=None, printFunc=None, bQuiet:bool = True, bRaiseExceptionIfNoCompletionDirExists:bool = False) -> bool:
		if printFunc is not None:
			assert callable(printFunc)
		else:
			printFunc = print

		# ----

		if bRaiseExceptionIfNoCompletionDirExists:
			# allow raising exceptions
			installFilePath = generateLocalBashCompletionFilePath(dirCandidates)
		else:
			# no exceptions allowed
			try:
				installFilePath = generateLocalBashCompletionFilePath(dirCandidates)
			except Exception as ee:
				if not bQuiet:
					printFunc(str(ee))
				return False

		# ----

		existingCompletionFileText = None
		if os.path.isfile(installFilePath):
			with open(installFilePath, "r") as f:
				existingCompletionFileText = f.read()

		newCompletionFileText = self.createBashCompletionFileText(bWithLocal=True)
		if existingCompletionFileText != newCompletionFileText:
			if not bQuiet:
				printFunc("Now installing bash completion file: {}".format(installFilePath))

			with open(installFilePath, "w") as f:
				f.write(newCompletionFileText)

		# ----

		return True
	#
	"""

	def installLocalBashCompletion(self, absAppFilePath:str, bDebug:bool = False):
		bc = BashCompletionLocal(bDebug=bDebug)
		bc._writeDebugData("absAppFilePath =", absAppFilePath)
		bc.install(absAppFilePath, self.allOptionNames, self.allCommandNames, bQuiet=True)
	#

#




