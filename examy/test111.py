string_to_split = "2322,0,content/submissions/submission_2d42f16f-030c-4939-bebf-71156490c498.py,1,content/submissions/submission_3cdf9695-98f6-4b2e-900f-72bc809f2e32.py,1,124,62,62,62"
result_list = string_to_split.split(",")

substring_start = result_list[2].find("submission_") + len("submission_")
substring_end = result_list[2].find(".", substring_start)

substring = result_list[2][substring_start:substring_end]

print(substring)