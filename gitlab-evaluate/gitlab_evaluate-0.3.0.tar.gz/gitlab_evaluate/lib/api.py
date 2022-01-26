from re import findall
from gitlab_ps_utils.api import GitLabApi
from gitlab_evaluate.lib import human_bytes as hb
from gitlab_evaluate.lib import utils

gl_api = GitLabApi()

# Project only keyset-based pagination - https://docs.gitlab.com/ee/api/#keyset-based-pagination

def get_last_id(link):
    # Get id_after value. If the Link key is missing it's done, with an empty list response
    return findall(r"id_after=(.+?)&", link)[0] if link else None

'''
Generates the URL to get the full project info with statistics
'''
def proj_info_get(i, source):
    '''Trying to create proper api call with project id.'''
    i = str(i)
    proj_inf_url = f"/api/v4/projects/{i}?statistics=true"
    gl_projects_info = source + proj_inf_url
    return gl_projects_info

def proj_pl_get(i, source):
    '''Trying to create proper api call with project id to get the number of pipelines.'''
    i = str(i)
    pl_inf_url = f"/api/v4/projects/{i}/pipelines"
    gl_proj_pl = source + pl_inf_url
    return gl_proj_pl

def proj_issue_get(i, source):
    '''Trying to create proper api call with project id to get the number of issues.'''
    i = str(i)
    issue_inf_url = f"/api/v4/projects/{i}/issues"
    gl_issue_pl = source + issue_inf_url
    return gl_issue_pl

def proj_branch_get(i, source):
    '''Trying to create proper api call with project id to get the number of branches.'''
    i = str(i)
    branch_inf_url = f"/api/v4/projects/{i}/repository/branches"
    gl_branch_pl = source + branch_inf_url
    return gl_branch_pl

def proj_mr_get(i, source):
    '''Trying to create proper api call with project id to get the number of MR's.'''
    i = str(i)
    mr_inf_url = f"/api/v4/projects/{i}/merge_requests"
    gl_mr_pl = source + mr_inf_url
    return gl_mr_pl

def proj_tag_get(i, source):
    '''Trying to create proper api call with project id to get the number of tags.'''
    i = str(i)
    tag_inf_url = f"/api/v4/projects/{i}/repository/tags"
    gl_tag_pl = source + tag_inf_url
    return gl_tag_pl

# def proj_commits_get(i, source):
#     '''Trying to create proper api call with project id to get the number of commits.'''
#     i = str(i)
#     commits_url = "/api/v4/projects/{i}/repository?statistics=yes"
#     gl_commits_pl = source + commits_url
#     return gl_commits_pl       
### Functions - Return API Data
# Gets the X-Total from the statistics page with the -I on a curl
def check_x_total_value_update_dict(check_func, p, url="", params={}, headers={}, value_column_name="DEFAULT_VALUE", over_column_name="DEFAULT_COLUMN_NAME", results={}):
    if resp := gl_api.generate_get_request(host="", api="", token=headers.get("private-token"), url=url): 
        num = int(resp.headers.get('X-Total'))
        num_over = check_func(num)
        results[value_column_name] = num
        results[over_column_name] = num_over
    else:
        print(f"Could not retrieve {value_column_name} for project: {p.get('id')} - {p.get('name')}")
# gets the full stats of the project and sorts based on the returned items, passing a few through the HumanReadable utility
def check_full_stats(url, project, my_dict, headers={}):
    if resp := gl_api.generate_get_request(host="", api="", token=headers.get("private-token"), url=url): 
        
        result = resp.json()
        if kind := result.get("namespace"):
            my_dict.update({"kind": kind.get("kind")})
        if stats := result.get("statistics"):
            # storage_size = result.get('storage_size')
            # commit_count = stats.get('commit_count')
            # repository_size = stats.get('repository_size')
            # wiki_size = stats.get['wiki_size']
            # lfs_objects_size = stats.get['lfs_objects_size']
            # job_artifacts_size = stats.get['job_artifacts_size']
            # snippets_size = stats.get['snippets_size']
            # packages_size = stats.get['packages_size']

            for k, v in stats.items():
                my_dict.update({ k: hb.HumanBytes.format(v, True) if k != "commit_count" else v, k + "_over": utils.check_size(k, v)}) 
                # my_dict[k] = {
                #     "value": hb.HumanBytes.format(v, True) if k != 'commit_count' else v,
                #     "over": utils.check_size(k, v)
                # }
        else:
            print(f"Could not extracts stats for project {project}.\n")
    else:
        print(f"Could not retrieve project with stats for project id: {project.get('id')}")

def getApplicationInfo(host,token,api):
    if resp := gl_api.generate_get_request(host=host, token=token, api=api):
        result = resp.json()
        ## error handling - look for 200 
        return result

def getVersion(host,token,api):
    if resp := gl_api.generate_get_request(host=host,token=token,api=api):
        result = resp.json()
        ## error handling - look for 200 
        return result
