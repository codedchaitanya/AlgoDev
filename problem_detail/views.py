
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import  TestCase, Question
from compile.models import CodeSubmission
from compile.runner import run_many
from pathlib import Path
from django.conf import settings
import uuid
import os
import google.generativeai as genai
from dashboard.models import UserSolvedQuestion
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from dotenv import load_dotenv

# Load variables from the .env file
load_dotenv()

def format_result(result):
    """Turn a RunResult into the text shown to the user and compared with the expected output."""
    error_data = result.stderr
    if result.timed_out:
        error_data = "Error: Timeout - Your code took too long to execute."
    final_output = result.stdout.strip()
    if error_data:
        final_output += "\n\nErrors:\n" + error_data.strip()
    return final_output


def run_code(language, code, input_data):
    """Run the code on one input (custom input on the problem page)."""
    return format_result(run_many(language, code, [input_data])[0])



def run_testcases(submission, question, visible_only=False):
    test_case_entry = TestCase.objects.filter(question=question).first()
    passed_testcases=0
    if not test_case_entry:
        return {'results': [], 'total_testcases': 0, 'passed_testcases': 0, 'score': 0}

    all_results = []
    
    # --- Helper function to read and parse a pair of files ---
    def parse_files(input_path, output_path, is_visible_flag):
        parsed_results = []
        if not input_path or not output_path:
            return parsed_results
        
        with open(input_path, 'r') as f:
            inputs = [i.strip() for i in f.read().split('---')]
        with open(output_path, 'r') as f:
            outputs = [o.strip() for o in f.read().split('---')]
        
        if len(inputs) != len(outputs):
            raise Exception("Test case file mismatch.")

        for i, o in zip(inputs, outputs):
            parsed_results.append({'input': i, 'expected': o, 'visible': is_visible_flag})
        return parsed_results

    try:
        # Always load the visible test cases
        visible_cases = parse_files(test_case_entry.input_file.path, test_case_entry.output_file.path, True)
        
        # If it's a full submission, also load the hidden test cases
        hidden_cases = []
        if not visible_only and test_case_entry.hidden_input_file and test_case_entry.hidden_output_file:
            hidden_cases = parse_files(test_case_entry.hidden_input_file.path, test_case_entry.hidden_output_file.path, False)

        # Combine the test cases for a final run
        all_test_cases = visible_cases + hidden_cases
        total_testcases = len(all_test_cases)
        passed_testcases = 0

        # Compile once and run every test case in the same sandbox
        runs = run_many(submission.language, submission.code, [case['input'] for case in all_test_cases])
        for case, run in zip(all_test_cases, runs):
            output = format_result(run).strip()
            # Case-insensitive, so Python's True/False match true/false in the expected files
            passed = output.replace('\r\n', '\n').lower() == case['expected'].replace('\r\n', '\n').lower()

            if passed:
                passed_testcases += 1
            
            all_results.append({
                'input': case['input'], 'expected': case['expected'],
                'output': output, 'passed': passed, 'visible': case['visible']
            })

    except Exception as e:
        all_results.append({
            'input': "Error processing files", 'expected': "N/A",
            'output': f"System Error: {str(e)}", 'passed': False, 'visible': True
        })
        total_testcases = 1

    return {
        'results': all_results,
        'total_testcases': total_testcases,
        'passed_testcases': passed_testcases,
        'score': (passed_testcases / total_testcases * 100) if total_testcases > 0 else 0
    }


@login_required
def submit(request, id):
    print("--- SUBMIT VIEW CALLED ---")
    test_case = get_object_or_404(TestCase, id=id)
    question = test_case.question

    # --- Prepare common context variables ---
    # This prevents you from repeating this code in every return statement
    input_content = ""
    output_content = ""
    if test_case.input_file:
        with open(test_case.input_file.path, "r") as infile:
            input_content = infile.read()
    if test_case.output_file:
        with open(test_case.output_file.path, "r") as outfile:
            output_content = outfile.read()
    
    context = {
        "test_case": test_case,
        "input_content": input_content,
        "output_content": output_content,
    }

    if request.method == "POST":
        
        language = request.POST.get("language")
        code = request.POST.get("code")
        input_data = request.POST.get("input_data", "")
        action = request.POST.get("action")
        

        submission = CodeSubmission(language=language, code=code, input_data=input_data)
        context["submission"] = submission # Add submission to context for re-rendering

        # --- ACTION: AI HELP ---
        # This action needs the full context of all test cases.
        if action == "ai_help":
            if not code.strip():
                    messages.error(request, "Code is empty. Please write a solution before seeking AI help.")
                # Redirect back to the same page to show the error
                    return redirect('submit_question', id=id)
            return ai_help(request, test_case)

        # --- ACTION: RUN CODE ---
        # This is where the custom input logic is prioritized.
        elif action == "run":
            # If the user provided custom input, run ONLY that.
            if input_data.strip():
                output = run_code(submission.language, submission.code, input_data)
                # Manually create a results dictionary for the template
                # We use a new variable 'custom_run_result' to avoid confusion.
                context["custom_run_result"] = {
                    'input': input_data,
                    'output': output
                }
            # If no custom input, run against the VISIBLE sample cases.
            else:
                if not code.strip():
                    messages.error(request, "Code is empty. Please write a solution before running.")
                # Redirect back to the same page to show the error
                    return redirect('submit_question', id=id)
                else:
                    context["test_results"] = run_testcases(submission, question, visible_only=True)

        # --- ACTION: SUBMIT CODE ---
        # This action ALWAYS runs against ALL test cases and ignores custom input.
        elif action == "submit":
            if not code.strip():
                messages.error(request, "Code is empty. Please write a solution before submitting.")
                # Redirect back to the same page to show the error
                return redirect('submit_question', id=id)
            test_results = run_testcases(submission, question, visible_only=False)
            context["test_results"] = test_results
            
            # --- NEW: Save submission results to the database ---
            final_verdict = "Accepted" if test_results.get('score') == 100 else "Wrong Answer"
            # Create and save a persistent record of this submission
            CodeSubmission.objects.create(
                user=request.user,
                question=question,
                language=language,
                code=code,
                score=test_results.get('score', 0),
                verdict=final_verdict
            )
            # This is where you track the user's solved questions
            if test_results.get('score') == 100:
                UserSolvedQuestion.objects.get_or_create(
                    user=request.user, 
                    question=question
                )
        
        return render(request, "question_detail.html", context)

    # This handles the initial GET request to the page
    return render(request, "question_detail.html", context)


def ai_help(request, test_case):
    """
    Handles the AI help request using a structured, dynamic prompt.
    """
    language = request.POST.get("language")
    code = request.POST.get("code")
    input_data = request.POST.get("input_data", "")
    submission = CodeSubmission(language=language, code=code,input_data=input_data)
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

   
    my_api_key = os.getenv('GOOGLE_API_KEY')
    
    # Configure the model with the loaded key
    genai.configure(api_key=my_api_key)
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

# In your problem_detail/views.py

@login_required
def submission_history_view(request, id, question_id):
    question = get_object_or_404(Question, id=question_id)
    
    # Fetch all submissions by the current user for this specific question
    submissions = CodeSubmission.objects.filter(
        user=request.user, 
        question=question
    ).order_by('-submitted_at') # Show the most recent first

    context = {
        'question': question,
        'submissions': submissions,
    }
    return render(request, 'submission_history.html', context)


