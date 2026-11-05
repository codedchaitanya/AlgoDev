from django.http import HttpResponse
from django.template import loader
from django.shortcuts import redirect, render
from django.contrib import messages
from .models import CodeSubmission 
from django.conf import settings
import os
import uuid
from .runner import run_many
from pathlib import Path
from django.contrib.auth.decorators import login_required
# from django.views.decorators.clickjacking import xframe_options_exempt

@login_required
def submit_compile(request):
    if request.method == "POST":
        # Manually fetch form data
        form = CodeSubmission(request.POST)
        language = request.POST.get("language")
        code = request.POST.get("code")
        input_data = request.POST.get("input_data")

        

        # Simple validation (can add more)
        if not language or not code:
            messages.info(request, "Language and code are required fields.")
            return redirect("/compile/")  # Or wherever your form page is

        # Save submission to DB
        submission = CodeSubmission(
            language=language,
            code=code,
            input_data=input_data,
        )
        submission.save()

        # Run the code and save output
        output = run_code(language, code, input_data)
        submission.output_data = output
        submission.save()

        return render(request, "result.html", {"submission": submission})
    selected_language = request.GET.get('lang', 'py') 
    # If GET request
    form = CodeSubmission()
    
    return render(request, "index.html", {"form": form,"selected_language": selected_language}) 



def run_code(language, code, input_data):
    result = run_many(language, code, [input_data])[0]
    final_output = result.stdout
    error_data = "Timeout - your code took too long to execute." if result.timed_out else result.stderr
    if error_data:
        final_output += "\nErrors:\n" + error_data
    return final_output
