# from django.shortcuts import render, get_object_or_404

# from django.http import HttpResponse
# from django.template import loader
# from django.shortcuts import redirect
# from django.contrib import messages
# from .models import TestCase
# from compile.models import CodeSubmission
# from compile.views import run_code
# from django.conf import settings

# from pathlib import Path
# from django.contrib.auth.decorators import login_required



# # def run_testcases(submission, question, visible_only=False):
# #     testcases = TestCase.objects.filter(question=question)
# #     if visible_only:
# #         testcases = testcases.filter(is_visible=True)

# #     results = []

# #     for test in testcases:
# #         with open(test.input_file.path, 'r') as f:
# #             input_data = f.read()

# #         expected_output = open(test.output_file.path, 'r').read().strip()

# #         output = run_code(submission.language, submission.code, input_data).strip()

# #         passed = output == expected_output

# #         results.append({
# #             'input': input_data,
# #             'expected': expected_output,
# #             'output': output,
# #             'passed': passed,
# #             'visible': test.is_visible,
# #         })

# #     return results


# # def submit(request, id):
# #     if request.method == "POST":
# #         language = request.POST.get("language")
# #         code = request.POST.get("code")
# #         input_data = request.POST.get("input_data")
# #         action = request.POST.get("action")
# #         qid = request.POST.get("question_id")

# #         submission = CodeSubmission(language=language, code=code, input_data=input_data)
# #         submission.save()

        
# #         testcase = TestCase.objects.get(id=qid)
# #         question = testcase.question
# #         visible_only = True if action == "run" else False
# #         results = run_testcases(submission, question, visible_only=visible_only)

# #         submission.output_data = results[0]["output"]
# #         submission.save()

# #         return render(request, "question_detail.html", {
# #             "submission": submission,
# #             "results": results,
# #             "detail": question  # also send question detail so it doesn't break
# #         })

# #     else:
# #         # Handle GET request — you must return an HttpResponse
# #         question = get_object_or_404(TestCase, id=id)
# #         return render(request, "question_detail.html", {"detail": question})

# def run_testcases(submission, question, visible_only=False):
#     testcases = TestCase.objects.filter(question=question)
#     if visible_only:
#         testcases = testcases.filter(is_visible=True)

#     results = []

#     for test in testcases:
#         with open(test.input_file.path, 'r') as f:
#             input_data = f.read().strip()

#         expected_output = open(test.output_file.path, 'r').read().strip()

#         output = run_code(submission.language, submission.code, input_data).strip()

#         passed = output == expected_output

#         results.append({
#             'input': input_data,
#             'expected': expected_output,
#             'output': output,
#             'passed': passed,
#             'visible': test.is_visible,
#         })

#     return results


# def submit(request, id):
#     if request.method == "POST":
#         language = request.POST.get("language")
#         code = request.POST.get("code")
#         input_data = request.POST.get("input_data")
#         action = request.POST.get("action")
#         qid = request.POST.get("question_id")

#         submission = CodeSubmission(language=language, code=code, input_data=input_data)
#         submission.save()

#         testcase = get_object_or_404(TestCase, id=qid)
#         question = testcase.question

#         visible_only = True if action == "run" else False
#         results = run_testcases(submission, question, visible_only=visible_only)

#         submission.output_data = results[0]["output"] if results else ""
#         submission.save()

#         # Read input/output text content for display (optional)
#         input_content = ""
#         output_content = ""
#         if testcase.input_file and testcase.output_file:
#             with open(testcase.input_file.path, "r") as infile:
#                 input_content = infile.read()
#             with open(testcase.output_file.path, "r") as outfile:
#                 output_content = outfile.read()

#         return render(request, "question_detail.html", {
#             "submission": submission,
#             "results": results,
#             "detail": testcase,  # full testcase
#             "input_content": input_content,
#             "output_content": output_content,
#         })

#     else:
#         testcase = get_object_or_404(TestCase, id=id)

#         input_content = ""
#         output_content = ""
#         if testcase.input_file and testcase.output_file:
#             with open(testcase.input_file.path, "r") as infile:
#                 input_content = infile.read()
#             with open(testcase.output_file.path, "r") as outfile:
#                 output_content = outfile.read()

#         return render(request, "question_detail.html", {
#             "detail": testcase,
#             "input_content": input_content,
#             "output_content": output_content
#         })

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import  TestCase, Question
from compile.models import CodeSubmission
import subprocess
from pathlib import Path
from django.conf import settings
import uuid
import os
import google.generativeai as genai
from dashboard.models import UserSolvedQuestion
from django.views.decorators.csrf import csrf_exempt

def run_code(language, code, input_data):
    project_path = Path(settings.BASE_DIR)
    directories = ["codes", "inputs", "outputs"]

    # Make sure the necessary directories exist
    for directory in directories:
        dir_path = project_path / directory
        dir_path.mkdir(parents=True, exist_ok=True)

    codes_dir = project_path / "codes"
    inputs_dir = project_path / "inputs"
    outputs_dir = project_path / "outputs"

    unique = str(uuid.uuid4())

    code_file_name = f"{unique}.{language}"
    input_file_name = f"{unique}.txt"
    output_file_name = f"{unique}.txt"

    code_file_path = codes_dir / code_file_name
    input_file_path = inputs_dir / input_file_name
    output_file_path = outputs_dir / output_file_name

    # Save the code to file
    with open(code_file_path, "w") as code_file:
        code_file.write(code)

    # Normalize input line endings
    input_data = (input_data or "").replace("\r\n", "\n")

    with open(input_file_path, "w") as input_file:
        input_file.write(input_data)

    with open(output_file_path, "w") as output_file:
        pass  # Create an empty output file

    output_data = ""
    error_data = ""

    try:
        if language == "cpp":
            executable_path = codes_dir / unique
            # Compile
            compile_result = subprocess.run(
                ["g++", str(code_file_path), "-o", str(executable_path)],
                capture_output=True, text=True, timeout=5
            )
            if compile_result.returncode != 0:
                error_data = compile_result.stderr
            else:
                # Run the program
                run_result = subprocess.run(
                    [str(executable_path)],
                    stdin=open(input_file_path, "r"),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=5
                )
                output_data = run_result.stdout
                error_data = run_result.stderr

        elif language == "py":
            run_result = subprocess.run(
                ["python", str(code_file_path)],
                stdin=open(input_file_path, "r"),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=5
            )
            output_data = run_result.stdout
            error_data = run_result.stderr

    except subprocess.TimeoutExpired:
        error_data = "Error: Timeout - Your code took too long to execute."
    except Exception as e:
        error_data = f"Error: {str(e)}"

    # Clean up files
    try:
        os.remove(code_file_path)
        os.remove(input_file_path)
        if language == "cpp" and 'executable_path' in locals():
            os.remove(executable_path)
    except:
        pass

    # Combine output and error
    final_output = output_data.strip()
    if error_data:
        final_output += "\n\nErrors:\n" + error_data.strip()

    return final_output

def run_testcases(submission, question, visible_only=False):
    testcases = TestCase.objects.filter(question=question)
    if visible_only:
        testcases = testcases.filter(is_visible=True)

    results = []
    total_testcases = testcases.count()
    passed_testcases = 0

    for test in testcases:
        try:
            with open(test.input_file.path, 'r') as f:
                input_data = f.read().strip()

            with open(test.output_file.path, 'r') as f:
                expected_output = f.read().strip()

            output = run_code(submission.language, submission.code, input_data).strip()

            # Normalize line endings for comparison
            passed = output.replace('\r\n', '\n') == expected_output.replace('\r\n', '\n')

            if passed:
                passed_testcases += 1

            results.append({
                'input': input_data,
                'expected': expected_output,
                'output': output,
                'passed': passed,
                'visible': test.is_visible,
            })
        except Exception as e:
            results.append({
                'input': "Error reading test case",
                'expected': "N/A",
                'output': f"Error processing test case: {str(e)}",
                'passed': False,
                'visible': test.is_visible,
            })

    return {
        'results': results,
        'total_testcases': total_testcases,
        'passed_testcases': passed_testcases,
        'score': (passed_testcases / total_testcases * 100) if total_testcases > 0 else 0
    }

# def submit(request, id):
#     if request.method == "POST":
#         language = request.POST.get("language")
#         code = request.POST.get("code")
#         input_data = request.POST.get("input_data", "")
#         action = request.POST.get("action")
#         question_id = request.POST.get("question_id")

#         if not language or not code:
#             messages.error(request, "Language and code are required fields.")
#             return redirect(request.META.get('HTTP_REFERER', '/'))

#         # Create submission
#         submission = CodeSubmission(
#             language=language,
#             code=code,
#             input_data=input_data,
#         )
#         submission.save()

#         question = get_object_or_404(Question, id=question_id)
#         visible_only = (action == "run")
        
#         test_results = run_testcases(submission, question, visible_only=visible_only)

#         # Update submission with first result's output (for display)
#         if test_results['results']:
#             submission.output_data = test_results['results'][0]['output']
#             submission.save()

#         # Get the first visible testcase for sample display
#         sample_testcase = TestCase.objects.filter(
#             question=question,
#             is_visible=True
#         ).first()

#         input_content = ""
#         output_content = ""
#         if sample_testcase:
#             with open(sample_testcase.input_file.path, "r") as infile:
#                 input_content = infile.read()
#             with open(sample_testcase.output_file.path, "r") as outfile:
#                 output_content = outfile.read()

#         return render(request, "question_detail.html", {
#             "submission": submission,
#             "test_results": test_results,
#             "question": question,
#             "input_content": input_content,
#             "output_content": output_content,
#             "action": action,
#         })

#     else:
#         question = get_object_or_404(Question, id=id)
#         sample_testcase = TestCase.objects.filter(
#             question=question,
#             is_visible=True
#         ).first()

#         input_content = ""
#         output_content = ""
#         if sample_testcase:
#             with open(sample_testcase.input_file.path, "r") as infile:
#                 input_content = infile.read()
#             with open(sample_testcase.output_file.path, "r") as outfile:
#                 output_content = outfile.read()

#         return render(request, "question_detail.html", {
#             "question": question,
#             "input_content": input_content,
#             "output_content": output_content
#         })

# views.py
def submit(request, id):
    test_case = get_object_or_404(TestCase, id=id)
    question = test_case.question
    # Get input/output content for display
    input_content = ""
    output_content = ""
    if test_case.input_file:
        with open(test_case.input_file.path, "r") as infile:
            input_content = infile.read()
    if test_case.output_file:
        with open(test_case.output_file.path, "r") as outfile:
            output_content = outfile.read()

    if request.method == "POST":
        # Handle form submission
        action = request.POST.get("action")

        if action == "ai_help":
            return ai_help(request,test_case)
        
        language = request.POST.get("language")
        code = request.POST.get("code")
        input_data = request.POST.get("input_data", "")
        
        
        submission = CodeSubmission(
            language=language,
            code=code,
            input_data=input_data,
        )
        submission.save()

        visible_only = (action == "run")
        test_results = run_testcases(submission, test_case.question, visible_only)
        
        if action=="submit":
            test_results = run_testcases(submission, question, visible_only=False)

        if test_results.get('score') == 100:
                # Use get_or_create to avoid creating duplicate entries if the user
                # resubmits a correct solution. It's an efficient and safe method.
                UserSolvedQuestion.objects.get_or_create(
                    user=request.user, 
                    question=question
                )
        
            
        return render(request, "question_detail.html", {
            "test_case": test_case,
            "submission": submission,
            "test_results": test_results,
            "input_content": input_content,
            "output_content": output_content,
        })
        

    return render(request, "question_detail.html", {
        "test_case": test_case,
        "input_content": input_content,
        "output_content": output_content,
    })







# In views.py

# def ai_help(request, test_case):
#     """
#     Handles the AI help request.
#     """
#     language = request.POST.get("language")
#     code = request.POST.get("code")

#     # Create a submission object to run test cases
#     submission = CodeSubmission(language=language, code=code)
    
#     # Run all test cases to gather data for the AI
#     test_results = run_testcases(submission, test_case.question, visible_only=False)

#     # Filter for failed test cases to send to the AI
#     failed_tests = [res for res in test_results['results'] if not res['passed']]

#     # if not failed_tests:
#     #     # If no tests failed, there's nothing to debug
#     #     return render(request, "question_detail.html", {
#     #         "test_case": test_case,
#     #         "submission": submission,
#     #         "test_results": test_results,
#     #         "ai_response": "All test cases passed! No need for AI help here."
#     #     })


#     # Configure the AI model
#     genai.configure(api_key='AIzaSyAVyq_KhYSWEW6yj01BX443N7epGQrcy5E')
#     model = genai.GenerativeModel('gemini-2.0-flash')

#     generation_config = genai.types.GenerationConfig(
#         max_output_tokens=200
#     )
    
#     # Construct a detailed prompt for the AI
#     prompt_parts = [
#         f"Programming Language: {language}",
#         f"Question Description: {test_case.description}",
#         "User's Code:",
#         code,
#         "The code failed the following test cases. Please review the code, identify the bug, and provide a corrected version with an explanation.",
#     ]

#     for test in failed_tests:
#         prompt_parts.append(f"\n--- FAILED TEST ---")
#         prompt_parts.append(f"Input:\n{test['input']}")
#         prompt_parts.append(f"Expected Output:\n{test['expected']}")
#         prompt_parts.append(f"Actual Output:\n{test['output']}")
#         prompt_parts.append("--- END TEST ---")

#     prompt = "\n".join(prompt_parts)

#     # Generate content
#     try:
#         ai_response_text = model.generate_content(prompt).text
#     except Exception as e:
#         ai_response_text = f"Could not get AI response. Error: {e}"

#     # Render the page again with the AI response
#     return render(request, "question_detail.html", {
#         "test_case": test_case,
#         "submission": submission,
#         "test_results": test_results,
#         "ai_response": ai_response_text,
#     })

# In views.py

def ai_help(request, test_case):
    """
    Handles the AI help request using a structured, dynamic prompt.
    """
    language = request.POST.get("language")
    code = request.POST.get("code")

    submission = CodeSubmission(language=language, code=code)
    test_results = run_testcases(submission, test_case.question, visible_only=False)
    failed_tests = [res for res in test_results['results'] if not res['passed']]

    # --- 1. Dynamically build the prompt ---
    prompt_context = [
        f"You are an expert AI code reviewer for an online programming judge. Your primary goal is to provide concise, structured, and helpful feedback on a user's code submission in about 200 words.",
        f"\n**Context:**",
        f"- **Problem:** {test_case.description}",
        f"- **Language:** {language}",
        f"- **User's Code:**\n``````"
    ]

    if not failed_tests:
        prompt_context.append("- **Test Results:** All test cases passed successfully.")
        # Instruct the AI to focus only on review
        prompt_context.append("\n**Your Task:**\nGenerate a response focusing *only* on the 'Code Review & Suggestions' section. Omit the 'Debugging Analysis' section entirely.")
    else:
        failed_details = ["- **Test Results:** The code failed the following test cases:"]
        for test in failed_tests:
            failed_details.append(
                f"  - **Input:** `{test['input']}`\n"
                f"    **Expected Output:** `{test['expected']}`\n"
                f"    **Actual Output:** `{test['output']}`"
            )
        prompt_context.append("\n".join(failed_details))
        # Instruct the AI to perform all tasks
        prompt_context.append("\n**Your Task:**\nGenerate a response with both the 'Code Review & Suggestions' and 'Debugging Analysis' sections.")

    # Add the required output structure to the prompt
    prompt_context.append(
        "\n---\n\n"
        "**1. Code Review & Suggestions**\n"
        "*   **Style Analysis:**\n"
        "*   **Improvements:**\n\n"
        "**2. Debugging Analysis**\n"
        "*   **[This section should only be included if test cases have failed]**\n"
        "*   **Bug:**\n"
        "*   **Explanation:**\n"
        "*   **Corrected Code:**"
    )

    prompt = "\n".join(prompt_context)

    # --- 2. Configure and call the AI Model ---
    genai.configure(api_key='AIzaSyAVyq_KhYSWEW6yj01BX443N7epGQrcy5E')
    model = genai.GenerativeModel('gemini-2.0-flash') # Or your preferred model
    
    generation_config = genai.types.GenerationConfig(
        max_output_tokens=400  # Increased slightly to accommodate structure
    )

    try:
        response = model.generate_content(
            prompt,
            generation_config=generation_config
        )
        ai_response_text = response.text
    except Exception as e:
        ai_response_text = f"Could not get AI response. Error: {e}"

    # --- FIX: Read sample input/output content here ---
    input_content = ""
    output_content = ""
    if test_case.input_file:
        with open(test_case.input_file.path, "r") as infile:
            input_content = infile.read()
    if test_case.output_file:
        with open(test_case.output_file.path, "r") as outfile:
            output_content = outfile.read()
    # --- 3. Render the response ---
    return render(request, "question_detail.html", {
        "test_case": test_case,
        "submission": submission,
        "test_results": test_results,
        "ai_response": ai_response_text,
        "input_content": input_content,
        "output_content": output_content,
    })



