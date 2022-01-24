from elements_sdk import StorageApi, MediaLibraryApi


def getWorkspaceIDsForProduction(api:StorageApi,production_id:int):
	""" Returns a list of all workspaces in the production given by the production.ID.
		Formatted as a list of dicts ([{'name':workspace.name,'id':workspace.ID,'path':workspace.path},...])  """

	wss = api.get_all_workspaces(production=production_id)

	ret = []
	for ws in wss:
		ret.append({'name':ws.name,'id':ws.id,'path':ws.path})
	return ret


def getEventsInWorkspace(api:StorageApi,workspace_id:int):
	""" Returns a list of folder names in the root of the workspace."""

	ws = api.get_workspace(id=workspace_id)

	dirs = api.get_file(path=ws.path)

	ret = []
	for dir in dirs.files:
		if dir.is_dir == True and dir.name[0] != ".":
			ret.append(dir.name)
	return ret


def getEquipmentInEvent(api:StorageApi,workspace_id:int,event:str):
	""" Returns a list of equipment names used in the event."""

	ws = api.get_workspace(id=workspace_id)

	eqs = api.get_file(path=ws.path+"/"+event)

	ret = []
	for eq in eqs.files:
		if eq.is_dir == True and eq.name[0] != ".":
			ret.append(eq.name)
	return ret


def getAssetDownloadURLByName(api:MediaLibraryApi,name:str):
	""" Searches for the one asset of filename name and returns its id, bundle_id (for downloading!) and file path"""

	assets = api.get_all_assets(display_name=name)

	print(assets)
	
	# TODO: Why is this necessary? Why does the Elements API deliver this as a string???
	bundles = eval(assets[0].bundles)

	return 'https://dm-medialib.geomar.de/api/media/download/'+str(bundles[0]['id'])


def getiFDO(api:StorageApi,workspace_id:int,event:str,equipment:str):
	""" Returns the file path to the iFDO """

	ws = api.get_workspace(id=workspace_id)
	dirs = api.get_file(path=ws.path)

	for dir in dirs.files:
		if dir.name == event:
			ifdo_path = ws.path + "/" + event + "/" + equipment + "/products/" + event + "_" + equipment + "_iFDO.yaml"
			return api.get_file(path = ifdo_path).path
	return False
