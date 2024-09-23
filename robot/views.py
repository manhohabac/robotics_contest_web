from datetime import date

from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout, get_user_model
from .forms import UserRegistrationForm, ChangePasswordForm, EditProfileForm, EditUserProfileForm, CompetitionForm, \
    CompetitionResultForm, KitForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.utils import timezone

from .models import UserProfile, Competition, Registration, Notification, CustomUser, CompetitionResult, Kit, KitDetail


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()  # Lưu người dùng mới

            # Phân biệt user và admin
            if not user.is_superuser:
                login(request, user)  # Tự động đăng nhập cho người dùng thường

                # Tạo thông báo cho người dùng hiện tại (không phải admin)
                Notification.objects.create(
                    user=user,
                    title="Chào mừng đến với ứng dụng quản lý cuộc thi robot",
                    content="Chào mừng bạn đã đến với ứng dụng thông tin quản lý các cuộc thi robot. Hãy bắt đầu khám phá các tính năng!",
                    created_at=timezone.now(),
                    notification_type='user'
                )

            # Tạo thông báo cho admin về người dùng mới
            admin_users = get_user_model().objects.filter(is_superuser=True)  # Lấy danh sách admin
            for admin in admin_users:
                Notification.objects.create(
                    user=admin,
                    title="Thông báo người dùng đăng ký mới",
                    content=f"Người dùng mới {user.full_name} với username {user.username} đã đăng ký thành công tài khoản trên hệ thống.",
                    created_at=timezone.now(),
                    notification_type='admin'
                )

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
def notification_view(request):
    # Lấy danh sách thông báo của người dùng và sắp xếp theo thời gian tạo
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    notifications_unread = notifications.filter(is_read=False).exists()

    # Tạo phân trang với mỗi trang hiển thị 6 thông báo
    paginator = Paginator(notifications, 6)  # Hiển thị 6 thông báo mỗi trang
    page_number = request.GET.get('page')  # Lấy số trang hiện tại từ URL
    page_obj = paginator.get_page(page_number)  # Lấy các thông báo tương ứng với trang hiện tại

    return render(request, 'notification.html', {
        'page_obj': page_obj,  # Thay đổi từ 'notifications' sang 'page_obj'
        'notifications_unread': notifications_unread
    })


@login_required
def mark_as_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    return redirect('notification')


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

                # Change password
                Notification.objects.create(
                    user=user,
                    title="Cập nhật mật khẩu thành công",
                    content="Bạn đã cập nhật thành công mật khẩu mới cho tài khoản của bạn.",
                    notification_type='user',
                    created_at=timezone.now()
                )

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

            # Tạo thông báo cho người dùng hoặc admin dựa trên vai trò
            if user.is_superuser:
                Notification.objects.create(
                    user=user,
                    title="Cập nhật thông tin cá nhân thành công",
                    content="Thông tin cá nhân của admin đã được cập nhật thành công.",
                    created_at=timezone.now(),
                    notification_type='admin'
                )
            else:
                Notification.objects.create(
                    user=user,
                    title="Cập nhật thông tin cá nhân thành công",
                    content="Thông tin cá nhân của bạn đã được cập nhật thành công.",
                    created_at=timezone.now(),
                    notification_type='user'
                )

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


@login_required
def contest_list(request):
    competitions = Competition.objects.filter(is_active=True)
    today = date.today()
    return render(request, 'contest.html', {'competitions': competitions, 'today': today})


@login_required
def competition_detail(request, competition_id):
    competition = get_object_or_404(Competition, id=competition_id)
    today = timezone.now().date()
    registration = Registration.objects.filter(user=request.user, competition=competition).first()
    current_participants = competition.registrations.exclude(is_cancelled=True).count()

    return render(request, 'competition_detail.html', {
        'competition': competition,
        'today': today,
        'registration': registration,
        'current_participants': current_participants,
    })


@login_required
def register_competition(request, competition_id):
    competition = get_object_or_404(Competition, id=competition_id)
    today = timezone.now().date()
    registration = Registration.objects.filter(user=request.user, competition=competition).first()

    if competition.start_date <= today <= competition.registration_deadline:
        current_participants = competition.registrations.exclude(is_cancelled=True).count()
        if competition.max_participants is None or current_participants < competition.max_participants:
            print(f"Max participants: {competition.max_participants}, Current participants: {current_participants}")
            if registration:
                if registration.is_cancelled:
                    # Nếu đã huỷ đăng ký, thông báo không thể đăng ký lại
                    messages.error(request, 'Bạn đã hủy đăng ký và không thể đăng ký lại.')
                else:
                    messages.info(request, 'Bạn đã đăng ký cuộc thi này rồi.')
            else:
                # Tạo đăng ký mới
                registration = Registration.objects.create(user=request.user, competition=competition, is_cancelled=False)
                messages.success(request, 'Đăng ký thành công!')

                # Tạo thông báo cho người dùng
                Notification.objects.create(
                    user=request.user,
                    title="Đăng ký thành công",
                    content=f"Bạn đã đăng ký cuộc thi {competition.name}.",
                    created_at=timezone.now(),
                    notification_type='user'
                )

                # Tạo thông báo cho admin
                ad_users = get_user_model()
                admin_users = ad_users.objects.filter(is_superuser=True)  # Lấy danh sách admin
                for admin in admin_users:
                    Notification.objects.create(
                        user=admin,
                        title="Thông báo đăng ký mới",
                        content=f"Người dùng {request.user.username} đã đăng ký cuộc thi {competition.name}.",
                        created_at=timezone.now(),
                        notification_type='admin'
                    )
        else:
            messages.error(request, 'Số lượng thí sinh đã đầy.')
    else:
        messages.error(request, 'Ngoài khoảng thời gian đăng ký.')

    # Cập nhật context với registration mới
    context = {
        'competition': competition,
        'registration': registration,
        'today': today,
    }

    return render(request, 'competition_detail.html', context)


@login_required
def cancel_registration(request, competition_id):
    competition = get_object_or_404(Competition, id=competition_id)
    registration = get_object_or_404(Registration, competition=competition, user=request.user)

    # Đánh dấu đăng ký là đã huỷ
    registration.is_cancelled = True
    registration.save()

    # Tạo thông báo cho người dùng hiện tại khi hủy đăng ký thành công
    Notification.objects.create(
        user=request.user,
        title="Hủy đăng ký thành công",
        content=f"Bạn đã hủy đăng ký cuộc thi {competition.name}.",
        created_at=timezone.now(),
        notification_type='user'
    )

    # Gửi thông báo cho tất cả các admin về việc hủy đăng ký
    admin_users = get_user_model().objects.filter(is_superuser=True)  # Lấy danh sách admin
    for admin in admin_users:
        Notification.objects.create(
            user=admin,
            title="Người dùng đã hủy đăng ký",
            content=f"Người dùng {request.user.username} đã hủy đăng ký cuộc thi {competition.name}.",
            created_at=timezone.now(),
            notification_type='admin'
        )

    messages.success(request, 'Hủy đăng ký thành công!')
    return redirect('competition_detail', competition_id=competition_id)  # Quay lại trang chi tiết cuộc thi


@login_required
def add_competition(request):
    if request.method == 'POST':
        form = CompetitionForm(request.POST, request.FILES)
        if form.is_valid():
            competition = form.save()
            CustomUser = get_user_model()  # Lấy model CustomUser

            # Tạo thông báo cho tất cả người dùng thường
            users = CustomUser.objects.filter(is_superuser=False)  # Lọc người dùng thường (không phải admin)
            for user in users:
                Notification.objects.create(
                    user=user,
                    title="Cuộc thi mới",
                    content=f"Thông tin về cuộc thi {competition.name} đã chính thức xuất hiện. Hãy tìm hiểu và tham gia ngay!",
                    created_at=timezone.now(),
                    notification_type='user'
                )

            # Tạo thông báo cho admin
            admin_users = CustomUser.objects.filter(is_superuser=True)  # Lấy danh sách admin
            for admin in admin_users:
                Notification.objects.create(
                    user=admin,
                    title=f"Cuộc thi mới {competition.name}",
                    content=f"Cuộc thi {competition.name} đã được {request.user.get_full_name()} tạo.",
                    created_at=timezone.now(),
                    notification_type='admin'
                )

            messages.success(request, f"Cuộc thi '{competition.name}' đã được tạo thành công!")
            return redirect('contest_list')  # Chuyển hướng về danh sách các cuộc thi sau khi lưu thành công
        else:
            # Nếu form không hợp lệ, bạn có thể xử lý lỗi ở đây nếu cần
            print(form.errors)  # In ra lỗi để kiểm tra

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


@login_required
def edit_competition(request, competition_id):
    competition = get_object_or_404(Competition, id=competition_id)

    if request.method == 'POST':
        form = CompetitionForm(request.POST, request.FILES, instance=competition)

        if form.is_valid():
            # Kiểm tra xem người dùng có upload hình ảnh mới không
            new_image = form.cleaned_data.get('new_image')
            if new_image:
                competition.image = new_image  # Cập nhật hình ảnh mới cho cuộc thi

            form.save()  # Lưu lại tất cả các thay đổi khác của form

            # Tạo thông báo cho tất cả người dùng thường
            users = CustomUser.objects.filter(is_superuser=False)  # Lọc người dùng thường (không phải admin)
            for user in users:
                Notification.objects.create(
                    user=user,
                    title="Cuộc thi đã được cập nhật",
                    content=f"Thông tin về cuộc thi {competition.name} đã được cập nhật. Hãy xem thông tin mới!",
                    created_at=timezone.now(),
                    notification_type='user'
                )

            # Gửi thông báo cho admin về việc cuộc thi đã được cập nhật
            admin_users = CustomUser.objects.filter(is_superuser=True)  # Lấy danh sách admin
            for admin in admin_users:
                Notification.objects.create(
                    user=admin,
                    title="Thông tin cuộc thi đã được cập nhật",
                    content=f"Người dùng {request.user.get_full_name()} đã chỉnh sửa thông tin cuộc thi {competition.name}.",
                    created_at=timezone.now(),
                    notification_type='admin'
                )

            messages.success(request, "Cập nhật thông tin cuộc thi thành công.")
            return redirect('competition_detail', competition_id=competition.id)
        else:
            print(form.errors)  # In ra lỗi để kiểm tra

    else:
        form = CompetitionForm(instance=competition)

    return render(request, 'edit_competition.html', {'form': form, 'competition': competition})


@login_required
def delete_competition(request, competition_id):
    competition = get_object_or_404(Competition, id=competition_id)

    if request.method == 'POST':
        competition_name = competition.name  # Lưu lại tên cuộc thi trước khi xóa
        competition.delete()

        # Tạo thông báo cho tất cả người dùng thường
        users = CustomUser.objects.filter(is_superuser=False)  # Lọc người dùng thường (không phải admin)
        for user in users:
            Notification.objects.create(
                user=user,
                title="Cuộc thi đã bị xóa",
                content=f"Cuộc thi {competition_name} đã bị xóa. Hãy theo dõi các cuộc thi khác!",
                created_at=timezone.now(),
                notification_type='user'
            )

        # Tạo thông báo cho admin về việc cuộc thi đã bị xóa
        admin_users = CustomUser.objects.filter(is_superuser=True)  # Lấy danh sách admin
        for admin in admin_users:
            Notification.objects.create(
                user=admin,
                title="Cuộc thi đã bị xóa",
                content=f"Người dùng {request.user.get_full_name()} đã xóa cuộc thi {competition_name}.",
                created_at=timezone.now(),
                notification_type='admin'
            )

        messages.success(request, f"Cuộc thi '{competition_name}' đã được xóa thành công.")
        return redirect('contest_list')

    return render(request, 'delete_competition.html', {'competition': competition})


@login_required
def add_result(request, competition_id):
    competition = get_object_or_404(Competition, id=competition_id)

    if request.method == 'POST':
        form = CompetitionResultForm(request.POST, competition=competition)

        # Kiểm tra nếu thí sinh đã có kết quả
        registration_id = request.POST.get('registration')
        if CompetitionResult.objects.filter(registration_id=registration_id).exists():
            messages.add_message(
                request, messages.ERROR,
                "Thí sinh này đã có kết quả trên hệ thống cho cuộc thi này, không thể thêm mới. Nếu có bất kì sự thay đổi nào xin vui lòng thực hiện chỉnh sửa.",
                extra_tags='duplicate-error'
            )
            return render(request, 'add_result.html', {'form': form, 'competition': competition})

        if form.is_valid():
            result = form.save()

            # Lấy thông tin người dùng tương ứng với kết quả vừa được thêm
            user = result.registration.user

            # Gửi thông báo chỉ đến người dùng đó
            Notification.objects.create(
                user=user,
                title="Kết quả cuộc thi đã được cập nhật",
                content=f"Kết quả của bạn trong cuộc thi {competition.name} đã được cập nhật. Hãy kiểm tra ngay nhé.",
                created_at=timezone.now(),
                notification_type='user'
            )

            # Tự động sắp xếp thứ hạng dựa trên điểm số
            competition_results = CompetitionResult.objects.filter(
                registration__competition=competition
            ).order_by('-score')

            for idx, competition_result in enumerate(competition_results, start=1):
                print(
                    f"{competition_result.registration.user.full_name} - Hạng: {idx} - Điểm: {competition_result.score}"
                )

            return redirect('result_detail', competition_id=competition.id)
    else:
        form = CompetitionResultForm(competition=competition)

    return render(request, 'add_result.html', {'form': form, 'competition': competition})


@login_required
def result_list(request):
    competitions = Competition.objects.all()  # Lấy tất cả các cuộc thi
    return render(request, 'result_list.html', {'competitions': competitions})


@login_required
def result_detail(request, competition_id):
    competition = get_object_or_404(Competition, id=competition_id)
    results = CompetitionResult.objects.filter(registration__competition=competition).order_by('-score')
    return render(request, 'result_detail.html', {'competition': competition, 'results': results})


@login_required
def edit_result(request, result_id):
    result = get_object_or_404(CompetitionResult, id=result_id)
    competition = result.registration.competition

    if request.method == 'POST':
        form = CompetitionResultForm(request.POST, instance=result, competition=competition)
        if form.is_valid():
            form.save()

            # Lấy thông tin người dùng tương ứng với kết quả được cập nhật
            user = result.registration.user

            # Gửi thông báo đến người dùng
            Notification.objects.create(
                user=user,
                title="Kết quả cuộc thi đã được cập nhật",
                content=f"Kết quả của bạn trong cuộc thi {competition.name} đã được cập nhật.",
                created_at=timezone.now(),
                notification_type='user'
            )

            # Tự động sắp xếp thứ hạng dựa trên điểm số sau khi cập nhật
            competition_results = CompetitionResult.objects.filter(
                registration__competition=competition
            ).order_by('-score')

            for idx, competition_result in enumerate(competition_results, start=1):
                print(f"{competition_result.registration.user.full_name} - Hạng: {idx} - Điểm: {competition_result.score}")

            return redirect('result_detail', competition_id=competition.id)
    else:
        form = CompetitionResultForm(instance=result, competition=competition)

    return render(request, 'edit_result.html', {'form': form, 'competition': competition, 'result': result})


def kit_list(request):
    kits = Kit.objects.all()
    return render(request, 'kit_list.html', {'kits': kits})


def kit_detail(request, kit_id):
    kit = get_object_or_404(Kit, id=kit_id)

    if request.method == 'POST':
        # Xử lý tải lên nhiều hình ảnh
        images = request.FILES.getlist('images')
        for image in images:
            KitDetail.objects.create(kit=kit, image=image)
        messages.success(request, 'Hình ảnh chi tiết đã được thêm thành công!')
        return redirect('kit_detail', kit_id=kit.id)

    kit_details = kit.details.all()
    return render(request, 'kit_detail.html', {'kit': kit, 'kit_details': kit_details})


def add_kit(request):
    if request.method == 'POST':
        form = KitForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Bộ thiết bị đã được thêm!')
            return redirect('kit_list')
    else:
        form = KitForm()

    return render(request, 'add_kit.html', {'form': form})


def edit_kit(request, kit_id):
    kit = get_object_or_404(Kit, id=kit_id)
    if request.method == 'POST':
        form = KitForm(request.POST, request.FILES, instance=kit)
        if form.is_valid():
            form.save()
            messages.success(request, 'Bộ thiết bị đã được chỉnh sửa!')
            return redirect('kit_detail', kit_id=kit.id)
    else:
        form = KitForm(instance=kit)

    return render(request, 'edit_kit.html', {'form': form, 'kit': kit})


def delete_kit(request, kit_id):
    kit = get_object_or_404(Kit, id=kit_id)
    if request.method == 'POST':
        kit.delete()
        messages.success(request, 'Bộ thiết bị đã được xóa!')
        return redirect('kit_list')

    return render(request, 'delete_kit.html', {'kit': kit})

