from .models import Submission, Problem
from django.db.models import Max, CharField, Value
from django.db.models.functions import Concat
import subprocess
import pandas as pd
import shutil
import os
# from .models import connections

def run_checker(contest_id: int, penalty_ratio = 0.8):
    # problems = Problem.objects.filter(contest_id=contest_id)
    # submissions = Submission.objects.filter(problem__in=problems).annotate(
    #     # full_name="participant_id",
    #     # labels="problem_id",
    #     # filename="id",
    #     ).values('participant_id', 'problem_id').annotate(Max('final_score')).values('submission_file', 'participant_id', 'problem_id')
    submissions = [i for i in Submission.objects.raw(f'SELECT id, "judge_submission"."submission_file", "judge_submission"."participant_id", "judge_submission"."problem_id", MAX(final_score) as final_score FROM "judge_submission" WHERE "judge_submission"."problem_id" IN (SELECT U0."code" FROM "judge_problem" U0 WHERE U0."contest_id" = {contest_id}) GROUP BY "judge_submission"."participant_id", "judge_submission"."problem_id"')]
    
    if len(submissions) < 2:
        return "No Plagiarism!!"
    
    submissions_records = pd.DataFrame.from_dict({
        "id":[i.id for i in submissions],
        "filename":[i.submission_file for i in submissions],
        "full_name":[i.participant_id for i in submissions],
        "labels":[i.problem_id for i in submissions],
        })

    submissions_records[["filename", "full_name", "labels"]].to_csv("./temp_file.csv", index=False)

    try:
        output = str(subprocess.check_output("dolos run -f csv -l char temp_file.csv".split(" ")))
    except Exception as e:
        return "Dolos error\n"+str(e)
    
    output_dir = output.split("\\n")[0].split(": ")[1]
    
    similarity = pd.read_csv(f"{output_dir}/pairs.csv")
    similarity = similarity[similarity["similarity"] > penalty_ratio]
    
    mapper = pd.Series(submissions_records["full_name"].values, index=submissions_records["filename"].values).to_dict()
    
    similarity.drop(columns=["id", "leftFileId", "rightFileId", 'leftCovered', 'rightCovered'], inplace=True)
    
    similarity["User_A"] = similarity["leftFilePath"].map(mapper)
    similarity["User_B"] = similarity["rightFilePath"].map(mapper)
    
    similarity["similarity"] = similarity["similarity"] * 100
    

    shutil.rmtree(output_dir, ignore_errors=True)
    os.remove("temp_file.csv")
    
    
    similarity_a = similarity.to_numpy()
    header = "<th>" + "</th><th>".join(list(similarity.columns)) + "</th>"
    content = ""
    
    for i in similarity_a:
        i = [str(j) for j in i]
        print("".join(i))
        content = content + "<tr><td>" + "</td><td>".join(i) + "</td></tr>"
    
    if len(similarity) > 0:
        return """<style>
table, th, td {
  border: 1px solid black;
}
</style><table>"""+header+content+"</table>"

    return "No Plagiarim!!"
