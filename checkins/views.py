from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Task, PomodoroSession
from django.db.models import Sum        
from .models import RewardLedger 

# ‑‑‑ Dashboard -----------------------------------------------------------
from django.db.models import Q
from .models import Buddy

@login_required
def dashboard(request):
     # 1. fetch tasks for this user
    tasks = Task.objects.filter(owner=request.user).order_by('deadline')

    # 2. look for buddy row where this user is either side
    buddy_row = Buddy.objects.filter(
        Q(user=request.user) | Q(buddy=request.user)
    ).select_related('user', 'buddy').first()
    
    credit = RewardLedger.objects.filter(creditor=request.user).aggregate(Sum('points'))['points__sum'] or 0
    debit  = RewardLedger.objects.filter(debtor=request.user).aggregate(Sum('points'))['points__sum']  or 0
    net_points = credit - debit 

    # 3. derive the "other" user for template
    buddy_user = None
    if buddy_row:
        buddy_user = buddy_row.buddy if buddy_row.user == request.user else buddy_row.user

    # 4. pass context
    return render(
        request,
        'checkins/dashboard.html',
        {'tasks': tasks, 'buddy_user': buddy_user,'net_points': net_points,}
    )



# ‑‑‑ Start Pomodoro (25‑minute timer) -----------------------------------
@login_required
def start_pomodoro(request, task_id):
    task = get_object_or_404(Task, pk=task_id, owner=request.user)

    # Ajax/POST will hit here when timer finishes
    if request.method == 'POST':
        PomodoroSession.objects.create(task=task,
                                       end_time=timezone.now())
        task.pomodoro_done += 1
        if task.pomodoro_done >= task.pomodoro_goal:
            task.completed = True
        task.save()
        return redirect('home')

    return render(request, 'checkins/pomodoro.html', {'task': task})
@login_required
def add_task(request):
    if request.method == 'POST':
        Task.objects.create(
            owner=request.user,
            title=request.POST['title'],
            deadline=request.POST['deadline'],
            pomodoro_goal=int(request.POST['goal'])   # saves user’s number
        )
        return redirect('home')
    return render(request, 'checkins/add_task.html')
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login as auth_login

def signup(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)          # auto‑login after sign‑up
            return redirect('home')
    else:
        form = UserCreationForm()

    return render(request, 'registration/signup.html', {'form': form})
@login_required
def complete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id, owner=request.user)
    task.completed      = True
    task.pomodoro_done  = task.pomodoro_goal   
    task.save()
    return redirect('home')
from django.db import IntegrityError, transaction
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Buddy

@login_required
def invite_buddy(request):
    if request.method == "POST":
        uname = request.POST.get('username', '').strip()

        try:
            other = User.objects.get(username=uname)
        except User.DoesNotExist:
            messages.error(request, "No user with that username.")
            return redirect('invite_buddy')

        if other == request.user:
            messages.error(request, "You cannot invite yourself.")
            return redirect('invite_buddy')

        # Check neither user is in a Buddy pair
        if Buddy.objects.filter(user__in=[request.user, other]) \
           | Buddy.objects.filter(buddy__in=[request.user, other]):
            messages.error(request, "One of you already has a buddy.")
            return redirect('invite_buddy')

        # Single row representing both users
        try:
            with transaction.atomic():
                Buddy.objects.create(user=request.user, buddy=other)
            messages.success(request, f"You and {other.username} are now study buddies!")
        except IntegrityError:
            messages.error(request, "Unexpected error pairing users.")

        return redirect('home')

    return render(request, 'checkins/invite_buddy_username.html')
