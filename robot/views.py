from datetime import date

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from .forms import UserRegistrationForm, ChangePasswordForm, EditProfileForm, EditUserProfileForm, CompetitionForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.utils import timezone

from .models import UserProfile, Competition, Registration


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Tự động đăng nhập sau khi đăng ký thành công
            return redirect('login')  # Thay 'home' bằng tên URL mà bạn muốn chuyển hướng sau khi đăng ký
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')  # Chuyển hướng đến trang sau khi đăng nhập thành công
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


@login_required
def home(request):
    return render(request, 'home.html')


def user_logout(request):
    logout(request)
    return redirect('login')  # Chuyển hướng đến trang đăng nhập sau khi đăng xuất


@login_required
def notification(request):
    # Lấy thông báo cho người dùng (nếu có thể)
    notifications = []  # Giả sử đây là danh sách các thông báo, bạn có thể thay bằng truy vấn thực tế
    return render(request, 'notification.html', {'notifications': notifications})


@login_required
def change_password(request):
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST, user=request.user)
        if form.is_valid():
            current_password = form.cleaned_data['current_password']
            new_password = form.cleaned_data['new_password']

            # Kiểm tra mật khẩu cũ và cập nhật mật khẩu mới
            user = request.user
            if user.check_password(current_password):
                user.set_password(new_password)
                user.save()
                update_session_auth_hash(request, user)  # Cập nhật session để tránh đăng xuất
                messages.success(request, 'Mật khẩu đã được thay đổi thành công.')
                return redirect('home')
            else:
                form.add_error('current_password', 'Mật khẩu cũ không đúng.')
        else:
            print(form.errors)
            messages.error(request, 'Vui lòng kiểm tra các lỗi trong biểu mẫu.')
    else:
        form = ChangePasswordForm(user=request.user)

    return render(request, 'change_password.html', {'form': form})


@login_required
def user_profile(request):
    user = request.user
    # Kiểm tra và tạo UserProfile nếu chưa tồn tại
    profile, created = UserProfile.objects.get_or_create(user=user)

    context = {
        'profile': profile,
    }
    return render(request, 'user_profile.html', context)


@login_required
def edit_profile(request):
    user = request.user
    profile, created = UserProfile.objects.get_or_create(user=user)

    if request.method == 'POST':
        user_form = EditProfileForm(request.POST, request.FILES, instance=user)
        profile_form = EditUserProfileForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Thông tin cá nhân đã được cập nhật.')
            return redirect('user_profile')  # Điều hướng về trang hồ sơ cá nhân sau khi chỉnh sửa
        else:
            print(user_form.errors)
            print(profile_form.errors)

    else:
        user_form = EditProfileForm(instance=user)
        profile_form = EditUserProfileForm(instance=profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'edit_profile.html', context)


# @login_required()
# def contest_list(request):
#     # Lọc các cuộc thi đang diễn ra hoặc sắp diễn ra
#     competitions = Competition.objects.filter(
#         is_active=True,
#         end_date__gte=timezone.now()
#     ).order_by('start_date')
#     return render(request, 'contest.html', {'competitions': competitions})


@login_required
def contest_list(request):
    competitions = Competition.objects.filter(is_active=True)
    today = date.today()
    return render(request, 'contest.html', {'competitions': competitions, 'today': today})


@login_required
def competition_detail(request, competition_id):
    competition = get_object_or_404(Competition, id=competition_id)
    today = date.today()
    return render(request, 'competition_detail.html', {
        'competition': competition,
        'today': today
    })


@login_required
def register_competition(request, competition_id):
    competition = get_object_or_404(Competition, id=competition_id)

    # Kiểm tra hạn đăng ký và số lượng thí sinh tối đa
    if competition.registration_deadline >= timezone.now().date() and \
            (competition.max_participants is None or competition.registrations.count() < competition.max_participants):
        registration, created = Registration.objects.get_or_create(
            user=request.user,
            competition=competition,
            defaults={'is_cancelled': False}
        )
        if not created and registration.is_cancelled:
            # Nếu đã có đăng ký nhưng bị hủy, khôi phục đăng ký
            registration.is_cancelled = False
            registration.save()

    return redirect('contest_list')


@login_required
def cancel_registration(request, competition_id):
    competition = get_object_or_404(Competition, id=competition_id)
    registration = get_object_or_404(Registration, competition=competition, user=request.user)
    registration.is_cancelled = True
    registration.save()
    return redirect('contest_list')


@login_required
def add_competition(request):
    if request.method == 'POST':
        form = CompetitionForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('contest_list')  # Chuyển hướng về danh sách các cuộc thi sau khi lưu thành công
    else:
        form = CompetitionForm()
    return render(request, 'add_competition.html', {'form': form})


@login_required
def registration_list(request, competition_id):
    competition = get_object_or_404(Competition, id=competition_id)
    registrations = Registration.objects.filter(competition=competition, is_cancelled=False)  # Lọc đăng ký chưa bị hủy
    context = {
        'competition': competition,
        'registrations': registrations
    }
    return render(request, 'registration_list.html', context)
