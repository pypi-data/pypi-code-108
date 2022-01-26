




import os
if os.name != "nt":
	import pwd




BASH_COMPLETION_DIR_CANDIDATES = [
	"~/.config/bash_completion.d/",
	"~/.bash_completion.d/",
	"~/.local/share/bash-completion/",		# compare: https://github.com/scop/bash-completion, "Q. Where should I install my own local completions?"
]



_MAIN_SCRIPT_PART = """_jk_argsparsing_completion_()
{
	local cur prev opts
	COMPREPLY=()

	SEARCHCMD=${COMP_WORDS[0]}
	#echo $SEARCHCMD > foo0.txt

	absLocalDirCandidate="$(realpath $(pwd)/$SEARCHCMD)"
	#echo "${absLocalDirCandidate}" > foo1.txt

	absCallerPath=""
	if [ -f "${absLocalDirCandidate}" ]; then
		absCallerPath="${absLocalDirCandidate}"
	else
		absInstalledCandidate=$(whereis "${SEARCHCMD}" | sed -nE 's/^.*:\s(\S+).*$/\\1/p')
		#echo "${absInstalledCandidate}" > foo2.txt

		if [ -f "${absInstalledCandidate}" ]; then
			absCallerPath="${absInstalledCandidate}"
		fi
	fi
	#echo "${absCallerPath}" > foo3.txt

	if [ -z "${absCallerPath}" ]; then
		COMPREPLY=""
		return 0
	fi

	slash="/"
	temp1=${absCallerPath//$slash/_}
	dot="."
	temp1=${temp1//$dot/_}
	callerID=${temp1}.bash-completion
	callerCompletionDataFile="$(realpath ~/.config/jk_argparsing/bash_completion.d/$callerID)"
	#echo "$callerCompletionDataFile" > foo.comp.txt

	cur="${COMP_WORDS[COMP_CWORD]}"
	prev="${COMP_WORDS[COMP_CWORD-1]}"
	. "$callerCompletionDataFile"

	if [[ ${cur} == -* ]] ; then
		COMPREPLY=( $(compgen -W "${jk_argsparsing_opts}" -- ${cur}) )
		return 0
	else
		COMPREPLY=( $(compgen -W "${jk_argsparsing_cmds}" -- ${cur}) )
		return 0
	fi
}
"""




class BashCompletionLocal(object):

	################################################################################################################################
	## Constructor
	################################################################################################################################

	#
	# Constructor method.
	#
	def __init__(self, dirCandidates:str = None, bDebug:bool = False):
		if os.name == 'nt':
			raise Exception("Sorry, the bash completion feature is only supported for non-Windows operating systems.")

		# ----

		self.__bDebug = bDebug

		# ----

		if dirCandidates is None:
			dirCandidates = BASH_COMPLETION_DIR_CANDIDATES
		else:
			for x in dirCandidates:
				assert isinstance(x, str)

		self.__homeDir = pwd.getpwuid(os.getuid()).pw_dir
		assert isinstance(self.__homeDir, str)
		assert os.path.isdir(self.__homeDir)

		self.__dirCandidates = []
		for dc in dirCandidates:
			if dc.startswith("~/"):
				p = os.path.join(self.__homeDir, dc[2:])
				self.__dirCandidates.append(p)

		# ---

		self._writeDebugData("dirCandidates:", self.__dirCandidates)
	#

	################################################################################################################################
	## Public Properties
	################################################################################################################################

	################################################################################################################################
	## Helper Methods
	################################################################################################################################

	def _writeDebugData(self, *args):
		if self.__bDebug:
			if args:
				print("DEBUG:", *args)
	#

	#
	# This method generates the local bash completion file path. Or throws an exception if this feature is not configured or not supported.
	#
	def _generateBCScriptFilePath(self, absScriptFilePath:str) -> str:
		scriptFileName = os.path.basename(absScriptFilePath)
		installDirPath = os.path.join(self.__homeDir, ".config/bash_completion.d")
		return os.path.join(installDirPath, scriptFileName + ".bash-completion")
	#

	def _generateBCDataFilePath(self, absScriptFilePath:str) -> str:
		callerID = absScriptFilePath.replace("/", "_").replace(".", "_")
		absDataFilePath = os.path.join(self.__homeDir, ".config/jk_argparsing/bash_completion.d/" + callerID + ".bash-completion")
		return absDataFilePath
	#

	def _createBCScriptFileText(self, absScriptFilePath:str):
		appName = os.path.basename(absScriptFilePath)

		return _MAIN_SCRIPT_PART + "\n" \
			+ "complete -F _jk_argsparsing_completion_ " + appName + "\n" \
			+ "complete -F _jk_argsparsing_completion_ ./" + appName + "\n" \
			+ "\n"
	#

	def _createBCDataFileText(self, absScriptFilePath:str, allOptions:list, allCommands:list):
		lines = [
			"jk_argsparsing_opts=\"" + " ".join(allOptions) + "\"",
			"jk_argsparsing_cmds=\"" + " ".join(allCommands) + "\"",
			"",
		]

		return "\n".join(lines)
	#

	################################################################################################################################
	## Public Methods
	################################################################################################################################

	def install(self, absScriptFilePath:str, options:list, allCommands:list, bQuiet:bool = True, printFunc=None) -> bool:
		assert isinstance(absScriptFilePath, str)
		assert os.path.isabs(absScriptFilePath)
		assert os.path.isfile(absScriptFilePath)

		if printFunc is not None:
			assert callable(printFunc)
		else:
			printFunc = print

		# ----

		installScriptFilePath = self._generateBCScriptFilePath(absScriptFilePath)
		installScriptDirPath = os.path.dirname(installScriptFilePath)
		if not os.path.isdir(installScriptDirPath):
			os.makedirs(installScriptDirPath, exist_ok=True)
		self._writeDebugData("installScriptDirPath:", installScriptDirPath)
		self._writeDebugData("installScriptFilePath:", installScriptFilePath)

		existingCompletionScriptFileText = None
		if os.path.isfile(installScriptFilePath):
			with open(installScriptFilePath, "r") as f:
				existingCompletionScriptFileText = f.read()

		newCompletionScriptFileText = self._createBCScriptFileText(absScriptFilePath)
		if existingCompletionScriptFileText != newCompletionScriptFileText:
			self._writeDebugData("Completion script file differs from expected.")
			if not bQuiet:
				printFunc("Now installing bash completion script file: {}".format(installScriptFilePath))
			self._writeDebugData("Now installing bash completion script file: {}".format(installScriptFilePath))

			with open(installScriptFilePath, "w") as f:
				f.write(newCompletionScriptFileText)
		else:
			self._writeDebugData("Completion script file exists with expected content.")

		# ----

		installDataFilePath = self._generateBCDataFilePath(absScriptFilePath)
		installDataDirPath = os.path.dirname(installDataFilePath)
		if not os.path.isdir(installDataDirPath):
			os.makedirs(installDataDirPath, exist_ok=True)
		self._writeDebugData("installDataDirPath:", installDataDirPath)
		self._writeDebugData("installDataFilePath:", installDataFilePath)

		existingCompletionDataFileText = None
		if os.path.isfile(installDataFilePath):
			with open(installDataFilePath, "r") as f:
				existingCompletionDataFileText = f.read()

		newCompletionDataFileText = self._createBCDataFileText(absScriptFilePath, options, allCommands)
		if existingCompletionDataFileText != newCompletionDataFileText:
			self._writeDebugData("Completion data file differs from expected.")
			if not bQuiet:
				printFunc("Now installing bash completion data file: {}".format(installDataFilePath))
			self._writeDebugData("Now installing bash completion data file: {}".format(installDataFilePath))

			with open(installDataFilePath, "w") as f:
				f.write(newCompletionDataFileText)
		else:
			self._writeDebugData("Completion data file exists with expected content.")

		# ----

		return True
	#

#















