from .models import Submission, Problem
from django.db.models import Max, CharField, Value
from django.db.models.functions import Concat
import subprocess
from pandas import DataFrame
# from .models import connections

def run_checker(contest_id: int):
    problems = Problem.objects.filter(contest_id=contest_id)
    submissions = Submission.objects.filter(problem__in=problems).annotate(
        # full_name="participant_id",
        # labels="problem_id",
        # filename="id",
        ).values().annotate(Max('final_score')).order_by('participant_id', 'problem_id')
    
    
    DataFrame.from_dict({
        "filename":[i['submission_file'] for i in submissions],
        "full_name":[i["participant_id"] for i in submissions],
        "labels":[i["problem_id"] for i in submissions],
        }).to_csv("./temp_file.csv", index=False)
    
    subprocess.run("dolos run -f csv -l char temp_file.csv".split(" "))
    
    pass