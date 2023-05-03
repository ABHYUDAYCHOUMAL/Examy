from .models import Submission, Problem
from django.db.models import Max, CharField, Value
from django.db.models.functions import Concat
import subprocess
import pandas as pd
import shutil
import os
# from .models import connections

def run_checker(contest_id: int, penalty_ratio = 0.8):
    problems = Problem.objects.filter(contest_id=contest_id)
    submissions = Submission.objects.filter(problem__in=problems).annotate(
        # full_name="participant_id",
        # labels="problem_id",
        # filename="id",
        ).values().annotate(Max('final_score')).order_by('participant_id', 'problem_id')
    
    if len(submissions) < 2:
        return
    
    pd.DataFrame.from_dict({
        "filename":[i['submission_file'] for i in submissions],
        "full_name":[i["participant_id"] for i in submissions],
        "labels":[i["problem_id"] for i in submissions],
        }).to_csv("./temp_file.csv", index=False)
    
    
    try:
        output = str(subprocess.check_output("dolos run -f csv -l char temp_file.csv".split(" ")))
    except Exception as e:
        print(e)
        return
    output_dir = output.split("\\n")[0].split(": ")[1]
    
    similarity = pd.read_csv(f"{output_dir}/pairs.csv")
    
    similarity = similarity[similarity["similarity"] > penalty_ratio]
    if len(similarity) > 0:
        similarity["rightFilePath"] = (similarity["rightFilePath"].apply(lambda x: x.split("_")[1].split(".")[0]))
        similarity["leftFilePath"] = similarity = (similarity["leftFilePath"].apply(lambda x: x.split("_")[1].split(".")[0]))
        
    try:
        final_set = similarity["leftFilePath"].unique() + similarity["rightFilePath"].unique()
        final_set = set(final_set)
        print(final_set)
        print(similarity["leftFilePath"])
    except Exception as err:
        print(err)
        return
   
    shutil.rmtree(output_dir, ignore_errors=True)
    os.remove("temp_file.csv")
