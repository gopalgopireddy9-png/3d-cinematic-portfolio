from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from .models import Job, Application, SavedJob, Category
from .forms import JobForm, ApplicationForm, JobSearchForm

def home(request):
    featured_jobs = Job.objects.filter(status='active', is_featured=True)[:6]
    recent_jobs = Job.objects.filter(status='active')[:8]
    categories = Category.objects.all()
    total_jobs = Job.objects.filter(status='active').count()
    return render(request, 'home.html', {'featured_jobs':featured_jobs,'recent_jobs':recent_jobs,'categories':categories,'total_jobs':total_jobs})

def job_list(request):
    form = JobSearchForm(request.GET)
    jobs = Job.objects.filter(status='active')
    if form.is_valid():
        q = form.cleaned_data.get('q')
        location = form.cleaned_data.get('location')
        job_type = form.cleaned_data.get('job_type')
        level = form.cleaned_data.get('level')
        salary_min = form.cleaned_data.get('salary_min')
        if q: jobs = jobs.filter(Q(title__icontains=q)|Q(description__icontains=q)|Q(skills_required__icontains=q))
        if location: jobs = jobs.filter(Q(location__icontains=location)|Q(is_remote=True))
        if job_type: jobs = jobs.filter(job_type=job_type)
        if level: jobs = jobs.filter(level=level)
        if salary_min: jobs = jobs.filter(salary_min__gte=salary_min)
    return render(request, 'jobs/list.html', {'jobs':jobs,'form':form})

def job_detail(request, pk):
    job = get_object_or_404(Job, pk=pk, status='active')
    job.views += 1; job.save(update_fields=['views'])
    has_applied = is_saved = False
    if request.user.is_authenticated:
        has_applied = Application.objects.filter(job=job, applicant=request.user).exists()
        is_saved = SavedJob.objects.filter(job=job, user=request.user).exists()
    related = Job.objects.filter(category=job.category, status='active').exclude(pk=pk)[:3]
    return render(request, 'jobs/detail.html', {'job':job,'has_applied':has_applied,'is_saved':is_saved,'related':related})

@login_required
def apply_job(request, pk):
    job = get_object_or_404(Job, pk=pk, status='active')
    if request.user.is_employer(): messages.error(request, 'Employers cannot apply.'); return redirect('job_detail', pk=pk)
    if Application.objects.filter(job=job, applicant=request.user).exists(): messages.warning(request, 'Already applied.'); return redirect('job_detail', pk=pk)
    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            app = form.save(commit=False); app.job = job; app.applicant = request.user; app.save()
            messages.success(request, 'Application submitted!'); return redirect('my_applications')
    else: form = ApplicationForm()
    return render(request, 'jobs/apply.html', {'form':form,'job':job})

@login_required
def save_job(request, pk):
    job = get_object_or_404(Job, pk=pk)
    saved, created = SavedJob.objects.get_or_create(user=request.user, job=job)
    if not created: saved.delete(); messages.info(request, 'Removed from saved.')
    else: messages.success(request, 'Job saved!')
    return redirect('job_detail', pk=pk)

@login_required
def my_applications(request):
    apps = Application.objects.filter(applicant=request.user).select_related('job','job__employer')
    return render(request, 'jobs/my_applications.html', {'applications':apps})

@login_required
def dashboard(request):
    if request.user.is_employer():
        jobs = Job.objects.filter(employer=request.user)
        recent_apps = Application.objects.filter(job__employer=request.user).select_related('job','applicant')[:10]
        total_apps = Application.objects.filter(job__employer=request.user).count()
        return render(request, 'dashboard/employer.html', {'jobs':jobs,'recent_apps':recent_apps,'total_apps':total_apps})
    apps = Application.objects.filter(applicant=request.user).select_related('job')
    saved = SavedJob.objects.filter(user=request.user).select_related('job')
    return render(request, 'dashboard/jobseeker.html', {'applications':apps,'saved_jobs':saved})

@login_required
def post_job(request):
    if not request.user.is_employer(): messages.error(request, 'Only employers can post jobs.'); return redirect('dashboard')
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False); job.employer = request.user; job.status = 'draft'; job.save()
            return redirect('job_payment', pk=job.pk)
    else: form = JobForm()
    return render(request, 'jobs/post_job.html', {'form':form})

@login_required
def manage_applications(request, pk):
    job = get_object_or_404(Job, pk=pk, employer=request.user)
    apps = Application.objects.filter(job=job).select_related('applicant')
    if request.method == 'POST':
        app_id = request.POST.get('app_id'); status = request.POST.get('status')
        app = get_object_or_404(Application, pk=app_id, job=job); app.status = status; app.save()
        messages.success(request, f'Status updated to {status}.')
    return render(request, 'jobs/manage_applications.html', {'job':job,'applications':apps})

def resume_database(request):
    from accounts.models import User
    if not request.user.is_authenticated: return redirect('login')
    if not request.user.is_employer(): messages.error(request, 'Employers only.'); return redirect('home')
    if not request.user.has_resume_access(): return redirect('buy_resume_access')
    q = request.GET.get('q',''); exp = request.GET.get('exp','')
    seekers = User.objects.filter(role='jobseeker', resume_public=True)
    if q: seekers = seekers.filter(Q(skills__icontains=q)|Q(bio__icontains=q))
    if exp: seekers = seekers.filter(years_experience__gte=int(exp))
    return render(request, 'jobs/resume_database.html', {'seekers':seekers,'q':q,'exp':exp})
