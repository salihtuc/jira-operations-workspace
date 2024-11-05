import com.atlassian.jira.security.roles.RoleActor
import com.atlassian.jira.component.ComponentAccessor
import com.atlassian.jira.security.roles.ProjectRoleManager
import com.atlassian.jira.bc.projectroles.ProjectRoleService

def userManager = ComponentAccessor.userManager
def projectRoleManager = ComponentAccessor.getComponent(ProjectRoleManager)
def projectRoleService = ComponentAccessor.getComponent(ProjectRoleService)

//Specify project and role
final def projectKey = '<PROJECT_KEY>'
final def roleNameToRemove = '<ROLE_NAME_TO_REMOVE_USERS>'
final def roleNameToAdd = '<ROLE_NAME_TO_ADD_USERS>'

final def actorType = 'atlassian-user-role-actor'

def project = ComponentAccessor.projectManager.getProjectByCurrentKey(projectKey)
def projectRoleToRemove = projectRoleManager.getProjectRole(roleNameToRemove)
def projectRoleToAdd = projectRoleManager.getProjectRole(roleNameToAdd)

def usernames = []

projectRoleService.getProjectRoleActors(projectRoleToRemove, project, null).roleActors.each { 
    usernames.add(it.parameter)
}

projectRoleService.removeActorsFromProjectRole(usernames as List<String>, projectRoleToRemove, project, actorType, null)
projectRoleService.addActorsToProjectRole(usernames as List<String>, projectRoleToAdd, project, actorType, null)
