from datetime import date, datetime
from io import BytesIO

import openpyxl
from django.core.files.base import ContentFile
from openpyxl.drawing.image import Image as OpenPyXLImage
import os
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout, get_user_model
from django.utils.timezone import make_naive
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from PIL import Image
import io

from .forms import UserRegistrationForm, ChangePasswordForm, EditProfileForm, EditUserProfileForm, CompetitionForm, \
    CompetitionResultForm, KitForm, KitImageForm, SponsorForm, FeedbackForm, GuideFileForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.utils import timezone

from .models import UserProfile, Competition, Registration, Notification, CustomUser, CompetitionResult, Kit, Sponsor, \
    Feedback, GuideFile


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

    return render(request, 'account/register.html', {'form': form})


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
    return render(request, 'account/login.html', {'form': form})


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

    # Tạo phân trang với mỗi trang hiển thị 7 thông báo
    paginator = Paginator(notifications, 7)  # Hiển thị 7 thông báo mỗi trang
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

    # Trả về phản hồi JSON để AJAX có thể xử lý
    return JsonResponse({'status': 'success'})


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

    return render(request, 'account/change_password.html', {'form': form})


@login_required
def user_profile(request):
    user = request.user
    # Kiểm tra và tạo UserProfile nếu chưa tồn tại
    profile, created = UserProfile.objects.get_or_create(user=user)

    context = {
        'profile': profile,
    }
    return render(request, 'profile/user_profile.html', context)


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
    return render(request, 'profile/edit_profile.html', context)


@login_required
def contest_list(request):
    competitions = Competition.objects.filter(is_active=True)
    today = date.today()
    return render(request, 'competition/contest.html', {'competitions': competitions, 'today': today})


@login_required
def competition_detail(request, competition_id):
    competition = get_object_or_404(Competition, id=competition_id)
    today = timezone.now().date()
    registration = Registration.objects.filter(user=request.user, competition=competition).first()
    current_participants = competition.registrations.exclude(is_cancelled=True).count()

    return render(request, 'competition/competition_detail.html', {
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

    return render(request, 'competition/competition_detail.html', context)


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

    return render(request, 'competition/add_competition.html', {'form': form})


@login_required
def registration_list(request, competition_id):
    competition = get_object_or_404(Competition, id=competition_id)
    registrations = Registration.objects.filter(competition=competition, is_cancelled=False)  # Lọc đăng ký chưa bị hủy
    context = {
        'competition': competition,
        'registrations': registrations
    }
    return render(request, 'competition/registration_list.html', context)


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

    return render(request, 'competition/edit_competition.html', {'form': form, 'competition': competition})


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

    return render(request, 'competition/delete_competition.html', {'competition': competition})


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
            return render(request, 'result/add_result.html', {'form': form, 'competition': competition})

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

    return render(request, 'result/add_result.html', {'form': form, 'competition': competition})


@login_required
def result_list(request):
    competitions = Competition.objects.all()  # Lấy tất cả các cuộc thi
    return render(request, 'result/result_list.html', {'competitions': competitions})


@login_required
def result_detail(request, competition_id):
    competition = get_object_or_404(Competition, id=competition_id)
    results = CompetitionResult.objects.filter(registration__competition=competition).order_by('-score')
    return render(request, 'result/result_detail.html', {'competition': competition, 'results': results})


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

    return render(request, 'result/edit_result.html', {'form': form, 'competition': competition, 'result': result})


@login_required
def kit_list(request):
    kits = Kit.objects.all()
    return render(request, 'kit/kit_list.html', {'kits': kits})


@login_required
def kit_create(request):
    if request.method == 'POST':
        form = KitForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Bộ thiết bị đã được tạo thành công.')
            return redirect('kit_list')
    else:
        form = KitForm()
    return render(request, 'kit/kit_form.html', {'form': form})


@login_required
def kit_update(request, pk):
    kit = get_object_or_404(Kit, pk=pk)  # Sử dụng get_object_or_404 để đảm bảo an toàn
    if request.method == 'POST':
        form = KitForm(request.POST, request.FILES, instance=kit)
        if form.is_valid():
            form.save()
            messages.success(request, 'Bộ thiết bị đã được cập nhật thành công.')
            return redirect('kit_list')
    else:
        form = KitForm(instance=kit)  # Đảm bảo giữ giá trị hiện tại

    return render(request, 'kit/kit_form.html', {'form': form, 'kit': kit})


@login_required
def kit_delete(request, pk):
    kit = Kit.objects.get(pk=pk)
    if request.method == 'POST':
        kit.delete()
        messages.success(request, 'Bộ thiết bị đã bị xóa thành công.')
        return redirect('kit_list')
    return render(request, 'kit/delete_kit.html', {'kit': kit})


@login_required
def kit_detail(request, pk):
    kit = get_object_or_404(Kit, pk=pk)
    images = kit.images.all()  # Lấy tất cả hình ảnh liên quan đến bộ kit

    if request.method == 'POST':
        image_form = KitImageForm(request.POST, request.FILES)
        if image_form.is_valid():
            new_image = image_form.save(commit=False)
            new_image.kit = kit  # Gán hình ảnh vào bộ kit
            new_image.save()
            return redirect('kit_detail', pk=pk)  # Reload lại trang sau khi upload
    else:
        image_form = KitImageForm()

    return render(request, 'kit/kit_detail.html', {'kit': kit, 'images': images, 'image_form': image_form})


@login_required
def add_image(request, kit_id):
    kit = get_object_or_404(Kit, id=kit_id)

    if request.method == 'POST':
        form = KitImageForm(request.POST, request.FILES)
        if form.is_valid():
            kit_image = form.save(commit=False)
            kit_image.kit = kit
            kit_image.save()
            return redirect('kit_detail', pk=kit.id)  # Chuyển hướng sau khi upload thành công
    else:
        form = KitImageForm()

    return render(request, 'kit/add_image.html', {'form': form, 'kit': kit})


@login_required
def sponsor_list(request):
    sponsors = Sponsor.objects.all()
    return render(request, 'sponsor/sponsor_list.html', {'sponsors': sponsors})


@login_required
def add_sponsor(request):
    if request.method == 'POST':
        form = SponsorForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('sponsor_list')
    else:
        form = SponsorForm()
    return render(request, 'sponsor/add_sponsor.html', {'form': form})


@login_required
def edit_sponsor(request, sponsor_id):
    sponsor = get_object_or_404(Sponsor, id=sponsor_id)
    if request.method == 'POST':
        form = SponsorForm(request.POST, request.FILES, instance=sponsor)
        if form.is_valid():
            form.save()
            return redirect('sponsor_list')  # Redirect đến danh sách nhà tài trợ
    else:
        form = SponsorForm(instance=sponsor)
    return render(request, 'sponsor/edit_sponsor.html', {'form': form})


@login_required
def delete_sponsor(request, sponsor_id):
    sponsor = get_object_or_404(Sponsor, id=sponsor_id)
    if request.method == 'POST':
        sponsor.delete()
        return redirect('sponsor_list')  # Redirect đến danh sách nhà tài trợ
    return render(request, 'sponsor/delete_sponsor.html', {'sponsor': sponsor})


@login_required
def submit_feedback(request):
    if request.method == "POST":
        form = FeedbackForm(request.POST, request.FILES)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.user = request.user

            # Xử lý ảnh
            if feedback.image:
                try:
                    img = Image.open(feedback.image)
                    img = img.convert('RGB')  # Chuyển đổi sang RGB

                    # Lưu vào một buffer
                    img_byte_arr = io.BytesIO()
                    img.save(img_byte_arr, format='JPEG')  # Lưu ảnh dưới dạng JPEG
                    img_byte_arr.seek(0)

                    # Tạo một ContentFile từ buffer
                    feedback.image.save(f"{feedback.image.name}.jpg", ContentFile(img_byte_arr.read()), save=False)
                except Exception as e:
                    form.add_error('image', 'Lỗi khi xử lý hình ảnh: ' + str(e))
                    messages.error(request, "Có lỗi xảy ra khi xử lý hình ảnh.")
                    return render(request, 'feedback/submit_feedback.html', {'form': form})

            feedback.save()
            messages.success(request, "Phản hồi của bạn đã được gửi thành công!")
            return redirect('home')  # Chuyển hướng về trang home sau khi gửi phản hồi
        else:
            # In ra lỗi để dễ debug
            print(form.errors)  # In ra các lỗi của form trong console
            messages.error(request, "Có lỗi xảy ra khi gửi phản hồi. Vui lòng kiểm tra lại.")
    else:
        form = FeedbackForm()

    return render(request, 'feedback/submit_feedback.html', {'form': form})


@login_required
def feedback_list(request):
    if request.user.is_superuser:
        feedback_list = Feedback.objects.all().order_by('-created_at')
        return render(request, 'feedback/feedback_list.html', {'feedback_list': feedback_list})
    else:
        messages.error(request, "Bạn không có quyền truy cập vào trang này.")
        return redirect('home')


@login_required
def export_feedback_to_excel(request):
    # Lấy danh sách phản hồi (feedback)
    feedback_list = Feedback.objects.all().order_by('-created_at')

    # Tạo workbook và worksheet
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Feedback Report"

    # Đặt font mặc định cho toàn bộ bảng (size 14)
    default_font = Font(size=14)

    # Đặt tiêu đề cột với font bôi đậm và kích thước 14, không có màu nền
    columns = ['STT', 'Chủ đề', 'Nội dung phản hồi', 'Đánh giá', 'Hình ảnh', 'Ngày phản hồi', 'Trạng thái']

    # Đảm bảo bôi đậm tiêu đề cột với font đậm và không có màu nền
    for col_num, column_title in enumerate(columns, start=1):
        cell = ws.cell(row=1, column=col_num, value=column_title)
        cell.font = Font(bold=True, size=14, color='000000')  # Đặt font đậm, size 14, không có màu nền
        cell.alignment = Alignment(horizontal='center', vertical='center')  # Căn giữa tiêu đề

    # Thêm dữ liệu vào bảng từ dòng thứ hai
    for index, feedback in enumerate(feedback_list, start=1):
        created_at_naive = make_naive(feedback.created_at)  # Chuyển timezone-aware datetime thành timezone-naive
        row = [
            index,
            feedback.subject,
            feedback.content.replace('\r\n', '\n'),  # Thay thế xuống dòng
            feedback.rating,
            '',
            created_at_naive.strftime("%d/%m/%Y"),
            'Đã xem' if feedback.is_viewed else 'Chưa xem'
        ]
        ws.append(row)

        # Đảm bảo nội dung phản hồi được wrap text
        ws.cell(row=index + 1, column=3).alignment = Alignment(wrap_text=True)  # Cột "Nội dung phản hồi"

        # Nếu có hình ảnh, thêm vào ô tương ứng
        if feedback.image:
            img_path = feedback.image.path
            if os.path.exists(img_path):
                img = OpenPyXLImage(img_path)

                # Điều chỉnh kích thước ảnh
                img.width = 300  # Xác định chiều rộng ảnh
                img.height = 200  # Xác định chiều cao ảnh

                # Thêm hình ảnh vào ô (cột 5 là "Hình ảnh")
                ws.add_image(img, f'E{index + 1}')

                # Cố định độ cao hàng dựa trên chiều cao của ảnh (1 đơn vị = 0.75 pixel)
                row_height = img.height * 0.75  # Chuyển đổi chiều cao ảnh sang đơn vị hàng
                ws.row_dimensions[index + 1].height = row_height  # Điều chỉnh độ cao hàng

    # Đặt độ rộng fix cứng cho cột "Hình ảnh"
    ws.column_dimensions['E'].width = 45  # 45 tương đương với khoảng 270 pixels

    # Điều chỉnh độ rộng các cột khác dựa trên dữ liệu
    for col_num, column_cells in enumerate(ws.columns, 1):
        col_letter = get_column_letter(col_num)

        # Lấy độ dài lớn nhất giữa tiêu đề cột và dữ liệu trong cột đó
        max_length = max([len(str(cell.value)) if cell.value else 0 for cell in column_cells])

        # Đặt độ rộng cho cột, cộng thêm 2 để dễ nhìn
        if col_letter != 'E':  # Trừ cột E vì đã fix cứng độ rộng
            ws.column_dimensions[col_letter].width = max_length + 2

        # Cập nhật kích thước chữ và căn giữa cho từng ô
        for cell in column_cells:
            cell.font = default_font  # Tăng kích thước chữ lên 14 cho toàn bộ dữ liệu
            cell.alignment = Alignment(horizontal='center', vertical='center')  # Căn giữa toàn bộ dữ liệu

    # Tạo một BytesIO để lưu workbook
    output = BytesIO()
    wb.save(output)  # Ghi workbook vào BytesIO
    output.seek(0)  # Đặt con trỏ về đầu để có thể đọc từ đầu

    # Tạo tên file theo ngày tháng
    filename = f"feedback_report_{datetime.now().strftime('%d-%m-%Y')}.xlsx"

    # Thiết lập phản hồi HTTP để trả file Excel về cho người dùng
    response = HttpResponse(output.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response['Content-Disposition'] = f'attachment; filename={filename}'

    # Reset lại dữ liệu phản hồi sau khi xuất ra file
    feedback_list.delete()

    return response


@login_required
def toggle_viewed_status(request, feedback_id):
    feedback = get_object_or_404(Feedback, id=feedback_id)

    if request.method == 'POST':
        # Đảo ngược giá trị của is_viewed
        feedback.is_viewed = not feedback.is_viewed
        feedback.save()

        # Trả về JSON với trạng thái mới
        return JsonResponse({'is_viewed': feedback.is_viewed})

    # Nếu không phải POST, trả về lỗi không hợp lệ
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def export_registrations_to_excel(request, competition_id):
    competition = get_object_or_404(Competition, id=competition_id)
    registrations = Registration.objects.filter(competition=competition, is_cancelled=False)

    # Tạo workbook và worksheet
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = f'Danh sách đăng ký {competition.name}'[:31]  # Giới hạn 31 ký tự

    # Thêm tiêu đề cột với bôi đậm
    columns = ['STT', 'Họ và tên', 'Ngày sinh', 'Tên trường', 'Ngày đăng ký']
    ws.append(columns)

    # Bôi đậm tiêu đề
    for cell in ws[1]:  # Dòng đầu tiên chứa tiêu đề
        cell.font = Font(bold=True, size=14)
        cell.alignment = Alignment(horizontal='center', vertical='center')

    # Thêm dữ liệu vào file Excel
    for idx, registration in enumerate(registrations, start=1):
        row = [
            idx,
            registration.user.full_name,
            registration.user.date_of_birth.strftime('%d/%m/%Y'),
            registration.user.school_name,
            registration.registration_date.strftime('%d/%m/%Y')
        ]
        ws.append(row)

        # Căn giữa cho từng ô trong hàng
        for cell in ws[idx + 1]:  # idx + 1 vì hàng đầu tiên là tiêu đề
            cell.alignment = Alignment(horizontal='center', vertical='center')

    # Điều chỉnh độ rộng của cột theo nội dung
    for column_cells in ws.columns:
        length = max(len(str(cell.value)) for cell in column_cells)
        ws.column_dimensions[column_cells[0].column_letter].width = length + 2

    # Điều chỉnh chiều cao của hàng
    for row in ws.iter_rows():
        ws.row_dimensions[row[0].row].height = 20  # Thiết lập chiều cao hàng là 20 (tùy chỉnh)

    # Lưu workbook vào một đối tượng file ảo
    file_stream = io.BytesIO()
    wb.save(file_stream)
    file_stream.seek(0)  # Đặt con trỏ đọc file về đầu

    # Thiết lập response để tải về file Excel
    response = HttpResponse(file_stream,
                            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename=Danh_sach_dang_ky_{competition.name}.xlsx'

    return response


@login_required
def export_results_to_excel(request, competition_id):
    competition = get_object_or_404(Competition, id=competition_id)
    results = CompetitionResult.objects.filter(registration__competition=competition).order_by('-score')

    # Tạo workbook và worksheet
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = f'Kết quả {competition.name}'[:31]  # Giới hạn 31 ký tự

    # Thêm tiêu đề cột
    columns = ['Thứ hạng', 'Thí sinh', 'Ngày sinh', 'Học sinh trường', 'Điểm số']
    ws.append(columns)

    # Bôi đậm và căn giữa tiêu đề cột
    for cell in ws[1]:  # ws[1] là hàng tiêu đề (hàng đầu tiên)
        cell.font = Font(bold=True, size=14)  # Bôi đậm
        cell.alignment = Alignment(horizontal='center', vertical='center')  # Căn giữa

    # Thêm dữ liệu vào file Excel
    for idx, result in enumerate(results, start=1):
        row = [
            idx,
            result.registration.user.full_name,
            result.registration.user.date_of_birth.strftime('%d/%m/%Y'),
            result.registration.user.school_name,
            result.score
        ]
        ws.append(row)

    # Căn giữa nội dung các ô
    for row in ws.iter_rows(min_row=2, max_row=ws.max_row):  # Bắt đầu từ hàng thứ 2 để bỏ qua tiêu đề
        for cell in row:
            cell.alignment = Alignment(horizontal='center', vertical='center')  # Căn giữa

    # Điều chỉnh độ rộng của cột theo nội dung
    for column_cells in ws.columns:
        length = max(len(str(cell.value)) for cell in column_cells)
        ws.column_dimensions[column_cells[0].column_letter].width = length + 2

    # Lưu workbook vào một đối tượng file ảo
    file_stream = io.BytesIO()
    wb.save(file_stream)
    file_stream.seek(0)  # Đặt con trỏ đọc file về đầu

    # Thiết lập response để tải về file Excel
    response = HttpResponse(file_stream,
                            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename=Ket_qua_{competition.name}.xlsx'

    return response


@login_required
def competition_guide(request, competition_id):
    competition = get_object_or_404(Competition, id=competition_id)

    if request.method == 'POST':
        guide_file = request.FILES.get('guide_file')
        note = request.POST.get('note')  # Lấy ghi chú từ form
        if guide_file:
            GuideFile.objects.create(competition=competition, file=guide_file, note=note)
            return redirect('competition_guide', competition_id=competition.id)

    guide_files = competition.guide_files.all()  # Lấy tất cả tài liệu hướng dẫn liên kết với cuộc thi

    # Tạo thuộc tính tên tệp cho từng guide_file
    for guide_file in guide_files:
        guide_file.file_name = os.path.basename(guide_file.file.name)

    return render(request, 'competition/competition_guide.html',
                  {'competition': competition, 'guide_files': guide_files})


@login_required
def edit_guide_file(request, pk):
    guide_file = get_object_or_404(GuideFile, pk=pk)

    if request.method == 'POST':
        form = GuideFileForm(request.POST, request.FILES, instance=guide_file)

        if form.is_valid():
            # Lưu ghi chú
            guide_file.note = form.cleaned_data['note']

            # Kiểm tra xem có tệp mới không
            if 'file' in request.FILES and request.FILES['file']:
                guide_file.file = request.FILES['file']  # Cập nhật tệp mới

            guide_file.save()  # Lưu thay đổi
            return redirect('competition_guide', competition_id=guide_file.competition.id)
    else:
        form = GuideFileForm(instance=guide_file)

    # Trích xuất tên tệp hiện tại
    current_file_name = os.path.basename(guide_file.file.name) if guide_file.file else "Chưa có tệp"

    return render(request, 'competition/edit_guide_file.html', {
        'form': form,
        'guide_file': guide_file,
        'current_file_name': current_file_name  # Thêm biến tên tệp vào ngữ cảnh
    })


@login_required
def delete_guide_file(request, pk):
    guide_file = get_object_or_404(GuideFile, pk=pk)
    competition_id = guide_file.competition.id
    guide_file.delete()
    return redirect('competition_guide', competition_id=competition_id)
