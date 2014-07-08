import json

import web

from common.tasks import Task
from common.tasks_problems import MultipleChoiceProblem
import frontend.submission_manager as submission_manager
from frontend.base import renderer
import frontend.user as User


# Task page
class TaskPage:
    # Simply display the page
    def GET(self, courseId, taskId):
        if User.isLoggedIn():
            #try:
                task = Task(courseId, taskId)
                return renderer.task(task)
            #except:
            #    raise web.notfound()
        else:
            return renderer.index(False)

    def POST(self, courseId, taskId):
        if User.isLoggedIn():
            #try:
                task = Task(courseId, taskId)
                userinput = web.input()
                if "@action" in userinput and userinput["@action"] == "submit":
                    # Reparse user input with array for multiple choices
                    needArray = self.listMultipleMultipleChoices(task)
                    userinput = web.input(**dict.fromkeys(needArray, []))
                    if not task.inputIsConsistent(userinput):
                        web.header('Content-Type', 'application/json')
                        return json.dumps({"status":"error", "text":"Please answer to all the questions. Your responses were not tested."});
                    submissionId = submission_manager.addJob(task, userinput)
                    web.header('Content-Type', 'application/json')
                    return json.dumps({"status":"ok", "submissionId":str(submissionId)});
                elif "@action" in userinput and userinput["@action"] == "check" and "submissionId" in userinput:
                    if submission_manager.isDone(userinput['submissionId']):
                        web.header('Content-Type', 'application/json')
                        result = submission_manager.getSubmission(userinput['submissionId'])
                        return self.submissionToJSON(result)
                    else:
                        web.header('Content-Type', 'application/json')
                        return json.dumps({'status':"waiting"});
                else:
                    raise web.notfound()
            #except:
            #    raise web.notfound()
        else:
            return renderer.index(False)

    def submissionToJSON(self, data):
        tojson = {'status':data['status'],'result':data['result'],'id':str(data["_id"]),'submittedOn':str(data['submittedOn'])}
        if "text" in data:
            tojson["text"] = data["text"]
        if "problems" in data:
            tojson["problems"] = data["problems"]
        return json.dumps(tojson)
        
    
    def listMultipleMultipleChoices(self, task):
        """ List problems in task that expect and array as input """
        o = []
        for problem in task.getProblems():
            if isinstance(problem, MultipleChoiceProblem) and problem.allowMultiple():
                o.append(problem.getId())
        return o
